import os
from datasets import load_dataset, DatasetDict

# =======================
# Paths
# =======================
# Get the directory of the current script
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the JSONL file (relative to script directory)
DATA_FILE = os.path.join(DATA_DIR, "train.jsonl")

# =======================
# Load JSONL dataset
# =======================
# Important: lines=True is required for JSONL files
dataset = load_dataset(
    "json",
    data_files={"train": DATA_FILE},
    lines=True
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
# Quick inspection: print first 3 examples
# =======================
for i, example in enumerate(dataset_dict["train"][:3]):
    print(f"\nExample {i}:")
    print("file_name:", example["file_name"])
    print("words:", example["words"])
    print("ner:", example["ner"])

# =======================
# Notes
# =======================
# Your dataset columns are:
# - file_name: filename of the annotated document
# - words: list of Greek tokens (spacy tokenizer)
# - ner: list of NER tags in IOB format
# Supported NER tags: ['O', 'B-TIME', 'I-TIME', 'B-LEGAL', 'I-LEGAL',
#                       'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC', 'B-PER', 'I-PER']
# The dataset is now fully loaded and ready for tokenization and model training.