import readline from "node:readline";
import fs from "node:fs";
import path from "node:path";
import { runAgent } from "./agent.js";
import { createMockProvider, createOpenAIProvider } from "./providers.js";

const provider = process.env.OPENAI_API_KEY ? createOpenAIProvider() : createMockProvider();

async function main() {
  if (process.argv[2] === "--demo") return demo();
  if (process.argv[2] === "--test") return test();
  return cli();
}

async function demo() {
  const results = [];
  for (const input of ["帮我算 23 * 17 + 8", "RAG"]) {
    const result = await runAgent(input, provider);
    results.push(result);
    console.log(JSON.stringify(result, null, 2));
  }
  writeJson("data/tool-calling-runs.json", results);
  console.log("\nwritten: data/tool-calling-runs.json");
}

async function test() {
  const result = await runAgent("23 * 17 + 8", createMockProvider());
  assert(result.toolCall.name === "calculator", "expected calculator");
  assert(result.answer.includes("399"), "expected math answer");
  console.log("2/2 tests passed");
}

async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  try { console.log(await runAgent(await question("> "), provider)); } finally { rl.close(); }
}

function assert(ok, msg) { if (!ok) throw new Error(msg); }
function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
