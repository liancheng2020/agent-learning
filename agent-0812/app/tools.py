import re
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from app.schemas import Finding, PatchPlan, PatchStep, Source


class ReadDiffArgs(BaseModel):
    diff_text: str = Field(min_length=1, max_length=200_000)


class SearchKnowledgeArgs(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=5)


class GeneratePatchPlanArgs(BaseModel):
    file: str = Field(min_length=1)
    findings: list[Finding]


KNOWLEDGE = [
    Source(id="guide:error-handling", title="异步交互", text="异步操作需要失败状态和用户反馈。", score=0),
    Source(id="guide:accessibility", title="可访问性", text="图片需要 alt，装饰图片使用空 alt。", score=0),
    Source(id="guide:security", title="凭据存储", text="浏览器存储敏感凭据前需要评估 XSS 风险。", score=0),
]


class Tool:
    def __init__(self, name: str, args_model: type[BaseModel], handler: Callable[..., Any], description: str) -> None:
        self.name = name
        self.args_model = args_model
        self.handler = handler
        self.description = description

    def call(self, arguments: dict[str, Any]) -> Any:
        validated = self.args_model.model_validate(arguments)
        return self.handler(**validated.model_dump())

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_model.model_json_schema(),
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        return self._tools[name].call(arguments)

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]


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
                findings.append(Finding(severity="medium", category="accessibility", file=file, line=line_no, message="图片缺少 alt。", suggestion="补充有意义的 alt。"))
            if "localStorage.setItem" in code:
                findings.append(Finding(severity="medium", category="security", file=file, line=line_no, message="可能在 localStorage 中存储敏感凭据。", suggestion="评估 httpOnly cookie 或缩短 token 生命周期。"))
            line_no += 1
        elif not raw.startswith("-"):
            line_no += 1
    return {"file": file, "findings": [item.model_dump() for item in findings]}


def search_knowledge(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    terms = set(re.findall(r"[a-z0-9-]+|[\u4e00-\u9fa5]+", query.lower()))
    scored = []
    for source in KNOWLEDGE:
        haystack = f"{source.id} {source.title} {source.text}".lower()
        score = sum(term in haystack for term in terms)
        if score:
            scored.append(source.model_copy(update={"score": score}))
    return [item.model_dump() for item in sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]]


def generate_patch_plan(file: str, findings: list[Finding | dict[str, Any]]) -> dict[str, Any]:
    validated_findings = [Finding.model_validate(item) for item in findings]
    actions = {
        "error-handling": "用 try/catch 包裹异步调用并展示失败状态",
        "accessibility": "为图片补充正确的 alt",
        "security": "调整敏感凭据的浏览器存储方案",
    }
    plan = PatchPlan(
        file=file,
        risk="requires-review" if any(item.severity == "high" for item in validated_findings) else "low",
        steps=[PatchStep(category=item.category, action=actions.get(item.category, "人工确认"), reason=item.message) for item in validated_findings],
    )
    return plan.model_dump()


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(Tool("read_diff", ReadDiffArgs, read_diff, "读取 Git diff 并返回结构化审查发现"))
    registry.register(Tool("search_knowledge", SearchKnowledgeArgs, search_knowledge, "检索与发现相关的本地规范"))
    registry.register(Tool("generate_patch_plan", GeneratePatchPlanArgs, generate_patch_plan, "根据发现生成可审查的修复计划"))
    return registry
