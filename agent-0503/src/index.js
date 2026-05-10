import readline from "node:readline";
import { stdin as input, stdout as output } from "node:process";
import { listToolSchemas, runAgent } from "./agent.js";

const demoPrompts = [
  "现在几点？",
  "帮我算一下 23 * 17 + 8",
  "Agent 是什么？",
];

const testCases = [
  {
    input: "现在几点？",
    expectedTool: "getCurrentTime",
  },
  {
    input: "帮我算一下 23 * 17 + 8",
    expectedTool: "calculator",
    expectedText: "399",
  },
  {
    input: "Agent 是什么？",
    expectedTool: "searchNotes",
    expectedText: "LLM plus tools",
  },
];

async function main() {
  const mode = process.argv[2];

  if (mode === "--demo") {
    await runDemo();
    return;
  }

  if (mode === "--test") {
    await runTests();
    return;
  }

  await runCli();
}

async function runCli() {
  console.log("Tool Calling Agent Demo");
  console.log("可用工具 schema:");
  console.log(JSON.stringify(listToolSchemas(), null, 2));
  console.log("\n输入问题开始对话，输入 exit 退出。\n");

  const rl = readline.createInterface({ input, output });
  const question = (prompt) => new Promise((resolve) => {
    rl.question(prompt, resolve);
  });

  try {
    while (true) {
      const userInput = await question("> ");
      if (["exit", "quit", "q"].includes(userInput.trim().toLowerCase())) {
        break;
      }

      const result = await runAgent(userInput);
      printAgentResult(result);
    }
  } finally {
    rl.close();
  }
}

async function runDemo() {
  for (const prompt of demoPrompts) {
    console.log(`\n> ${prompt}`);
    const result = await runAgent(prompt);
    printAgentResult(result);
  }
}

async function runTests() {
  let passed = 0;

  for (const testCase of testCases) {
    const result = await runAgent(testCase.input);
    const toolName = result.toolCalls[0]?.name;
    const toolMatched = toolName === testCase.expectedTool;
    const textMatched = testCase.expectedText
      ? result.answer.includes(testCase.expectedText)
      : true;
    const ok = toolMatched && textMatched;

    if (ok) {
      passed += 1;
    }

    console.log(`${ok ? "PASS" : "FAIL"} ${testCase.input}`);
    console.log(`  expected tool: ${testCase.expectedTool}`);
    console.log(`  actual tool:   ${toolName ?? "none"}`);
    console.log(`  answer:        ${result.answer.replace(/\n/g, " ")}`);
  }

  if (passed !== testCases.length) {
    process.exitCode = 1;
  }

  console.log(`\n${passed}/${testCases.length} tests passed`);
}

function printAgentResult(result) {
  for (const toolCall of result.toolCalls) {
    console.log(`[tool call] ${toolCall.name} ${JSON.stringify(toolCall.arguments)}`);
  }

  console.log(`[answer] ${result.answer}\n`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
