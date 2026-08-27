# Frontend Review Agent 简历材料

## 项目名称

**Frontend Review Agent：可评测、可追踪、可部署的前端代码审查 Agent**

技术栈：`Python`、`FastAPI`、`Pydantic`、`RAG`、`pgvector`、`Redis`、`Docker Compose`、`Nginx`、`pytest`、`JavaScript`

## 通用项目描述

将前端 Diff Review Demo 演进为完整 Agent 应用，打通规则审查、知识检索与引用、稳定 JSON、人工审批、运行 Trace、Redis 缓存、故障演练和 Compose 部署。12 条前端评测 Case 上，Tuned 版本的问题命中率与引用正确率由 Baseline 的 45.45%/27.27%提升到 100%/100%；22 条自动化测试覆盖 API、审批、缓存、Trace、部署配置和五类故障。

## AI 前端开发岗位版本

- 设计并实现 Agent 审查工作台，展示 Diff、审查发现、工具次数、规范引用、错误码与 `traceId`，完成 1280px 桌面端和 390px 移动端浏览器验收。
- 将 FastAPI 结构化结果映射为可理解的页面状态，对模型超时、工具异常、检索为空、JSON 失败、审批拒绝分别提供阻断、降级和恢复建议。
- 使用 Nginx 托管静态前端并反向代理 `/api`，通过 Docker Compose 编排前端、API、PostgreSQL/pgvector 和 Redis。

## AI 应用全栈岗位版本

- 基于 FastAPI/Pydantic 建立审查、检索、评测、审批、Patch 和 Trace API，统一参数校验与稳定 JSON 返回。
- 使用 PostgreSQL/pgvector 持久化审批记录和 256 维知识向量，使用 Redis TTL 缓存重复审查；Redis 断连时降级至内存缓存，不影响核心链路。
- 实现 `pending -> approved/rejected` 人工审批状态机，高风险操作只有审批通过且未执行时才可执行，防止越权和重复副作用。
- 建立 Docker Compose 四服务部署、健康检查、持久卷和 `.env.example`，并以 pytest 覆盖关键业务边界。

## Agent 应用开发岗位版本

- 将前端规范封装为 RAG 知识库，完成文档 Chunk、Metadata、Embedding、向量检索、重排与引用，Agent 审查时自动调用 `search_knowledge`。
- 建立 12 条真实前端问题评测集，量化命中率、引用正确率、JSON 合法率、工具成功率和平均延迟，基于失败样本迭代检索参数与规则。
- 为每次运行记录模型信息、Prompt 版本、工具入参/结果、耗时、token/cost、错误栈和 `traceId`，支持按 Trace 复盘失败阶段。
- 实现五种确定性故障注入，验证超时、工具错误、空检索、非法 JSON 和审批拒绝下的失败关闭与可恢复反馈。

## STAR 面试讲法

**S（背景）**：原项目只能在前端页面展示规则结果，缺少服务边界、知识依据、评测、可观测性和高风险操作保护。

**T（任务）**：把它改造成一个面试时可运行、可解释、可验证的 Agent 应用，并覆盖常见生产故障。

**A（行动）**：先拆分 FastAPI、Agent、Tool、RAG 和 Trace；再增加 Pydantic Schema、知识检索引用和自动评测；随后补齐审批状态机、Redis 降级、PostgreSQL/pgvector、Compose 部署和五类故障演练；最后用 API 测试和真实浏览器截图验收。

**R（结果）**：形成四服务可部署项目、12 条评测集、22 条自动化测试和完整 Demo；Tuned 在当前确定性数据集上达到 100% Case 通过率、问题命中率和引用正确率。

## 30 秒自我介绍

我原来是前端工程师，长期负责中后台、H5 和小程序。最近把这类业务经验延伸到 AI 应用工程：我独立实现了一个前端代码审查 Agent，从 FastAPI、RAG、Tool Calling、结构化输出，到审批、Trace、Redis 和 Docker 部署都有完整代码和评测。我的优势不是只会调模型 API，而是能把 Agent 做成用户看得懂、出错可恢复、结果可验证的产品。

## 使用原则

- 简历只保留与目标 JD 最相关的 3-4 条，不要把三个岗位版本全部堆进去。
- 面试时明确 100% 指标来自 12 条本地确定性评测集，不把它包装成线上准确率。
- 当前模型与 Embedding 为本地确定性实现，真实 Provider、认证/RBAC、OpenTelemetry 和生产压测属于下一阶段。
