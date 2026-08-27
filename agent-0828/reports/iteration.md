# Day 14 评测迭代报告

## 失败样本

Baseline 未通过：react-index-key, vue-vfor-key, vue-reactive-destructure, typescript-non-null, performance-heavy-import, performance-image, security-dangerous-html, security-hardcoded-key。

## 迭代动作

- 规则：从 5 类基础规则扩充到 11 类，补齐 React key、Vue、TS 空值、代码分割和硬编码密钥。
- 检索：top-k 从 1 调整为 3，增加词法重排与 topic boost 0.2。
- 输出：每条 finding 强制绑定至少一条可核验 quote，继续由 Pydantic 校验 JSON。

## 实测结果

| 指标 | Baseline | Tuned |
| --- | ---: | ---: |
| 命中率 | 45.45% | 100.00% |
| 引用正确率 | 27.27% | 100.00% |
| JSON 合法率 | 100.00% | 100.00% |
| 工具成功率 | 100.00% | 100.00% |
| 平均延迟 | 0.194 ms | 0.527 ms |

结论只适用于当前 12 条回归集。下一步应持续加入真实误报、改写代码和跨文件上下文样本，避免只针对现有数据集调参。
