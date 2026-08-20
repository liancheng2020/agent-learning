# Agent 0809：架构梳理

第 1 周 Day 1。目标不是继续堆功能，而是先读懂 `agent-0518`，明确从离线前端 Demo 升级为 Agent 服务时，各层应该负责什么。

## 今日任务

1. 阅读 `ARCHITECTURE.md` 的现状数据流和目标数据流。
2. 对照 `agent-0518/src/server.js`、`src/agent.js`、`src/tools.js`、`src/trace.js` 与 `public/app.js`。
3. 能口述一次请求如何经过 Browser、API、Agent、Tool、Trace 再返回前端。

## 掌握标准

- 能解释 API 层和 Agent 编排层为什么要分开。
- 能解释 Tool 是受约束的能力接口，不等于普通工具函数。
- 能解释 `traceId` 如何串起一次完整运行。
- 能指出 `agent-0518` 仍是规则型 Demo，不是真正的模型驱动 Agent。

