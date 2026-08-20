import json
import os
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.errors import AgentError, ProviderFailure
from app.providers import ModelProvider
from app.schemas import ReviewRequest, ReviewResult, ToolCallSummary
from app.tools import ToolExecutor
from app.trace import TraceStore


SYSTEM_PROMPT = """你是前端代码审查 Agent。根据用户 diff 自主调用已注册工具。
先调用 read_diff，再根据 findings 调用 search_knowledge 和 generate_patch_plan。
工具完成后只输出 JSON，且必须符合 ReviewSynthesis JSON Schema。不要输出 Markdown，不要编造工具结果。"""


class ReviewAgent:
    def __init__(self, provider: ModelProvider, executor: ToolExecutor, trace: TraceStore) -> None:
        self.provider = provider
        self.executor = executor
        self.trace = trace
        self.timeout_s = float(os.getenv("TOOL_TIMEOUT_SECONDS", "2"))
        self.max_retries = int(os.getenv("TOOL_MAX_RETRIES", "1"))

    async def events(self, request: ReviewRequest, trace_id: str | None = None) -> AsyncIterator[dict[str, Any]]:
        trace_id = trace_id or f"tr_{uuid4().hex[:16]}"
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请审查以下 Git diff。\n\n{request.diff_text}\n\n当前代码：\n{request.code}"},
        ]
        summaries: list[ToolCallSummary] = []
        self.trace.emit(trace_id, "run.started", provider=self.provider.name)
        yield _event("phase", trace_id, stage="received", label="请求已接收")

        for step in range(1, 7):
            self.trace.emit(trace_id, "provider.started", step=step, provider=self.provider.name)
            yield _event("phase", trace_id, stage="planning", label="Agent 正在规划下一步", step=step)
            try:
                turn = await self.provider.next_turn(request, messages, self.executor.schemas())
            except ProviderFailure as error:
                self.trace.emit(trace_id, "provider.failed", code=error.code)
                raise AgentError(error.code, error.message, trace_id) from error
            messages.append(turn.assistant_message)

            if turn.final:
                result = ReviewResult(trace_id=trace_id, provider=self.provider.name, tool_calls=summaries, **turn.final.model_dump())
                self.trace.emit(trace_id, "run.completed", findingCount=len(result.findings))
                yield _event("final", trace_id, result=result.model_dump())
                return

            if not turn.tool_calls:
                raise AgentError("PROVIDER_INVALID_OUTPUT", "Provider 未返回工具调用或最终结果", trace_id)

            for call in turn.tool_calls:
                yield _event("tool", trace_id, tool=call.name, status="running")
                result, record = await self.executor.execute(call.name, call.arguments, trace_id, self.timeout_s, self.max_retries)
                summary = ToolCallSummary.model_validate(record)
                summaries.append(summary)
                yield _event("tool", trace_id, tool=call.name, status=summary.status, attempts=summary.attempts, latencyMs=summary.latency_ms)
                messages.append({"role": "tool", "tool_call_id": call.id, "name": call.name, "content": json.dumps(result, ensure_ascii=False)})

        raise AgentError("AGENT_MAX_STEPS", "Agent 超过最大工具调用轮次", trace_id)

    async def run(self, request: ReviewRequest) -> ReviewResult:
        async for item in self.events(request):
            if item["event"] == "final":
                return ReviewResult.model_validate(item["result"])
        raise RuntimeError("agent finished without final result")


def _event(event_type: str, trace_id: str, **payload: Any) -> dict[str, Any]:
    return {"event": event_type, "traceId": trace_id, **payload}

