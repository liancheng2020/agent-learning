from pathlib import Path

from src.corpus import chunk_document, load_documents
from src.service import build_index


def test_parse_chunk_index_and_search(tmp_path: Path) -> None:
    corpus = Path(__file__).resolve().parents[2] / "agent-0816" / "knowledge"
    documents = load_documents(corpus)
    assert len(documents) == 15
    assert all(chunk.metadata["topic"] for doc in documents for chunk in chunk_document(doc))
    store = build_index(corpus, tmp_path / "knowledge.db")
    assert store.count() >= 15
    hits = store.search("React useEffect dependency cleanup", top_k=3, topic="react")
    assert hits
    assert all(hit.chunk.metadata["topic"] == "react" for hit in hits)
    assert any("Effect" in hit.chunk.content for hit in hits)
