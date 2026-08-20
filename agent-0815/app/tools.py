import asyncio
import inspect
import re
import time
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.errors import AgentError
from app.schemas import Finding, PatchPlan, PatchStep, Source
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
    def __init__(self, name: str, description: str, args_model: type[BaseModel], handler: Callable[..., Any], fallback: Callable[..., Any] | None = None) -> None:
        self.name = name
        self.description = description
        self.args_model = args_model
        self.handler = handler
        self.fallback = fallback

    def api_schema(self) -> dict[str, Any]:
        return {"type": "function", "function": {"name": self.name, "description": self.description, "parameters": self.args_model.model_json_schema()}}


class ToolExecutor:
    def __init__(self, tools: list[Tool], trace: TraceStore | None = None) -> None:
        self.tools = {tool.name: tool for tool in tools}
        self.trace = trace or trace_store

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.api_schema() for tool in self.tools.values()]

    async def execute(self, name: str, arguments: dict[str, Any], trace_id: str, timeout_s: float, max_retries: int) -> tuple[Any, dict[str, Any]]:
        tool = self.tools.get(name)
        if not tool:
            raise AgentError("TOOL_NOT_FOUND", f"未注册的工具：{name}", trace_id, {"tool": name})
        try:
            args = tool.args_model.model_validate(arguments).model_dump()
        except ValidationError as error:
            self.trace.emit(trace_id, "tool.failed", tool=name, code="TOOL_INVALID_ARGUMENTS")
            raise AgentError("TOOL_INVALID_ARGUMENTS", "工具参数校验失败", trace_id, {"tool": name, "errors": error.errors(include_input=False)}) from error

        started = time.perf_counter()
        last_error: Exception | None = None
        for attempt in range(1, max_retries + 2):
            self.trace.emit(trace_id, "tool.started", tool=name, attempt=attempt)
            try:
                result = await asyncio.wait_for(_invoke(tool.handler, args), timeout=timeout_s)
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
            result = await _invoke(tool.fallback, args)
            latency_ms = int((time.perf_counter() - started) * 1000)
            self.trace.emit(trace_id, "tool.degraded", tool=name, latencyMs=latency_ms)
            return result, {"name": name, "status": "degraded", "attempts": max_retries + 1, "latency_ms": latency_ms}

        code = "TOOL_TIMEOUT" if isinstance(last_error, TimeoutError) else "TOOL_EXECUTION_FAILED"
        self.trace.emit(trace_id, "tool.failed", tool=name, code=code)
        raise AgentError(code, f"工具 {name} 执行失败", trace_id, {"tool": name, "attempts": max_retries + 1}) from last_error


async def _invoke(handler: Callable[..., Any], args: dict[str, Any]) -> Any:
    value = handler(**args)
    return await value if inspect.isawaitable(value) else value


def read_diff(diff_text: str) -> dict[str, Any]:
    file_match = re.search(r"^\+\+\+ b/(.+)$", diff_text, re.MULTILINE)
    file = file_match.group(1) if file_match else "unknown"
    findings: list[Finding] = []
    line_no = 1
    for raw in diff_text.splitlines():
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw)
        if hunk:
            line_no = int(hunk.group(1))
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            code = raw[1:]
            if "await " in code:
                findings.append(Finding(severity="high", category="error-handling", file=file, line=line_no, message="异步调用缺少明确失败处理。", suggestion="增加 try/catch，并提供用户可见的失败状态。"))
            if "<img" in code and "alt=" not in code:
                findings.append(Finding(severity="medium", category="accessibility", file=file, line=line_no, message="图片缺少 alt 属性。", suggestion="添加有意义的 alt；装饰图片使用空 alt。"))
            if "localStorage.setItem" in code:
                findings.append(Finding(severity="medium", category="security", file=file, line=line_no, message="可能将敏感凭据写入 localStorage。", suggestion="评估 httpOnly cookie 或缩短 token 生命周期。"))
            line_no += 1
        elif not raw.startswith("-"):
            line_no += 1
    if findings and not re.search(r"\.(test|spec)\.", diff_text):
        findings.append(Finding(severity="low", category="testing", file=file, line=1, message="缺少配套测试更新。", suggestion="补充成功、失败和可访问性测试。"))
    return {"file": file, "findings": [item.model_dump() for item in findings]}


KNOWLEDGE = [
    Source(id="guide:error-handling", title="异步交互", text="异步操作需要处理失败状态并向用户提供反馈。", score=0),
    Source(id="guide:accessibility", title="可访问性", text="图片需要有意义的 alt；装饰图片使用空 alt。", score=0),
    Source(id="guide:security", title="凭据存储", text="浏览器存储敏感凭据前需要评估 XSS、生命周期和 Cookie 方案。", score=0),
    Source(id="guide:testing", title="回归测试", text="修复应覆盖成功路径、失败路径和可访问性行为。", score=0),
]


def search_knowledge(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    terms = set(re.findall(r"[a-z0-9-]+|[\u4e00-\u9fa5]+", query.lower()))
    scored: list[Source] = []
    for source in KNOWLEDGE:
        haystack = f"{source.id} {source.title} {source.text}".lower()
        score = sum(term in haystack for term in terms)
        if score:
            scored.append(source.model_copy(update={"score": score}))
    return [item.model_dump() for item in sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]]


def knowledge_fallback(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    return [{"id": "fallback:manual-review", "title": "人工审查", "text": "知识检索暂不可用，请人工核对审查发现。", "score": 0}]


def generate_patch_plan(file: str, findings: list[Finding | dict[str, Any]]) -> dict[str, Any]:
    validated_findings = [Finding.model_validate(item) for item in findings]
    actions = {
        "error-handling": "用 try/catch 包裹异步调用并展示失败状态",
        "accessibility": "为图片补充正确的 alt",
        "security": "调整敏感凭据的浏览器存储方案",
        "testing": "补充回归测试",
    }
    plan = PatchPlan(
        file=file,
        risk="requires-review" if any(item.severity == "high" for item in validated_findings) else "low",
        steps=[PatchStep(category=item.category, action=actions.get(item.category, "人工确认"), reason=item.message) for item in validated_findings],
    )
    return plan.model_dump()


def build_executor(trace: TraceStore | None = None) -> ToolExecutor:
    return ToolExecutor([
        Tool("read_diff", "解析 Git diff 并返回结构化前端审查发现", ReadDiffArgs, read_diff),
        Tool("search_knowledge", "检索与审查发现相关的工程规范", SearchKnowledgeArgs, search_knowledge, fallback=knowledge_fallback),
        Tool("generate_patch_plan", "根据审查发现生成可人工审查的修复计划", GeneratePatchPlanArgs, generate_patch_plan),
    ], trace=trace)
