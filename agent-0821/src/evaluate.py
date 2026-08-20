from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.agent import ReviewAgent
from src.retrieval import KnowledgeRetriever
from src.schemas import ReviewResult
from src.service import build_index


class EvalCase(BaseModel):
    id: str
    title: str
    diff_text: str
    expected_categories: list[str]
    expected_topics: list[str]
    expected_citations: dict[str, str]


def load_cases(path: Path) -> list[EvalCase]:
    return [EvalCase.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate(agent: ReviewAgent, cases: list[EvalCase]) -> dict[str, Any]:
    expected_total = matched_total = 0
    citation_total = citation_correct = 0
    json_valid = 0
    tool_total = tool_success = 0
    latencies: list[float] = []
    results: list[dict[str, Any]] = []
    for case in cases:
        started = time.perf_counter()
        result = agent.review(case.diff_text)
        latencies.append((time.perf_counter() - started) * 1000)
        try:
            ReviewResult.model_validate_json(result.model_dump_json())
            valid = True
            json_valid += 1
        except Exception:
            valid = False
        findings = {item.category: item for item in result.findings}
        expected = set(case.expected_categories)
        actual = set(findings)
        matched = expected & actual
        expected_total += len(expected)
        matched_total += len(matched)
        citation_failures: list[str] = []
        for category, document_id in case.expected_citations.items():
            citation_total += 1
            finding = findings.get(category)
            correct = bool(finding and any(item.document_id == document_id and item.quote for item in finding.citations))
            citation_correct += int(correct)
            if not correct:
                citation_failures.append(category)
        tool_total += len(result.tool_runs)
        tool_success += sum(run.status == "completed" for run in result.tool_runs)
        results.append(
            {
                "id": case.id,
                "passed": expected == actual and not citation_failures and valid,
                "expected": sorted(expected),
                "actual": sorted(actual),
                "missing": sorted(expected - actual),
                "unexpected": sorted(actual - expected),
                "citation_failures": citation_failures,
                "latency_ms": round(latencies[-1], 3),
            }
        )
    return {
        "summary": {
            "cases": len(cases),
            "hit_rate": round(matched_total / expected_total, 4) if expected_total else 1.0,
            "citation_accuracy": round(citation_correct / citation_total, 4) if citation_total else 1.0,
            "json_valid_rate": round(json_valid / len(cases), 4),
            "tool_success_rate": round(tool_success / tool_total, 4) if tool_total else 1.0,
            "avg_latency_ms": round(sum(latencies) / len(latencies), 3),
            "case_pass_rate": round(sum(item["passed"] for item in results) / len(results), 4),
        },
        "cases": results,
    }


def build_agent(root: Path) -> ReviewAgent:
    corpus = root.parent / "agent-0816" / "knowledge"
    store = build_index(corpus, root / "data" / "knowledge.db")
    return ReviewAgent(KnowledgeRetriever(store), top_k=3)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=root / "reports" / "eval-report.json")
    args = parser.parse_args()
    report = evaluate(build_agent(root), load_cases(root / "data" / "eval-dataset.jsonl"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
