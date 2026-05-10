export function reviewDiff(diffText) {
  const lines = diffText.split("\n");
  const file = extractFile(lines);
  const findings = [];

  for (const [index, line] of lines.entries()) {
    if (!line.startsWith("+") || line.startsWith("+++")) continue;
    const code = line.slice(1);
    const lineNumber = index + 1;

    if (/await\s+/.test(code) && !hasNearbyTryCatch(lines, index)) {
      findings.push(finding({
        severity: "high",
        category: "error-handling",
        file,
        line: lineNumber,
        message: "新增 async 调用缺少错误处理。",
        suggestion: "为 async 调用增加 try/catch，并向用户展示失败状态。"
      }));
    }

    if (/<img\b/.test(code) && !/\balt=/.test(code)) {
      findings.push(finding({
        severity: "medium",
        category: "accessibility",
        file,
        line: lineNumber,
        message: "图片缺少 alt 属性。",
        suggestion: "为 img 添加有意义的 alt，装饰图使用 alt=\"\"。"
      }));
    }

    if (/localStorage\.setItem/.test(code)) {
      findings.push(finding({
        severity: "medium",
        category: "security",
        file,
        line: lineNumber,
        message: "敏感 token 被写入 localStorage。",
        suggestion: "评估使用 httpOnly cookie 或更严格的 token 生命周期策略。"
      }));
    }
  }

  if (findings.length > 0 && !/\.test\.|\.spec\./.test(diffText)) {
    findings.push(finding({
      severity: "low",
      category: "testing",
      file,
      line: 1,
      message: "当前 diff 没有看到配套测试更新。",
      suggestion: "补充成功、失败和可访问性相关测试。"
    }));
  }

  return {
    summary: `发现 ${findings.length} 个审查问题。`,
    findings
  };
}

function finding(input) {
  return {
    severity: input.severity,
    category: input.category,
    file: input.file,
    line: input.line,
    message: input.message,
    suggestion: input.suggestion
  };
}

function extractFile(lines) {
  const target = lines.find((line) => line.startsWith("+++ b/"));
  if (target) return target.replace("+++ b/", "");

  const gitHeader = lines.find((line) => line.startsWith("diff --git "));
  const match = gitHeader?.match(/\sb\/(.+)$/);
  return match?.[1] || "unknown";
}

function hasNearbyTryCatch(lines, index) {
  const window = lines.slice(Math.max(0, index - 4), Math.min(lines.length, index + 5)).join("\n");
  return /\btry\b|\bcatch\b/.test(window);
}
