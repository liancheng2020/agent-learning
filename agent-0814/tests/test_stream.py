from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sse_contains_phase_tools_and_final() -> None:
    response = client.post("/review/stream", json={"diff_text": "+++ b/App.jsx\n@@ -1 +1 @@\n+await api.load()"})
    assert response.status_code == 200
    assert "event: phase" in response.text
    assert response.text.count("event: tool") == 6
    assert "event: final" in response.text

