import path from "node:path";
import { runReviewAgent } from "./agent.js";
import { ApprovalStore } from "./approvals.js";
import { runEval } from "./eval.js";
import { sampleCode, sampleDiff } from "./sampleDiff.js";
import { Trace } from "./trace.js";

async function main() {
  if (process.argv[2] === "--demo") return demo();
  if (process.argv[2] === "--test") return test();
  return demo();
}

function demo() {
  const trace = new Trace(path.resolve("data/trace.jsonl"));
  const result = runReviewAgent({ diffText: sampleDiff, code: sampleCode, trace, approvalStore: new ApprovalStore() });
  console.log(JSON.stringify({ runId: result.runId, review: result.review, sources: result.sources, patchPlan: result.patch.plan, approval: result.approval, metrics: result.metrics }, null, 2));
  console.log("\nPATCH\n");
  console.log(result.patch.patch);
}

function test() {
  const report = runEval();
  for (const check of report.checks) console.log(`${check.ok ? "PASS" : "FAIL"} ${check.name}`);
  assert(report.passed === report.total, "evaluation failed");
  console.log(`\n${report.passed}/${report.total} eval checks passed`);
}

function assert(ok, message) { if (!ok) throw new Error(message); }
main().catch((error) => { console.error(error); process.exitCode = 1; });
