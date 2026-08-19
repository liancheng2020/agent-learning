import { reviewDiff } from "./review.js";
import { generatePatch } from "./patch.js";
import { searchKnowledge } from "./rag.js";

export const tools = {
  reviewDiff: { description: "Analyze a frontend git diff and return structured findings.", execute: reviewDiff },
  searchKnowledge: { description: "Retrieve review guidance relevant to a query.", execute: searchKnowledge },
  generatePatch: { description: "Generate a reviewable patch plan and unified diff.", execute: generatePatch },
};

export function listTools() { return Object.entries(tools).map(([name, tool]) => ({ name, description: tool.description })); }
