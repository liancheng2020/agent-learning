import { runAgent } from "./agent.js";
import { TraceLogger, readJsonl } from "./traceLogger.js";

export const evalCases = [
  {
    name: "math tool selection",
    input: "帮我算一下 23 * 17 + 8",
    expectedTool: "calculator",
    expectedText: "399",
  },
  {
    name: "notes search selection",
    input: "structured output 是什么？",
    expectedTool: "searchNotes",
    expectedText: "testable",
  },
  {
    name: "checklist fallback",
    input: "RAG 学习任务",
    expectedTool: "createChecklist",
    expectedText: "执行清单",
  },
];

export async function runEval({ tracePath }) {
  const trace = new TraceLogger({ filePath: tracePath });
  const results = [];

  for (const testCase of evalCases) {
    const result = await runAgent(testCase.input, { trace });
    const passed =
      result.ok &&
      result.toolCall.name === testCase.expectedTool &&
      result.answer.toLowerCase().includes(testCase.expectedText.toLowerCase());

    results.push({
      name: testCase.name,
      passed,
      expectedTool: testCase.expectedTool,
      actualTool: result.toolCall.name,
      expectedText: testCase.expectedText,
      answer: result.answer,
    });
  }

  const records = readJsonl(tracePath);
  const completedRuns = records.filter((record) => record.type === "run.completed");
  const toolSelections = records.filter((record) => record.type === "tool.selected");

  return {
    passed: results.filter((result) => result.passed).length,
    total: results.length,
    results,
    traceSummary: {
      tracePath,
      records: records.length,
      completedRuns: completedRuns.length,
      toolSelections: toolSelections.length,
    },
  };
}
