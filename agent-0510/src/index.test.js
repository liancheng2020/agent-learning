import fs from "node:fs";
import "./buildSampleTrace.js";

const trace = fs.readFileSync("data/trace.jsonl", "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line));
assert(trace.length === 5, "expected 5 trace records");
assert(trace.some((record) => record.type === "tool.selected"), "expected tool.selected");
assert(trace.some((record) => record.type === "run.completed" && record.ok), "expected completed run");
console.log("3/3 tests passed");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}
