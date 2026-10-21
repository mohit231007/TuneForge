from tuneforge import provenance


def test_runtime_provenance_without_cuda(monkeypatch):
    monkeypatch.setattr(provenance.torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(provenance, "git_commit", lambda: "abc123")

    result = provenance.runtime_provenance()

    assert result["git_commit"] == "abc123"
    assert result["cuda_available"] is False
    assert result["gpu_name"] is None
    assert result["compute_capability"] is None


def test_runtime_provenance_with_cuda(monkeypatch):
    monkeypatch.setattr(provenance.torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(
        provenance.torch.cuda,
        "get_device_capability",
        lambda _index: (7, 5),
    )
    monkeypatch.setattr(
        provenance.torch.cuda,
        "get_device_name",
        lambda _index: "Tesla T4",
    )
    monkeypatch.setattr(provenance, "git_commit", lambda: "def456")

    result = provenance.runtime_provenance()

    assert result["git_commit"] == "def456"
    assert result["gpu_name"] == "Tesla T4"
    assert result["compute_capability"] == "7.5"
