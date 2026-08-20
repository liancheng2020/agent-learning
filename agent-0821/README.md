# Agent 0821：RAG 自动评测

第 2 周 Day 13。脚本逐条运行 12 个 Eval Case，输出命中率、引用正确率、JSON 合法率、工具成功率、平均延迟，并保留逐例失败原因。

```bash
python -m src.evaluate
pytest
```

报告写入 `reports/eval-report.json`。其中命中率按期望 category 计算，引用正确率要求引用命中指定规范文档，JSON 合法率通过 Pydantic 序列化后重新校验。

掌握标准：能从失败 case 定位是规则漏检、检索错误、引用错误、输出契约失败还是工具执行失败。
