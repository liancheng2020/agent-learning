# Agent 0825：Redis 审查缓存

第 3 周 Day 17。项目在审批与 Trace 完整链路上，仅为“相同 Diff + 相同 Prompt 版本”的重复审查接入 Redis 缓存。

## 为什么只做缓存

重复运行 Eval、刷新页面或重试请求时，同一 Diff 会触发相同检索和审查。缓存能直接降低延迟和模型成本；当前项目没有跨实例会话需求，也没有真实公网流量，因此暂不引入 Redis Session 或限流。

## 实现

- 默认主缓存：Redis，key 为 `SHA-256(prompt_version + diff)`。
- TTL：默认 300 秒，可通过 `REVIEW_CACHE_TTL_SECONDS` 调整。
- Redis 断连：自动降级到进程内缓存，审查请求不中断。
- Trace：每次请求仍生成新的 `trace_id`，记录 cache hit、backend 和 degraded。
- 安全性：缓存内容不复用旧 `trace_id`，Prompt 升级会自动产生新 key。

## 运行

```bash
cp .env.example .env
docker compose up -d redis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8125
```

不启动 Redis 也可以运行，`GET /health` 会显示 `degraded: true`，服务使用内存缓存继续工作。

## API

- `POST /review`：结果增加 `cache_hit` 与 `trace_id`。
- `GET /traces/{trace_id}`：查看缓存、工具、token/cost 和错误事件。
- `GET /health`：查看 Redis 可用性和降级状态。
- Day 15 的审批、Patch、高风险操作接口继续保留。

面试讲解、2 分钟演示步骤和高频追问见 [`INTERVIEW.md`](./INTERVIEW.md)。

## 掌握标准

- 能解释为什么 key 必须包含 Prompt 版本。
- 能证明第二次相同审查命中缓存，但仍生成新的 Trace。
- 能解释 Redis 故障为何应该 fail-open 到内存缓存，而不是让审查服务不可用。
- 能说明当前只选缓存、不同时堆会话和限流的工程理由。
