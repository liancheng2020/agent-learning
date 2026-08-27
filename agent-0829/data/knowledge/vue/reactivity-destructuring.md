---
id: vue-reactivity-destructuring
topic: vue
title: Vue 响应式对象解构
tags: [vue, reactivity, props, toRefs]
source: internal-frontend-standard
---
# Vue 响应式对象解构

直接解构 `reactive` 对象会让基本类型属性失去响应性。需要保持响应性时使用 `toRefs` 或 `toRef`；对于 props，优先直接通过 `props.name` 读取，或使用框架版本支持的响应式 props 解构。

不要把 `ref` 的 `.value` 提前取出后长期保存为普通变量。跨函数传递状态时要明确传递 ref 还是当前值。

## 审查检查点

- 搜索 `const { ... } = reactive(...)` 和对 props 的直接解构。
- 检查解构值是否需要随源状态更新。
- 检查 API 参数需要快照还是响应式引用。
