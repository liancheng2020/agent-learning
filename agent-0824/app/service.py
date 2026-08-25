from pathlib import Path

from app.corpus import chunk_document, load_documents
from app.embeddings import HashEmbeddingProvider
from app.store import SQLiteVectorStore


def build_index(corpus: Path, database: Path) -> SQLiteVectorStore:
    store = SQLiteVectorStore(database, HashEmbeddingProvider())
    chunks = [chunk for document in load_documents(corpus) for chunk in chunk_document(document)]
    store.replace(chunks)
    return store
