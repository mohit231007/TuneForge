from __future__ import annotations

import torch


def generate_response(model, tokenizer, prompt: str, max_new_tokens: int = 256) -> str:
    messages = [{"role": "user", "content": prompt}]
    rendered = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    device = next(model.parameters()).device
    inputs = tokenizer(rendered, return_tensors="pt").to(device)

    model.eval()
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    new_tokens = outputs[0][inputs["input_ids"].shape[1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def generate_many(model, tokenizer, prompts: list[str], max_new_tokens: int = 256) -> list[str]:
    return [
        generate_response(model, tokenizer, prompt, max_new_tokens=max_new_tokens)
        for prompt in prompts
    ]
