from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

import requests

from tuneforge.queue import cancel_pending_job, enqueue_job, queue_snapshot, retry_job


class ExecutionBackend(Protocol):
    name: str

    def submit(self, run_id: str, config_path: str) -> dict: ...
    def cancel(self, run_id: str) -> bool: ...
    def retry(self, run_id: str, config_path: str) -> dict: ...
    def snapshot(self) -> dict: ...


@dataclass
class LocalFilesystemBackend:
    name: str = "local-filesystem"

    def submit(self, run_id: str, config_path: str) -> dict:
        return enqueue_job(run_id, config_path)

    def cancel(self, run_id: str) -> bool:
        return cancel_pending_job(run_id)

    def retry(self, run_id: str, config_path: str) -> dict:
        return retry_job(run_id, config_path)

    def snapshot(self) -> dict:
        return {
            "backend": self.name,
            **queue_snapshot(),
        }


@dataclass
class WebhookBackend:
    base_url: str
    token: str | None = None
    name: str = "remote-webhook"

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def submit(self, run_id: str, config_path: str) -> dict:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/jobs",
            json={"run_id": run_id, "config_path": config_path},
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def cancel(self, run_id: str) -> bool:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/jobs/{run_id}/cancel",
            headers=self._headers(),
            timeout=10,
        )
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True

    def retry(self, run_id: str, config_path: str) -> dict:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/jobs/{run_id}/retry",
            json={"config_path": config_path},
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def snapshot(self) -> dict:
        response = requests.get(
            f"{self.base_url.rstrip('/')}/queue",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        payload["backend"] = self.name
        return payload


def get_execution_backend() -> ExecutionBackend:
    mode = os.getenv("TUNEFORGE_EXECUTION_BACKEND", "local").lower()

    if mode == "local":
        return LocalFilesystemBackend()

    if mode == "webhook":
        base_url = os.getenv("TUNEFORGE_REMOTE_WORKER_URL")
        if not base_url:
            raise RuntimeError(
                "TUNEFORGE_REMOTE_WORKER_URL is required for webhook execution."
            )
        return WebhookBackend(
            base_url=base_url,
            token=os.getenv("TUNEFORGE_REMOTE_WORKER_TOKEN"),
        )

    raise RuntimeError(f"Unsupported TuneForge execution backend: {mode}")
