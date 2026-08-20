import argparse
import json
from pathlib import Path

from src.embeddings import HashEmbeddingProvider
from src.service import build_index
from src.store import SQLiteVectorStore

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT.parent / "agent-0816" / "knowledge"
DEFAULT_DB = ROOT / "data" / "knowledge.db"


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--topic")
    args = parser.parse_args()
    if args.command == "build":
        store = build_index(DEFAULT_CORPUS, DEFAULT_DB)
        print(f"indexed {store.count()} chunks")
        return
    store = SQLiteVectorStore(DEFAULT_DB, HashEmbeddingProvider())
    if store.count() == 0:
        store = build_index(DEFAULT_CORPUS, DEFAULT_DB)
    payload = [
        {"id": hit.chunk.id, "score": round(hit.score, 4), "topic": hit.chunk.metadata["topic"], "text": hit.chunk.content}
        for hit in store.search(args.query, topic=args.topic)
    ]
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
