import asyncio
import inspect
import re
import time
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.errors import ToolError
from app.schemas import Finding
from app.trace import TraceStore, trace_store


class ReadDiffArgs(BaseModel):
    diff_text: str = Field(min_length=1, max_length=200_000)


class SearchKnowledgeArgs(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=5)


class GeneratePatchPlanArgs(BaseModel):
    file: str = Field(min_length=1)
    findings: list[Finding]


class Tool:
    def __init__(self, name: str, args_model: type[BaseModel], handler: Callable[..., Any], fallback: Callable[..., Any] | None = None) -> None:
        self.name = name
        self.args_model = args_model
        self.handler = handler
        self.fallback = fallback


class ToolExecutor:
    def __init__(self, tools: list[Tool], trace: TraceStore | None = None) -> None:
        self.tools = {tool.name: tool for tool in tools}
        self.trace = trace or trace_store

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        trace_id: str,
        timeout_s: float = 1.0,
        max_retries: int = 1,
    ) -> tuple[Any, dict[str, Any]]:
        tool = self.tools.get(name)
        if not tool:
            raise ToolError("TOOL_NOT_FOUND", f"unknown tool: {name}", trace_id, {"tool": name})
        try:
            validated = tool.args_model.model_validate(arguments).model_dump()
        except ValidationError as error:
            self.trace.emit(trace_id, "tool.failed", tool=name, code="TOOL_INVALID_ARGUMENTS")
            raise ToolError("TOOL_INVALID_ARGUMENTS", "tool arguments failed validation", trace_id, {"tool": name, "errors": error.errors(include_input=False)}) from error

        started = time.perf_counter()
        last_error: Exception | None = None
        for attempt in range(1, max_retries + 2):
            self.trace.emit(trace_id, "tool.started", tool=name, attempt=attempt)
            try:
                result = await asyncio.wait_for(_invoke(tool.handler, validated), timeout=timeout_s)
                latency_ms = int((time.perf_counter() - started) * 1000)
                self.trace.emit(trace_id, "tool.completed", tool=name, attempt=attempt, latencyMs=latency_ms)
                return result, {"name": name, "status": "completed", "attempts": attempt, "latency_ms": latency_ms}
            except TimeoutError as error:
                last_error = error
                self.trace.emit(trace_id, "tool.retry", tool=name, attempt=attempt, code="TOOL_TIMEOUT")
            except Exception as error:
                last_error = error
                self.trace.emit(trace_id, "tool.retry", tool=name, attempt=attempt, code="TOOL_EXECUTION_FAILED")

        if tool.fallback:
            result = await _invoke(tool.fallback, validated)
            latency_ms = int((time.perf_counter() - started) * 1000)
            self.trace.emit(trace_id, "tool.degraded", tool=name, latencyMs=latency_ms)
            return result, {"name": name, "status": "degraded", "attempts": max_retries + 1, "latency_ms": latency_ms}

        code = "TOOL_TIMEOUT" if isinstance(last_error, TimeoutError) else "TOOL_EXECUTION_FAILED"
        self.trace.emit(trace_id, "tool.failed", tool=name, code=code)
        raise ToolError(code, f"tool {name} failed", trace_id, {"tool": name, "attempts": max_retries + 1}) from last_error


async def _invoke(handler: Callable[..., Any], arguments: dict[str, Any]) -> Any:
    result = handler(**arguments)
    return await result if inspect.isawaitable(result) else result


def read_diff(diff_text: str) -> dict[str, Any]:
    file_match = re.search(r"^\+\+\+ b/(.+)$", diff_text, re.MULTILINE)
    file = file_match.group(1) if file_match else "unknown"
    findings: list[Finding] = []
    line_no = 1
    for raw in diff_text.splitlines():
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw)
        if hunk:
            line_no = int(hunk.group(1))
        elif raw.startswith("+") and not raw.startswith("+++"):
            code = raw[1:]
            if "await " in code:
                findings.append(Finding(severity="high", category="error-handling", file=file, line=line_no, message="异步调用缺少明确失败处理。", suggestion="增加 try/catch 和失败状态。"))
            if "<img" in code and "alt=" not in code:
                findings.append(Finding(severity="medium", category="accessibility", file=file, line=line_no, message="图片缺少 alt。", suggestion="补充 alt。"))
            line_no += 1
    return {"file": file, "findings": [item.model_dump() for item in findings]}


def search_knowledge(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    entries = {
        "error-handling": {"id": "guide:error-handling", "title": "异步交互", "text": "异步操作需要失败状态和用户反馈。", "score": 1},
        "accessibility": {"id": "guide:accessibility", "title": "可访问性", "text": "图片需要 alt。", "score": 1},
    }
    return [entry for key, entry in entries.items() if key in query][:top_k]


def knowledge_fallback(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    return [{"id": "fallback:manual-review", "title": "人工审查", "text": "知识库不可用，请人工核对 finding。", "score": 0}]


def generate_patch_plan(file: str, findings: list[Finding | dict[str, Any]]) -> dict[str, Any]:
    validated_findings = [Finding.model_validate(item) for item in findings]
    return {
        "file": file,
        "risk": "requires-review" if any(item.severity == "high" for item in validated_findings) else "low",
        "steps": [{"category": item.category, "action": "按建议修改并补测试", "reason": item.message} for item in validated_findings],
    }


def build_executor(trace: TraceStore | None = None) -> ToolExecutor:
    return ToolExecutor([
        Tool("read_diff", ReadDiffArgs, read_diff),
        Tool("search_knowledge", SearchKnowledgeArgs, search_knowledge, fallback=knowledge_fallback),
        Tool("generate_patch_plan", GeneratePatchPlanArgs, generate_patch_plan),
    ], trace=trace)
