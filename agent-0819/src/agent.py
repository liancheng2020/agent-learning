from __future__ import annotations

import time
from dataclasses import asdict

from src.retrieval import KnowledgeRetriever
from src.rules import match_rules
from src.schemas import CitationModel, ReviewFinding, ReviewResult, ToolRun


class ReviewAgent:
    def __init__(self, retriever: KnowledgeRetriever, top_k: int = 2) -> None:
        self.retriever = retriever
        self.top_k = top_k

    def review(self, diff_text: str) -> ReviewResult:
        findings: list[ReviewFinding] = []
        tool_runs: list[ToolRun] = []
        for rule in match_rules(diff_text):
            started = time.perf_counter()
            try:
                citations = self.retriever.search_with_citations(rule.query, self.top_k, rule.topic)
                status = "completed"
            except Exception:
                citations = []
                status = "failed"
            latency = (time.perf_counter() - started) * 1000
            tool_runs.append(ToolRun(name="search_knowledge", query=rule.query, status=status, latency_ms=latency))
            if not citations:
                continue
            findings.append(
                ReviewFinding(
                    category=rule.category,
                    severity=rule.severity,
                    message=rule.message,
                    suggestion=rule.suggestion,
                    topic=rule.topic,
                    citations=[CitationModel.model_validate(asdict(item)) for item in citations],
                )
            )
        summary = f"发现 {len(findings)} 个问题；每条问题均已检索并引用前端规范。"
        return ReviewResult(summary=summary, findings=findings, tool_runs=tool_runs, prompt_version="rules-v1")
