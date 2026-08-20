from uuid import uuid4

from app.schemas import Finding, PatchPlan, ReviewRequest, ReviewResponse, Source, ToolCallRecord
from app.tools import ToolExecutor, build_executor
from app.trace import TraceStore, trace_store


class ReviewAgent:
    def __init__(self, executor: ToolExecutor | None = None, trace: TraceStore | None = None) -> None:
        self.trace = trace or trace_store
        self.executor = executor or build_executor(self.trace)

    async def run(self, request: ReviewRequest, trace_id: str | None = None) -> ReviewResponse:
        trace_id = trace_id or f"tr_{uuid4().hex[:16]}"
        self.trace.emit(trace_id, "run.started")
        records: list[ToolCallRecord] = []

        read, record = await self.executor.execute("read_diff", {"diff_text": request.diff_text}, trace_id)
        records.append(ToolCallRecord.model_validate(record))
        findings = [Finding.model_validate(item) for item in read["findings"]]

        query = " ".join(item.category for item in findings) or "frontend review"
        source_data, record = await self.executor.execute("search_knowledge", {"query": query}, trace_id)
        records.append(ToolCallRecord.model_validate(record))

        plan_data, record = await self.executor.execute("generate_patch_plan", {"file": read["file"], "findings": [item.model_dump() for item in findings]}, trace_id)
        records.append(ToolCallRecord.model_validate(record))

        response = ReviewResponse(
            trace_id=trace_id,
            summary=f"发现 {len(findings)} 个问题",
            findings=findings,
            sources=[Source.model_validate(item) for item in source_data],
            patch_plan=PatchPlan.model_validate(plan_data),
            tool_calls=records,
        )
        self.trace.emit(trace_id, "run.completed", findingCount=len(findings))
        return response

