import readline from "node:readline";
import { createLearningPlan, renderPlanMarkdown } from "./plannerAgent.js";
import { validateLearningPlan } from "./schema.js";

async function main() {
  const mode = process.argv[2];

  if (mode === "--demo") {
    runDemo();
    return;
  }

  if (mode === "--test") {
    runTests();
    return;
  }

  await runCli();
}

function runDemo() {
  const result = createLearningPlan();
  printResult(result);
}

function runTests() {
  const result = createLearningPlan();
  assert(result.ok, `expected generated plan to be valid: ${result.errors.join(", ")}`);

  const requiredTopLevelFields = [
    "date",
    "theme",
    "goal",
    "schedule",
    "checklist",
    "acceptanceCriteria",
    "nextStep",
  ];

  for (const field of requiredTopLevelFields) {
    assert(field in result.plan, `expected field ${field}`);
  }

  assert(result.plan.schedule.length >= 3, "expected at least 3 schedule items");
  assert(result.plan.checklist.length >= 4, "expected at least 4 checklist items");
  assert(result.plan.acceptanceCriteria.length >= 3, "expected at least 3 acceptance criteria");

  const invalidErrors = validateLearningPlan({
    date: "2026-05-05",
    theme: "",
  });
  assert(invalidErrors.length > 0, "expected invalid plan to produce validation errors");

  console.log("PASS generated plan matches schema");
  console.log("PASS invalid plan is rejected");
  console.log("\n2/2 tests passed");
}

async function runCli() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  const question = (prompt) => new Promise((resolve) => {
    rl.question(prompt, resolve);
  });

  try {
    const goal = await question("今天的学习目标是什么？");
    const hoursText = await question("今晚可用学习时间，单位小时，默认 2：");
    const availableHours = Number.parseFloat(hoursText) || 2;

    const result = createLearningPlan({
      goal: goal.trim() || undefined,
      availableHours,
    });

    printResult(result);
  } finally {
    rl.close();
  }
}

function printResult(result) {
  if (!result.ok) {
    console.error("计划结构校验失败：");
    for (const error of result.errors) {
      console.error(`- ${error}`);
    }
    process.exitCode = 1;
    return;
  }

  console.log("STRUCTURED_JSON_OUTPUT");
  console.log(JSON.stringify(result.plan, null, 2));
  console.log("\nMARKDOWN_VIEW");
  console.log(renderPlanMarkdown(result.plan));
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
