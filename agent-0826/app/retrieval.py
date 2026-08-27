from __future__ import annotations

from dataclasses import replace

from app.embeddings import tokenize
from app.models import Citation, SearchHit
from app.store import VectorStore


class KnowledgeRetriever:
    def __init__(self, store: VectorStore, rerank: bool = True, topic_boost: float = 0.15) -> None:
        self.store = store
        self.rerank = rerank
        self.topic_boost = topic_boost

    def search(self, query: str, top_k: int = 3, topic: str | None = None) -> list[SearchHit]:
        candidates = self.store.search(query, top_k=max(top_k * 4, 10), topic=topic)
        if not self.rerank:
            return candidates[:top_k]
        query_terms = set(tokenize(query))
        reranked: list[SearchHit] = []
        for hit in candidates:
            content_terms = set(tokenize(f"{hit.chunk.content} {' '.join(hit.chunk.metadata['tags'])}"))
            lexical = len(query_terms & content_terms) / max(len(query_terms), 1)
            topic_bonus = self.topic_boost if topic and hit.chunk.metadata["topic"] == topic else 0.0
            score = hit.vector_score * 0.65 + lexical * 0.35 + topic_bonus
            reranked.append(replace(hit, score=score))
        return sorted(reranked, key=lambda item: item.score, reverse=True)[:top_k]

    def search_with_citations(self, query: str, top_k: int = 3, topic: str | None = None) -> list[Citation]:
        return [citation_from_hit(hit) for hit in self.search(query, top_k=top_k, topic=topic)]


def citation_from_hit(hit: SearchHit) -> Citation:
    content = hit.chunk.content.strip()
    quote = content[:240]
    return Citation(
        chunk_id=hit.chunk.id,
        document_id=hit.chunk.document_id,
        title=str(hit.chunk.metadata["title"]),
        topic=str(hit.chunk.metadata["topic"]),
        source_path=str(hit.chunk.metadata["source_path"]),
        quote=quote,
        score=round(hit.score, 6),
    )
