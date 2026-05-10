# Agent 0515: Real MCP Server Shape

主题：用 JSON-RPC 风格实现一个接近 MCP 的 server shape。

不依赖 MCP SDK，但接口按 `tools/list`、`tools/call`、`resources/list`、`resources/read` 组织，方便以后替换成标准 SDK。

```bash
npm run demo
npm test
npm start
```
