export const calculatorTool = {
  name: "calculator",
  description: "Calculate a basic arithmetic expression.",
  parameters: {
    type: "object",
    properties: {
      expression: {
        type: "string",
        description: "A math expression using numbers and +, -, *, /, %, parentheses.",
      },
    },
    required: ["expression"],
    additionalProperties: false,
  },
  execute({ expression }) {
    if (typeof expression !== "string" || expression.trim() === "") {
      throw new Error("expression must be a non-empty string");
    }

    const normalized = expression.replace(/\s+/g, "");
    if (!/^[\d+\-*/%.()]+$/.test(normalized)) {
      throw new Error("expression contains unsupported characters");
    }

    const result = Function(`"use strict"; return (${normalized});`)();
    if (typeof result !== "number" || !Number.isFinite(result)) {
      throw new Error("expression did not produce a finite number");
    }

    return {
      expression,
      result,
    };
  },
};
