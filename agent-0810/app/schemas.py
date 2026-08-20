from typing import Literal

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    diff_text: str = Field(min_length=1, max_length=200_000)
    code: str = Field(default="", max_length=200_000)


class Finding(BaseModel):
    severity: Literal["high", "medium", "low"]
    category: str
    file: str
    line: int = Field(ge=1)
    message: str
    suggestion: str


class ReviewResponse(BaseModel):
    summary: str
    findings: list[Finding]

