from datasets import load_dataset

# Replace old dataset loading
dataset = load_dataset("json", data_files={"train": "train.jsonl"})["train"]

# Tokenization function
def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=512
    )

dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])