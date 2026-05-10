import path from "node:path";
import readline from "node:readline";
import { runAgent } from "./agent.js";
import { runEval } from "./evalRunner.js";
import { TraceLogger, readJsonl } from "./traceLogger.js";

const tracePath = path.resolve("data/trace.jsonl");
const evalTracePath = path.resolve("data/eval-trace.jsonl");

async function main() {
  const mode = process.argv[2];

  if (mode === "--demo") {
    await runDemo();
    return;
  }

  if (mode === "--eval") {
    await runEvalCli();
    return;
  }

  await runCli();
}

async function runDemo() {
  const trace = new TraceLogger({ filePath: tracePath });
  const inputs = [
    "帮我算一下 23 * 17 + 8",
    "structured output 是什么？",
    "Agent 工程学习任务",
  ];

  for (const input of inputs) {
    const result = await runAgent(input, { trace });
    console.log(`\n> ${input}`);
    console.log(`[tool] ${result.toolCall.name}`);
    console.log(`[answer]\n${result.answer}`);
  }

  const records = readJsonl(tracePath);
  console.log(`\ntrace written: ${tracePath}`);
  console.log(`trace records: ${records.length}`);
}

async function runEvalCli() {
  const report = await runEval({ tracePath: evalTracePath });

  for (const result of report.results) {
    console.log(`${result.passed ? "PASS" : "FAIL"} ${result.name}`);
    console.log(`  expected tool: ${result.expectedTool}`);
    console.log(`  actual tool:   ${result.actualTool}`);
    console.log(`  answer:        ${result.answer.replace(/\n/g, " ")}`);
  }

  console.log(`\n${report.passed}/${report.total} eval cases passed`);
  console.log(`trace records: ${report.traceSummary.records}`);
  console.log(`trace path: ${report.traceSummary.tracePath}`);

  if (report.passed !== report.total) {
    process.exitCode = 1;
  }
}

async function runCli() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  const question = (prompt) => new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
  const trace = new TraceLogger({ filePath: tracePath });

  try {
    while (true) {
      const input = await question("> ");
      if (["exit", "quit", "q"].includes(input.trim().toLowerCase())) {
        break;
      }

      const result = await runAgent(input, { trace });
      console.log(`[tool] ${result.toolCall.name}`);
      console.log(result.answer);
    }
  } finally {
    rl.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
