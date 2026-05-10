import readline from "node:readline";
import fs from "node:fs";
import path from "node:path";
import { runWithApproval } from "./approvalAgent.js";

async function main() {
  if (process.argv[2] === "--demo") return demo();
  if (process.argv[2] === "--test") return test();
  return cli();
}
function demo() {
  const results = [
    runWithApproval("删除文件"),
    runWithApproval("删除文件", { deleteFile: true }),
    runWithApproval("读取文件")
  ];
  writeJson("data/approval-log.json", results);
  for (const result of results) console.log(result);
  console.log("\nwritten: data/approval-log.json");
}
function test() {
  assert(runWithApproval("删除文件").status === "needs_approval", "expected approval");
  assert(runWithApproval("删除文件", { deleteFile: true }).status === "executed", "expected executed");
  assert(runWithApproval("读取文件").risk === "low", "expected low risk");
  console.log("3/3 tests passed");
}
async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const q = (p) => new Promise((r) => rl.question(p, r));
  try { console.log(runWithApproval(await q("> "))); } finally { rl.close(); }
}
function assert(ok, msg) { if (!ok) throw new Error(msg); }
function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
