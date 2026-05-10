import readline from "node:readline";
import { answerWithRag } from "./ragAgent.js";

async function main() {
  const mode = process.argv[2];
  if (mode === "--demo") return demo();
  if (mode === "--test") return test();
  return cli();
}

function demo() {
  for (const q of ["RAG 为什么需要引用来源？", "Agent memory 是什么？", "量子编译是什么？"]) {
    const result = answerWithRag(q);
    console.log(`\n> ${q}`);
    console.log(result.answer);
  }
}

function test() {
  const rag = answerWithRag("RAG cite sources");
  assert(rag.ok, "expected RAG answer");
  assert(rag.sources[0].id === "doc-rag", "expected doc-rag source");
  assert(rag.answer.includes("Sources:"), "expected citations");
  const miss = answerWithRag("quantum compiler");
  assert(!miss.ok, "expected unknown answer to refuse");
  console.log("2/2 tests passed");
}

async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  try {
    const q = await question("Question: ");
    console.log(answerWithRag(q).answer);
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
