# mistral7b_lora_cpu_safe.py
import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, PeftModel

# ==========================
# DEVICE SETUP (CPU SAFE)
# ==========================
DEVICE = "cpu"
print(f"Using device: {DEVICE}")

# Reduce memory fragmentation
os.environ["PYTORCH_ALLOC_CONF"] = "max_split_size_mb:64,garbage_collection_threshold:0.6"

# ==========================
# CONFIG
# ==========================
MODEL_NAME = "mistralai/Mistral-7B-v0.1"
DATA_FILE = "/.venv_gpu/train.jsonl"
OUTPUT_DIR = "./qlora_output"
FINAL_DIR = "./final_model"

MAX_LENGTH = 128
BATCH_SIZE = 1
GRAD_ACCUM = 8
EPOCHS = 3
LR = 2e-4

# ==========================
# TOKENIZER
# ==========================
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

# ==========================
# LOAD MODEL (CPU)
# ==========================
print("Loading Mistral-7B on CPU...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map={"": "cpu"},  # force CPU for all layers
    torch_dtype=torch.float32,  # full precision
    low_cpu_mem_usage=True
)
model.gradient_checkpointing_enable()
model.config.use_cache = False

# ==========================
# APPLY LoRA (CPU)
# ==========================
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

# ==========================
# LOAD DATASET
# ==========================
print("Loading dataset...")
dataset = load_dataset("json", data_files={"train": DATA_FILE})["train"]

def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        max_length=MAX_LENGTH
    )

dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])

# ==========================
# DATA COLLATOR
# ==========================
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# ==========================
# TRAINING ARGUMENTS
# ==========================
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM,
    num_train_epochs=EPOCHS,
    learning_rate=LR,
    logging_steps=10,
    save_strategy="epoch",
    fp16=False,             # CPU training, no fp16
    optim="adamw_torch",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator
)

# ==========================
# TRAIN + SAVE LoRA
# ==========================
if __name__ == "__main__":
    print("Starting training on CPU...")
    trainer.train()

    print("Saving LoRA adapter...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # Free memory
    torch.cuda.empty_cache()

    print("Reloading base model for merge...")
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map={"": "cpu"},
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    )

    print("Merging LoRA weights into base model...")
    merged_model = PeftModel.from_pretrained(base_model, OUTPUT_DIR)
    merged_model = merged_model.merge_and_unload()
    merged_model.to(DEVICE)

    print("Saving FINAL standalone model...")
    merged_model.save_pretrained(FINAL_DIR)
    tokenizer.save_pretrained(FINAL_DIR)
    print("Model ready at:", FINAL_DIR)

    # ==========================
    # QUICK INFERENCE TEST
    # ==========================
    prompt = """### Instruction:
Extract legal entities from this Romanian text.

### Input:
HOTĂRÂRE nr. 402 din 2022 privind aprobarea...

### Response:
"""
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    outputs = merged_model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.2
    )
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))