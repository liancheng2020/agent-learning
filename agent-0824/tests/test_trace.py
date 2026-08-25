from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]


def build_test_app(tmp_path: Path):
    return create_app(ROOT, tmp_path / "approvals.db", tmp_path / "trace.jsonl")


def test_trace_records_model_prompt_tool_usage_cost_and_latency(tmp_path: Path) -> None:
    application = build_test_app(tmp_path)
    client = TestClient(application)
    review = client.post("/review", json={"diff_text": "+localStorage.setItem('accessToken', token);"})
    assert review.status_code == 200
    trace_id = review.json()["trace_id"]
    events = client.get(f"/traces/{trace_id}").json()["events"]

    started = next(event for event in events if event["event"] == "run.started")
    assert started["model"]["name"] == "rule-rag-reviewer-v1"
    assert started["prompt_version"] == "review-tuned-v3"

    tool = next(event for event in events if event["event"] == "tool.completed")
    assert tool["tool"]["name"] == "search_knowledge"
    assert tool["tool"]["arguments"]["query"]
    assert tool["tool"]["result"]["citation_count"] >= 1
    assert tool["metrics"]["duration_ms"] >= 0

    completed = next(event for event in events if event["event"] == "run.completed")
    assert completed["metrics"]["input_tokens"] > 0
    assert completed["metrics"]["output_tokens"] > 0
    assert completed["metrics"]["cost_usd"] == 0
    assert completed["metrics"]["duration_ms"] >= 0


def test_tool_failure_trace_contains_error_stack(tmp_path: Path) -> None:
    application = build_test_app(tmp_path)

    def fail_search(*args, **kwargs):
        raise RuntimeError("vector store unavailable")

    application.state.review_agent.retriever.search_with_citations = fail_search
    client = TestClient(application)
    review = client.post("/review", json={"diff_text": "+localStorage.setItem('accessToken', token);"})
    assert review.status_code == 200
    events = client.get(f"/traces/{review.json()['trace_id']}").json()["events"]
    failed = next(event for event in events if event["event"] == "tool.failed")
    assert failed["error"]["type"] == "RuntimeError"
    assert failed["error"]["message"] == "vector store unavailable"
    assert "Traceback" in failed["error"]["stack"]
    assert events[-1]["status"] == "degraded"
