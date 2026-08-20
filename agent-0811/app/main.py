from fastapi import Depends, FastAPI

from app.providers import ModelProvider, create_provider
from app.schemas import ReviewRequest, ReviewResponse

app = FastAPI(title="Frontend Review Agent - Day 3", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
async def review(
    request: ReviewRequest,
    provider: ModelProvider = Depends(create_provider),
) -> ReviewResponse:
    payload = await provider.review(request)
    return ReviewResponse(provider=provider.name, **payload.model_dump())

