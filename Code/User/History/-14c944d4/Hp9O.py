import os
from datasets import load_dataset, DatasetDict

# =======================
# Paths
# =======================
# Get current script directory
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# JSONL file (relative path)
DATA_FILE = os.path.join(DATA_DIR, "train.jsonl")

# =======================
# Column names
# =======================
# Your dataset columns: file_name, words, ner
column_names = ["file_name", "words", "ner"]

# =======================
# Load dataset
# =======================
dataset = load_dataset(
    "json",
    data_files={"train": DATA_FILE},
    field=None  # each line is a full JSON object
)

# Convert to DatasetDict
dataset_dict = DatasetDict({
    "train": dataset["train"]
})

# =======================
# Verify dataset
# =======================
print("Columns:", dataset_dict["train"].column_names)
print("Number of examples:", len(dataset_dict["train"]))
print("First example:", dataset_dict["train"][0])

# =======================
# Optional: quick inspection
# =======================
# Print first 3 examples
for i, example in enumerate(dataset_dict["train"][:3]):
    print(f"\nExample {i}:")
    print("file_name:", example["file_name"])
    print("words:", example["words"])
    print("ner:", example["ner"])