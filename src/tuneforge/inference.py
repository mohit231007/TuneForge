from __future__ import annotations

import time

import torch


def response_repetition_ratio(text: str) -> float:
    tokens = text.split()
    if not tokens:
        return 0.0
    return 1.0 - (len(set(tokens)) / len(tokens))


def generate_response_with_metrics(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 256,
) -> dict:
    messages = [{"role": "user", "content": prompt}]
    rendered = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    device = next(model.parameters()).device
    inputs = tokenizer(rendered, return_tensors="pt").to(device)

    model.eval()

    if torch.cuda.is_available():
        torch.cuda.synchronize()

    started = time.perf_counter()

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    if torch.cuda.is_available():
        torch.cuda.synchronize()

    latency_seconds = time.perf_counter() - started
    new_tokens = outputs[0][inputs["input_ids"].shape[1] :]
    text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    token_count = int(new_tokens.shape[0])

    return {
        "response": text,
        "latency_seconds": round(latency_seconds, 4),
        "generated_tokens": token_count,
        "tokens_per_second": round(token_count / latency_seconds, 4)
        if latency_seconds > 0
        else 0.0,
        "word_count": len(text.split()),
        "repetition_ratio": round(response_repetition_ratio(text), 4),
    }


def generate_response(model, tokenizer, prompt: str, max_new_tokens: int = 256) -> str:
    return generate_response_with_metrics(
        model,
        tokenizer,
        prompt,
        max_new_tokens=max_new_tokens,
    )["response"]


def generate_many(model, tokenizer, prompts: list[str], max_new_tokens: int = 256) -> list[str]:
    return [
        generate_response(model, tokenizer, prompt, max_new_tokens=max_new_tokens)
        for prompt in prompts
    ]
