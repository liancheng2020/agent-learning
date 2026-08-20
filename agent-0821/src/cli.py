import argparse
import json
from dataclasses import asdict
from pathlib import Path

from src.embeddings import HashEmbeddingProvider
from src.retrieval import KnowledgeRetriever
from src.service import build_index
from src.store import SQLiteVectorStore

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT.parent / "agent-0816" / "knowledge"
DATABASE = ROOT / "data" / "knowledge.db"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--topic")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    store = SQLiteVectorStore(DATABASE, HashEmbeddingProvider())
    if store.count() == 0:
        store = build_index(CORPUS, DATABASE)
    citations = KnowledgeRetriever(store).search_with_citations(args.query, args.top_k, args.topic)
    print(json.dumps([asdict(item) for item in citations], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
