# use_model.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_PATH = "./final_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto"
)

prompt = """### Instruction:
Extract legal entities from this Romanian text.

### Input:
HOTĂRÂRE nr. 402 din 2022 privind aprobarea unui act legislativ.

### Response:
"""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.2)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))