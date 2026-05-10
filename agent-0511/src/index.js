import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { reviewDiff } from "./reviewAgent.js";
import { sampleDiff } from "./sampleDiff.js";

async function main() {
  const mode = process.argv[2];
  if (mode === "--demo") return demo();
  if (mode === "--test") return test();
  return cli();
}

function demo() {
  const report = reviewDiff(sampleDiff);
  writeJson("data/review-report.json", report);
  writeText("data/sample.diff", sampleDiff);
  console.log(JSON.stringify(report, null, 2));
  console.log("\nwritten: data/review-report.json");
}

function test() {
  const report = reviewDiff(sampleDiff);
  assert(report.findings.some((item) => item.category === "error-handling"), "expected error handling finding");
  assert(report.findings.some((item) => item.category === "accessibility"), "expected accessibility finding");
  assert(report.findings.some((item) => item.category === "testing"), "expected testing finding");
  assert(report.findings.every((item) => item.file === "src/LoginButton.jsx"), "expected file path");
  console.log("4/4 tests passed");
}

async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  try {
    const path = await question("Diff file path, empty for sample: ");
    const diff = path.trim() ? fs.readFileSync(path.trim(), "utf8") : sampleDiff;
    console.log(JSON.stringify(reviewDiff(diff), null, 2));
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
