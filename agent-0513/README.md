# Agent 0513: Real LLM Tool Calling

主题：真实 LLM API 接入的工具调用骨架。

默认使用本地 mock provider，保证无 API key 也能运行。设置 `OPENAI_API_KEY` 后，可切换到真实 API 请求骨架。

```bash
npm run demo
npm test
npm start
```

你要掌握：

- provider 抽象：mock 和 real API 可以互换。
- tool schema：模型知道可以调用什么工具。
- tool result：工具执行结果再交给模型综合回答。
- fallback：没有 key 或 API 失败时不影响本地学习。
