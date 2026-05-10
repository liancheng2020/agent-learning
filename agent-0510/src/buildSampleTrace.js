import fs from "node:fs";
import path from "node:path";

const tracePath = path.resolve("data/trace.jsonl");
fs.mkdirSync(path.dirname(tracePath), { recursive: true });

const runId = "run_demo_0510";
const records = [
  { ts: new Date().toISOString(), type: "run.started", runId, input: "帮我检查这个 diff" },
  { ts: new Date().toISOString(), type: "tool.selected", runId, toolCall: { name: "readDiff", arguments: { file: "demo.diff" } } },
  { ts: new Date().toISOString(), type: "tool.completed", runId, toolName: "readDiff", durationMs: 18, result: { lines: 42 } },
  { ts: new Date().toISOString(), type: "answer.completed", runId, answer: "发现 2 个风险：缺少错误处理、缺少测试。" },
  { ts: new Date().toISOString(), type: "run.completed", runId, ok: true }
];

fs.writeFileSync(tracePath, records.map((record) => JSON.stringify(record)).join("\n"));
console.log(`sample trace written: ${tracePath}`);
