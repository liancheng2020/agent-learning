# Agent 0512: Patch Suggestion Agent

主题：从 review finding 生成可校验 patch。

`agent-0511` 负责发现问题；`agent-0512` 负责把问题转成修复建议和 unified diff。

## 今日学习任务

1. 读取一段有问题的组件代码。
2. 根据 finding 生成 patch plan。
3. 输出 unified diff。
4. 对 patch 做基本校验：必须包含 `---`、`+++`、`@@`、新增行。
5. 跑测试确认 patch 覆盖错误处理、alt、测试建议。

## 运行

```bash
npm run demo
npm test
npm start
```

## 面试要能讲

- 自动修复不能只输出“建议你改”，要产出可审查的 patch。
- 高风险修复应该先生成 patch plan，再等待人工确认。
- Patch Agent 必须有校验和回滚策略，不能直接无脑改文件。
