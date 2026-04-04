import json
from datasets import load_dataset

OUTPUT_FILE = "legalnero_llm_train.jsonl"

dataset = load_dataset("joelniklaus/legalnero", split="train")

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


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for example in dataset:
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

print("Dataset created:", OUTPUT_FILE)