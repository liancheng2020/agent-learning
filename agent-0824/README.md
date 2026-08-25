# Agent 0824：结构化 Trace

第 3 周 Day 16。在人工审批版上补齐端到端 Trace，让一次 Agent 运行可以通过 `trace_id` 解释成功、降级和失败原因。

## 记录内容

- 模型：provider、model name 和每百万 token 单价。
- Prompt：`prompt_version`，用于定位行为变更来自哪个版本。
- Tool：名称、结构化入参、结果摘要和耗时。
- Usage：input/output/total token 估算与 cost。
- Error：异常类型、消息和完整 Python stack trace。
- Run：总耗时和 `completed/degraded` 状态。

当前审查器是本地规则模型，因此 token 是近似值、cost 为 0。字段结构已经与真实 LLM Provider 解耦，接入真实 usage 后无需修改 Trace API。

## API

- `POST /review`：返回结果和 `trace_id`。
- `GET /traces/{trace_id}`：查询完整事件时间线。
- Day 15 的审批、Patch 和高风险操作接口全部保留。

## 运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8124
```

## 掌握标准

- 能从 `trace_id` 定位失败工具和错误栈。
- 能区分 token 估算与 Provider 返回的真实 usage。
- 能解释为什么 Trace 记录结果摘要，而不是无边界保存全部敏感输入。
- 能通过 Prompt 版本对比回归问题。
