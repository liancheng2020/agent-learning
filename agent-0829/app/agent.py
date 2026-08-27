from __future__ import annotations

import time
import traceback
from dataclasses import asdict
from uuid import uuid4

from app.retrieval import KnowledgeRetriever
from app.rules import match_rules
from app.schemas import CitationModel, ReviewFinding, ReviewResult, ToolRun
from app.trace import MODEL, TraceStore, estimate_cost, estimate_tokens


class ReviewAgent:
    def __init__(
        self,
        retriever: KnowledgeRetriever,
        top_k: int = 2,
        version: str = "tuned",
        traces: TraceStore | None = None,
    ) -> None:
        self.retriever = retriever
        self.top_k = top_k
        self.version = version
        self.traces = traces

    def review(self, diff_text: str, trace_id: str | None = None) -> ReviewResult:
        prompt_version = f"review-{self.version}-v3"
        trace_id = trace_id or (
            self.traces.start(prompt_version, {"diff_chars": len(diff_text)})
            if self.traces
            else f"trc_{uuid4().hex}"
        )
        run_started = time.perf_counter()
        findings: list[ReviewFinding] = []
        tool_runs: list[ToolRun] = []
        for rule in match_rules(diff_text, self.version):
            started = time.perf_counter()
            try:
                citations = self.retriever.search_with_citations(rule.query, self.top_k, rule.topic)
                status = "completed"
                if self.traces:
                    self.traces.emit(
                        trace_id,
                        "tool.completed",
                        tool={
                            "name": "search_knowledge",
                            "arguments": {"query": rule.query, "top_k": self.top_k, "topic": rule.topic},
                            "result": {
                                "citation_count": len(citations),
                                "document_ids": [item.document_id for item in citations],
                            },
                        },
                        metrics={"duration_ms": round((time.perf_counter() - started) * 1000, 3)},
                    )
            except Exception as error:
                citations = []
                status = "failed"
                if self.traces:
                    self.traces.emit(
                        trace_id,
                        "tool.failed",
                        tool={
                            "name": "search_knowledge",
                            "arguments": {"query": rule.query, "top_k": self.top_k, "topic": rule.topic},
                            "result": None,
                        },
                        metrics={"duration_ms": round((time.perf_counter() - started) * 1000, 3)},
                        error={
                            "type": type(error).__name__,
                            "message": str(error),
                            "stack": traceback.format_exc(),
                        },
                    )
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
        result = ReviewResult(
            trace_id=trace_id,
            summary=summary,
            findings=findings,
            tool_runs=tool_runs,
            prompt_version=prompt_version,
        )
        if self.traces:
            input_tokens = estimate_tokens(diff_text)
            output_tokens = estimate_tokens(result.model_dump_json())
            self.traces.emit(
                trace_id,
                "run.completed",
                model=MODEL,
                prompt_version=prompt_version,
                metrics={
                    "duration_ms": round((time.perf_counter() - run_started) * 1000, 3),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "cost_usd": estimate_cost(input_tokens, output_tokens),
                },
                status="degraded" if any(run.status == "failed" for run in tool_runs) else "completed",
            )
        return result
