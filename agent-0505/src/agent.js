import { tools } from "./tools.js";

export async function runAgent(input, { trace }) {
  const runId = createRunId();
  trace.event("run.started", { runId, input });

  const toolCall = planToolCall(input);
  trace.event("tool.selected", { runId, toolCall });

  const startedAt = Date.now();
  try {
    const tool = tools[toolCall.name];
    const toolResult = await tool.execute(toolCall.arguments);
    trace.event("tool.completed", {
      runId,
      toolName: toolCall.name,
      durationMs: Date.now() - startedAt,
      result: toolResult,
    });

    const answer = synthesizeAnswer(toolCall, toolResult);
    trace.event("answer.completed", { runId, answer });
    trace.event("run.completed", { runId, ok: true });

    return {
      runId,
      ok: true,
      toolCall,
      toolResult,
      answer,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    trace.event("tool.failed", {
      runId,
      toolName: toolCall.name,
      durationMs: Date.now() - startedAt,
      error: message,
    });
    trace.event("run.completed", { runId, ok: false });

    return {
      runId,
      ok: false,
      toolCall,
      error: message,
      answer: `执行失败：${message}`,
    };
  }
}

function planToolCall(input) {
  const text = input.trim();
  const expression = text.match(/([0-9][0-9+\-*/%.()\s]*[+\-*/%][0-9+\-*/%.()\s]*[0-9])/);
  if (expression?.[1]) {
    return {
      name: "calculator",
      arguments: {
        expression: expression[1].trim(),
      },
    };
  }

  const lowerText = text.toLowerCase();
  for (const keyword of ["tool calling", "structured output", "eval"]) {
    if (lowerText.includes(keyword)) {
      return {
        name: "searchNotes",
        arguments: {
          query: keyword,
        },
      };
    }
  }

  return {
    name: "createChecklist",
    arguments: {
      topic: text || "Agent 学习",
    },
  };
}

function synthesizeAnswer(toolCall, toolResult) {
  if (toolCall.name === "calculator") {
    return `${toolResult.expression} = ${toolResult.result}`;
  }

  if (toolCall.name === "searchNotes") {
    if (toolResult.matches.length === 0) {
      return `没有找到和 ${toolResult.query} 相关的笔记。`;
    }

    return toolResult.matches.map((item) => `${item.title}: ${item.content}`).join("\n");
  }

  if (toolCall.name === "createChecklist") {
    return [
      `${toolResult.topic} 的执行清单：`,
      ...toolResult.items.map((item, index) => `${index + 1}. ${item}`),
    ].join("\n");
  }

  return JSON.stringify(toolResult);
}

function createRunId() {
  return `run_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}
