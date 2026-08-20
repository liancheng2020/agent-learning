from pathlib import Path

from fastapi.testclient import TestClient

from app.evaluate import build_agent, compare, evaluate, load_cases
from app.main import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_knowledge_base_is_self_contained() -> None:
    assert len(list((ROOT / "data" / "knowledge").rglob("*.md"))) == 15


def test_review_returns_findings_tools_and_exact_citations() -> None:
    response = client.post(
        "/review",
        json={"diff_text": "+++ b/src/auth.ts\n@@ -1 +1 @@\n+localStorage.setItem('accessToken', token);"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["findings"][0]["category"] == "security-token-storage"
    assert body["tool_runs"][0]["status"] == "completed"
    citation = body["findings"][0]["citations"][0]
    source_text = Path(citation["source_path"]).read_text(encoding="utf-8")
    assert citation["quote"] in source_text


def test_health_search_and_review_contracts() -> None:
    assert client.get("/health").json()["status"] == "ok"
    search = client.post("/knowledge/search", json={"query": "Vue v-for key", "topic": "vue", "top_k": 2})
    assert search.status_code == 200
    assert all(item["topic"] == "vue" for item in search.json()["citations"])
    assert client.post("/review", json={"diff_text": ""}).status_code == 422


def test_tuned_evaluation_reaches_quality_gates() -> None:
    cases = load_cases(ROOT / "data" / "eval-dataset.jsonl")
    summary = evaluate(build_agent(ROOT, "tuned"), cases)["summary"]
    assert summary["hit_rate"] >= 0.9
    assert summary["citation_accuracy"] >= 0.9
    assert summary["json_valid_rate"] == 1.0
    assert summary["tool_success_rate"] == 1.0


def test_iteration_is_driven_by_baseline_failures() -> None:
    report = compare(ROOT)
    assert report["baseline_failures"]
    assert report["tuned"]["hit_rate"] > report["baseline"]["hit_rate"]
    assert (ROOT / "reports" / "iteration.md").exists()
