const knowledge = [
  { id: "guide:error-handling", title: "异步交互", text: "前端异步操作需要处理失败状态，并为用户提供可见反馈。" },
  { id: "guide:accessibility", title: "可访问性", text: "图片需要有意义的 alt 文本；纯装饰图片应使用空 alt。" },
  { id: "guide:security", title: "Token 存储", text: "浏览器存储敏感凭据前应评估 XSS 风险、生命周期与 httpOnly cookie 方案。" },
  { id: "guide:testing", title: "回归测试", text: "修复应覆盖成功路径、失败路径和可访问性行为。" },
];

export function searchKnowledge(query, topK = 3) {
  const terms = tokenize(query);
  return knowledge
    .map((item) => ({ ...item, score: terms.reduce((score, term) => score + (haystack(item).includes(term) ? 1 : 0), 0) }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}

export function listResources() { return knowledge.map(({ id, title }) => ({ id, title })); }
function haystack(item) { return `${item.id} ${item.title} ${item.text}`.toLowerCase(); }
function tokenize(value) { return String(value).toLowerCase().match(/[a-z0-9]+|[\u4e00-\u9fa5]+/g) || []; }
