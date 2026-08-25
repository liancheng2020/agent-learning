# Agent 0823：人工审批状态机

第 3 周 Day 15。项目在 Frontend Review RAG Agent 上增加 Human-in-the-loop：生成 Patch、应用 Patch 或部署前，必须经过 `pending -> approved/rejected`。

## 核心流程

1. `POST /patches/requests` 创建 `pending` 审批，不生成 Patch。
2. `POST /approvals/{id}/decision` 由人工批准或拒绝，决策不可重复修改。
3. 只有 `approved` 才能调用 `POST /patches/{id}/generate`。
4. 生成接口只返回候选 unified diff，不直接改源码。
5. `apply_patch`、`deploy` 使用相同审批门禁。

审批记录持久化在 SQLite，响应会隐藏源码正文，只暴露必要摘要。

## 运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8123
```

## 掌握标准

- 能解释为什么“模型建议执行”不等于“系统允许执行”。
- 能画出 `pending -> approved/rejected` 状态转换并说明非法转换。
- 能证明 Patch 在审批前、拒绝后都不会生成。
- 能说明审批记录为什么需要持久化、操作者和原因。
