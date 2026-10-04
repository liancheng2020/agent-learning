# Agent 0826 面试材料（Day 18：Docker Compose 全栈部署）

## 30 秒介绍

> 我把上一版的单进程 Agent 拆成了 4 个健康检查完备的 Compose 服务：Nginx 托管前端并反代 `/api`、FastAPI 运行 Agent 与业务接口、PostgreSQL 16 + pgvector 同时保存审批记录和 256 维知识向量、Redis 做 TTL 缓存。`depends_on: service_healthy` 保证启动顺序，数据用命名卷持久化，全部外部配置收敛到 `.env`。为了不拖慢测试，本地 pytest 默认回退 SQLite 向量库/审批库和内存缓存，不依赖任何外部服务。14 条测试覆盖 API、缓存、Trace 和部署契约。

## 2 分钟演示

1. `cp .env.example .env`，`docker compose up --build -d`，`docker compose ps` 展示 4 个服务全部 `Up (healthy)`。
2. 打开前端 `http://127.0.0.1:8080`，提交 Diff，浏览器只请求同源 `/api/*`，由 Nginx 反代到 `api:8000`。
3. 查 `/health`，展示 `approval_store=postgres`、`vector_store=postgres`、`cache.backend=redis`，证明后端确实切到了容器化存储。
4. 相同 Diff 调两次 `/review`，展示 `cache_hit=false -> true`。
5. `docker compose down`（保留卷）再 `up -d`，说明审批记录和向量仍在。
6. `docker compose down -v` 清理数据卷。

## 关键取舍

- **为什么拆成 4 个服务**：前端、API、数据库、缓存的故障域和扩缩容节奏不同，拆开后每个组件都能独立健康检查、重启和替换，边界可写进测试。
- **为什么 PostgreSQL 同时存审批和向量**：pgvector 扩展让一套库同时承载事务性审批数据和向量检索，少一个组件就少一份一致性负担。
- **为什么用 Nginx 反代 `/api`**：前端与 API 同源，避免跨域配置并隐藏后端端口；Nginx 只做静态资源和代理，不掺业务逻辑。
- **为什么要健康检查 + `depends_on` 条件**：api 必须在 Postgres、Redis 都 healthy 之后才启动，否则会出现“启动即崩溃”的竞态。
- **为什么本地默认回退 SQLite/内存**：测试要快、要确定，不能依赖 Docker；后端由 `VECTOR_STORE_BACKEND`、`APP_DATABASE_BACKEND`、`CACHE_BACKEND` 三个环境变量切换，代码路径同构。

## 高频追问

### 四个服务分别做什么？

Nginx 提供前端静态资源和 `/api` 反向代理；FastAPI 运行 Agent、审批状态机、Trace 和结构化 API；PostgreSQL 16 + pgvector 保存审批记录和知识向量；Redis 只缓存“相同 Diff + Prompt 版本”的审查结果。

### 后端如何在 Postgres 和 SQLite 之间切换？

`app/service.py` 按 `VECTOR_STORE_BACKEND` 选择 `PostgresVectorStore` 或 `SQLiteVectorStore`；审批库按 `APP_DATABASE_BACKEND` 选择 `PostgresApprovalStore` 或 SQLite；缓存按 `CACHE_BACKEND` 选择 Redis 或内存。默认值都是本地友好的 SQLite/内存。

### 启动顺序怎么保证？

compose 里 `api.depends_on.postgres/redis` 都写成 `condition: service_healthy`，并且三个后端服务各自定义了 healthcheck；不健康就不会被判定为就绪。

### 数据会随容器删除而丢失吗？

不会。`postgres_data`、`redis_data`、`api_runtime` 三个命名卷持久化，`docker compose down` 保留数据，只有 `down -v` 才清空。

### 部署阶段踩过什么坑？

切到 Postgres 后端时 api 容器启动即崩溃，报 `'Connection' object has no attribute 'executemany'`。原因是 psycopg3 的 `Connection` 只有 `execute`，没有 `executemany`（SQLite 的 Connection 恰好有，所以本地模式一直掩盖了它）。修法是显式开 cursor：`with connection.cursor() as cursor: cursor.executemany(...)`。这类问题正说明“本地能跑”不等于“部署能跑”，多后端同构是必须的。

## 复习标准

能讲清 4 个服务的职责边界、环境变量如何驱动后端切换、启动顺序与数据持久化机制，并举出至少一个只在容器/Postgres 下才暴露的真实排障案例。每题先给结论，再落到本项目的具体文件和配置。
