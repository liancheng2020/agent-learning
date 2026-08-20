# Agent Engineering Learning Roadmap

本文档整理 `agent-0503` 到 `agent-0822` 的学习路径、项目说明、运行方式和面试讲法。

当前定位：前端开发工程师转 Agent 工程师。路线不是单纯学概念，而是用一组可运行项目逐步覆盖 Agent 应用落地能力。

## 总体进阶路线

### 第一阶段：Agent 基础闭环

目标：理解 Agent 和普通 Chatbot 的区别，完成最小可运行闭环。

- `agent-0503`: Tool Calling
- `agent-0504`: Structured Output
- `agent-0505`: Trace and Eval

掌握后应能回答：

- Agent 如何选择和调用工具？
- 工具结果如何进入最终回答？
- 为什么输出要结构化？
- 没有 trace 的 Agent 为什么难以调试？

### 第二阶段：Agent 核心能力

目标：补齐初级 Agent 工程师常见能力栈。

- `agent-0506`: RAG
- `agent-0507`: Memory
- `agent-0508`: Workflow
- `agent-0509`: MCP Style Server
- `agent-0510`: Trace Dashboard

掌握后应能回答：

- RAG 为什么会答错？
- 记忆应该如何存储、检索、更新？
- Workflow 和多 Agent 的边界是什么？
- MCP 的 tools、resources、prompts 分别解决什么问题？
- 如何把 Agent 运行链路展示给用户和开发者？

### 第三阶段：前端优势结合 Agent

目标：把前端工程经验转成可面试作品。

- `agent-0511`: Frontend Code Review Agent
- `agent-0512`: Patch Suggestion Agent

掌握后应能回答：

- 如何把代码审查结果做成结构化 findings？
- 如何从 finding 生成 patch plan？
- 为什么自动修复不能直接静默改文件？

### 第四阶段：工程化补强

目标：从教学 demo 升级到更接近真实项目。

- `agent-0513`: Real LLM Tool Calling
- `agent-0514`: Embedding RAG
- `agent-0515`: Real MCP Server Shape
- `agent-0516`: Human Approval Agent
- `agent-0517`: Cost and Latency Monitor

掌握后应能回答：

- 如何抽象 mock provider 和 real provider？
- Embedding RAG 的 chunk、embedding、topK、citation 怎么串起来？
- MCP Server 的 JSON-RPC 调用形态是什么？
- 哪些工具调用需要人工审批？
- 如何估算一次 Agent 运行的 token、成本和耗时？

### 第五阶段：完整作品

目标：形成一个能用于面试展示的端到端项目。

- `agent-0518`: Frontend Review Agent Pro

它整合了：

- diff review
- structured findings
- patch plan
- unified diff
- trace
- eval
- metrics
- web dashboard

### 第六阶段：从前端 Demo 到 Agent 服务

目标：把 `agent-0518` 升级为可测试、可观测、可接真实模型的 FastAPI Agent 服务。

- `agent-0809`: 架构与数据流梳理
- `agent-0810`: FastAPI API 与测试
- `agent-0811`: Mock / DeepSeek Provider 与稳定 JSON
- `agent-0812`: Tool Calling
- `agent-0813`: Tool 容错与 Trace
- `agent-0814`: SSE 流式前端
- `agent-0815`: Frontend Review Agent 服务化作品

### 第七阶段：RAG 与自动评测

目标：让 Review Agent 使用真实知识库，并通过数据集和指标持续验证效果。

- `agent-0816`: 前端规范知识库
- `agent-0817`: Chunk、Embedding 与 SQLite 向量检索
- `agent-0818`: 检索重排与引用
- `agent-0819`: Review Agent 自动检索知识库
- `agent-0820`: Eval Dataset
- `agent-0821`: RAG 自动评测
- `agent-0822`: Frontend Review RAG Agent 完整作品

## 统一运行方式

每个项目基本都支持：

```bash
cd ./agent-xxxx
npm run demo
npm test
npm start
```

其中：

- `npm run demo`: 运行样例
- `npm test`: 跑验收测试或 eval
- `npm start`: 交互模式或本地服务

`agent-0809` 到 `agent-0822` 使用 Python，基本运行方式为：

