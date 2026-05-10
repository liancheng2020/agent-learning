import readline from "node:readline";
import fs from "node:fs";
import path from "node:path";
import { answer, evaluateRetrieval, search } from "./rag.js";

async function main() {
  if (process.argv[2] === "--demo") return demo();
  if (process.argv[2] === "--test") return test();
  return cli();
}
function demo() {
  const queries = ["how does rag retrieve sources", "mcp tools resources"];
  const report = queries.map((query) => ({ query, hits: search(query), answer: answer(query) }));
  writeJson("data/rag-report.json", report);
  for (const item of report) console.log(`\n> ${item.query}\n${item.answer.answer}`);
  console.log("\nwritten: data/rag-report.json");
}
function test() {
  const report = evaluateRetrieval([{ query: "rag chunks embeds", expectedDocId: "rag" }, { query: "mcp resources tools", expectedDocId: "mcp" }]);
  assert(report.every((r) => r.hit), "expected retrieval hits");
  assert(answer("rag").sources.length > 0, "expected source");
  console.log("2/2 tests passed");
}
async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const q = (p) => new Promise((r) => rl.question(p, r));
  try { console.log(answer(await q("Question: ")).answer); } finally { rl.close(); }
}
function assert(ok, msg) { if (!ok) throw new Error(msg); }
function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
