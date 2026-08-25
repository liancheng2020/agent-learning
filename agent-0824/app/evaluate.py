from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.agent import ReviewAgent
from app.embeddings import HashEmbeddingProvider
from app.retrieval import KnowledgeRetriever
from app.schemas import ReviewResult
from app.service import build_index
from app.store import SQLiteVectorStore
from app.trace import TraceStore


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
    expected_total = matched_total = citation_total = citation_correct = 0
    json_valid = tool_total = tool_success = 0
    latencies: list[float] = []
    case_reports: list[dict[str, Any]] = []
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
        expected_total += len(expected)
        matched_total += len(expected & actual)
        citation_failures: list[str] = []
        for category, document_id in case.expected_citations.items():
            citation_total += 1
            finding = findings.get(category)
            correct = bool(finding and any(c.document_id == document_id and c.quote for c in finding.citations))
            citation_correct += int(correct)
            if not correct:
                citation_failures.append(category)
        tool_total += len(result.tool_runs)
        tool_success += sum(run.status == "completed" for run in result.tool_runs)
        case_reports.append(
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
            "case_pass_rate": round(sum(case["passed"] for case in case_reports) / len(case_reports), 4),
        },
        "cases": case_reports,
    }


def build_agent(root: Path, version: str = "tuned", traces: TraceStore | None = None) -> ReviewAgent:
    database = root / "data" / "knowledge.db"
    if version == "tuned" or not database.exists():
        store = build_index(root / "data" / "knowledge", database)
    else:
        store = SQLiteVectorStore(database, HashEmbeddingProvider())
    if version == "baseline":
        return ReviewAgent(KnowledgeRetriever(store, rerank=False, topic_boost=0), top_k=1, version="baseline", traces=traces)
    return ReviewAgent(KnowledgeRetriever(store, rerank=True, topic_boost=0.2), top_k=3, version="tuned", traces=traces)


def compare(root: Path) -> dict[str, Any]:
    cases = load_cases(root / "data" / "eval-dataset.jsonl")
    baseline = evaluate(build_agent(root, "baseline"), cases)
    tuned = evaluate(build_agent(root, "tuned"), cases)
    root.joinpath("reports").mkdir(exist_ok=True)
    root.joinpath("reports/baseline.json").write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
    root.joinpath("reports/tuned.json").write_text(json.dumps(tuned, ensure_ascii=False, indent=2), encoding="utf-8")
    failures = [case["id"] for case in baseline["cases"] if not case["passed"]]
    report = f"""# Day 14 评测迭代报告

## 失败样本

Baseline 未通过：{", ".join(failures) or "无"}。

## 迭代动作

- 规则：从 5 类基础规则扩充到 11 类，补齐 React key、Vue、TS 空值、代码分割和硬编码密钥。
- 检索：top-k 从 1 调整为 3，增加词法重排与 topic boost 0.2。
- 输出：每条 finding 强制绑定至少一条可核验 quote，继续由 Pydantic 校验 JSON。

## 实测结果

| 指标 | Baseline | Tuned |
| --- | ---: | ---: |
| 命中率 | {baseline["summary"]["hit_rate"]:.2%} | {tuned["summary"]["hit_rate"]:.2%} |
| 引用正确率 | {baseline["summary"]["citation_accuracy"]:.2%} | {tuned["summary"]["citation_accuracy"]:.2%} |
| JSON 合法率 | {baseline["summary"]["json_valid_rate"]:.2%} | {tuned["summary"]["json_valid_rate"]:.2%} |
| 工具成功率 | {baseline["summary"]["tool_success_rate"]:.2%} | {tuned["summary"]["tool_success_rate"]:.2%} |
| 平均延迟 | {baseline["summary"]["avg_latency_ms"]:.3f} ms | {tuned["summary"]["avg_latency_ms"]:.3f} ms |

结论只适用于当前 12 条回归集。下一步应持续加入真实误报、改写代码和跨文件上下文样本，避免只针对现有数据集调参。
"""
    root.joinpath("reports/iteration.md").write_text(report, encoding="utf-8")
    return {"baseline": baseline["summary"], "tuned": tuned["summary"], "baseline_failures": failures}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=["baseline", "tuned"], default="tuned")
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()
    payload = compare(root) if args.compare else evaluate(
        build_agent(root, args.version),
        load_cases(root / "data" / "eval-dataset.jsonl"),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
