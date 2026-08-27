# Agent 0825 面试材料

## 30 秒介绍

> 我把一个前端 Diff Review Demo 演进成 FastAPI Agent 服务：它用 RAG 返回可核验规范引用，用 Pydantic 保证结构化输出；Patch 和部署等高风险动作必须经过 SQLite 持久化人工审批；每次运行记录模型、Prompt、工具、耗时、token/cost 和错误栈；重复 Diff 使用 Redis TTL 缓存，Redis 断连时降级到内存。23 条分层测试覆盖审批、Trace、缓存和故障场景。

## 2 分钟演示

1. 打开 `/docs`，调用 `/review`，展示 finding、citation、`trace_id` 和 `cache_hit=false`。
2. 再次提交相同 Diff，展示 `cache_hit=true`、工具状态 `cached`，并证明 `trace_id` 不同。
3. 查询 `/traces/{trace_id}`，展示 Prompt 版本、缓存事件、工具参数/结果和 token/cost。
4. 创建 Patch 请求，证明状态为 `pending` 时生成接口返回 409。
5. 审批为 `approved` 后生成 unified diff；创建 `rejected` 样本证明始终不可执行。
6. 停止 Redis 后查看 `/health`，展示 `degraded=true` 且审查仍可用。

## 关键取舍

- **为什么 SQLite 存审批**：审批必须跨请求持久化，并用条件更新保证状态转换原子性。
- **为什么不自动应用 Patch**：模型输出只是候选方案，高风险副作用必须与推理阶段隔离。
- **为什么 Trace 记录 Prompt 版本**：同一输入在 Prompt 升级后可能行为变化，需要可回溯。
- **为什么缓存 key 包含 Prompt 版本**：避免新逻辑错误复用旧审查结果。
- **为什么只用 Redis 缓存**：重复审查是当前真实问题；会话和限流没有需求，暂不堆组件。
- **为什么 Redis 断连可降级**：缓存不是正确性依赖，故障不应该阻断核心审查。

## 高频追问

### 如何避免重复执行高风险操作？

审批决策只能从 `pending` 转换一次；执行结果通过 `status='approved' AND result_json IS NULL` 条件更新，第二次执行返回 409。

### Trace 会不会泄露敏感数据？

当前工具结果只保存 citation 数量和 document id 等摘要。生产环境还应增加字段级脱敏、保留周期、访问控制和采样率。

### 当前 token/cost 准确吗？

本地规则模型的 token 是字符近似值、cost 为 0。接真实 Provider 后应优先采用响应中的 usage，并按模型版本配置价格。

### Redis 缓存会不会造成脏数据？

key 包含 Prompt 版本和完整 Diff 哈希，TTL 默认为 300 秒。规则、知识库或模型版本变化时，还应把对应版本加入 key 或主动失效。

### 还缺哪些生产能力？

- 审批身份认证、RBAC 和审计导出。
- PostgreSQL/pgvector、真实 Embedding 和真实模型 usage。
- 分布式 Trace/OpenTelemetry、指标告警和日志脱敏。
- 幂等键、任务队列和真正的 Patch sandbox。
