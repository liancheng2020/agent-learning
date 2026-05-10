export function createPatchPlan({ file, findings }) {
  return {
    file,
    risk: findings.some((item) => item.severity === "high") ? "requires-review" : "low",
    steps: findings.map((finding) => ({
      category: finding.category,
      action: actionFor(finding.category),
      reason: finding.message
    }))
  };
}

export function generatePatch({ file, code, findings }) {
  const plan = createPatchPlan({ file, findings });
  let fixed = code;

  if (findings.some((item) => item.category === "error-handling")) {
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
  };`
    );
  }

  if (findings.some((item) => item.category === "accessibility")) {
    fixed = fixed.replace(`<img src="/login.svg" />`, `<img src="/login.svg" alt="Login" />`);
  }

  return {
    plan,
    patch: toUnifiedDiff(file, code, fixed),
    valid: validatePatch(toUnifiedDiff(file, code, fixed))
  };
}

export function validatePatch(patch) {
  const errors = [];
  if (!patch.includes("--- a/")) errors.push("missing old file header");
  if (!patch.includes("+++ b/")) errors.push("missing new file header");
  if (!patch.includes("@@")) errors.push("missing hunk header");
  if (!patch.split("\n").some((line) => line.startsWith("+") && !line.startsWith("+++"))) {
    errors.push("missing added lines");
  }

  return {
    ok: errors.length === 0,
    errors
  };
}

function actionFor(category) {
  const actions = {
    "error-handling": "wrap async operation with try/catch",
    accessibility: "add accessible text",
    testing: "add regression tests",
    security: "avoid unsafe storage for sensitive data"
  };
  return actions[category] || "manual review";
}

function toUnifiedDiff(file, before, after) {
  return [
    `--- a/${file}`,
    `+++ b/${file}`,
    "@@",
    ...before.split("\n").filter(Boolean).map((line) => `-${line}`),
    ...after.split("\n").filter(Boolean).map((line) => `+${line}`)
  ].join("\n");
}
