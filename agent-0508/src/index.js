import readline from "node:readline";
import { runWorkflow } from "./workflow.js";

async function main() {
  const mode = process.argv[2];
  if (mode === "--demo") return demo();
  if (mode === "--test") return test();
  return cli();
}

function demo() {
  console.log(JSON.stringify(runWorkflow("构建一个代码审查 Agent"), null, 2));
}

function test() {
  const result = runWorkflow("学习 workflow");
  assert(result.plan.length === 4, "expected 4 planned steps");
  assert(result.ok, "expected workflow review to pass");
  assert(result.executions.every((item) => item.status === "done"), "expected all steps done");
  console.log("3/3 tests passed");
}

async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  try {
    const goal = await question("Goal: ");
    console.log(JSON.stringify(runWorkflow(goal), null, 2));
  } finally {
    rl.close();
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
