export function reviewDiff(diffText) {
  const lines = diffText.split("\n");
  const file = extractFile(lines);
  const findings = [];
  lines.forEach((line, index) => {
    if (!line.startsWith("+") || line.startsWith("+++")) return;
    const code = line.slice(1);
    const lineNo = index + 1;
    if (/await\s+/.test(code) && !near(lines, index, /\btry\b|\bcatch\b/)) findings.push(make("high", "error-handling", file, lineNo, "Async 调用缺少错误处理。", "增加 try/catch 和失败状态。"));
    if (/<img\b/.test(code) && !/\balt=/.test(code)) findings.push(make("medium", "accessibility", file, lineNo, "图片缺少 alt 属性。", "添加有意义 alt 或 alt=\"\"。"));
    if (/localStorage\.setItem/.test(code)) findings.push(make("medium", "security", file, lineNo, "token 写入 localStorage。", "评估 httpOnly cookie 或缩短 token 生命周期。"));
  });
  if (findings.length && !/\.test\.|\.spec\./.test(diffText)) findings.push(make("low", "testing", file, 1, "缺少配套测试更新。", "补充成功、失败、可访问性测试。"));
  return { summary: `发现 ${findings.length} 个问题`, findings };
}

function make(severity, category, file, line, message, suggestion) { return { severity, category, file, line, message, suggestion }; }
function near(lines, index, pattern) { return pattern.test(lines.slice(Math.max(0, index - 4), index + 5).join("\n")); }
function extractFile(lines) {
  const plus = lines.find((line) => line.startsWith("+++ b/"));
  if (plus) return plus.replace("+++ b/", "");
  const header = lines.find((line) => line.startsWith("diff --git "));
  return header?.match(/\sb\/(.+)$/)?.[1] || "unknown";
}
