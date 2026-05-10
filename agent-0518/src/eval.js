import { Trace } from "./trace.js";
import { runReviewAgent } from "./agent.js";
import { sampleCode, sampleDiff } from "./sampleDiff.js";

export function runEval(tracePath = "data/eval-trace.jsonl") {
  const trace = new Trace(tracePath);
  const result = runReviewAgent({ diffText: sampleDiff, code: sampleCode, trace });
  const checks = [
    ["finds error handling", result.review.findings.some((f) => f.category === "error-handling")],
    ["finds accessibility", result.review.findings.some((f) => f.category === "accessibility")],
    ["finds testing", result.review.findings.some((f) => f.category === "testing")],
    ["patch valid", result.patch.valid.ok],
    ["requires review", result.patch.plan.risk === "requires-review"]
  ];
  return { passed: checks.filter(([, ok]) => ok).length, total: checks.length, checks: checks.map(([name, ok]) => ({ name, ok })), result };
}
