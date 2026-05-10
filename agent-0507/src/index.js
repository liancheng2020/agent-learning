import readline from "node:readline";
import { createMemoryAgent } from "./memoryAgent.js";
import { MemoryStore } from "./memoryStore.js";

async function main() {
  const mode = process.argv[2];
  if (mode === "--demo") return demo();
  if (mode === "--test") return test();
  return cli();
}

function demo() {
  const agent = createMemoryAgent(new MemoryStore("data/demo-memory.json"));
  for (const input of ["记住: 学习偏好 = 项目制学习", "学习偏好 是什么？"]) {
    const result = agent.run(input);
    console.log(`\n> ${input}\n[${result.action}] ${result.answer}`);
  }
}

function test() {
  const agent = createMemoryAgent(new MemoryStore("data/test-memory.json"));
  const write = agent.run("记住: role = frontend developer");
  const read = agent.run("role");
  assert(write.action === "remember", "expected remember action");
  assert(read.answer.includes("frontend developer"), "expected recalled memory");
  console.log("2/2 tests passed");
}

async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  const agent = createMemoryAgent();
  try {
    while (true) {
      const input = await question("> ");
      if (["q", "quit", "exit"].includes(input.trim())) break;
      console.log(agent.run(input).answer);
    }
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
