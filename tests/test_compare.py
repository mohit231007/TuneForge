import json

from tuneforge import compare


def test_compare_runs_reports_numeric_deltas(tmp_path, monkeypatch):
    monkeypatch.setattr(compare, "REGISTRY_DIR", tmp_path)
    monkeypatch.setattr(compare, "get_run", lambda run_id: object())

    for run_id, loss, size in [
        ("TF-LEFT", 2.0, 100),
        ("TF-RIGHT", 1.5, 120),
    ]:
        artifact_dir = tmp_path / run_id / "artifacts"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "run_metadata.json").write_text(
            json.dumps({
                "config": {"model_name": "tiny", "dataset_name": "data"},
                "training": {"training_loss": loss, "global_step": 10, "effective_batch_size": 16},
                "parameters": {"trainable_percentage": 0.1},
                "adapter": {"size_bytes": size, "quantization_mode": "none"},
                "hardware": {"gpu_name": "T4", "precision": {"fp16": True}},
            }),
            encoding="utf-8",
        )

    result = compare.compare_runs("TF-LEFT", "TF-RIGHT")

    assert result["delta_right_minus_left"]["training_loss"] == -0.5
    assert result["delta_right_minus_left"]["adapter_size_bytes"] == 20
