# Agent 0819：自动检索知识库的 Review Agent

第 2 周 Day 11。Agent 先审查 Diff，再为每条 finding 自动调用 `search_knowledge`，不依赖模型记忆补写规范。

Windows PowerShell：

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m pytest
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

输出受 Pydantic 约束，每条 finding 至少有一条真实引用；每次知识检索都记录为 tool run。没有引用的 finding 不会伪装成有依据的结论。

掌握标准：能解释规则定位、知识工具、引用绑定和结构化输出的完整链路。
