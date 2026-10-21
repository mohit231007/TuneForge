from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from tuneforge.queue import claim_next_job, finish_job
from tuneforge.studio import set_run_status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TuneForge GPU worker")
    parser.add_argument("--once", action="store_true", help="Process at most one queued job.")
    parser.add_argument("--poll-seconds", type=float, default=3.0)
    parser.add_argument("--worker-id", default=None)
    return parser.parse_args()


def execute_job(job: dict, worker_id: str) -> int:
    run_id = job["run_id"]
    config_path = job["config_path"]
    run_dir = Path(config_path).parent
    log_path = run_dir / "train.log"

    set_run_status(
        run_id,
        "running",
        f"Claimed by worker {worker_id}.",
        worker_id=worker_id,
    )

    with log_path.open("a", encoding="utf-8") as log_handle:
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "tuneforge.train",
                "--config",
                config_path,
            ],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            env=os.environ.copy(),
            check=False,
        )

    success = process.returncode == 0

    finish_job(
        run_id,
        success=success,
        details={"return_code": process.returncode, "worker_id": worker_id},
    )

    if success:
        set_run_status(
            run_id,
            "completed",
            "Training completed successfully.",
            worker_id=worker_id,
        )
    else:
        set_run_status(
            run_id,
            "failed",
            f"Training failed with return code {process.returncode}.",
            worker_id=worker_id,
        )

    return process.returncode


def main() -> None:
    args = parse_args()
    worker_id = args.worker_id or f"{socket.gethostname()}-{os.getpid()}"

    try:
        import torch
        if not torch.cuda.is_available():
            raise SystemExit(
                "TuneForge worker requires a CUDA-capable host. "
                "No job was claimed."
            )
    except ImportError as exc:
        raise SystemExit("PyTorch is required by the TuneForge worker.") from exc

    while True:
        job = claim_next_job(worker_id)

        if job is None:
            if args.once:
                return
            time.sleep(args.poll_seconds)
            continue

        execute_job(job, worker_id)

        if args.once:
            return


if __name__ == "__main__":
    main()
