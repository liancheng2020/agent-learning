import readline from "node:readline";
import { callTool, getPrompt, listCapabilities, readResource } from "./miniMcpServer.js";

async function main() {
  const mode = process.argv[2];
  if (mode === "--demo") return demo();
  if (mode === "--test") return test();
  return cli();
}

function demo() {
  console.log("capabilities", JSON.stringify(listCapabilities(), null, 2));
  console.log("resource", readResource("docs://agent"));
  console.log("prompt", getPrompt("review"));
  console.log("tool", callTool("listFiles", { path: "src" }));
}

function test() {
  const caps = listCapabilities();
  assert(caps.tools.includes("listFiles"), "expected listFiles tool");
  assert(readResource("docs://agent").text.includes("tools"), "expected agent resource");
  assert(callTool("summarize", { text: "abcdef" }).result.summary === "abcdef", "expected summarize");
  console.log("3/3 tests passed");
}

async function cli() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  try {
    const uri = await question("Resource URI: ");
    console.log(readResource(uri));
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
