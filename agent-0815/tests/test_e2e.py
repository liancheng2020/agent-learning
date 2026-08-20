from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SAMPLE = """diff --git a/src/Login.jsx b/src/Login.jsx
--- a/src/Login.jsx
+++ b/src/Login.jsx
@@ -1,1 +1,3 @@
+const result = await api.login();
+return <img src=\"/avatar.png\" />;
"""


def test_01_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_02_review_runs_provider_and_three_tools() -> None:
    response = client.post("/review", json={"diff_text": SAMPLE})
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert [item["name"] for item in body["tool_calls"]] == ["read_diff", "search_knowledge", "generate_patch_plan"]
    assert {item["category"] for item in body["findings"]} >= {"error-handling", "accessibility", "testing"}


def test_03_empty_diff_is_rejected_at_api_boundary() -> None:
    response = client.post("/review", json={"diff_text": ""})
    assert response.status_code == 422


def test_04_sse_stream_contains_public_stages_tools_and_final() -> None:
    response = client.post("/review/stream", json={"diff_text": SAMPLE})
    assert response.status_code == 200
    assert "event: phase" in response.text
    assert response.text.count("event: tool") == 6
    assert "event: final" in response.text


def test_05_trace_id_links_response_to_persisted_trace() -> None:
    result = client.post("/review", json={"diff_text": SAMPLE}).json()
    response = client.get(f"/traces/{result['trace_id']}")
    events = response.json()["events"]
    assert response.status_code == 200
    assert events[0]["event"] == "run.started"
    assert events[-1]["event"] == "run.completed"
    assert all(item["traceId"] == result["trace_id"] for item in events)

