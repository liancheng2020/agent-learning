# Agent 0814：SSE 流式前端

第 1 周 Day 6。FastAPI 使用 `text/event-stream` 逐步发送公开运行事件，浏览器用 `fetch + ReadableStream` 解析 SSE，因此可以通过 POST 发送较大的 diff。

## 运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8114
```

打开 `http://127.0.0.1:8114`。

## 必须掌握

- SSE 帧由 `event:`、`data:` 和空行组成。
- 原生 `EventSource` 只方便 GET；本项目用流式 `fetch` 支持 POST JSON。
- 前端需要处理粘包和半包，所以保留未完成的 `buffer`。
- 页面展示阶段和工具状态，不展示模型私有推理过程。

