# Agent 0511: Frontend Code Review Agent

主题：结构化代码审查 Agent。

这个项目把你的前端背景转成 Agent 项目：输入一段 diff，Agent 输出结构化 review findings。

## 今日学习任务

1. 理解代码审查 Agent 的输入输出。
2. 设计 `ReviewFinding` 结构。
3. 实现规则型 diff analyzer。
4. 输出 severity、category、file、line、message、suggestion。
5. 用测试验证至少 3 类问题：错误处理、可访问性、测试缺口。

## 运行

```bash
npm run demo
npm test
npm start
```

## 面试要能讲

- 代码审查 Agent 不应该只返回一段建议，而应该返回可排序、可筛选、可定位的结构化 findings。
- 前端代码审查可以覆盖：可访问性、错误处理、性能、状态管理、测试缺口。
- 真实 LLM 版本里，规则 analyzer 可以变成工具，LLM 负责综合判断和解释。
