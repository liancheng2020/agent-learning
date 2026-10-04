# Agent 0827 面试材料（Day 19：Agent 故障演练）

## 30 秒介绍

> 在可部署全栈的基线上，我给 Agent 补上了“可重复的故障演练”能力：模型超时、工具异常、检索为空、JSON 失败、审批拒绝五类场景都能通过 `POST /drills/run` 一键触发。每个场景返回统一的错误结构 `code + message + suggestion + trace_id + retryable`，并由 FastAPI 的 `exception_handler` 统一渲染状态码；页面直接展示中文说明、处理建议和 `traceId`。每次演练都写入 Trace，配合参数化测试把故障行为固化成回归用例，而不是靠人肉复现。18 条测试覆盖 API、缓存、部署、Trace 和故障演练。

## 2 分钟演示

1. `docker compose up --build -d`，打开前端页面，展示五个演练按钮。
2. `curl -X POST .../drills/run -d '{"scenario":"model_timeout"}'` → `504 MODEL_TIMEOUT`，页面只提示重试/缩小 Diff，不展示残缺结果。
3. 依次触发 `tool_exception`（502）、`invalid_json`（502），说明都是 fail-closed。
4. 触发 `empty_retrieval` → `200 degraded / KNOWLEDGE_NOT_FOUND`，结果降级但**不伪造引用**。
5. 触发 `approval_rejected` → `200 blocked / APPROVAL_REJECTED`，生产操作被阻断，原审批决定不可覆盖。
6. 用返回的 `trace_id` 查 `/traces/{trace_id}`，展示 `drill.injected`、`drill.failed/completed` 事件。

## 五类场景与行为

| 场景 | 错误码 | 行为 |
| --- | --- | --- |
| 模型超时 | `MODEL_TIMEOUT` | 504，不展示不完整结果，提示重试或缩小 Diff |
| 工具异常 | `TOOL_EXECUTION_FAILED` | 502，停止无依据推断，提示检查工具 trace |
| 检索为空 | `KNOWLEDGE_NOT_FOUND` | 200 降级成功，不伪造引用，提示调整查询或知识库 |
| JSON 失败 | `MODEL_JSON_INVALID` | 502，拒绝不符合 Schema 的模型结果 |
| 审批拒绝 | `APPROVAL_REJECTED` | 200 阻断高风险操作，保留最终审批状态 |

## 关键取舍

- **为什么统一错误结构**：调用方和前端只需处理一套 `code/message/suggestion/trace_id/retryable`，异常在 `exception_handler` 里集中渲染，避免每个接口各写一套。
- **fail-open 还是 fail-closed**：判断“是否影响结论可信度”。检索为空只是缺依据，可以降级（fail-open）；模型超时和 JSON 失败会让结果不可信，必须拒绝（fail-closed），绝不把半截结果当成功。
- **为什么审批拒绝不是 5xx**：它是业务上的正常阻断，不是服务故障，所以用 200 + `status=blocked` 表达，保留 `APPROVAL_REJECTED` 语义。
- **为什么要写 Trace**：每次演练记录 `drill.injected` 和 `drill.failed/completed`，排查时先定位失败阶段，再结合 `traceId` 串联工具与审批事件。
- **为什么用演练而不是口头描述**：把故障变成可重复、可测试的入口，参数化用例能把行为（状态码 + 错误码 + 可重试性）锁死，防止回归。

## 高频追问

### 五类场景各自的行为差异是什么？

前两类（超时、工具异常）和 JSON 失败是硬失败，返回 4xx/5xx 且不产出结果；检索为空是可降级成功；审批拒绝是业务阻断。`FaultDrillService.run` 用一个 `_fail`（抛 `FaultDrillError`）和一个 `_complete`（返回 `DrillResult`）区分这两类出口。

### `retryable` 怎么决定？

由故障性质决定：超时、工具瞬时异常、JSON 偶发失败可重试（`retryable=true`）；检索为空、审批拒绝需要人先调整输入或风险项，标为不可盲目重试。

### 为什么 JSON 失败不直接重试多次？

结构化输出失败应先保证“不把坏数据当成功”。只做有限重试，仍失败就返回 `MODEL_JSON_INVALID`，同时提示检查 Schema 和 Prompt 版本，避免用重试掩盖根因。

### 这些演练能自动回归吗？

能。`tests/test_fault_drills.py` 用 `@pytest.mark.parametrize` 覆盖 `model_timeout/tool_exception/invalid_json` 的状态码与错误码，另有独立用例断言降级、审批阻断以及页面包含全部场景、`suggestion` 和 `traceId`。

### 页面反馈为什么重要？

故障可观测不止是后端日志。页面展示 `code`、中文说明、处理建议和 `traceId`，让使用者知道“发生了什么、能不能重试、拿什么 traceId 找后端”，把错误从“看不懂的报错”变成可操作的恢复指引。

## 复习标准

能背出五类场景的错误码与 HTTP 状态，能解释 fail-open 与 fail-closed 的分界、`retryable` 的判定，以及演练如何用参数化测试固化。回答时先说行为，再指出对应实现（`app/faults.py`、`/drills/run`、`exception_handler`）。
