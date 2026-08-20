import asyncio

import pytest
from pydantic import BaseModel

from app.errors import ToolError
from app.tools import Tool, ToolExecutor, build_executor
from app.trace import TraceStore


class EmptyArgs(BaseModel):
    pass


@pytest.mark.asyncio
async def test_invalid_arguments_have_stable_error_code() -> None:
    with pytest.raises(ToolError) as caught:
        await build_executor().execute("search_knowledge", {"query": "", "top_k": 99}, "tr_validation")
    assert caught.value.code == "TOOL_INVALID_ARGUMENTS"
    assert caught.value.trace_id == "tr_validation"


@pytest.mark.asyncio
async def test_timeout_retries_then_fails() -> None:
    attempts = 0

    async def slow() -> None:
        nonlocal attempts
        attempts += 1
        await asyncio.sleep(0.05)

    executor = ToolExecutor([Tool("slow", EmptyArgs, slow)])
    with pytest.raises(ToolError) as caught:
        await executor.execute("slow", {}, "tr_timeout", timeout_s=0.005, max_retries=1)
    assert caught.value.code == "TOOL_TIMEOUT"
    assert attempts == 2


@pytest.mark.asyncio
async def test_fallback_marks_tool_as_degraded() -> None:
    def broken() -> None:
        raise RuntimeError("offline")

    executor = ToolExecutor([Tool("knowledge", EmptyArgs, broken, fallback=lambda: ["manual-review"])])
    result, record = await executor.execute("knowledge", {}, "tr_fallback", max_retries=0)
    assert result == ["manual-review"]
    assert record["status"] == "degraded"


@pytest.mark.asyncio
async def test_trace_records_retry_and_failure() -> None:
    trace = TraceStore()
    executor = ToolExecutor([Tool("broken", EmptyArgs, lambda: 1 / 0)], trace=trace)
    with pytest.raises(ToolError):
        await executor.execute("broken", {}, "tr_events", max_retries=0)
    assert [item["event"] for item in trace.get("tr_events")] == ["tool.started", "tool.retry", "tool.failed"]

