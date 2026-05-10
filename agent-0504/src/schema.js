export const learningPlanSchema = {
  type: "object",
  required: ["date", "theme", "goal", "schedule", "checklist", "acceptanceCriteria", "nextStep"],
  properties: {
    date: "string",
    theme: "string",
    goal: "string",
    schedule: "array",
    checklist: "array",
    acceptanceCriteria: "array",
    nextStep: "string",
  },
};

export function validateLearningPlan(plan) {
  const errors = [];

  if (!isObject(plan)) {
    return ["plan must be an object"];
  }

  for (const field of learningPlanSchema.required) {
    if (!(field in plan)) {
      errors.push(`missing required field: ${field}`);
    }
  }

  requireString(plan, "date", errors);
  requireString(plan, "theme", errors);
  requireString(plan, "goal", errors);
  requireArray(plan, "schedule", errors);
  requireArray(plan, "checklist", errors);
  requireArray(plan, "acceptanceCriteria", errors);
  requireString(plan, "nextStep", errors);

  if (Array.isArray(plan.schedule)) {
    plan.schedule.forEach((item, index) => {
      if (!isObject(item)) {
        errors.push(`schedule[${index}] must be an object`);
        return;
      }
      requireString(item, "time", errors, `schedule[${index}]`);
      requireString(item, "task", errors, `schedule[${index}]`);
      requireString(item, "output", errors, `schedule[${index}]`);
    });
  }

  if (Array.isArray(plan.checklist)) {
    plan.checklist.forEach((item, index) => {
      if (typeof item !== "string" || item.trim() === "") {
        errors.push(`checklist[${index}] must be a non-empty string`);
      }
    });
  }

  if (Array.isArray(plan.acceptanceCriteria)) {
    plan.acceptanceCriteria.forEach((item, index) => {
      if (typeof item !== "string" || item.trim() === "") {
        errors.push(`acceptanceCriteria[${index}] must be a non-empty string`);
      }
    });
  }

  return errors;
}

function requireString(target, field, errors, prefix = "plan") {
  if (typeof target[field] !== "string" || target[field].trim() === "") {
    errors.push(`${prefix}.${field} must be a non-empty string`);
  }
}

function requireArray(target, field, errors, prefix = "plan") {
  if (!Array.isArray(target[field]) || target[field].length === 0) {
    errors.push(`${prefix}.${field} must be a non-empty array`);
  }
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
