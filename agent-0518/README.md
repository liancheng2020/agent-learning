# Frontend Review Agent Pro

一个可离线运行的前端代码审查 Agent 项目。它把规则审查、检索增强上下文、结构化 Patch、人工审批、JSONL trace、eval、成本估算与 Dashboard 组合成可演示的工作流。

## 运行

```bash
npm test
npm run demo
npm start
```

打开 <http://localhost:5118>，粘贴 Git diff 与当前组件代码后运行审查。

## 工作流

```text
diff + code
→ reviewDiff（结构化 findings）
→ searchKnowledge（本地规范检索与来源）
→ generatePatch（Patch plan + unified diff）
→ approval（高风险 patch 等待确认）
→ trace + metrics
→ dashboard
```

## 已实现能力

- 前端审查规则：异步错误处理、图片 alt、可能的 token 存储、测试缺口。
- patch 不直接写文件；高风险修复会创建与 patch 哈希绑定的审批请求。
- JSONL trace 只追加，不会因新 run 覆盖历史。
- 内置 RAG 风格的规范检索，并把来源随 run 返回。
- 可切换 `minimal`、`balanced`、`strict` 审查偏好；服务端保存当前偏好。
- Dashboard 展示输入、findings、检索来源、patch、审批状态、trace 和汇总指标。
- 无副作用的 eval 覆盖审查、检索、patch、审批与 trace。

## 安全边界

项目只生成可审查 patch，不会自动应用 patch、执行命令或访问仓库外文件。生产化时应在隔离 worktree 应用 diff，运行 lint、类型检查和测试后再进入人工审批与合并流程。
