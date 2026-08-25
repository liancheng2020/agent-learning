---
id: react-effect-dependencies
topic: react
title: React Effect 依赖与清理
tags: [react, useEffect, dependencies, cleanup]
source: internal-frontend-standard
---
# React Effect 依赖与清理

`useEffect` 必须声明回调读取的响应式值。遗漏依赖会让闭包继续读取旧值；不稳定对象或函数依赖则可能造成重复执行。优先移动无关逻辑、使用函数式更新，确需稳定引用时再使用 `useMemo` 或 `useCallback`。

订阅、定时器和请求应提供清理逻辑。异步结果写入状态前要确认组件仍有效，或使用 `AbortController` 取消请求。

## 审查检查点

- 检查 Effect 中使用的 props、state 和函数是否完整出现在依赖数组。
- 检查事件监听、定时器、订阅和请求是否在 cleanup 中释放。
- 不允许用禁用 lint 规则掩盖依赖问题。
