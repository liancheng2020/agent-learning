from fastapi import FastAPI

from app.agent import ReviewAgent
from app.schemas import ReviewRequest, ReviewResponse

app = FastAPI(title="Frontend Review Agent - Day 4")
agent = ReviewAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
async def review(request: ReviewRequest) -> ReviewResponse:
    return await agent.run(request)

