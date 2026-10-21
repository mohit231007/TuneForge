import pytest
from fastapi import HTTPException

from api.security import read_only_mode, require_write_access


def test_read_only_mode_defaults_off(monkeypatch):
    monkeypatch.delenv("TUNEFORGE_READ_ONLY", raising=False)
    assert read_only_mode() is False


def test_read_only_mode_accepts_true(monkeypatch):
    monkeypatch.setenv("TUNEFORGE_READ_ONLY", "true")
    assert read_only_mode() is True


def test_write_access_blocked_in_read_only_mode(monkeypatch):
    monkeypatch.setenv("TUNEFORGE_READ_ONLY", "true")

    with pytest.raises(HTTPException) as exc:
        require_write_access()

    assert exc.value.status_code == 403
