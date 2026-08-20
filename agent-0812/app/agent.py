from app.schemas import Finding, PatchPlan, ReviewRequest, ReviewResponse, Source, ToolCallRecord
from app.tools import ToolRegistry, build_registry


class ReviewAgent:
    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or build_registry()

    async def run(self, request: ReviewRequest) -> ReviewResponse:
        calls: list[ToolCallRecord] = []

        read_args = {"diff_text": request.diff_text}
        read_result = self.registry.call("read_diff", read_args)
        calls.append(ToolCallRecord(name="read_diff", arguments={"diff_text": "<omitted>"}))
        findings = [Finding.model_validate(item) for item in read_result["findings"]]

        query = " ".join(item.category for item in findings) or "frontend review"
        search_args = {"query": query, "top_k": 3}
        sources = [Source.model_validate(item) for item in self.registry.call("search_knowledge", search_args)]
        calls.append(ToolCallRecord(name="search_knowledge", arguments=search_args))

        plan_args = {"file": read_result["file"], "findings": [item.model_dump() for item in findings]}
        patch_plan = PatchPlan.model_validate(self.registry.call("generate_patch_plan", plan_args))
        calls.append(ToolCallRecord(name="generate_patch_plan", arguments={"file": read_result["file"], "finding_count": len(findings)}))

        return ReviewResponse(
            summary=f"发现 {len(findings)} 个问题",
            findings=findings,
            sources=sources,
            patch_plan=patch_plan,
            tool_calls=calls,
        )

