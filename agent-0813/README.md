# Agent 0813：Tool 容错与可观测性

第 1 周 Day 5。所有 Tool 都通过 `ToolExecutor` 执行，统一处理参数校验、超时、重试、降级、错误码和 trace。

## 运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8113
```

## 稳定错误码

- `TOOL_NOT_FOUND`
- `TOOL_INVALID_ARGUMENTS`
- `TOOL_TIMEOUT`
- `TOOL_EXECUTION_FAILED`

## 必须掌握

- 超时限制的是单次尝试；重试次数必须有上限。
- 只有幂等或明确可重试的操作才适合自动重试。
- 降级结果必须标记 `degraded`，不能伪装成正常成功。
- 用户拿到 `trace_id` 后，可以查询一次运行的完整事件链。

