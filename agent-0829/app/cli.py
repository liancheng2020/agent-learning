import argparse
import json
from dataclasses import asdict
from pathlib import Path

from app.evaluate import build_agent

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    review = subparsers.add_parser("review")
    review.add_argument("diff_file", type=Path)
    search = subparsers.add_parser("search")
    search.add_argument("query")
    search.add_argument("--topic")
    args = parser.parse_args()
    agent = build_agent(ROOT, "tuned")
    if args.command == "review":
        result = agent.review(args.diff_file.read_text(encoding="utf-8"))
        print(result.model_dump_json(indent=2))
        return
    citations = agent.retriever.search_with_citations(args.query, top_k=3, topic=args.topic)
    print(json.dumps([asdict(item) for item in citations], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
