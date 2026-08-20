import json
import os
import re
from abc import ABC, abstractmethod

import httpx

from app.schemas import Finding, ReviewPayload, ReviewRequest


class ModelProvider(ABC):
    name: str

    @abstractmethod
    async def review(self, request: ReviewRequest) -> ReviewPayload:
        raise NotImplementedError


class MockProvider(ModelProvider):
    name = "mock"

    async def review(self, request: ReviewRequest) -> ReviewPayload:
        file = _extract_file(request.diff_text)
        findings: list[Finding] = []
        for line_no, code in _added_lines(request.diff_text):
            if "await " in code:
                findings.append(Finding(
                    severity="high", category="error-handling", file=file, line=line_no,
                    message="异步调用需要确认失败处理。", suggestion="增加 try/catch 和失败状态。",
                ))
            if "<img" in code and "alt=" not in code:
                findings.append(Finding(
                    severity="medium", category="accessibility", file=file, line=line_no,
                    message="图片缺少 alt 属性。", suggestion="补充有意义的 alt。",
                ))
        return ReviewPayload(summary=f"发现 {len(findings)} 个问题", findings=findings)


class DeepSeekProvider(ModelProvider):
    name = "deepseek"

    def __init__(self, api_key: str, model: str = "deepseek-chat") -> None:
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is required")
        self.api_key = api_key
        self.model = model

    async def review(self, request: ReviewRequest) -> ReviewPayload:
        schema = ReviewPayload.model_json_schema()
        messages = [
            {
                "role": "system",
                "content": "你是前端代码审查 Agent。只输出 JSON，不输出 Markdown。输出必须符合给定 JSON Schema。",
            },
            {
                "role": "user",
                "content": f"JSON Schema:\n{json.dumps(schema, ensure_ascii=False)}\n\nGit diff:\n{request.diff_text}\n\n当前代码:\n{request.code}",
            },
        ]
        async with httpx.AsyncClient(base_url="https://api.deepseek.com", timeout=30.0) as client:
            response = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "temperature": 0,
                },
            )
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return ReviewPayload.model_validate_json(content)


def create_provider() -> ModelProvider:
    provider = os.getenv("PROVIDER", "mock").lower()
    if provider == "mock":
        return MockProvider()
    if provider == "deepseek":
        return DeepSeekProvider(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        )
    raise ValueError(f"unsupported provider: {provider}")


def _extract_file(diff_text: str) -> str:
    match = re.search(r"^\+\+\+ b/(.+)$", diff_text, re.MULTILINE)
    return match.group(1) if match else "unknown"


def _added_lines(diff_text: str) -> list[tuple[int, str]]:
    current = 1
    result: list[tuple[int, str]] = []
    for raw in diff_text.splitlines():
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw)
        if hunk:
            current = int(hunk.group(1))
        elif raw.startswith("+") and not raw.startswith("+++"):
            result.append((current, raw[1:]))
            current += 1
        elif not raw.startswith("-"):
            current += 1
    return result

