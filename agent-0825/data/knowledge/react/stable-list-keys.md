---
id: react-stable-list-keys
topic: react
title: React 列表使用稳定 Key
tags: [react, list, key, reconciliation]
source: internal-frontend-standard
---
# React 列表使用稳定 Key

列表项的 `key` 用于标识跨渲染周期中的同一实体。可排序、插入或删除的列表不能使用数组下标作为 key，否则组件状态可能附着到错误项目，造成输入内容错位或动画异常。

优先使用后端实体 ID。没有 ID 时，应在数据创建阶段生成稳定标识，而不是在 render 中调用随机数或时间戳。

## 审查检查点

- 搜索 `key={index}`、`key={i}` 和 render 中生成随机 key 的代码。
- 确认 key 在兄弟节点范围内唯一且不会随排序改变。
- Fragment 列表同样需要显式稳定 key。
