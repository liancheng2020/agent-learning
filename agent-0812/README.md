# Agent 0812：Tool Calling

第 1 周 Day 4。把原本直接调用的审查函数放进 Tool Registry，Agent 只能通过工具名称和结构化参数调用能力。

## 运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8112
```

## 三个工具

- `read_diff`：解析新增代码并生成 findings。
- `search_knowledge`：根据 finding 类别检索规范来源。
- `generate_patch_plan`：生成可审查的修复步骤和风险等级。

## 必须掌握

- Tool = 名称 + 描述 + 参数 Schema + 执行函数。
- Agent 负责调用顺序和上下文，Tool 只负责单一能力。
- 模型或外部输入给出的工具参数必须先通过 Pydantic 校验。
- Tool Calling 不意味着允许模型执行任意函数，只能调用注册表白名单。

