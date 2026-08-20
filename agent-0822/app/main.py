from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.evaluate import build_agent, compare
from app.retrieval import KnowledgeRetriever
from app.schemas import ReviewResult

ROOT = Path(__file__).resolve().parents[1]
agent = build_agent(ROOT, "tuned")
retriever: KnowledgeRetriever = agent.retriever

app = FastAPI(title="Frontend Review RAG Agent", version="2.0.0")
app.mount("/static", StaticFiles(directory=ROOT / "app" / "static"), name="static")


class ReviewRequest(BaseModel):
    diff_text: str = Field(min_length=1, max_length=200_000)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    topic: str | None = None
    top_k: int = Field(default=3, ge=1, le=10)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "app" / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "service": "frontend-review-rag-agent", "knowledge_documents": 15}


@app.post("/review", response_model=ReviewResult)
def review(request: ReviewRequest) -> ReviewResult:
    return agent.review(request.diff_text)


@app.post("/knowledge/search")
def search(request: SearchRequest) -> dict[str, object]:
    citations = retriever.search_with_citations(request.query, request.top_k, request.topic)
    return {"query": request.query, "citations": [asdict(item) for item in citations]}


@app.post("/eval")
def run_evaluation() -> dict[str, object]:
    return compare(ROOT)
