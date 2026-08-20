# Agent 0820：前端 Review Eval Dataset

第 2 周 Day 12。数据集位于 `data/eval-dataset.jsonl`，共 12 条真实前端问题样本，覆盖五个知识主题和一条无问题对照样本。

```bash
python -m src.validate_dataset
pytest
```

每行是一个独立 JSON 对象，包含 Diff、期望 category、期望 topic，以及每个 category 应引用的规范文档 ID。新增样本时必须写清可自动断言的检查点。
