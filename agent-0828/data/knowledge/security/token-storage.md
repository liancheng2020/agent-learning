---
id: security-token-storage
topic: security
title: 浏览器凭据存储
tags: [security, token, localStorage, cookie]
source: internal-frontend-standard
---
# 浏览器凭据存储

长期访问令牌不应直接写入 `localStorage`，因为任意成功执行的 XSS 都能读取它。Web 应用优先评估 `HttpOnly`、`Secure`、合适 `SameSite` 的 Cookie，并配合 CSRF 防护。

确需浏览器存储时，应缩短令牌寿命、限制权限、实现轮换和撤销，并在威胁模型中记录选择原因。

## 审查检查点

- 搜索 `localStorage.setItem` 是否存入 token、session 或用户敏感数据。
- 检查 Cookie 属性和 CSRF 策略是否配套。
- 日志、URL 和错误信息不得泄漏令牌。
