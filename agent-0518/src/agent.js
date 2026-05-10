import { reviewDiff } from "./review.js";
import { generatePatch } from "./patch.js";
import { summarize } from "./metrics.js";

export function runReviewAgent({ diffText, code, trace }) {
  const runId = `run_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
  const startedAt = Date.now();
  trace.event("run.started", { runId, inputBytes: diffText.length });
  const review = reviewDiff(diffText);
  trace.event("review.completed", { runId, findings: review.findings });
  const patch = generatePatch({ file: review.findings[0]?.file || "unknown", code, findings: review.findings });
  trace.event("patch.generated", { runId, plan: patch.plan, valid: patch.valid });
  const metrics = summarize({ startedAt, findings: review.findings, patch: patch.patch });
  trace.event("metrics.completed", { runId, metrics });
  trace.event("run.completed", { runId, ok: patch.valid.ok });
  return { runId, review, patch, metrics };
}
