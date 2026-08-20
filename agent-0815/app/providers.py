import json
import os
from abc import ABC, abstractmethod
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import ValidationError

from app.errors import ProviderFailure
from app.schemas import ReviewRequest, ReviewSynthesis, ToolCall

load_dotenv()


class ProviderTurn:
    def __init__(self, assistant_message: dict[str, Any], tool_calls: list[ToolCall] | None = None, final: ReviewSynthesis | None = None) -> None:
        self.assistant_message = assistant_message
        self.tool_calls = tool_calls or []
        self.final = final


class ModelProvider(ABC):
    name: str

    @abstractmethod
    async def next_turn(self, request: ReviewRequest, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ProviderTurn:
        raise NotImplementedError


class MockProvider(ModelProvider):
    name = "mock"

    async def next_turn(self, request: ReviewRequest, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ProviderTurn:
        results = {item["name"]: json.loads(item["content"]) for item in messages if item.get("role") == "tool"}
        if "read_diff" not in results:
            return _mock_call("call_read", "read_diff", {"diff_text": request.diff_text})
        if "search_knowledge" not in results:
            categories = " ".join(item["category"] for item in results["read_diff"]["findings"]) or "frontend review"
            return _mock_call("call_search", "search_knowledge", {"query": categories, "top_k": 3})
        if "generate_patch_plan" not in results:
            return _mock_call("call_plan", "generate_patch_plan", {"file": results["read_diff"]["file"], "findings": results["read_diff"]["findings"]})
        synthesis = ReviewSynthesis(
            summary=f"发现 {len(results['read_diff']['findings'])} 个问题",
            findings=results["read_diff"]["findings"],
            sources=results["search_knowledge"],
            patch_plan=results["generate_patch_plan"],
        )
        return ProviderTurn({"role": "assistant", "content": synthesis.model_dump_json()}, final=synthesis)


def _mock_call(call_id: str, name: str, arguments: dict[str, Any]) -> ProviderTurn:
    call = ToolCall(id=call_id, name=name, arguments=arguments)
    message = {"role": "assistant", "content": None, "tool_calls": [{"id": call_id, "type": "function", "function": {"name": name, "arguments": json.dumps(arguments, ensure_ascii=False)}}]}
    return ProviderTurn(message, tool_calls=[call])


class DeepSeekProvider(ModelProvider):
    name = "deepseek"

    def __init__(self, api_key: str, model: str = "deepseek-chat") -> None:
        if not api_key:
            raise ProviderFailure("PROVIDER_CONFIG_ERROR", "缺少 DEEPSEEK_API_KEY")
        self.api_key = api_key
        self.model = model

    async def next_turn(self, request: ReviewRequest, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ProviderTurn:
        try:
            async with httpx.AsyncClient(base_url="https://api.deepseek.com", timeout=45.0) as client:
                response = await client.post(
                    "/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "tools": tools,
                        "tool_choice": "auto",
                        "response_format": {"type": "json_object"},
                        "temperature": 0,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise ProviderFailure("PROVIDER_REQUEST_FAILED", "DeepSeek 请求失败") from error

        message = response.json()["choices"][0]["message"]
        assistant_message = {"role": "assistant", "content": message.get("content")}
        raw_calls = message.get("tool_calls") or []
        if raw_calls:
            assistant_message["tool_calls"] = raw_calls
            try:
                calls = [ToolCall(id=item["id"], name=item["function"]["name"], arguments=json.loads(item["function"]["arguments"])) for item in raw_calls]
            except (KeyError, TypeError, json.JSONDecodeError) as error:
                raise ProviderFailure("PROVIDER_INVALID_OUTPUT", "模型返回了无效的工具调用") from error
            return ProviderTurn(assistant_message, tool_calls=calls)
        try:
            final = ReviewSynthesis.model_validate_json(message.get("content") or "")
        except ValidationError as error:
            raise ProviderFailure("PROVIDER_INVALID_OUTPUT", "模型最终 JSON 不符合 ReviewSynthesis") from error
        return ProviderTurn(assistant_message, final=final)


def create_provider() -> ModelProvider:
    name = os.getenv("PROVIDER", "mock").lower()
    if name == "mock":
        return MockProvider()
    if name == "deepseek":
        return DeepSeekProvider(os.getenv("DEEPSEEK_API_KEY", ""), os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    raise ProviderFailure("PROVIDER_CONFIG_ERROR", f"不支持的 Provider：{name}")

