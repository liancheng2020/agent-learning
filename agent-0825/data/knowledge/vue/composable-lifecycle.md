---
id: vue-composable-lifecycle
topic: vue
title: Vue Composable 生命周期清理
tags: [vue, composable, lifecycle, cleanup]
source: internal-frontend-standard
---
# Vue Composable 生命周期清理

Composable 中注册的事件、定时器、观察器和外部订阅必须跟随组件作用域释放。使用 `onUnmounted`、`onScopeDispose` 或 watch 返回的停止函数，避免页面切换后继续运行。

Composable 应返回最小公开状态，不要把内部可变对象全部暴露给调用方。异步逻辑要处理竞态和过期响应。

## 审查检查点

- 检查 `addEventListener`、`setInterval`、`watch` 是否有对应清理。
- 检查异步请求是否会被旧响应覆盖新状态。
- 检查调用方能否绕过方法直接修改内部状态。
