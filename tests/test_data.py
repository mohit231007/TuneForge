from tuneforge.data import format_dolly_to_chat


def test_format_without_context():
    example = {
        "instruction": "Explain LoRA.",
        "context": "",
        "response": "LoRA adds trainable low-rank adapters.",
    }
    result = format_dolly_to_chat(example)

    assert result["messages"][0] == {"role": "user", "content": "Explain LoRA."}
    assert result["messages"][1]["role"] == "assistant"


def test_format_with_context():
    example = {
        "instruction": "Summarize this.",
        "context": "Context text.",
        "response": "Summary.",
    }
    result = format_dolly_to_chat(example)

    assert result["messages"][0]["content"] == "Summarize this.\nContext text."
