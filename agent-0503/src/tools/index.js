import { calculatorTool } from "./calculator.js";
import { getCurrentTimeTool } from "./getCurrentTime.js";
import { searchNotesTool } from "./searchNotes.js";

export const tools = [calculatorTool, getCurrentTimeTool, searchNotesTool];

export const toolRegistry = new Map(tools.map((tool) => [tool.name, tool]));
