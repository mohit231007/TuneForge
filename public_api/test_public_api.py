from fastapi.testclient import TestClient

from main import MAX_CONTENT_LENGTH, app

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
    assert response.headers["cache-control"] == "no-store"


def test_capabilities_are_read_only():
    response = client.get("/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["read_only"] is True
    assert body["can_train"] is False


def test_public_create_is_blocked():
    response = client.post("/experiments", json={})
    assert response.status_code == 403


def test_rule_evaluation():
    response = client.post(
        "/evaluation/rules",
        json={
            "response": "one two three",
            "rules": {"min_words": 3, "max_words": 3},
        },
    )
    assert response.status_code == 200
    assert response.json()["result"]["passed"] is True


def test_evaluation_response_length_is_bounded():
    response = client.post(
        "/evaluation/rules",
        json={"response": "x" * 8001, "rules": {}},
    )
    assert response.status_code == 422


def test_evaluation_rule_count_is_bounded():
    response = client.post(
        "/evaluation/rules",
        json={
            "response": "safe response",
            "rules": {"contains": [f"term-{i}" for i in range(11)]},
        },
    )
    assert response.status_code == 422


def test_evaluation_word_bounds_are_bounded():
    response = client.post(
        "/evaluation/rules",
        json={
            "response": "safe response",
            "rules": {"max_words": 2001},
        },
    )
    assert response.status_code == 422


def test_declared_oversized_request_is_rejected_early():
    response = client.post(
        "/evaluation/rules",
        headers={"Content-Length": str(MAX_CONTENT_LENGTH + 1)},
        content=b"{}",
    )
    assert response.status_code == 413


def test_invalid_workspace_is_rejected():
    response = client.get(
        "/capabilities",
        headers={"X-TuneForge-Workspace": "../escape"},
    )
    assert response.status_code == 422
