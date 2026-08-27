from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class CitationModel(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    topic: str
    source_path: str
    quote: str
    score: float


class ReviewFinding(BaseModel):
    category: str
    severity: Literal["high", "medium", "low"]
    message: str
    suggestion: str
    topic: str
    citations: list[CitationModel] = Field(min_length=1)


class ToolRun(BaseModel):
    name: Literal["search_knowledge"]
    query: str
    status: Literal["completed", "failed", "cached"]
    latency_ms: float = Field(ge=0)


class ReviewResult(BaseModel):
    trace_id: str
    cache_hit: bool = False
    summary: str
    findings: list[ReviewFinding]
    tool_runs: list[ToolRun]
    prompt_version: str


ApprovalAction = Literal["generate_patch", "apply_patch", "deploy"]
ApprovalStatus = Literal["pending", "approved", "rejected"]


class PatchRequest(BaseModel):
    file_path: str = Field(min_length=1, max_length=500)
    original_text: str = Field(max_length=200_000)
    proposed_text: str = Field(max_length=200_000)
    requested_by: str = Field(default="developer", min_length=1, max_length=100)
    reason: str = Field(default="Agent 生成候选 Patch", min_length=1, max_length=500)


class OperationRequest(BaseModel):
    action: Literal["apply_patch", "deploy"]
    target: str = Field(min_length=1, max_length=500)
    requested_by: str = Field(default="developer", min_length=1, max_length=100)
    reason: str = Field(min_length=1, max_length=500)


class ApprovalDecision(BaseModel):
    decision: Literal["approved", "rejected"]
    decided_by: str = Field(min_length=1, max_length=100)
    reason: str = Field(default="", max_length=500)


class ApprovalRecord(BaseModel):
    id: str
    action: ApprovalAction
    status: ApprovalStatus
    requested_by: str
    reason: str
    payload_summary: dict[str, Any]
    result: dict[str, Any] | None = None
    created_at: datetime
    decided_at: datetime | None = None
    decided_by: str | None = None


class PatchArtifact(BaseModel):
    approval_id: str
    file_path: str
    summary: str
    unified_diff: str
