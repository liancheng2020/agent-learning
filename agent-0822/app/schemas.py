from typing import Literal

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
    status: Literal["completed", "failed"]
    latency_ms: float = Field(ge=0)


class ReviewResult(BaseModel):
    summary: str
    findings: list[ReviewFinding]
    tool_runs: list[ToolRun]
    prompt_version: str
