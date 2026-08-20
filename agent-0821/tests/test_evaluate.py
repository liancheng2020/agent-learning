from pathlib import Path

from src.evaluate import build_agent, evaluate, load_cases


def test_evaluation_outputs_required_metrics(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    agent = build_agent(root)
    report = evaluate(agent, load_cases(root / "data" / "eval-dataset.jsonl"))
    summary = report["summary"]
    assert {"hit_rate", "citation_accuracy", "json_valid_rate", "tool_success_rate", "avg_latency_ms"} <= summary.keys()
    assert summary["cases"] == 12
    assert summary["hit_rate"] >= 0.9
    assert summary["citation_accuracy"] >= 0.8
    assert summary["json_valid_rate"] == 1.0
    assert summary["tool_success_rate"] == 1.0
