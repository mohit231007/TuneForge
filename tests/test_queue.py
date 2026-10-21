from pathlib import Path

from tuneforge import queue


def test_enqueue_claim_finish(tmp_path, monkeypatch):
    pending = tmp_path / "pending"
    claimed = tmp_path / "claimed"
    done = tmp_path / "done"
    failed = tmp_path / "failed"

    for directory in [pending, claimed, done, failed]:
        directory.mkdir()

    monkeypatch.setattr(queue, "PENDING_DIR", pending)
    monkeypatch.setattr(queue, "CLAIMED_DIR", claimed)
    monkeypatch.setattr(queue, "DONE_DIR", done)
    monkeypatch.setattr(queue, "FAILED_DIR", failed)

    queue.enqueue_job("TF-ABC12345", "config.yaml")
    claimed_job = queue.claim_next_job("worker-1")

    assert claimed_job["run_id"] == "TF-ABC12345"
    assert claimed_job["worker_id"] == "worker-1"

    queue.finish_job("TF-ABC12345", success=True)

    assert (done / "TF-ABC12345.json").exists()
    assert not (claimed / "TF-ABC12345.json").exists()


def test_cancel_pending_job(tmp_path, monkeypatch):
    pending = tmp_path / "pending"
    pending.mkdir()
    monkeypatch.setattr(queue, "PENDING_DIR", pending)

    queue.enqueue_job("TF-CANCEL01", "config.yaml")

    assert queue.cancel_pending_job("TF-CANCEL01") is True
    assert not (pending / "TF-CANCEL01.json").exists()
