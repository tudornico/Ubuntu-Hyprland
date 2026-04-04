# prepare_openai_model_ready.py
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

# ==========================
# CONFIG
# ==========================
MODEL_NAME = "mistralai/Mistral-7B-v0.1"
DATA_FILE = "train.jsonl"  # your local dataset
OUTPUT_DIR = "./qlora_output"
FINAL_DIR = "./final_model"

MAX_LENGTH = 512
BATCH_SIZE = 32
GRAD_ACCUM = 8
EPOCHS = 3
LR = 2e-4

# ==========================
# 4-BIT CONFIG
# ==========================
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
# BASE MODEL
# ==========================
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto"
)
model.gradient_checkpointing_enable()
model.config.use_cache = False

# ==========================
# LORA CONFIG
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
dataset = load_dataset("json", data_files={"train": DATA_FILE})["train"]

def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH
    )

dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

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
    fp16=True,
    optim="paged_adamw_8bit",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator
)

# ==========================
# TRAIN + MERGE + SAVE
# ==========================
if __name__ == "__main__":
    print("Starting training...")
    trainer.train()

    print("Saving LoRA adapter...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("Reloading base model for merge...")
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    print("Merging LoRA weights...")
    merged_model = PeftModel.from_pretrained(base_model, OUTPUT_DIR)
    merged_model = merged_model.merge_and_unload()

    print("Saving FINAL standalone model...")
    merged_model.save_pretrained(FINAL_DIR)
    tokenizer.save_pretrained(FINAL_DIR)

    print("Model is ready at:", FINAL_DIR)

    # ==========================
    # QUICK INFERENCE TEST
    # ==========================
    prompt = """### Instruction:
Extract legal entities from this Romanian text.

### Input:
HOTĂRÂRE nr. 402 din 2022 privind aprobarea...

### Response:
"""
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = merged_model.generate(**inputs, max_new_tokens=150, temperature=0.2)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))