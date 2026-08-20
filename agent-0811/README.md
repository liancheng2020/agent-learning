# Agent 0811：Provider 抽象与稳定 JSON

第 1 周 Day 3。`ModelProvider` 隔离模型厂商，默认 `MockProvider` 保证本地和 CI 稳定；`DeepSeekProvider` 调用真实 Chat Completions API。

## 运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8111
```

真实模型运行时，在终端环境中设置 `PROVIDER=deepseek` 和 `DEEPSEEK_API_KEY`。不要把密钥写进源码或提交到 Git。

## 必须掌握

- 业务层依赖 `ModelProvider`，而不是依赖某个 SDK。
- Mock 用于单测、离线演示和控制成本；真实 Provider 用于集成验证。
- JSON Mode 只约束输出格式，Pydantic 才负责字段、枚举和类型校验。
- 即使模型返回合法 JSON，也可能不符合业务 Schema，必须拒绝或重试。

