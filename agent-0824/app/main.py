from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.approval import ApprovalNotFound, ApprovalStore, InvalidApprovalTransition
from app.evaluate import build_agent, compare
from app.patches import generate_patch
from app.retrieval import KnowledgeRetriever
from app.schemas import (
    ApprovalDecision,
    ApprovalRecord,
    OperationRequest,
    PatchArtifact,
    PatchRequest,
    ReviewResult,
)
from app.trace import TraceStore

ROOT = Path(__file__).resolve().parents[1]


class ReviewRequest(BaseModel):
    diff_text: str = Field(min_length=1, max_length=200_000)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    topic: str | None = None
    top_k: int = Field(default=3, ge=1, le=10)


def create_app(
    root: Path = ROOT,
    approval_database: Path | None = None,
    trace_path: Path | None = None,
) -> FastAPI:
    traces = TraceStore(trace_path or root / "data" / "trace.jsonl")
    review_agent = build_agent(root, "tuned", traces)
    retriever: KnowledgeRetriever = review_agent.retriever
    approvals = ApprovalStore(approval_database or root / "data" / "approvals.db")
    application = FastAPI(title="Frontend Review Trace Agent", version="3.1.0")
    application.state.review_agent = review_agent
    application.state.traces = traces
    application.mount("/static", StaticFiles(directory=root / "app" / "static"), name="static")

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(root / "app" / "static" / "index.html")

    @application.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "service": "frontend-review-trace-agent", "approval_store": "sqlite", "trace_store": "jsonl"}

    @application.get("/traces/{trace_id}")
    def get_trace(trace_id: str) -> dict[str, object]:
        events = traces.get(trace_id)
        if not events:
            raise HTTPException(status_code=404, detail="trace not found")
        return {"trace_id": trace_id, "events": events}

    @application.post("/review", response_model=ReviewResult)
    def review(request: ReviewRequest) -> ReviewResult:
        return review_agent.review(request.diff_text)

    @application.post("/knowledge/search")
    def search(request: SearchRequest) -> dict[str, object]:
        citations = retriever.search_with_citations(request.query, request.top_k, request.topic)
        return {"query": request.query, "citations": [asdict(item) for item in citations]}

    @application.post("/eval")
    def run_evaluation() -> dict[str, object]:
        return compare(root)

    @application.post("/patches/requests", response_model=ApprovalRecord, status_code=202)
    def request_patch(request: PatchRequest) -> ApprovalRecord:
        return approvals.create(
            "generate_patch",
            request.model_dump(exclude={"requested_by", "reason"}),
            request.requested_by,
            request.reason,
        )

    @application.post("/operations/requests", response_model=ApprovalRecord, status_code=202)
    def request_operation(request: OperationRequest) -> ApprovalRecord:
        return approvals.create(
            request.action,
            {"target": request.target},
            request.requested_by,
            request.reason,
        )

    @application.get("/approvals/{approval_id}", response_model=ApprovalRecord)
    def get_approval(approval_id: str) -> ApprovalRecord:
        try:
            return approvals.get(approval_id)
        except ApprovalNotFound as error:
            raise HTTPException(status_code=404, detail="approval not found") from error

    @application.post("/approvals/{approval_id}/decision", response_model=ApprovalRecord)
    def decide_approval(approval_id: str, request: ApprovalDecision) -> ApprovalRecord:
        try:
            return approvals.decide(approval_id, request.decision, request.decided_by, request.reason)
        except ApprovalNotFound as error:
            raise HTTPException(status_code=404, detail="approval not found") from error
        except InvalidApprovalTransition as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @application.post("/patches/{approval_id}/generate", response_model=PatchArtifact)
    def generate_approved_patch(approval_id: str) -> PatchArtifact:
        try:
            approvals.require_approved(approval_id, "generate_patch")
            payload = approvals.get_payload(approval_id)
            artifact = generate_patch(approval_id=approval_id, **payload)
            approvals.save_result(approval_id, artifact.model_dump())
            return artifact
        except ApprovalNotFound as error:
            raise HTTPException(status_code=404, detail="approval not found") from error
        except InvalidApprovalTransition as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @application.post("/operations/{approval_id}/execute")
    def execute_approved_operation(approval_id: str) -> dict[str, object]:
        try:
            approval = approvals.get(approval_id)
            approvals.require_approved(approval_id, approval.action)
            if approval.action == "generate_patch":
                raise InvalidApprovalTransition("generate_patch 必须使用 Patch 生成接口")
            result = {
                "approval_id": approval_id,
                "action": approval.action,
                "executed": True,
                "target": approval.payload_summary["target"],
            }
            approvals.save_result(approval_id, result)
            return result
        except ApprovalNotFound as error:
            raise HTTPException(status_code=404, detail="approval not found") from error
        except InvalidApprovalTransition as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    return application


app = create_app()
