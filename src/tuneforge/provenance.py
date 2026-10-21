from __future__ import annotations

import platform
import subprocess
from pathlib import Path

import torch


def git_commit(repo_root: str | Path = ".") -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(repo_root),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def runtime_provenance() -> dict:
    cuda_available = torch.cuda.is_available()
    capability = None
    gpu_name = None

    if cuda_available:
        major, minor = torch.cuda.get_device_capability(0)
        capability = f"{major}.{minor}"
        gpu_name = torch.cuda.get_device_name(0)

    return {
        "git_commit": git_commit(),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "compute_capability": capability,
    }
