import pytest
from fastapi import HTTPException

from api.security import require_access


def test_workspace_access_defaults_without_configured_key(monkeypatch):
    monkeypatch.delenv("TUNEFORGE_API_KEY", raising=False)

    assert require_access("demo-workspace", None) == "demo-workspace"


def test_configured_api_key_is_required(monkeypatch):
    monkeypatch.setenv("TUNEFORGE_API_KEY", "secret")

    with pytest.raises(HTTPException) as exc:
        require_access("demo", "wrong")

    assert exc.value.status_code == 401


def test_invalid_workspace_identifier_is_rejected(monkeypatch):
    monkeypatch.delenv("TUNEFORGE_API_KEY", raising=False)

    with pytest.raises(HTTPException) as exc:
        require_access("../escape", None)

    assert exc.value.status_code == 422
