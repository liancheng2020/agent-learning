# Agent 0518: Frontend Review Agent Pro

完整作品：前端代码审查 Agent。

能力：

- 读取 diff
- 输出结构化 review findings
- 生成 patch plan 和 unified diff
- 记录 JSONL trace
- 跑 eval 用例
- Web dashboard 展示 findings、trace、patch

运行：

```bash
npm run demo
npm test
npm start
```

打开：

```text
http://localhost:5118
```

面试讲法：

- 这是一个面向前端场景的 Agent 应用，不是普通聊天机器人。
- Review 输出是结构化 findings，可排序、可定位、可测试。
- Patch 生成不会直接改文件，而是先生成 plan 和 diff，留给人工审查。
- Trace 记录每一步，能定位失败原因。
- Eval 用例保证改代码后质量不回退。
