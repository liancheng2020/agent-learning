from typing import Literal

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    diff_text: str = Field(min_length=1, max_length=200_000)
    code: str = Field(default="", max_length=200_000)


class Finding(BaseModel):
    severity: Literal["high", "medium", "low"]
    category: str = Field(min_length=1)
    file: str = Field(min_length=1)
    line: int = Field(ge=1)
    message: str = Field(min_length=1)
    suggestion: str = Field(min_length=1)


class ReviewPayload(BaseModel):
    summary: str = Field(min_length=1)
    findings: list[Finding]


class ReviewResponse(ReviewPayload):
    provider: str

