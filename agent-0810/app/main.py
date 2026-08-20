from fastapi import FastAPI

from app.reviewer import review_diff
from app.schemas import ReviewRequest, ReviewResponse

app = FastAPI(title="Frontend Review Agent - Day 2", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest) -> ReviewResponse:
    return review_diff(request.diff_text)

