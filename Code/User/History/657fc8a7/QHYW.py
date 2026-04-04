from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_path = "./final_model"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

prompt = """### Instruction:
Extract legal entities.

### Input:
HOTĂRÂRE nr. 402 din 2022

### Response:
"""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    temperature=0.2
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))