import os
from datasets import load_dataset, DatasetDict, Features, Sequence, Value
from transformers import AutoTokenizer

# =======================
# Paths
# =======================
# Directory of this script
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# JSONL dataset path
DATA_FILE = os.path.join(DATA_DIR, "train.jsonl")

# =======================
# Define dataset features
# =======================
features = Features({
    "file_name": Value("string"),       # document identifier
    "words": Sequence(Value("string")), # list of tokens
    "ner": Sequence(Value("string"))    # IOB tags
})

# =======================
# Load JSONL dataset
# =======================
dataset = load_dataset(
    "json",
    data_files={"train": DATA_FILE},
    features=features
)

# Wrap in DatasetDict
dataset_dict = DatasetDict({"train": dataset["train"]})

# =======================
# Verify dataset
# =======================
print("Columns:", dataset_dict["train"].column_names)
print("Number of examples:", len(dataset_dict["train"]))
print("First example:", dataset_dict["train"][0])

# =======================
# Inspect first 3 examples
# =======================
for i, example in enumerate(dataset_dict["train"][:3]):
    print(f"\nExample {i}:")
    print("file_name:", example["file_name"])
    print("words:", example["words"])
    print("ner:", example["ner"])

# =======================
# Tokenization and Label Alignment
# =======================
# Example: using a multilingual or Greek tokenizer
# Replace with any transformer tokenizer you will use (Mistral-7B might require custom tokenizer)
TOKENIZER_NAME = "bert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME, use_fast=True)

# Define label list
label_list = ['O', 'B-TIME', 'I-TIME', 'B-LEGAL', 'I-LEGAL',
              'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC', 'B-PER', 'I-PER']
label_to_id = {label: i for i, label in enumerate(label_list)}

# Function to tokenize and align labels
def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(examples["words"], 
                                 is_split_into_words=True,
                                 truncation=True,
                                 padding=False)
    
    labels = []
    for i, word_ids in enumerate(tokenized_inputs.word_ids(batch_index=0)):
        example_labels = []
        prev_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                example_labels.append(-100)  # special tokens
            else:
                label_str = examples["ner"][word_idx]
                # If a word is split into multiple tokens, label first subword as normal, rest as -100
                if word_idx != prev_word_idx:
                    example_labels.append(label_to_id[label_str])
                else:
                    example_labels.append(-100)
                prev_word_idx = word_idx
        labels.append(example_labels)
    tokenized_inputs["labels"] = labels[0]  # batch_index=0
    return tokenized_inputs

# Apply tokenization to first example (for demonstration)
sample_example = dataset_dict["train"][0]
tokenized_example = tokenize_and_align_labels(sample_example)
print("\nTokenized example keys:", tokenized_example.keys())
print("Input IDs:", tokenized_example["input_ids"])
print("Labels:", tokenized_example["labels"])

# =======================
# Notes
# =======================
# - dataset_dict["train"] is ready for training.
# - You can map `tokenize_and_align_labels` over the entire dataset for full preprocessing:
#   tokenized_dataset = dataset_dict.map(tokenize_and_align_labels, batched=False)
# - Label alignment handles subword tokens with -100 for ignored positions.
# - Ready for Hugging Face Trainer or custom fine-tuning loop with Mistral-7B.