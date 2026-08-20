from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_review_returns_structured_findings() -> None:
    response = client.post("/review", json={"diff_text": "+++ b/App.jsx\n@@ -1,1 +1,2 @@\n+await api.load()\n+<img src=\"a.png\" />"})
    assert response.status_code == 200
    assert {item["category"] for item in response.json()["findings"]} == {"error-handling", "accessibility"}


def test_review_validates_empty_diff() -> None:
    assert client.post("/review", json={"diff_text": ""}).status_code == 422

