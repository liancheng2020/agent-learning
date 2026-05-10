import readline from "node:readline";
import fs from "node:fs";
import path from "node:path";
import { generatePatch } from "./patchAgent.js";
import { sampleCode, sampleFindings } from "./sampleCode.js";

async function main() {
  const mode = process.argv[2];
  if (mode === "--demo") return demo();
  if (mode === "--test") return test();
  return cli();
}

function demo() {
  const result = generatePatch({
    file: "src/LoginButton.jsx",
    code: sampleCode,
    findings: sampleFindings
  });
  writeJson("data/patch-report.json", result);
  writeText("data/login-button.patch", result.patch);
  console.log(JSON.stringify(result.plan, null, 2));
  console.log("\nPATCH\n");
  console.log(result.patch);
  console.log("\nwritten: data/patch-report.json, data/login-button.patch");
}

function test() {
  const result = generatePatch({ file: "src/LoginButton.jsx", code: sampleCode, findings: sampleFindings });
  assert(result.valid.ok, "expected valid patch");
  assert(result.plan.risk === "requires-review", "expected high risk review gate");
  assert(result.patch.includes("try {"), "expected try/catch patch");
  assert(result.patch.includes('alt="Login"'), "expected alt patch");
  console.log("4/4 tests passed");
}

async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  try {
    await question("Press enter to generate sample patch...");
    demo();
  } finally {
    rl.close();
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function writeText(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, data);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
