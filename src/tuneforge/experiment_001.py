from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import torch

from tuneforge.config import load_config
from tuneforge.persistence import save_json
from tuneforge.provenance import runtime_provenance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run canonical TuneForge Experiment 001 and package evidence."
    )
    parser.add_argument(
        "--config",
        default="configs/experiment_001.yaml",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the configured output directory before starting.",
    )
    return parser.parse_args()


def _run_module(module: str, *args: str) -> None:
    command = [sys.executable, "-m", module, *args]
    print("$", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _telemetry_points(path: Path) -> list[dict]:
    if not path.exists():
        return []
    points = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            points.append(json.loads(line))
    return points


def _write_markdown(evidence: dict, path: Path) -> None:
    hardware = evidence["run_metadata"]["hardware"]
    params = evidence["run_metadata"]["parameters"]
    training = evidence["run_metadata"]["training"]
    adapter = evidence["run_metadata"]["adapter"]
    scorecard = evidence["evaluation"]["scorecard"]

    lines = [
        "# TuneForge Experiment 001 Evidence",
        "",
        f"- Git commit: `{evidence['provenance'].get('git_commit')}`",
        f"- GPU: {hardware.get('gpu_name')}",
        f"- Compute capability: {hardware.get('compute_capability')}",
        f"- Precision: {hardware.get('precision')}",
        f"- Model: {evidence['run_metadata']['config'].get('model_name')}",
        f"- Dataset: {evidence['run_metadata']['config'].get('dataset_name')}",
        f"- Seed: {evidence['run_metadata']['config'].get('seed')}",
        f"- Training samples: {evidence['run_metadata']['config'].get('num_train_samples')}",
        f"- Trainable parameters: {params.get('trainable_parameters')}",
        f"- Total parameters: {params.get('total_parameters')}",
        f"- Trainable percentage: {params.get('trainable_percentage'):.6f}%",
        f"- Final training loss: {training.get('training_loss')}",
        f"- Global steps: {training.get('global_step')}",
        f"- Adapter size bytes: {adapter.get('size_bytes')}",
        f"- Adapter size MB: {adapter.get('size_bytes', 0) / (1024 ** 2):.4f}",
        f"- Evaluation prompt count: {scorecard.get('prompt_count')}",
        f"- Deterministic generation: {scorecard.get('generation_is_deterministic')}",
        "",
        "## Verification",
        "",
        f"- Prompt identity preserved: {evidence['verification']['same_prompts']}",
        f"- Telemetry points captured: {evidence['verification']['telemetry_points']}",
        f"- Loss entries captured: {evidence['verification']['loss_entries']}",
        "",
        "## Files",
        "",
    ]
    for item in evidence["manifest"]:
        lines.append(f"- `{item['path']}` — SHA256 `{item['sha256']}`")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    output_dir = Path(config.output_dir)

    if not torch.cuda.is_available():
        raise RuntimeError(
            "Experiment 001 requires a CUDA GPU. In Colab select a T4 GPU runtime."
        )

    gpu_name = torch.cuda.get_device_name(0)
    major, minor = torch.cuda.get_device_capability(0)
    print(
        f"Experiment 001 hardware: {gpu_name} "
        f"(compute capability {major}.{minor})",
        flush=True,
    )

    if args.clean and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    config_snapshot = output_dir / "experiment_config.yaml"
    shutil.copy2(args.config, config_snapshot)

    _run_module(
        "tuneforge.train",
        "--config",
        args.config,
    )

    adapter_dir = output_dir / "final-adapter"
    _run_module(
        "tuneforge.evaluate",
        "--config",
        args.config,
        "--adapter",
        str(adapter_dir),
    )

    run_metadata_path = output_dir / "run_metadata.json"
    telemetry_path = output_dir / "telemetry.jsonl"
    comparison_json_path = output_dir / "evaluation" / "comparison.json"
    comparison_csv_path = output_dir / "evaluation" / "comparison.csv"

    required = [
        run_metadata_path,
        telemetry_path,
        comparison_json_path,
        comparison_csv_path,
        config_snapshot,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"Experiment evidence files missing: {missing}")

    run_metadata = _read_json(run_metadata_path)
    comparison = _read_json(comparison_json_path)
    telemetry = _telemetry_points(telemetry_path)

    configured_prompts = list(config.evaluation_prompts)
    evaluated_prompts = [
        item["prompt"]
        for item in comparison.get("comparisons", [])
    ]
    same_prompts = configured_prompts == evaluated_prompts
    if not same_prompts:
        raise RuntimeError(
            "Evaluation prompt mismatch detected; refusing to package evidence."
        )

    loss_entries = [
        point["loss"]
        for point in telemetry
        if point.get("loss") is not None
    ]

    manifest = []
    for path in required:
        manifest.append(
            {
                "path": str(path.relative_to(output_dir)),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )

    evidence = {
        "experiment_id": "experiment-001",
        "provenance": runtime_provenance(),
        "run_metadata": run_metadata,
        "evaluation": comparison,
        "verification": {
            "same_prompts": same_prompts,
            "telemetry_points": len(telemetry),
            "loss_entries": len(loss_entries),
            "required_files_present": True,
        },
        "manifest": manifest,
    }

    evidence_json = output_dir / "experiment_001_evidence.json"
    save_json(evidence, evidence_json)

    evidence_markdown = output_dir / "EXPERIMENT_001_EVIDENCE.md"
    _write_markdown(evidence, evidence_markdown)

    archive_path = output_dir / "experiment_001_evidence.zip"
    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for path in [
            *required,
            evidence_json,
            evidence_markdown,
        ]:
            archive.write(
                path,
                arcname=path.relative_to(output_dir),
            )

    print("\nExperiment 001 completed successfully.")
    print(f"Evidence JSON: {evidence_json}")
    print(f"Evidence summary: {evidence_markdown}")
    print(f"Evidence archive: {archive_path}")
    print(
        json.dumps(
            {
                "git_commit": evidence["provenance"].get("git_commit"),
                "gpu_name": run_metadata["hardware"].get("gpu_name"),
                "compute_capability": run_metadata["hardware"].get(
                    "compute_capability"
                ),
                "trainable_percentage": run_metadata["parameters"].get(
                    "trainable_percentage"
                ),
                "training_loss": run_metadata["training"].get(
                    "training_loss"
                ),
                "adapter_size_bytes": run_metadata["adapter"].get(
                    "size_bytes"
                ),
                "telemetry_points": len(telemetry),
                "evaluation_prompts": len(configured_prompts),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
