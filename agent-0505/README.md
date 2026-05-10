# Agent 0505: Tracing and Eval

今天的学习主题是：Agent 可观测性与最小评估。

前两个项目分别解决：

- `agent-0503`: Agent 怎么调用工具
- `agent-0504`: Agent 怎么输出稳定结构

这个项目解决第三个工程问题：Agent 每一步做了什么，能不能被记录、回放、测试。

## 今日学习计划

1. 理解 trace 的价值：记录输入、工具选择、工具结果、最终回答、错误。
2. 实现 JSONL trace：每一行都是一个事件，方便追加写入和后续分析。
3. 实现 eval cases：用固定输入检查工具选择和回答内容。
4. 统计通过率：不要只靠肉眼看 demo。
5. 复盘失败案例：知道 Agent 为什么错，比只看成功样例更重要。

## 运行

```bash
npm run demo
```

运行 eval：

```bash
npm test
```

交互模式：

```bash
npm start
```

## 输出文件

- `data/trace.jsonl`: demo 和交互模式的 trace
- `data/eval-trace.jsonl`: eval 的 trace

## 你今天要掌握的点

Agent 工程不能只停留在“它看起来回答对了”。你需要能回答：

- 它为什么选这个工具？
- 工具参数是什么？
- 工具是否失败？
- 最终答案是否符合预期？
- 同一批用例下，改代码后通过率有没有下降？

## 验收标准

- `npm run demo` 能生成 `data/trace.jsonl`
- `npm test` 能跑完 3 条 eval case
- trace 里能看到 `run.started`、`tool.selected`、`tool.completed`、`answer.completed`、`run.completed`
- eval 报告能显示 expected tool 和 actual tool

## 明天衔接

把 trace 和 eval 结果可视化，做一个简单前端页面展示每次 Agent 运行链路。
