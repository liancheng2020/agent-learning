# Tool Calling Agent Demo

一个最小可运行的 Agent 工具调用示例。它展示了完整闭环：

```text
用户输入 -> Agent 判断工具 -> 调用工具 -> 读取工具结果 -> 生成最终回答
```

## 可用工具

- `calculator`: 计算基础数学表达式
- `getCurrentTime`: 获取当前本地时间
- `searchNotes`: 搜索本地 mock 学习笔记

## 运行

```bash
npm run demo
```

交互模式：

```bash
npm start
```

测试：

```bash
npm test
```

## 验收输入

```text
现在几点？
帮我算一下 23 * 17 + 8
Agent 是什么？
```

## 后续升级方向

- 把 `src/agent.js` 里的 `planToolCall` 替换为真实 LLM tool calling。
- 把工具调用过程写入 JSONL，形成可回放日志。
- 给工具增加权限控制，例如文件读取、命令执行前需要确认。
- 增加 eval 测试集，统计工具选择准确率和最终回答质量。
