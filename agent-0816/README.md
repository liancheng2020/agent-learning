# Agent 0816：前端规范知识库

第 2 周 Day 8。目标不是收集长文章，而是把可执行的前端规范整理为适合 RAG 检索的短文档。

知识库包含 React、Vue、TypeScript、性能、安全五个主题，每个主题三篇。每篇文档都有稳定 id、主题、标签和来源元数据，正文包含规则、原因与审查检查点。

Windows PowerShell：

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python src/validate_corpus.py
python -m pytest
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/validate_corpus.py
python -m pytest
```

掌握标准：能解释为什么 RAG 文档要短、元数据要稳定、检查点要具体，并能新增一篇通过验证的规范文档。
