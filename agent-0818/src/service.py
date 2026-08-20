from pathlib import Path

from src.corpus import chunk_document, load_documents
from src.embeddings import HashEmbeddingProvider
from src.store import SQLiteVectorStore


def build_index(corpus: Path, database: Path) -> SQLiteVectorStore:
    store = SQLiteVectorStore(database, HashEmbeddingProvider())
    chunks = [chunk for document in load_documents(corpus) for chunk in chunk_document(document)]
    store.replace(chunks)
    return store
