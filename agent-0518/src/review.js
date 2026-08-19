export function reviewDiff(diffText, { profile = "balanced" } = {}) {
  const lines = String(diffText).split("\n");
  const file = extractFile(lines);
  const findings = [];
  let nextLine = 1;

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const hunk = line.match(/^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
    if (hunk) { nextLine = Number(hunk[1]); continue; }
    if (line.startsWith("+++") || line.startsWith("---")) continue;
    if (line.startsWith("-")) continue;
    if (line.startsWith("+")) {
      const code = line.slice(1);
      inspectAddedLine({ code, lineNo: nextLine, lines, index, file, profile, findings });
      nextLine += 1;
      continue;
    }
    nextLine += 1;
  }

  if (findings.length > 0 && !/\.test\.|\.spec\./.test(diffText) && profile !== "minimal") {
    findings.push(make("low", "testing", file, 1, "缺少配套测试更新。", "补充成功、失败、可访问性测试。"));
  }
  return { summary: `发现 ${findings.length} 个问题`, findings };
}

function inspectAddedLine({ code, lineNo, lines, index, file, profile, findings }) {
  if (/await\s+/.test(code) && !near(lines, index, /\btry\b|\bcatch\b/)) {
    findings.push(make("high", "error-handling", file, lineNo, "Async 调用缺少错误处理。", "增加 try/catch，并提供用户可见的失败状态。"));
  }
  if (/<img\b/.test(code) && !/\balt=/.test(code)) {
    findings.push(make("medium", "accessibility", file, lineNo, "图片缺少 alt 属性。", "添加有意义的 alt；装饰图片使用 alt=\"\"。"));
  }
  if (profile !== "minimal" && /localStorage\.setItem/.test(code)) {
    findings.push(make("medium", "security", file, lineNo, "可能将 token 写入 localStorage。", "确认是否为敏感凭据；评估 httpOnly cookie 或缩短 token 生命周期。"));
  }
}

function make(severity, category, file, line, message, suggestion) {
  return { id: `${category}:${file}:${line}`, severity, category, file, line, message, suggestion };
}
function near(lines, index, pattern) { return pattern.test(lines.slice(Math.max(0, index - 4), index + 5).join("\n")); }
function extractFile(lines) {
  const plus = lines.find((line) => line.startsWith("+++ b/"));
  if (plus) return plus.replace("+++ b/", "");
  return lines.find((line) => line.startsWith("diff --git "))?.match(/\sb\/(.+)$/)?.[1] || "unknown";
}
