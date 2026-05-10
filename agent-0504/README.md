# Agent 0504: Structured Planner

今天的学习主题是：结构化输出与任务拆解 Agent。

这个项目实现了一个最小 Planner Agent。它不会只返回一段自然语言，而是返回一个可校验的学习计划对象，包含：

- `date`
- `theme`
- `goal`
- `schedule`
- `checklist`
- `acceptanceCriteria`
- `nextStep`

## 为什么今天学这个

昨天的 Tool Calling 解决的是“Agent 如何调用工具”。今天要解决的是“Agent 如何稳定地产出可被程序继续处理的结果”。

实际 Agent 工程里，自由文本很难继续自动化；结构化输出可以被保存、校验、测试、展示，也能作为下一个 Agent 或工具的输入。

## 今日学习计划

1. 复盘 Tool Calling 项目，观察工具结果和最终回复之间的结构差异。
2. 设计 `LearningPlan` schema。
3. 实现 `createLearningPlan`，输出稳定 JSON。
4. 实现 `validateLearningPlan`，拒绝缺字段、空字段、错误类型。
5. 跑通 demo 和 test。
6. 写下明天要做的唯一目标。

## 运行

```bash
npm run demo
```

交互生成：

```bash
npm start
```

测试：

```bash
npm test
```

## 验收标准

- `npm run demo` 能输出 `STRUCTURED_JSON_OUTPUT` 和 `MARKDOWN_VIEW`。
- `npm test` 能通过结构校验测试。
- 输出结果不是纯文本，而是能被程序消费的对象。

## 下一步

把今天生成的计划和执行过程写入 JSONL 文件，做成最小 tracing/eval 日志。
