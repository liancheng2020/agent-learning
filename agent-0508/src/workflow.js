import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const stepsPath = join(__dirname, "../data/workflowSteps.json");
const stepTemplates = JSON.parse(readFileSync(stepsPath, "utf8"));

export function runWorkflow(goal) {
  const plan = planSteps(goal);
  const executions = plan.map(executeStep);
  const review = reviewResult(goal, executions);
  return { goal, plan, executions, review, ok: review.passed };
}

function planSteps(goal) {
  return stepTemplates.map((step) => ({
    id: step.id,
    task: (step.taskTemplate || step.task).replace("{goal}", goal)
  }));
}

function executeStep(step) {
  return { ...step, status: "done", output: `${step.task} -> completed` };
}

function reviewResult(goal, executions) {
  const passed = executions.every((item) => item.status === "done") && executions.length >= 4;
  return {
    passed,
    findings: passed ? [] : [`${goal} 的执行步骤不完整`],
    summary: passed ? "workflow passed" : "workflow failed"
  };
}
