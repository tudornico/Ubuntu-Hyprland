# prepare_dataset.py
from datasets import load_dataset

DATA_FILE = "train.jsonl"

print("Loading dataset from local JSONL file...")
dataset = load_dataset("json", data_files={"train": DATA_FILE})

print("Dataset loaded:")
print(dataset)