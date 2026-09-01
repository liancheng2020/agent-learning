# Agent 0822：Frontend Review RAG Agent

第 2 周 Day 14 完整作品。项目把前端规范知识库、SQLite 向量检索、重排、可核验引用、Diff Review Agent、JSONL 数据集和自动评测整合为一个可运行的 FastAPI 应用。

## 快速开始

Windows PowerShell：

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m pytest
python -m app.evaluate --compare
python -m uvicorn app.main:app --reload --port 8122
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python -m app.evaluate --compare
python -m uvicorn app.main:app --reload --port 8122
```

打开：

- Dashboard：`http://127.0.0.1:8122`
- OpenAPI：`http://127.0.0.1:8122/docs`
- 健康检查：`http://127.0.0.1:8122/health`

## API

- `POST /review`：审查 Diff，每条 finding 返回规范引用。
- `POST /knowledge/search`：独立验证检索和引用。
- `POST /eval`：运行 baseline/tuned 对比并刷新报告。
- `GET /health`：服务和知识库状态。

## 实现边界

- 默认 Hash Embedding 离线、确定、免费，适合学习和回归测试，不代表生产语义向量质量。
- `EmbeddingProvider` 与 `SQLiteVectorStore` 已隔离，后续可替换真实 Embedding 和 PostgreSQL + pgvector。
- 当前规则集只覆盖数据集中定义的 11 类前端问题；评测满分不等于可替代人工 Code Review。
- 评测报告位于 `reports/baseline.json`、`reports/tuned.json`、`reports/iteration.md`。

## 掌握标准

1. 能从 Markdown 解释到 Chunk、Embedding、SQLite 和 rerank 的数据流。
2. 能证明每条引用是源 chunk 的精确片段。
3. 能新增一条规范、一条检测规则和一条 Eval Case。
4. 能运行 baseline/tuned 评测，并根据失败样本修改规则或检索参数。
5. 能解释为什么当前 12 条满分仍需要更多真实线上样本。
