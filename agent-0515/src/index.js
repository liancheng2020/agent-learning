import readline from "node:readline";
import fs from "node:fs";
import path from "node:path";
import { handleRpc } from "./serverCore.js";

async function main() {
  if (process.argv[2] === "--demo") return demo();
  if (process.argv[2] === "--test") return test();
  return cli();
}
function demo() {
  const requests = [{ id: 1, method: "tools/list" }, { id: 2, method: "tools/call", params: { name: "getPackageInfo" } }, { id: 3, method: "resources/list" }];
  const transcript = requests.map((request) => ({ request, response: handleRpc(request) }));
  writeJson("data/mcp-transcript.json", transcript);
  for (const item of transcript) console.log(JSON.stringify(item.response, null, 2));
  console.log("\nwritten: data/mcp-transcript.json");
}
function test() {
  assert(handleRpc({ id: 1, method: "tools/list" }).result.length > 0, "tools list");
  assert(handleRpc({ id: 2, method: "tools/call", params: { name: "echo", arguments: { a: 1 } } }).result.a === 1, "tool call");
  assert(handleRpc({ id: 3, method: "bad" }).error, "error response");
  console.log("3/3 tests passed");
}
async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  rl.on("line", (line) => console.log(JSON.stringify(handleRpc(JSON.parse(line)))));
}
function assert(ok, msg) { if (!ok) throw new Error(msg); }
function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
