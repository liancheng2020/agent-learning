---
id: react-error-boundaries
topic: react
title: React 错误边界与异步失败
tags: [react, error-boundary, async, fallback]
source: internal-frontend-standard
---
# React 错误边界与异步失败

页面级和独立业务区域应设置错误边界，避免单个渲染错误导致整页空白。错误边界需要可恢复的降级界面，并上报组件栈与 traceId。

错误边界不会自动捕获事件处理器或异步请求失败，这些路径仍需 `try/catch`、请求状态和用户可见的重试入口。

## 审查检查点

- 检查关键路由或复杂模块是否有错误边界。
- 检查异步调用是否处理 loading、success、error 三种状态。
- 错误提示不得只写入控制台而不给用户反馈。
