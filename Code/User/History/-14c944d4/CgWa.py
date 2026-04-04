# mistral7b_lora_train_safe.py
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, PeftModel
import os

# ==========================
# DEVICE DETECTION
# ==========================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# Avoid CUDA memory fragmentation if GPU
if DEVICE == "cuda":
    os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

# ==========================
# CONFIG
# ==========================
MODEL_NAME = "mistralai/Mistral-7B-v0.1"
DATA_FILE = "train.jsonl"
OUTPUT_DIR = "./qlora_output"
FINAL_DIR = "./final_model"

MAX_LENGTH = 128       # safe for 11GB GPU
BATCH_SIZE = 1         # per-device batch size
GRAD_ACCUM = 8
EPOCHS = 3
LR = 2e-4

# ==========================
# 4-BIT CONFIG (GPU only)
# ==========================
bnb_config = None
if DEVICE == "cuda":
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16
    )

# ==========================
# TOKENIZER
# ==========================
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

# ==========================
# LOAD MODEL
# ==========================
print("Loading model...")
model_kwargs = {"device_map": "auto"} if DEVICE == "cuda" else {}
if bnb_config:
    model_kwargs["quantization_config"] = bnb_config

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    **model_kwargs
)
model.gradient_checkpointing_enable()
model.config.use_cache = False

# ==========================
# APPLY LoRA
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

# Free GPU memory after LoRA setup
if DEVICE == "cuda":
    torch.cuda.empty_cache()

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

# Dynamic padding
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
    pad_to_multiple_of=None
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
    fp16=False if DEVICE == "cuda" else False,
    optim="paged_adamw_8bit" if DEVICE == "cuda" else "adamw_torch",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator
)

# ==========================
# TRAIN + SAVE
# ==========================
if __name__ == "__main__":
    print("Starting training...")
    trainer.train()

    print("Saving LoRA adapter...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # Free memory before merge
    if DEVICE == "cuda":
        torch.cuda.empty_cache()

    print("Reloading base model for merge...")
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        device_map="auto" if DEVICE == "cuda" else None
    )

    print("Merging LoRA weights...")
    merged_model = PeftModel.from_pretrained(base_model, OUTPUT_DIR)
    merged_model = merged_model.merge_and_unload()

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