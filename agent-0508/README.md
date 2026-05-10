# Agent 0508: Workflow Agent

主题：Planner -> Executor -> Reviewer 工作流。

你要掌握：不是所有事情都交给模型自由发挥；可控工作流通常比多 Agent 更稳定。

运行：

```bash
npm run demo
npm test
npm start
```

面试能讲：

- Planner 负责拆任务。
- Executor 负责执行确定步骤。
- Reviewer 负责检查输出是否达标。
