from tuneforge.studio import validate_experiment


def valid_payload():
    return {
        "model_name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "dataset_name": "databricks/databricks-dolly-15k",
        "dataset": {"source": "huggingface", "path": None},
        "quantization": {"mode": "none"},
        "seed": 42,
        "num_train_samples": 1000,
        "max_seq_length": 512,
        "lora": {
            "r": 8,
            "alpha": 16,
            "dropout": 0.05,
            "target_modules": ["q_proj", "v_proj"],
        },
        "training": {
            "per_device_batch_size": 4,
            "gradient_accumulation_steps": 4,
        },
    }


def test_valid_experiment_has_no_errors():
    assert validate_experiment(valid_payload()) == []


def test_qlora_mode_is_valid():
    payload = valid_payload()
    payload["quantization"]["mode"] = "4bit"

    assert validate_experiment(payload) == []


def test_unknown_quantization_mode_is_rejected():
    payload = valid_payload()
    payload["quantization"]["mode"] = "8bit"

    errors = validate_experiment(payload)

    assert "quantization.mode must be either 'none' or '4bit'." in errors


def test_local_dataset_requires_path():
    payload = valid_payload()
    payload["dataset"] = {"source": "local", "path": None}

    errors = validate_experiment(payload)

    assert "Local dataset source requires a path." in errors


def test_lora_requires_targets():
    payload = valid_payload()
    payload["lora"]["target_modules"] = []

    errors = validate_experiment(payload)

    assert "At least one LoRA target module is required." in errors
