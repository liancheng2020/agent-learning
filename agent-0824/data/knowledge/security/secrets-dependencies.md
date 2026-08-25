---
id: security-secrets-dependencies
topic: security
title: 前端密钥与依赖安全
tags: [security, secret, dependency, supply-chain]
source: internal-frontend-standard
---
# 前端密钥与依赖安全

打包进浏览器的变量都可被用户读取，因此前端代码不能保存服务端 API 密钥、私钥或数据库凭据。公开标识符也应限制来源、额度和权限，敏感调用通过后端代理完成。

依赖升级应审查锁文件、维护状态和安全公告。避免无必要引入大型或低维护依赖，并在 CI 中执行密钥扫描和依赖审计。

## 审查检查点

- 搜索 `sk-`、`apiKey`、`secret` 等硬编码凭据模式。
- 检查前端环境变量是否被误认为秘密。
- 新依赖需说明用途、体积、许可证和维护情况。
