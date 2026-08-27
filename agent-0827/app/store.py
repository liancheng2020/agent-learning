from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Protocol

import psycopg
from psycopg.rows import dict_row

from app.embeddings import EmbeddingProvider
from app.models import Chunk, SearchHit


class VectorStore(Protocol):
    def replace(self, chunks: list[Chunk]) -> None: ...

    def count(self) -> int: ...

    def search(self, query: str, top_k: int = 3, topic: str | None = None) -> list[SearchHit]: ...


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


class PostgresVectorStore:
    def __init__(self, dsn: str, embeddings: EmbeddingProvider, dimensions: int = 256) -> None:
        self.dsn = dsn
        self.embeddings = embeddings
        self.dimensions = dimensions
        self._create_schema()

    def _connect(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _create_schema(self) -> None:
        with self._connect() as connection:
            connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
            connection.execute(
                f"""CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB NOT NULL,
                embedding VECTOR({self.dimensions}) NOT NULL
                )"""
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops)"
            )

    def replace(self, chunks: list[Chunk]) -> None:
        vectors = self.embeddings.embed([chunk.content for chunk in chunks])
        rows = [
            (
                chunk.id,
                chunk.document_id,
                chunk.content,
                json.dumps(chunk.metadata, ensure_ascii=False),
                _vector_literal(vector),
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        with self._connect() as connection:
            connection.execute("DELETE FROM chunks")
            connection.executemany(
                "INSERT INTO chunks VALUES (%s, %s, %s, %s::jsonb, %s::vector)",
                rows,
            )

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM chunks").fetchone()
        return int(row["count"])

    def search(self, query: str, top_k: int = 3, topic: str | None = None) -> list[SearchHit]:
        vector = _vector_literal(self.embeddings.embed([query])[0])
        params: list[object] = [vector]
        where = ""
        if topic:
            where = "WHERE metadata->>'topic' = %s"
            params.append(topic)
        params.extend([vector, top_k])
        sql = f"""
            SELECT id, document_id, content, metadata,
                   1 - (embedding <=> %s::vector) AS vector_score
            FROM chunks
            {where}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [
            SearchHit(
                chunk=Chunk(
                    id=row["id"],
                    document_id=row["document_id"],
                    content=row["content"],
                    metadata=row["metadata"],
                ),
                vector_score=float(row["vector_score"]),
                score=float(row["vector_score"]),
            )
            for row in rows
        ]


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{value:.10f}" for value in vector) + "]"
