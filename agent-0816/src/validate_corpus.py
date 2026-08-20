from __future__ import annotations

import re
from pathlib import Path

import yaml

REQUIRED = {"id", "topic", "title", "tags", "source"}
TOPICS = {"react", "vue", "typescript", "performance", "security"}


def parse_document(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: 缺少 YAML front matter")
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict):
        raise ValueError(f"{path}: 元数据必须是对象")
    return metadata, match.group(2).strip()


def validate_corpus(root: Path) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    counts = {topic: 0 for topic in TOPICS}
    for path in sorted(root.rglob("*.md")):
        try:
            metadata, body = parse_document(path)
            missing = REQUIRED - metadata.keys()
            if missing:
                errors.append(f"{path.name}: 缺少 {sorted(missing)}")
                continue
            doc_id = str(metadata["id"])
            topic = str(metadata["topic"])
            if doc_id in ids:
                errors.append(f"{path.name}: id 重复 {doc_id}")
            ids.add(doc_id)
            if topic not in TOPICS:
                errors.append(f"{path.name}: 非法 topic {topic}")
            else:
                counts[topic] += 1
            if not isinstance(metadata["tags"], list) or not metadata["tags"]:
                errors.append(f"{path.name}: tags 必须是非空数组")
            if len(body) < 120 or "## 审查检查点" not in body:
                errors.append(f"{path.name}: 正文过短或缺少审查检查点")
        except (OSError, ValueError, yaml.YAMLError) as error:
            errors.append(str(error))
    for topic, count in counts.items():
        if count < 2:
            errors.append(f"{topic}: 文档不足 2 篇，当前 {count} 篇")
    return errors


if __name__ == "__main__":
    corpus = Path(__file__).resolve().parents[1] / "knowledge"
    failures = validate_corpus(corpus)
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"知识库验证通过：{len(list(corpus.rglob('*.md')))} 篇文档")
