from pathlib import Path

from src.retrieval import KnowledgeRetriever
from src.service import build_index


def test_rerank_returns_exact_security_citations(tmp_path: Path) -> None:
    corpus = Path(__file__).resolve().parents[2] / "agent-0816" / "knowledge"
    store = build_index(corpus, tmp_path / "knowledge.db")
    retriever = KnowledgeRetriever(store)
    hits = retriever.search("localStorage token XSS cookie", top_k=3, topic="security")
    citations = retriever.search_with_citations("localStorage token XSS cookie", top_k=3, topic="security")
    assert citations[0].document_id == "security-token-storage"
    assert all(item.topic == "security" for item in citations)
    by_chunk = {hit.chunk.id: hit.chunk.content for hit in hits}
    assert all(item.quote in by_chunk[item.chunk_id] for item in citations)
