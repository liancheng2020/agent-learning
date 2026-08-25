---
id: typescript-avoid-any
topic: typescript
title: 用 unknown 替代不受控 any
tags: [typescript, any, unknown, narrowing]
source: internal-frontend-standard
---
# 用 unknown 替代不受控 any

`any` 会关闭属性访问、参数和返回值的类型检查，并把不安全类型扩散到调用链。外部输入、JSON 和异常对象应先声明为 `unknown`，经过类型守卫或 Schema 校验后再使用。

第三方库确实缺少类型时，应把 `any` 限制在适配器边界，并立即转换成项目内的明确类型。

## 审查检查点

- 搜索显式 `any`、`as any` 和无约束泛型。
- 检查 API 响应是否在运行时验证后才进入业务层。
- 禁止用 any 只为消除编译错误。
