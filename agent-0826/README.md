# Agent 0826：Docker Compose 全栈部署

第 3 周 Day 18。将前端、FastAPI、PostgreSQL/pgvector 和 Redis 拆成四个健康检查完备的 Compose 服务。

## 启动

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

```bash
docker compose down
```

连同 PostgreSQL、Redis 数据一起清理：

```bash
docker compose down -v
```

## 本地开发

不使用 Docker 时默认回退到 SQLite 向量库、SQLite 审批库和 Redis/内存缓存；原有 pytest 不依赖外部服务。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

环境变量说明见 [`.env.example`](./.env.example)，容器数据流见 [`ARCHITECTURE.md`](./ARCHITECTURE.md)。
