import { getTool, tools } from "./tools.js";

export async function runAgent(input, provider) {
  const toolSchemas = tools.map(({ name, description, parameters }) => ({ name, description, parameters }));
  const toolCall = await provider.selectTool(input, toolSchemas);
  const tool = getTool(toolCall.name);
  if (!tool) throw new Error(`unknown tool: ${toolCall.name}`);
  const toolResult = await tool.execute(toolCall.arguments || {});
  const answer = await provider.finalAnswer(input, toolCall, toolResult);
  return { input, toolCall, toolResult, answer };
}
