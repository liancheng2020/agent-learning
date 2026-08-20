from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.agent import ReviewAgent
from app.errors import AgentError
from app.schemas import ErrorResponse, ReviewRequest, ReviewResponse
from app.trace import trace_store

app = FastAPI(title="Frontend Review Agent - Day 5")
agent = ReviewAgent()


@app.exception_handler(AgentError)
async def agent_error_handler(_: Request, error: AgentError) -> JSONResponse:
    status = 422 if error.code == "TOOL_INVALID_ARGUMENTS" else 502
    body = ErrorResponse(code=error.code, message=error.message, trace_id=error.trace_id, details=error.details)
    return JSONResponse(status_code=status, content=body.model_dump())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
async def review(request: ReviewRequest) -> ReviewResponse:
    return await agent.run(request)


@app.get("/traces/{trace_id}")
def trace(trace_id: str) -> dict[str, object]:
    return {"trace_id": trace_id, "events": trace_store.get(trace_id)}

