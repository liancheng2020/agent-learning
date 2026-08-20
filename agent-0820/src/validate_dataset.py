from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class EvalCase(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    diff_text: str = Field(min_length=1)
    expected_categories: list[str]
    expected_topics: list[str]
    expected_citations: dict[str, str]


def load_dataset(path: Path) -> list[EvalCase]:
    cases: list[EvalCase] = []
    ids: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        case = EvalCase.model_validate(json.loads(line))
        if case.id in ids:
            raise ValueError(f"line {number}: duplicate id {case.id}")
        if set(case.expected_citations) != set(case.expected_categories):
            raise ValueError(f"line {number}: citation keys must match categories")
        ids.add(case.id)
        cases.append(case)
    if len(cases) < 10:
        raise ValueError("dataset requires at least 10 cases")
    return cases


if __name__ == "__main__":
    dataset = Path(__file__).resolve().parents[1] / "data" / "eval-dataset.jsonl"
    cases = load_dataset(dataset)
    print(f"数据集验证通过：{len(cases)} 条")
