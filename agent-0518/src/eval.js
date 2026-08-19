import { runReviewAgent } from "./agent.js";
import { ApprovalStore } from "./approvals.js";
import { MemoryTrace } from "./trace.js";
import { sampleCode, sampleDiff } from "./sampleDiff.js";

export function runEval() {
  const trace = new MemoryTrace();
  const approvals = new ApprovalStore();
  const result = runReviewAgent({ diffText: sampleDiff, code: sampleCode, trace, approvalStore: approvals });
  let rejectedMutation = false;
  try { approvals.approve(result.approval.actionId, { patch: `${result.patch.patch}\nchanged` }); } catch { rejectedMutation = true; }
  const checks = [
    ["finds error handling", result.review.findings.some((item) => item.category === "error-handling")],
    ["finds accessibility", result.review.findings.some((item) => item.category === "accessibility")],
    ["retrieves guidance", result.sources.some((item) => item.id === "guide:accessibility")],
    ["generates a valid patch", result.patch.valid.ok],
    ["requires approval for high risk patch", result.approval?.status === "needs_approval"],
    ["binds approval to the reviewed patch", rejectedMutation],
    ["records an inspectable workflow trace", trace.records.some((item) => item.type === "retrieval.completed")],
  ];
  return { passed: checks.filter(([, ok]) => ok).length, total: checks.length, checks: checks.map(([name, ok]) => ({ name, ok })), result };
}
