from pathlib import Path

from src.validate_corpus import validate_corpus


def test_corpus_is_valid() -> None:
    root = Path(__file__).resolve().parents[1] / "knowledge"
    assert validate_corpus(root) == []
    assert len(list(root.rglob("*.md"))) == 15
