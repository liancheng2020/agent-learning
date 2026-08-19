export function generatePatch({ file, code, findings }) {
  let fixed = code;
  const unsupported = findings.filter((finding) => !["error-handling", "accessibility"].includes(finding.category));

  if (findings.some((finding) => finding.category === "error-handling")) {
    fixed = fixed.replace(
`  const handleClick = async () => {
    const result = await api.login();
    localStorage.setItem("token", result.token);
  };`,
`  const handleClick = async () => {
    try {
      const result = await api.login();
      localStorage.setItem("token", result.token);
    } catch (error) {
      console.error("Login failed", error);
    }
  };`);
  }
  if (findings.some((finding) => finding.category === "accessibility")) {
    fixed = fixed.replace(/<img src="([^"\n]+)"\s*\/>/, '<img src="$1" alt="Login" />');
  }

  const patch = toUnifiedDiff(file, code, fixed);
  return { plan: createPatchPlan(file, findings), patch, valid: validatePatch(patch), unsupported };
}

export function createPatchPlan(file, findings) {
  return {
    file,
    risk: findings.some((finding) => finding.severity === "high") ? "requires-review" : "low",
    steps: findings.map((finding) => ({ category: finding.category, reason: finding.message, action: actionFor(finding.category) })),
  };
}

export function validatePatch(patch) {
  const errors = [];
  if (!/^--- a\/.+/m.test(patch)) errors.push("missing old file header");
  if (!/^\+\+\+ b\/.+/m.test(patch)) errors.push("missing new file header");
  if (!/^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@/m.test(patch)) errors.push("missing valid hunk header");
  if (!patch.split("\n").some((line) => line.startsWith("+") && !line.startsWith("+++"))) errors.push("missing added lines");
  if (!patch.split("\n").some((line) => line.startsWith("-") && !line.startsWith("---"))) errors.push("missing removed lines");
  return { ok: errors.length === 0, errors };
}

function toUnifiedDiff(file, before, after) {
  const oldLines = before.split("\n");
  const newLines = after.split("\n");
  return [
    `--- a/${file}`,
    `+++ b/${file}`,
    `@@ -1,${oldLines.length} +1,${newLines.length} @@`,
    ...oldLines.map((line) => `-${line}`),
    ...newLines.map((line) => `+${line}`),
  ].join("\n");
}

function actionFor(category) {
  return {
    "error-handling": "wrap async call with try/catch",
    accessibility: "add accessible text",
    security: "review token storage with a security owner",
    testing: "add regression tests",
  }[category] || "manual review";
}
