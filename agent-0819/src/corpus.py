from __future__ import annotations

import re
from pathlib import Path

import yaml

from src.models import Chunk, Document


def parse_document(path: Path) -> Document:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: invalid front matter")
    metadata = yaml.safe_load(match.group(1))
    required = {"id", "title", "topic", "tags", "source"}
    if not isinstance(metadata, dict) or required - metadata.keys():
        raise ValueError(f"{path}: incomplete metadata")
    return Document(
        id=str(metadata["id"]),
        title=str(metadata["title"]),
        topic=str(metadata["topic"]),
        tags=[str(tag) for tag in metadata["tags"]],
        source=str(metadata["source"]),
        source_path=str(path),
        content=match.group(2).strip(),
    )


def load_documents(root: Path) -> list[Document]:
    return [parse_document(path) for path in sorted(root.rglob("*.md"))]


def chunk_document(document: Document, max_chars: int = 520) -> list[Chunk]:
    blocks = [item.strip() for item in re.split(r"\n\s*\n", document.content) if item.strip()]
    chunks: list[str] = []
    current = ""
    for block in blocks:
        candidate = f"{current}\n\n{block}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = block
        else:
            current = candidate
    if current:
        chunks.append(current)
    return [
        Chunk(
            id=f"{document.id}#{index}",
            document_id=document.id,
            content=content,
            metadata={
                "title": document.title,
                "topic": document.topic,
                "tags": document.tags,
                "source": document.source,
                "source_path": document.source_path,
                "chunk_index": index,
            },
        )
        for index, content in enumerate(chunks)
    ]
