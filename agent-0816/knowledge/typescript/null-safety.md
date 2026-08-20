---
id: typescript-null-safety
topic: typescript
title: TypeScript 空值安全
tags: [typescript, null, optional, strict]
source: internal-frontend-standard
---
# TypeScript 空值安全

项目应开启 `strictNullChecks`，并在数据边界显式处理 `null` 与 `undefined`。非空断言 `!` 只消除编译器提示，不会提供运行时保证，容易把数据缺失变成线上异常。

优先使用提前返回、可选链、默认值或类型守卫。只有在生命周期和 DOM 约束能严格证明非空时才使用非空断言，并留下可验证条件。

## 审查检查点

- 搜索 `value!`、`document.querySelector(...)!` 等非空断言。
- 检查 API 可选字段是否有缺失路径测试。
- 检查默认值是否掩盖真正的数据错误。
