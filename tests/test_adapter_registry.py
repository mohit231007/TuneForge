import pytest

from tuneforge import adapter_registry


def test_adapter_lifecycle_happy_path(tmp_path, monkeypatch):
    monkeypatch.setattr(adapter_registry, "REGISTRY_DIR", tmp_path)

    adapter = adapter_registry.register_adapter({"model_name": "tiny"})
    adapter_id = adapter["adapter_id"]

    validated = adapter_registry.transition_adapter(
        adapter_id,
        "validated",
        "Evaluation passed.",
    )
    assert validated["lifecycle"] == "validated"

    production = adapter_registry.transition_adapter(
        adapter_id,
        "production",
        "Approved for production.",
    )
    assert production["lifecycle"] == "production"

    archived = adapter_registry.transition_adapter(
        adapter_id,
        "archived",
        "Superseded.",
    )
    assert archived["lifecycle"] == "archived"


def test_invalid_adapter_transition_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(adapter_registry, "REGISTRY_DIR", tmp_path)

    adapter = adapter_registry.register_adapter({"model_name": "tiny"})

    with pytest.raises(ValueError):
        adapter_registry.transition_adapter(
            adapter["adapter_id"],
            "production",
            "Skipping validation is not allowed.",
        )
