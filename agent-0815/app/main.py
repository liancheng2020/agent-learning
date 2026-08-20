import json

from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.agent import ReviewAgent
from app.errors import AgentError, ProviderFailure
from app.providers import create_provider
from app.schemas import ErrorResponse, ReviewRequest, ReviewResult
from app.tools import build_executor
from app.trace import trace_store

app = FastAPI(title="Frontend Review Agent", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def get_agent() -> ReviewAgent:
    try:
        provider = create_provider()
    except ProviderFailure as error:
        raise AgentError(error.code, error.message, "tr_config") from error
    return ReviewAgent(provider, build_executor(trace_store), trace_store)


@app.exception_handler(AgentError)
async def agent_error_handler(_: Request, error: AgentError) -> JSONResponse:
    status = 422 if error.code == "TOOL_INVALID_ARGUMENTS" else 502
    body = ErrorResponse(code=error.code, message=error.message, trace_id=error.trace_id, details=error.details)
    return JSONResponse(status_code=status, content=body.model_dump())


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "frontend-review-agent"}


@app.post("/review", response_model=ReviewResult, responses={422: {"model": ErrorResponse}, 502: {"model": ErrorResponse}})
async def review(request: ReviewRequest, agent: ReviewAgent = Depends(get_agent)) -> ReviewResult:
    return await agent.run(request)


@app.post("/review/stream")
async def review_stream(request: ReviewRequest, agent: ReviewAgent = Depends(get_agent)) -> StreamingResponse:
    async def stream():
        try:
            async for item in agent.events(request):
                yield _sse(item["event"], item)
        except AgentError as error:
            yield _sse("error", ErrorResponse(code=error.code, message=error.message, trace_id=error.trace_id, details=error.details).model_dump())

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/traces/{trace_id}")
def trace(trace_id: str) -> dict[str, object]:
    return {"trace_id": trace_id, "events": trace_store.get(trace_id)}


def _sse(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

