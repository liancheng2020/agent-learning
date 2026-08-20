import json

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.agent import review_events
from app.schemas import ReviewRequest, ReviewResult

app = FastAPI(title="Frontend Review Agent - Day 6")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResult)
async def review(request: ReviewRequest) -> ReviewResult:
    async for item in review_events(request):
        if item["event"] == "final":
            return ReviewResult.model_validate(item["result"])
    raise RuntimeError("agent finished without a result")


@app.post("/review/stream")
async def review_stream(request: ReviewRequest) -> StreamingResponse:
    async def stream():
        async for item in review_events(request):
            yield f"event: {item['event']}\ndata: {json.dumps(item, ensure_ascii=False)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

