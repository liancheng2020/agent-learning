---
id: vue-list-keys
topic: vue
title: Vue v-for 稳定 Key
tags: [vue, v-for, key, list]
source: internal-frontend-standard
---
# Vue v-for 稳定 Key

`v-for` 渲染的有状态元素和组件应提供稳定且唯一的 `:key`。使用数组下标会在排序、过滤和插入后复用错误的 DOM 或组件实例。

key 应来自实体 ID，不应使用对象本身、随机数或每次渲染都变化的值。`v-for` 与 `v-if` 不宜放在同一元素上，应先过滤数据或使用 template 包裹。

## 审查检查点

- 检查所有 `v-for` 是否有 `:key`。
- 检查 key 是否使用 index 或不稳定表达式。
- 检查列表重排后组件本地状态是否仍对应正确实体。
