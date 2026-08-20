from pathlib import Path

from src.validate_dataset import load_dataset


def test_dataset_has_valid_real_cases() -> None:
    path = Path(__file__).resolve().parents[1] / "data" / "eval-dataset.jsonl"
    cases = load_dataset(path)
    assert len(cases) == 12
    assert {"react", "vue", "typescript", "performance", "security"} <= {
        topic for case in cases for topic in case.expected_topics
    }
    assert any(not case.expected_categories for case in cases)
