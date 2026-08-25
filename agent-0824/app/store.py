from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.embeddings import EmbeddingProvider
from app.models import Chunk, SearchHit


class SQLiteVectorStore:
    def __init__(self, path: Path, embeddings: EmbeddingProvider) -> None:
        self.path = path
        self.embeddings = embeddings
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._create_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                embedding TEXT NOT NULL
                )"""
            )

    def replace(self, chunks: list[Chunk]) -> None:
        vectors = self.embeddings.embed([chunk.content for chunk in chunks])
        rows = [
            (chunk.id, chunk.document_id, chunk.content, json.dumps(chunk.metadata, ensure_ascii=False), json.dumps(vector))
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        with self._connect() as connection:
            connection.execute("DELETE FROM chunks")
            connection.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?)", rows)

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])

    def search(self, query: str, top_k: int = 3, topic: str | None = None) -> list[SearchHit]:
        query_vector = self.embeddings.embed([query])[0]
        sql = "SELECT * FROM chunks"
        rows: list[sqlite3.Row]
        with self._connect() as connection:
            rows = list(connection.execute(sql))
        hits: list[SearchHit] = []
        for row in rows:
            metadata = json.loads(row["metadata"])
            if topic and metadata.get("topic") != topic:
                continue
            vector = json.loads(row["embedding"])
            score = sum(left * right for left, right in zip(query_vector, vector, strict=True))
            chunk = Chunk(id=row["id"], document_id=row["document_id"], content=row["content"], metadata=metadata)
            hits.append(SearchHit(chunk=chunk, vector_score=score, score=score))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:top_k]
