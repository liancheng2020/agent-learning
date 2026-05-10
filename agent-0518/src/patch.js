export function generatePatch({ file, code, findings }) {
  let fixed = code;
  if (findings.some((f) => f.category === "error-handling")) {
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
  if (findings.some((f) => f.category === "accessibility")) fixed = fixed.replace(`<img src="/login.svg" />`, `<img src="/login.svg" alt="Login" />`);
  const patch = [`--- a/${file}`, `+++ b/${file}`, "@@", ...code.split("\n").filter(Boolean).map((l) => `-${l}`), ...fixed.split("\n").filter(Boolean).map((l) => `+${l}`)].join("\n");
  return { plan: createPatchPlan(file, findings), patch, valid: validatePatch(patch) };
}

export function createPatchPlan(file, findings) {
  return { file, risk: findings.some((f) => f.severity === "high") ? "requires-review" : "low", steps: findings.map((f) => ({ category: f.category, reason: f.message, action: action(f.category) })) };
}

export function validatePatch(patch) {
  const errors = [];
  if (!patch.includes("--- a/")) errors.push("missing old header");
  if (!patch.includes("+++ b/")) errors.push("missing new header");
  if (!patch.includes("@@")) errors.push("missing hunk");
  if (!patch.split("\n").some((line) => line.startsWith("+") && !line.startsWith("+++"))) errors.push("missing additions");
  return { ok: errors.length === 0, errors };
}

function action(category) {
  return { "error-handling": "wrap async call with try/catch", accessibility: "add alt text", security: "review token storage", testing: "add regression tests" }[category] || "manual review";
}
