# Agent 0827：Agent 故障演练

第 3 周 Day 19。在完整部署基线上加入可重复故障注入、统一错误结构、traceId 和页面恢复建议。

## 五类演练

| 场景 | 错误码 | 行为 |
| --- | --- | --- |
| 模型超时 | `MODEL_TIMEOUT` | 返回 504，不展示不完整结果，提示重试或缩小 Diff |
| 工具异常 | `TOOL_EXECUTION_FAILED` | 返回 502，停止无依据推断，提示检查工具 trace |
| 检索为空 | `KNOWLEDGE_NOT_FOUND` | 降级成功，不伪造引用，提示调整查询或知识库 |
| JSON 失败 | `MODEL_JSON_INVALID` | 返回 502，拒绝不符合 Schema 的模型结果 |
| 审批拒绝 | `APPROVAL_REJECTED` | 阻断高风险操作，保留最终审批状态 |

每次演练都会写入 trace，页面展示 `code`、中文说明、处理建议和 `traceId`。

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

环境变量说明见 [`.env.example`](./.env.example)，容器数据流见 [`ARCHITECTURE.md`](./ARCHITECTURE.md)。故障演练入口为 `POST /drills/run`。