```bash
cd ./agent-xxxx
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

完整服务项目可使用 `uvicorn app.main:app --reload --port 端口号` 启动。

## 项目详细说明

### agent-0503: Tool Calling Agent

路径：

```text
./agent-0503
```

学习主题：Agent 工具调用。

项目目标：实现一个最小 Agent，让它根据用户输入选择工具、执行工具，并把工具结果整理成最终回答。

核心能力：

- `calculator`: 计算数学表达式
- `getCurrentTime`: 获取当前时间
- `searchNotes`: 搜索本地 mock 笔记

重点文件：

- `src/agent.js`: 工具选择、调用和回答生成
- `src/index.js`: CLI、demo、test 入口

你要理解：

- Tool schema 的作用
- 工具参数为什么需要结构化
- 工具失败为什么要被捕获
- Agent 不只是生成文本，而是能调用外部能力完成任务

面试讲法：

> 我先做了一个最小 Tool Calling Agent。它根据用户问题选择 calculator、time 或 notes 工具，执行后再生成最终回答。这个项目让我理解了 Agent 和普通 Chatbot 的关键区别：Agent 可以使用工具完成任务。

### agent-0504: Structured Planner

路径：

```text
./agent-0504
```

学习主题：结构化输出。

项目目标：让 Agent 输出可校验的学习计划对象，而不是一段自由文本。

核心能力：

- 设计 `LearningPlan` schema
- 生成 `schedule`、`checklist`、`acceptanceCriteria`
- 校验缺字段、空字段和类型错误
- 同时输出 JSON 和 Markdown 视图

重点文件：

- `src/schema.js`: schema 和校验函数
- `src/plannerAgent.js`: 计划生成和 Markdown 渲染
- `src/index.js`: demo、test、CLI 入口

你要理解：

- 稳定 JSON 不能只靠 prompt
- 输出必须能被程序继续处理
- schema 校验是 Agent 工程化的基础

面试讲法：

> 我把自然语言计划改造成结构化对象，并用 schema 做运行时校验。这样 Agent 的输出可以被保存、测试、展示，也能作为下一个工具或 Agent 的输入。

### agent-0505: Tracing and Eval

路径：

```text
./agent-0505
```

学习主题：可观测性和最小评估。

项目目标：记录 Agent 每一步执行轨迹，并用 eval case 验证工具选择和回答质量。

核心能力：

- 写入 JSONL trace
- 记录 `run.started`、`tool.selected`、`tool.completed`、`answer.completed`
- 跑固定 eval cases
- 输出通过率和 trace summary

重点文件：

- `src/traceLogger.js`: JSONL trace
- `src/evalRunner.js`: eval 用例和统计
- `src/agent.js`: Agent 执行链路

data 产物：

- `data/trace.jsonl`
- `data/eval-trace.jsonl`

你要理解：

- 没有 trace 的 Agent 难以调试
- eval 可以防止改代码后能力退化
- 评估不应只靠肉眼看 demo

面试讲法：

> 我为 Agent 加了 trace 和 eval。每次运行都会记录输入、工具选择、工具结果和最终回答。测试时会检查工具是否选对、答案是否包含预期内容。

### agent-0506: Mini RAG

路径：

```text
./agent-0506
```

学习主题：RAG 基础。

项目目标：实现一个最小检索增强问答系统。

核心能力：

- 本地文档检索
- 简单相关性排序
- 来源引用
- 无资料时拒答

重点文件：

- `src/ragAgent.js`: 检索和回答
- `src/index.js`: demo、test、CLI

data 产物：

- `data/docs.json`

你要理解：

- RAG 是先检索相关上下文，再生成回答
- 答案需要引用来源
- 没检索到资料时应该拒答，而不是编造

面试讲法：

> 这个项目实现了一个 mini RAG。它会根据 query 搜索本地资料，找到相关 sources 后再回答；如果没有来源，就明确拒答。

### agent-0507: Memory Agent

路径：

```text
./agent-0507
```

学习主题：Agent 记忆。

项目目标：实现可写入、可检索、可持久化的简单记忆系统。

核心能力：

- `remember`: 写入 key-value 记忆
- `search`: 根据 query 检索相关记忆
- JSON 文件持久化
- 区分写入和召回动作

重点文件：

- `src/memoryStore.js`: 记忆存储
- `src/memoryAgent.js`: 记忆 Agent

data 产物：

- `data/memory.json`
- `data/demo-memory.json`
- `data/test-memory.json`

你要理解：

- 记忆不是无限追加聊天记录
- 记忆需要可更新、可检索、可删除
- 只有相关记忆才应该进入上下文

面试讲法：

> 我实现了一个 key-value memory store，支持写入和检索。这个项目让我理解长期记忆应该结构化存储，而不是把所有历史对话都塞给模型。

### agent-0508: Workflow Agent

路径：

```text
./agent-0508
```

学习主题：可控工作流。

项目目标：实现 Planner -> Executor -> Reviewer 三段式工作流。

核心能力：

- Planner 拆任务
- Executor 执行每个步骤
- Reviewer 检查是否完成
- 输出完整 workflow result

重点文件：

- `src/workflow.js`: 工作流核心
- `src/index.js`: demo、test、CLI

data 产物：

- `data/workflowSteps.json`

你要理解：

- 很多任务不需要多 Agent，自定义 workflow 更稳定
- Planner、Executor、Reviewer 是常见工程模式
- 不是所有决策都应该交给模型自由发挥

面试讲法：

> 我实现了一个三段式 workflow。Planner 负责拆步骤，Executor 负责执行，Reviewer 负责验收。这个模式比完全开放式多 Agent 更可控。

### agent-0509: Mini MCP Style Server

路径：

```text
./agent-0509
```

学习主题：MCP 思维模型。

项目目标：用简化方式理解 MCP 的 tools、resources、prompts。

核心能力：

- `tools`: 执行动作
- `resources`: 暴露上下文
- `prompts`: 暴露提示模板
- 列出和调用能力

重点文件：

- `src/miniMcpServer.js`: MCP 风格能力实现
- `src/index.js`: demo、test、CLI

data 产物：

- `data/resources.json`
- `data/prompts.json`
- `data/fileListings.json`

你要理解：

- MCP 的价值是标准化 Agent 连接外部系统的方式
- tools 用于执行，resources 用于上下文，prompts 用于模板

面试讲法：

> 我做了一个 mini MCP style server，暴露 tools、resources 和 prompts。虽然不是标准 SDK，但它让我理解 MCP 的三类核心能力和调用边界。

### agent-0510: Agent Trace Dashboard

路径：

```text
./agent-0510
```

学习主题：Agent 运行链路可视化。

项目目标：把 JSONL trace 展示成前端 dashboard。

核心能力：

- Node 静态服务
- `/api/trace` 返回 trace records
- 前端展示 run、tool call、completed 数量
- 时间线展示每条事件详情

重点文件：

- `src/server.js`: 静态服务和 API
- `src/buildSampleTrace.js`: 生成样例 trace
- `public/index.html`
- `public/app.js`
- `public/style.css`

data 产物：

- `data/trace.jsonl`

你要理解：

- Agent 产品不能只有聊天框
- 调试 Agent 需要看到运行链路
- 前端能力可以转化成 Agent 工程优势

面试讲法：

> 我用前端页面把 Agent trace 可视化，展示每次运行的输入、工具选择、工具结果和完成状态。这体现了我作为前端开发者转 Agent 工程的优势。

### agent-0511: Frontend Code Review Agent

路径：

```text
./agent-0511
```

学习主题：结构化代码审查。

项目目标：输入 diff，输出可定位、可筛选、可测试的 review findings。

核心能力：

- 解析 diff 文件路径
- 检查 async 错误处理
- 检查图片 alt
- 检查 token 存储风险
- 检查测试缺口

重点文件：

- `src/reviewAgent.js`: 代码审查规则
- `src/sampleDiff.js`: 样例 diff
- `src/index.js`: demo、test、CLI

data 产物：

- `data/sample.diff`
- `data/review-report.json`

你要理解：

- Review Agent 的输出应该是结构化 findings
- finding 应包含 severity、category、file、line、message、suggestion
- 结构化结果可以进入 dashboard、eval 或 patch agent

面试讲法：

> 我做了一个前端代码审查 Agent，它能从 diff 中识别错误处理、可访问性、安全和测试问题，并输出结构化 findings。

### agent-0512: Patch Suggestion Agent

路径：

```text
./agent-0512
```

学习主题：从 finding 到 patch。

项目目标：根据 review findings 生成 patch plan 和 unified diff。

核心能力：

- 生成 patch plan
- 标记高风险修复需要 review
- 生成 unified diff
- 校验 patch 是否包含 old/new header、hunk、added lines

重点文件：

- `src/patchAgent.js`: patch plan 和 diff 生成
- `src/sampleCode.js`: 样例代码和 findings
- `src/index.js`: demo、test、CLI

data 产物：

- `data/patch-report.json`
- `data/login-button.patch`

你要理解：

- 自动修复应该先生成可审查 patch
- 高风险 patch 不应静默应用
- Patch 也需要结构化校验

面试讲法：

> 我把 review finding 转成 patch plan 和 unified diff。它不会直接改文件，而是把风险和修复步骤展示出来，等待人工审查。

### agent-0513: Real LLM Tool Calling

路径：

```text
./agent-0513
```

学习主题：真实 LLM API 接入骨架。

项目目标：把 Agent 的模型层抽象成 provider，让 mock provider 和 real provider 可以互换。

核心能力：

- `createMockProvider`
- `createOpenAIProvider`
- provider 选择工具
- tool schema 传入 provider
- 工具执行后再生成 final answer

重点文件：

- `src/providers.js`: mock provider 和 real provider 骨架
- `src/tools.js`: 工具定义
- `src/agent.js`: provider + tools 组合

data 产物：

- `data/tool-calling-runs.json`

你要理解：

- 教学项目可以用 mock provider，真实项目要接 LLM API
- provider 抽象能避免业务逻辑和模型供应商耦合
- 没有 API key 时也应该能本地跑 demo 和 test

面试讲法：

> 我把模型调用抽象成 provider。mock provider 用于本地测试，real provider 可以接真实 API。这样 Agent 核心逻辑不会被模型供应商绑定。

### agent-0514: Embedding RAG

路径：

```text
./agent-0514
```

学习主题：更接近真实 RAG 的向量检索。

项目目标：实现 chunk、embedding、cosine search、topK、citation 和 retrieval eval。

核心能力：

- 文档 chunk
- 本地 hash embedding
- cosine 相似度
- topK 检索
- sources 引用
- retrieval eval

重点文件：

- `src/rag.js`: RAG 核心流程
- `src/index.js`: demo、test、CLI

data 产物：

- `data/rag-report.json`

你要理解：

- RAG 质量主要受 chunk、embedding、retrieval、rerank 和 generation 影响
- 检索评估和回答评估要分开看
- 正确 source 是否被召回是核心指标之一

面试讲法：

> 我实现了一个本地 embedding RAG，用 hash vector 模拟 embedding，并用 cosine 做 topK 检索。它还包含 retrieval eval，用来检查正确文档是否被召回。

### agent-0515: Real MCP Server Shape

路径：

```text
./agent-0515
```

学习主题：接近 MCP 的 JSON-RPC server shape。

项目目标：用 JSON-RPC 风格组织 tools 和 resources，方便未来替换为标准 MCP SDK。

核心能力：

- `tools/list`
- `tools/call`
- `resources/list`
- `resources/read`
- JSON-RPC 成功响应
- JSON-RPC 错误响应

重点文件：

- `src/serverCore.js`: JSON-RPC handler
- `src/index.js`: demo、test、stdin CLI

data 产物：

- `data/mcp-transcript.json`

你要理解：

- MCP 本质上是 Agent 和外部系统之间的标准能力协议
- server 要明确暴露工具、资源和错误响应
- 协议层和业务工具实现应该分离

面试讲法：

> 我实现了一个 JSON-RPC 风格的 MCP server shape，包含 tools/list、tools/call、resources/list、resources/read。这让我理解了 MCP server 的接口边界。

### agent-0516: Human Approval Agent

路径：

```text
./agent-0516
```

学习主题：高风险工具调用审批。

项目目标：根据 action 风险级别决定是否需要人工确认。

核心能力：

- action planning
- risk classification
- high-risk approval gate
- approved 后执行
- low-risk 直接执行

重点文件：

- `src/approvalAgent.js`: 风险分类和审批逻辑
- `src/index.js`: demo、test、CLI

data 产物：

- `data/approval-log.json`

你要理解：

- 写文件、删除文件、发邮件、付款、部署等属于高风险工具
- Agent 不应该静默执行高风险动作
- human-in-the-loop 是安全落地的重要机制

面试讲法：

> 我实现了一个审批门禁。高风险动作比如 deleteFile 会先返回 needs_approval，只有用户确认后才会执行。

### agent-0517: Cost and Latency Monitor

路径：

```text
./agent-0517
```

学习主题：成本、耗时和运行指标。

项目目标：估算一次 Agent 运行的 tokens、cost、latency，并汇总多次运行指标。

核心能力：

- 粗略 token 估算
- input/output cost 估算
- latency 记录
- ok rate
- total cost
- average latency

重点文件：

- `src/monitor.js`: 指标计算
- `src/index.js`: demo、test、CLI

data 产物：

- `data/metrics-report.json`

你要理解：

- Agent 工程需要关注质量，也需要关注成本和延迟
- 多工具、多轮 Agent 的成本可能快速上升
- 监控指标应该成为 trace 的一部分

面试讲法：

> 我实现了一个 cost and latency monitor，用来估算每次 run 的 token、成本、耗时和成功率。这是 Agent 从 demo 到生产必须补齐的一环。

### agent-0518: Frontend Review Agent Pro

路径：

```text
./agent-0518
```

学习主题：完整 Agent 作品。

项目目标：整合前面能力，做一个端到端前端代码审查 Agent。

核心能力：

- diff review
- structured findings
- patch plan
- unified diff
- patch validation
- JSONL trace
- eval checks
- metrics summary
- web dashboard

重点文件：

- `src/agent.js`: 完整 Agent 编排
- `src/review.js`: diff review
- `src/patch.js`: patch plan 和 diff
- `src/trace.js`: trace 记录
- `src/eval.js`: eval 检查
- `src/metrics.js`: 成本和耗时估算
- `src/server.js`: dashboard 服务
- `public/index.html`
- `public/app.js`
- `public/style.css`

data 产物：

- `data/trace.jsonl`
- `data/eval-trace.jsonl`

运行：

```bash
cd ./agent-0518
npm run demo
npm test
npm start
```

本地页面：

```text
http://localhost:5118
```

你要理解：

- 一个完整 Agent 作品需要同时具备输入、推理/规则、工具/动作、输出、trace、eval、UI
- Findings 要结构化
- Patch 要可审查
- 高风险修复要人工确认
- Dashboard 能体现前端工程师的优势

面试讲法：

> 我最终把前面的能力整合成 Frontend Review Agent Pro。它能读取前端 diff，输出结构化代码审查 findings，生成 patch plan 和 unified diff，记录 trace，跑 eval，并提供 Web dashboard 展示运行链路。这是一个面向真实前端工程场景的 Agent 应用。

## agent-0809 到 agent-0822 项目一览

| 项目 | 学习重点 | 完成结果 |
| --- | --- | --- |
| `agent-0809` | 架构梳理 | 画清 Browser、API、Agent、Tool、Trace 数据流 |
| `agent-0810` | FastAPI | 实现 `/health`、`/review` 和 pytest |
| `agent-0811` | Provider 与稳定 JSON | 隔离 Mock/DeepSeek，并用 Pydantic 校验输出 |
| `agent-0812` | Tool Calling | 将审查、知识检索和修复计划注册为工具 |
| `agent-0813` | Tool 容错 | 实现校验、超时、重试、降级、错误码和 trace |
| `agent-0814` | SSE 流式输出 | 前端实时展示阶段、工具状态和最终结果 |
| `agent-0815` | 第 1 周作品 | 完成可运行、可测试、可观测的 Review Agent 服务 |
| `agent-0816` | 知识库 | 建立 React、Vue、TypeScript、性能、安全规范库 |
| `agent-0817` | RAG 索引 | 实现解析、Chunk、Metadata、Embedding 和 SQLite 检索 |
| `agent-0818` | 重排与引用 | 返回命中的规范原文和可核验来源 |
| `agent-0819` | Agent + RAG | 审查 Diff 时自动调用知识库 |
| `agent-0820` | Eval Dataset | 建立 12 条真实前端问题与期望检查点 |
| `agent-0821` | 自动评测 | 统计命中率、引用正确率、JSON、工具和延迟指标 |
| `agent-0822` | 第 2 周作品 | 整合 FastAPI、RAG、Dashboard 和 Baseline/Tuned 评测 |

推荐先运行 `agent-0815` 理解服务化 Agent，再运行 `agent-0822` 理解 RAG 与评测闭环。

## 当前能力地图

完成这些项目后，你已经覆盖初级 Agent 工程师的主要基础能力：

- Tool Calling
- Structured Output
- RAG
- Memory
- Workflow
- MCP 思维模型
- Trace
- Eval
- Human Approval
- Cost and Latency Monitor
- Agent Dashboard
- 代码审查 Agent
- Patch Suggestion Agent
- FastAPI Agent Service
- Mock / Real Provider 抽象
- Tool 容错与错误码
- SSE 流式交互
- SQLite 向量检索与重排
- Citation 自动校验
- Eval Dataset 与量化指标

还需要继续加强：

- 接入生产级 embedding 服务或 pgvector
- 使用标准 MCP SDK
- 支持真实 Git diff 和项目文件读取
- 持续扩充来自真实项目的 eval dataset
- 更严格的权限和安全模型
- 部署到可访问环境

## 已完成的两周升级

- 第 1 周 `agent-0809` 到 `agent-0815`：完成 FastAPI、Provider、Tool Calling、容错、Trace、SSE 和端到端测试。
- 第 2 周 `agent-0816` 到 `agent-0822`：完成知识库、向量检索、重排、引用、Eval Dataset 和自动评测。
- 当前主作品为 `agent-0822`，`agent-0518` 用于展示最初的规则型 Demo，`agent-0815` 用于展示服务化过程。

## 面试准备重点问题

必须能讲清楚：

1. Agent 和普通 Chatbot 的区别是什么？
2. Tool Calling 失败时怎么处理？
3. RAG 为什么会答错，怎么评估？
4. 怎么让 Agent 输出稳定 JSON？
5. 怎么知道一次 Agent 运行为什么失败？
6. MCP 的 tools、resources、prompts 分别是什么？
7. 什么时候用 Workflow，什么时候用多 Agent？
8. 高风险工具调用为什么需要人工审批？
9. Agent 项目如何做 eval？
10. 你的前端背景如何帮助你做 Agent 工程？

## 作品集推荐主线

对外展示时，不建议逐个介绍所有练习项目。更好的说法是：

```text
我先用 0503-0518 完成 Agent 基础能力拆解；
再用 0809-0821 完成服务化、RAG 和评测升级；
最后整合成 0822 Frontend Review RAG Agent。
```

重点展示：

- `agent-0822`：主作品，展示完整 RAG 与评测闭环
- `agent-0815`：展示 Agent 服务化、Tool 容错和 SSE
- `agent-0518`：展示从规则型 Demo 到工程化作品的演进起点
- `agent-0515`、`agent-0516`：补充展示 MCP 和人工审批理解

## 每天复盘模板

```md
# 日期

## 今天看的项目

## 我理解的核心概念

## 我能讲清楚的点

## 我还不理解的点

## 明天唯一目标
```

## 最终目标

当前目标不是“看完 Agent 教程”，而是能拿着 `agent-0822` 讲清楚：

- 为什么它是 Agent，不是 Chatbot
- Diff 如何触发规则和知识库工具
- 文档如何经过 Chunk、Embedding、检索和重排
- 引用如何保证来自真实规范片段
- Eval Dataset 如何量化命中率、引用和工具成功率
- FastAPI、Pydantic、Trace 和前端 Dashboard 如何形成完整产品

能独立运行、修改并讲清楚这些，你就具备投递初级或转型型 Agent 工程岗位的项目基础。
