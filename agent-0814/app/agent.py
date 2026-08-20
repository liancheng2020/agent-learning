import asyncio
import re
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.schemas import Finding, ReviewRequest, ReviewResult


async def review_events(request: ReviewRequest, trace_id: str | None = None) -> AsyncIterator[dict[str, Any]]:
    trace_id = trace_id or f"tr_{uuid4().hex[:16]}"
    yield event("phase", trace_id, stage="received", label="请求已接收")
    await asyncio.sleep(0)
    yield event("phase", trace_id, stage="planning", label="Agent 正在规划工具调用")

    yield event("tool", trace_id, tool="read_diff", status="running")
    file, findings = _read_diff(request.diff_text)
    yield event("tool", trace_id, tool="read_diff", status="completed", findingCount=len(findings))

    yield event("tool", trace_id, tool="search_knowledge", status="running")
    sources = _search_knowledge(findings)
    yield event("tool", trace_id, tool="search_knowledge", status="completed", sourceCount=len(sources))

    yield event("tool", trace_id, tool="generate_patch_plan", status="running")
    patch_plan = _generate_patch_plan(file, findings)
    yield event("tool", trace_id, tool="generate_patch_plan", status="completed", risk=patch_plan["risk"])

    result = ReviewResult(
        trace_id=trace_id,
        summary=f"发现 {len(findings)} 个问题",
        findings=findings,
        sources=sources,
        patch_plan=patch_plan,
    )
    yield event("final", trace_id, result=result.model_dump())


def event(event_type: str, trace_id: str, **data: Any) -> dict[str, Any]:
    return {"event": event_type, "traceId": trace_id, **data}


def _read_diff(diff_text: str) -> tuple[str, list[Finding]]:
    match = re.search(r"^\+\+\+ b/(.+)$", diff_text, re.MULTILINE)
    file = match.group(1) if match else "unknown"
    findings: list[Finding] = []
    line_no = 1
    for raw in diff_text.splitlines():
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw)
        if hunk:
            line_no = int(hunk.group(1))
        elif raw.startswith("+") and not raw.startswith("+++"):
            code = raw[1:]
            if "await " in code:
                findings.append(Finding(severity="high", category="error-handling", file=file, line=line_no, message="异步调用缺少失败处理。", suggestion="增加 try/catch 和失败状态。"))
            if "<img" in code and "alt=" not in code:
                findings.append(Finding(severity="medium", category="accessibility", file=file, line=line_no, message="图片缺少 alt。", suggestion="补充有意义的 alt。"))
            line_no += 1
    return file, findings


def _search_knowledge(findings: list[Finding]) -> list[dict[str, object]]:
    guides = {
        "error-handling": {"id": "guide:error-handling", "title": "异步交互", "text": "异步操作应处理错误并给用户反馈。", "score": 1},
        "accessibility": {"id": "guide:accessibility", "title": "可访问性", "text": "图片必须设置合适的 alt。", "score": 1},
    }
    return [guides[item.category] for item in findings if item.category in guides]


def _generate_patch_plan(file: str, findings: list[Finding]) -> dict[str, object]:
    return {
        "file": file,
        "risk": "requires-review" if any(item.severity == "high" for item in findings) else "low",
        "steps": [{"category": item.category, "action": item.suggestion} for item in findings],
    }

