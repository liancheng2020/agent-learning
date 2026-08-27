from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    topic: str
    content: str
    source_path: str
    tags: list[str] = field(default_factory=list)
    source: str = ""


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    vector_score: float
    score: float


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    document_id: str
    title: str
    topic: str
    source_path: str
    quote: str
    score: float
