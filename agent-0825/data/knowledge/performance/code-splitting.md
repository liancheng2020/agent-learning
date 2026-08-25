---
id: performance-code-splitting
topic: performance
title: 路由与重模块代码分割
tags: [performance, bundle, lazy, import]
source: internal-frontend-standard
---
# 路由与重模块代码分割

首屏不需要的路由、编辑器、图表和管理模块应使用动态 `import()` 分割，减少初始 JavaScript 下载、解析与执行成本。懒加载边界必须提供稳定 loading 和错误状态。

代码分割不是越细越好。应基于路由和明显的重依赖划分，并通过 bundle analyzer 与真实网络指标验证收益。

## 审查检查点

- 检查首屏是否同步引入大型图表、编辑器或完整工具库。
- 检查动态 import 是否有加载和失败 UI。
- 比较修改前后的首包体积，而不是只看模块数量。
