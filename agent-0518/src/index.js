import path from "node:path";
import { Trace } from "./trace.js";
import { runReviewAgent } from "./agent.js";
import { runEval } from "./eval.js";
import { sampleCode, sampleDiff } from "./sampleDiff.js";

async function main() {
  if (process.argv[2] === "--demo") return demo();
  if (process.argv[2] === "--test") return test();
  return demo();
}

function demo() {
  const trace = new Trace(path.resolve("data/trace.jsonl"));
  const result = runReviewAgent({ diffText: sampleDiff, code: sampleCode, trace });
  console.log(JSON.stringify({ review: result.review, patchPlan: result.patch.plan, metrics: result.metrics }, null, 2));
  console.log("\nPATCH\n");
  console.log(result.patch.patch);
}

function test() {
  const report = runEval(path.resolve("data/eval-trace.jsonl"));
  for (const check of report.checks) console.log(`${check.ok ? "PASS" : "FAIL"} ${check.name}`);
  console.log(`\n${report.passed}/${report.total} eval checks passed`);
  if (report.passed !== report.total) process.exitCode = 1;
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
