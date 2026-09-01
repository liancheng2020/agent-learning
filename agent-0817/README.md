# Agent 0817：文档索引与 SQLite 向量检索

第 2 周 Day 9。项目实现文档解析、Chunk、Metadata、Embedding 接口和 SQLite 向量检索。

Windows PowerShell：

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m src.cli build
python -m src.cli search 'React useEffect 依赖遗漏'
python -m pytest
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.cli build
python -m src.cli search "React useEffect 依赖遗漏"
python -m pytest
```

默认读取 `../agent-0816/knowledge`，索引写入 `data/knowledge.db`。默认 Embedding 是离线确定性实现，不依赖模型密钥；生产环境可实现同一 `EmbeddingProvider` 协议并迁移到 PostgreSQL + pgvector。

掌握标准：能讲清文档、Chunk、向量、相似度和 metadata filter 各自解决的问题。
