import readline from "node:readline";
import fs from "node:fs";
import path from "node:path";
import { estimateCost, recordRun, summarize } from "./monitor.js";

async function main() {
  if (process.argv[2] === "--demo") return demo();
  if (process.argv[2] === "--test") return test();
  return cli();
}
function demo() {
  const records = ["tool calling", "rag eval", "mcp"].map(recordRun);
  const report = { records, summary: summarize(records) };
  writeJson("data/metrics-report.json", report);
  console.log(records);
  console.log(report.summary);
  console.log("\nwritten: data/metrics-report.json");
}
function test() {
  assert(estimateCost({ inputTokens: 100, outputTokens: 100 }) > 0, "expected cost");
  assert(summarize([recordRun("a"), recordRun("b")]).runs === 2, "expected run count");
  console.log("2/2 tests passed");
}
async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const q = (p) => new Promise((r) => rl.question(p, r));
  try { console.log(recordRun(await q("> "))); } finally { rl.close(); }
}
function assert(ok, msg) { if (!ok) throw new Error(msg); }
function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
