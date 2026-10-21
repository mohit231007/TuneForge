from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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
