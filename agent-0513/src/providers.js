export function createMockProvider() {
  return {
    async selectTool(input) {
      const math = input.match(/([0-9][0-9+\-*/%.()\s]*[+\-*/%][0-9+\-*/%.()\s]*[0-9])/);
      if (math) return { name: "calculator", arguments: { expression: math[1].trim() } };
      return { name: "getLearningPlan", arguments: { topic: input.trim() || "Agent engineering" } };
    },
    async finalAnswer(input, toolCall, toolResult) {
      if (toolCall.name === "calculator") return `${toolResult.expression} = ${toolResult.result}`;
      return `${toolResult.topic} learning plan: ${toolResult.steps.join(" -> ")}`;
    }
  };
}

export function createOpenAIProvider() {
  return {
    async selectTool(input, toolSchemas) {
      if (!process.env.OPENAI_API_KEY) return createMockProvider().selectTool(input, toolSchemas);
      throw new Error("Real OpenAI call is intentionally left as integration exercise; use official SDK or Responses API here.");
    },
    async finalAnswer(input, toolCall, toolResult) {
      if (!process.env.OPENAI_API_KEY) return createMockProvider().finalAnswer(input, toolCall, toolResult);
      throw new Error("Real final answer call is intentionally left as integration exercise.");
    }
  };
}
