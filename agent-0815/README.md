# Agent 0815：Frontend Review Agent 完整作品

第 1 周 Day 7。这个项目把 `agent-0518` 的规则型前端 Demo 升级为可测试、可观测、可替换模型 Provider、支持 Tool Calling 和 SSE 的 FastAPI Agent 服务。

## 快速开始

Windows PowerShell：

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload --port 8115
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload --port 8115
```

打开：

- Dashboard：`http://127.0.0.1:8115`
- OpenAPI：`http://127.0.0.1:8115/docs`
- 健康检查：`http://127.0.0.1:8115/health`

默认使用 Mock Provider，不需要密钥且不会产生调用费用。

## 接入 DeepSeek

服务已经按照 DeepSeek 的 OpenAI 兼容 Chat Completions、JSON Output 和 Tool Calls 接口接入。把环境变量设置在本机，不要写进源码：

Windows PowerShell：

```powershell
$env:PROVIDER = 'deepseek'
$env:DEEPSEEK_API_KEY = '你的新密钥'
$env:DEEPSEEK_MODEL = 'deepseek-chat'
python -m uvicorn app.main:app --reload --port 8115
```

macOS / Linux：

```bash
export PROVIDER=deepseek
export DEEPSEEK_API_KEY="你的新密钥"
export DEEPSEEK_MODEL=deepseek-chat
python -m uvicorn app.main:app --reload --port 8115
```

你之前发在聊天中的密钥应当轮换后再使用。

## 已实现能力

- Mock / DeepSeek Provider 抽象。
- `read_diff`、`search_knowledge`、`generate_patch_plan` Tool Calling。
- Pydantic 稳定 JSON 合约。
- Tool 参数校验、超时、重试、降级和稳定错误码。
- JSONL Trace 与 `traceId` 查询。
- 普通 `/review` 与流式 `/review/stream`。
- SSE Dashboard 展示公开阶段、工具状态和最终结果。
- 5 条端到端测试和两分钟演示/录屏脚本。

## 你要达到的掌握标准

1. 能画出 Browser、API、Agent、Provider、Tool、Trace 的数据流。
2. 能解释为什么 Mock Provider 是可靠测试的一部分。
3. 能自己新增一个 Pydantic Tool，并注册到 ToolExecutor。
4. 能解释 Tool Calling 失败后何时重试、何时降级、何时直接失败。
5. 能从一个 `traceId` 定位 Provider 或 Tool 的失败阶段。
6. 能在不看源码的情况下完成两分钟项目演示。

## 官方参考

- [DeepSeek Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion)
- [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode)
- [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls)
