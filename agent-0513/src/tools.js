export const tools = [
  {
    name: "calculator",
    description: "Calculate a safe arithmetic expression.",
    parameters: { type: "object", required: ["expression"], properties: { expression: { type: "string" } } },
    execute(args) {
      const exp = String(args.expression || "").replace(/\s+/g, "");
      if (!/^[\d+\-*/%.()]+$/.test(exp)) throw new Error("unsafe expression");
      return { expression: args.expression, result: Function(`"use strict"; return (${exp});`)() };
    }
  },
  {
    name: "getLearningPlan",
    description: "Create a short learning plan for a topic.",
    parameters: { type: "object", required: ["topic"], properties: { topic: { type: "string" } } },
    execute(args) {
      return { topic: args.topic, steps: ["read docs", "build minimal demo", "write eval", "review trace"] };
    }
  }
];

export function getTool(name) {
  return tools.find((tool) => tool.name === name);
}
