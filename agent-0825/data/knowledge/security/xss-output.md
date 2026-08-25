---
id: security-xss-output
topic: security
title: HTML 输出与 XSS 防护
tags: [security, xss, innerHTML, v-html]
source: internal-frontend-standard
---
# HTML 输出与 XSS 防护

React 的 `dangerouslySetInnerHTML`、Vue 的 `v-html` 和原生 `innerHTML` 会绕过默认文本转义。未经可信白名单清洗的用户输入、富文本或第三方内容不得进入这些接口。

需要渲染富文本时使用成熟清洗库，固定允许标签与属性，并通过 CSP 降低残余风险。不要用正则表达式自行清洗 HTML。

## 审查检查点

- 搜索所有 HTML 注入入口并追踪数据来源。
- 确认清洗发生在渲染前且配置使用允许列表。
- 增加脚本标签、事件属性和恶意 URL 测试。
