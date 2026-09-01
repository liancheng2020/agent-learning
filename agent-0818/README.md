# Agent 0818：检索重排与可核验引用

第 2 周 Day 10。在向量召回后使用词法覆盖率和 topic 过滤重排，并返回命中的规范原文。

Windows PowerShell：

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m src.cli 'localStorage token XSS' --topic security
python -m pytest
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.cli "localStorage token XSS" --topic security
python -m pytest
```

每条引用包含 `document_id`、`chunk_id`、标题、主题、源文件、分数和 `quote`。quote 必须来自真实 chunk，不能让模型自行编造。

掌握标准：能区分召回和重排，能证明回答中的引用来自哪份文档的哪个 chunk。
