# After LoRA wrap
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()
model.to(DEVICE)  # <<< Move to GPU

# After merge
merged_model = PeftModel.from_pretrained(base_model, OUTPUT_DIR)
merged_model = merged_model.merge_and_unload()
merged_model.to(DEVICE)  # <<< Move to GPU