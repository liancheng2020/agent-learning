# Agent 0826：Docker Compose 全栈部署

第 3 周 Day 18。将前端、FastAPI、PostgreSQL/pgvector 和 Redis 拆成四个健康检查完备的 Compose 服务。

## 启动

Windows PowerShell：

```powershell
Copy-Item .env.example .env
# 修改 .env 中的 POSTGRES_PASSWORD
docker compose up --build -d
docker compose ps
```

macOS / Linux：

```bash
cp .env.example .env
# 修改 .env 中的 POSTGRES_PASSWORD
docker compose up --build -d
docker compose ps
```

访问：

- 前端：`http://127.0.0.1:8080`
- API 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

停止并保留数据：

Windows PowerShell 和 macOS / Linux 通用：

```bash
docker compose down
```

连同 PostgreSQL、Redis 数据一起清理：

Windows PowerShell 和 macOS / Linux 通用：

```bash
docker compose down -v
```

## 本地开发

不使用 Docker 时默认回退到 SQLite 向量库、SQLite 审批库和 Redis/内存缓存；原有 pytest 不依赖外部服务。

Windows PowerShell：

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m pytest
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

环境变量说明见 [`.env.example`](./.env.example)，容器数据流见 [`ARCHITECTURE.md`](./ARCHITECTURE.md)。
