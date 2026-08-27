---
id: typescript-discriminated-unions
topic: typescript
title: 用可辨识联合表达状态
tags: [typescript, union, state, exhaustive]
source: internal-frontend-standard
---
# 用可辨识联合表达状态

加载状态不应由多个可能冲突的布尔值表达。使用带 `status` 字段的可辨识联合，可以保证 loading、success、error 分支的数据结构互斥，并让 TypeScript 自动缩小类型。

在 `switch` 的 default 分支使用 `never` 做穷尽检查，新增状态后编译器会提示所有遗漏处理的位置。

## 审查检查点

- 检查 `isLoading`、`hasError`、`data` 是否能组合出非法状态。
- 检查联合类型是否有稳定的判别字段。
- 检查状态分支是否通过 never 穷尽。
