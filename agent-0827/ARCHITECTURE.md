# Day 19 故障演练架构

```mermaid
flowchart LR
    Browser["Browser"] --> Frontend["Nginx frontend :8080"]
    Frontend -->|/api/*| API["FastAPI :8000"]
    API --> Drills["FaultDrillService"]
    Drills --> Timeout["model_timeout"]
    Drills --> Tool["tool_exception"]
    Drills --> Empty["empty_retrieval"]
    Drills --> Json["invalid_json"]
    Drills --> Rejected["approval_rejected"]
    Timeout --> Fail["FaultDrillError"]
    Tool --> Fail
    Json --> Fail
    Fail --> Handler["exception_handler"]
    Handler --> Error["code + message + suggestion + trace_id + retryable"]
    Empty --> Degraded["DrillResult status=degraded"]
    Rejected --> Blocked["DrillResult status=blocked"]
    Rejected --> Approval["审批状态机 pending -> rejected"]
    Drills --> Trace["TraceStore drill.injected / drill.failed / drill.completed"]
    Handler --> API
    Degraded --> API
    Blocked --> API
```

## 边界

- 演练只注入**可控**故障，不触发真实外部依赖，结果确定、可重复。
- 硬失败（模型超时、工具异常、JSON 失败）走 fail-closed：抛 `FaultDrillError`，由统一 `exception_handler` 渲染，不产出任何结果。
- 可降级/阻断场景（检索为空、审批拒绝）返回 `200` + `status`，保留业务语义，不计入服务错误。
- 每个场景有固定的错误码与 HTTP 状态码，作为前后端契约被参数化测试锁定。
- 每次演练写入 Trace（`drill.injected` / `drill.failed` / `drill.completed`），并返回 `trace_id` 供排查串联。
- 页面只依赖统一错误结构展示 `code`、中文说明、处理建议和 `traceId`，不解析各接口的私有格式。
