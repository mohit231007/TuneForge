from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_security_headers_are_present():
    response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert "s-maxage=300" in response.headers["cache-control"]


def test_capabilities_are_read_only():
    response = client.get("/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["read_only"] is True
    assert body["can_train"] is False


def test_every_write_method_is_blocked():
    for method in ["post", "put", "patch", "delete"]:
        response = getattr(client, method)("/evaluation/rules", json={})
        assert response.status_code == 403


def test_public_experiment_creation_is_blocked():
    response = client.post("/experiments", json={})
    assert response.status_code == 403


def test_invalid_workspace_is_rejected():
    response = client.get(
        "/capabilities",
        headers={"X-TuneForge-Workspace": "../escape"},
    )
    assert response.status_code == 422


def test_public_collections_are_empty():
    assert client.get("/experiments").json() == []
    assert client.get("/adapters").json() == []
