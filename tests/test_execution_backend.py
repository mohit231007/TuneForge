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


def test_webhook_backend_sends_config_payload(tmp_path, monkeypatch):
    from tuneforge.execution_backend import WebhookBackend

    config = tmp_path / "experiment.yaml"
    config.write_text("model_name: tiny\n", encoding="utf-8")
    captured = {}

    class Response:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"accepted": True}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        return Response()

    monkeypatch.setattr("tuneforge.execution_backend.requests.post", fake_post)

    result = WebhookBackend("https://worker.example").submit(
        "TF-REMOTE01",
        str(config),
    )

    assert result == {"accepted": True}
    assert captured["json"]["run_id"] == "TF-REMOTE01"
    assert captured["json"]["config_yaml"] == "model_name: tiny\n"
