from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.cache import MemoryCache
from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(ROOT, tmp_path / "approvals.db", tmp_path / "trace.jsonl", MemoryCache()))


@pytest.mark.parametrize(
    ("scenario", "status_code", "code"),
    [
        ("model_timeout", 504, "MODEL_TIMEOUT"),
        ("tool_exception", 502, "TOOL_EXECUTION_FAILED"),
        ("invalid_json", 502, "MODEL_JSON_INVALID"),
    ],
)
def test_failed_drills_return_actionable_error(
    client: TestClient, scenario: str, status_code: int, code: str
) -> None:
    response = client.post("/drills/run", json={"scenario": scenario})
    assert response.status_code == status_code
    body = response.json()
    assert body["code"] == code
    assert body["message"]
    assert body["suggestion"]
    assert body["trace_id"].startswith("trc_")


def test_empty_retrieval_degrades_without_fabricating_citations(client: TestClient) -> None:
    response = client.post("/drills/run", json={"scenario": "empty_retrieval"})
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["code"] == "KNOWLEDGE_NOT_FOUND"


def test_rejected_approval_blocks_execution(client: TestClient) -> None:
    response = client.post("/drills/run", json={"scenario": "approval_rejected"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert body["code"] == "APPROVAL_REJECTED"
    assert body["details"]["approval_status"] == "rejected"


def test_page_contains_all_drills_and_understandable_feedback(client: TestClient) -> None:
    html = client.get("/").text
    javascript = client.get("/static/app.js").text
    for scenario in (
        "model_timeout",
        "tool_exception",
        "empty_retrieval",
        "invalid_json",
        "approval_rejected",
    ):
        assert scenario in html
    assert "suggestion" in javascript
    assert "traceId" in javascript
