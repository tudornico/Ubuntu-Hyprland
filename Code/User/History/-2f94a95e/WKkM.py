import requests
import json
import time

# ==============================
# CONFIG
# ==============================

DATASET_API = "https://datasets-server.huggingface.co/rows"
DATASET_NAME = "joelniklaus/legalnero"
CONFIG = "default"
SPLIT = "train"

BATCH_SIZE = 100      # API limit chunk
OUTPUT_FILE = "legalnero_llm_train.jsonl"

# ==============================
# ENTITY EXTRACTION FUNCTION
# ==============================

def extract_entities(words, tags):
    entities = {}
    current_entity = []
    current_label = None

    for word, tag in zip(words, tags):
        if tag.startswith("B-"):
            if current_entity:
                entities.setdefault(current_label, []).append(" ".join(current_entity))
            current_entity = [word]
            current_label = tag[2:]

        elif tag.startswith("I-") and current_label == tag[2:]:
            current_entity.append(word)

        else:
            if current_entity:
                entities.setdefault(current_label, []).append(" ".join(current_entity))
                current_entity = []
                current_label = None

    if current_entity:
        entities.setdefault(current_label, []).append(" ".join(current_entity))

    return entities

# ==============================
# FETCH DATA VIA API
# ==============================

def fetch_batch(offset, length):
    params = {
        "dataset": DATASET_NAME,
        "config": CONFIG,
        "split": SPLIT,
        "offset": offset,
        "length": length
    }

    response = requests.get(DATASET_API, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

# ==============================
# BUILD LLM DATASET
# ==============================

def build_dataset():
    offset = 0
    total_written = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        while True:
            print(f"Fetching rows {offset} → {offset + BATCH_SIZE}")
            data = fetch_batch(offset, BATCH_SIZE)

            rows = data.get("rows", [])
            if not rows:
                break

            for row in rows:
                example = row["row"]
                words = example["words"]
                tags = example["ner"]

                text = " ".join(words)
                entities = extract_entities(words, tags)

                formatted = {
                    "text": f"""### Instruction:
Extract all legal entities from the Romanian legal text.

### Input:
{text}

### Response:
{json.dumps(entities, ensure_ascii=False)}"""
                }

                f.write(json.dumps(formatted, ensure_ascii=False) + "\n")
                total_written += 1

            offset += BATCH_SIZE
            time.sleep(0.5)  # polite delay

    print(f"\nDataset created: {OUTPUT_FILE}")
    print(f"Total examples written: {total_written}")

# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    build_dataset()