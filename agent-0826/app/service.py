import os
from pathlib import Path

from app.corpus import chunk_document, load_documents
from app.embeddings import HashEmbeddingProvider
from app.store import PostgresVectorStore, SQLiteVectorStore, VectorStore


def build_index(corpus: Path, database: Path) -> VectorStore:
    embeddings = HashEmbeddingProvider()
    if os.getenv("VECTOR_STORE_BACKEND", "sqlite").lower() == "postgres":
        store: VectorStore = PostgresVectorStore(
            os.getenv("DATABASE_URL", "postgresql://agent:agent@127.0.0.1:5432/agent"),
            embeddings,
        )
    else:
        store = SQLiteVectorStore(database, embeddings)
    chunks = [chunk for document in load_documents(corpus) for chunk in chunk_document(document)]
    store.replace(chunks)
    return store
