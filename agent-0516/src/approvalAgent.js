export function classify(action) {
  if (/delete|write|send|pay|deploy/i.test(action.name)) return "high";
  if (/read|list|search/i.test(action.name)) return "low";
  return "medium";
}

export function planAction(input) {
  if (/删除|delete/i.test(input)) return { name: "deleteFile", args: { path: "demo.txt" } };
  if (/写入|write/i.test(input)) return { name: "writeFile", args: { path: "demo.txt", content: "hello" } };
  return { name: "readFile", args: { path: "demo.txt" } };
}

export function runWithApproval(input, approvals = {}) {
  const action = planAction(input);
  const risk = classify(action);
  if (risk === "high" && !approvals[action.name]) {
    return { status: "needs_approval", risk, action, message: `需要人工确认才能执行 ${action.name}` };
  }
  return { status: "executed", risk, action, result: `mock executed ${action.name}` };
}
