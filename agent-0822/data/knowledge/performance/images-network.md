---
id: performance-images-network
topic: performance
title: 图片与网络资源优化
tags: [performance, image, lazy, dimensions]
source: internal-frontend-standard
---
# 图片与网络资源优化

非首屏图片应使用懒加载，并提供 `width`、`height` 或稳定宽高比，避免布局偏移。根据显示尺寸提供响应式图片和现代格式，不要让缩略图下载原始大图。

首屏主图需要谨慎设置优先级，不能把所有资源都标为高优先级。接口请求应去重、取消过期请求并限制并发。

## 审查检查点

- 检查非首屏 `<img>` 是否包含 `loading="lazy"`。
- 检查图片是否有明确尺寸并匹配实际展示大小。
- 检查同一数据是否被多个组件重复请求。
