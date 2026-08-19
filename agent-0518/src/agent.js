import { generatePatch } from "./patch.js";
import { searchKnowledge } from "./rag.js";
import { reviewDiff } from "./review.js";
import { summarizeRun } from "./metrics.js";

export function runReviewAgent({ diffText, code, trace, approvalStore, profile = "balanced" }) {
  const runId = `run_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
  const startedAt = Date.now();
  trace.event("run.started", { runId, inputBytes: diffText.length, profile });

  trace.event("tool.selected", { runId, tool: "reviewDiff" });
  const review = reviewDiff(diffText, { profile });
  trace.event("review.completed", { runId, findings: review.findings });

  const query = review.findings.map((finding) => finding.category).join(" ");
  const sources = searchKnowledge(query);
  trace.event("retrieval.completed", { runId, query, sources: sources.map(({ id, score }) => ({ id, score })) });

  trace.event("tool.selected", { runId, tool: "generatePatch" });
  const patch = generatePatch({ file: review.findings[0]?.file || "unknown", code, findings: review.findings });
  trace.event("patch.generated", { runId, plan: patch.plan, valid: patch.valid, unsupported: patch.unsupported.map((finding) => finding.id) });

  const approval = approvalStore?.request({ runId, patch: patch.patch, risk: patch.plan.risk }) ?? null;
  if (approval) trace.event("approval.requested", { runId, actionId: approval.actionId, patchHash: approval.patchHash });

  const metrics = summarizeRun({ startedAt, findings: review.findings, patch: patch.patch });
  trace.event("metrics.completed", { runId, metrics });
  const ok = patch.valid.ok;
  trace.event("run.completed", { runId, ok });
  return { runId, ok, profile, review, sources, patch, approval, metrics };
}
