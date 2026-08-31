# Agent 0810：FastAPI 服务化

第 1 周 Day 2。把规则型审查从 Node Demo 中拆出来，放进有明确请求/响应 Schema 的 FastAPI 服务。

## 运行

Windows PowerShell：

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload --port 8110
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload --port 8110
```

访问 `http://127.0.0.1:8110/docs` 调试 `/health` 和 `/review`。

## 必须掌握

- FastAPI 路由、请求体和 `response_model`。
- Pydantic 如何在业务代码执行前拒绝空 diff。
- `TestClient` 如何覆盖成功和参数错误路径。
- API 层只处理协议，规则放在 `reviewer.py`。

