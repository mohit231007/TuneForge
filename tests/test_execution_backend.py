from tuneforge.execution_backend import LocalFilesystemBackend


def test_local_backend_name():
    backend = LocalFilesystemBackend()
    assert backend.name == "local-filesystem"


def test_local_snapshot_contains_backend(monkeypatch):
    monkeypatch.setattr(
        "tuneforge.execution_backend.queue_snapshot",
        lambda: {"pending": 1, "claimed": 2, "done": 3, "failed": 4},
    )

    snapshot = LocalFilesystemBackend().snapshot()

    assert snapshot["backend"] == "local-filesystem"
    assert snapshot["pending"] == 1
