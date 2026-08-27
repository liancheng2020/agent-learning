---
id: performance-render-profiling
topic: performance
title: 渲染性能先测量后优化
tags: [performance, render, profiler, memo]
source: internal-frontend-standard
---
# 渲染性能先测量后优化

不要无差别添加 memo。先用 React Profiler、Vue Devtools 或 Performance 面板确认提交次数、耗时组件和长任务，再针对昂贵计算、无意义子树更新或不稳定 props 优化。

虚拟列表适用于大量可视项，防抖和节流适用于高频输入；这些策略都要验证交互延迟和可访问性影响。

## 审查检查点

- 要求性能改动附带基线和优化后数据。
- 检查 memo 依赖是否正确，比较成本是否高于渲染成本。
- 检查长列表是否一次创建过多 DOM 节点。
