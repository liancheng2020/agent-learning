import { toolRegistry, tools } from "./tools/index.js";

export function listToolSchemas() {
  return tools.map(({ name, description, parameters }) => ({
    name,
    description,
    parameters,
  }));
}

export async function runAgent(userInput) {
  const messages = [
    { role: "user", content: userInput },
  ];

  const toolCall = planToolCall(userInput);
  if (!toolCall) {
    return {
      answer: "我没有找到需要调用的工具。你可以问我时间、数学计算，或者本地笔记里的 Agent/RAG/Tool Calling 内容。",
      messages,
      toolCalls: [],
    };
  }

  messages.push({
    role: "assistant",
    toolCall,
  });

  const toolResult = await executeToolCall(toolCall);
  messages.push({
    role: "tool",
    name: toolCall.name,
    content: toolResult,
  });

  const answer = synthesizeAnswer(userInput, toolCall, toolResult);
  messages.push({
    role: "assistant",
    content: answer,
  });

  return {
    answer,
    messages,
    toolCalls: [toolCall],
  };
}

function planToolCall(input) {
  const text = input.trim();

  if (/(几点|时间|现在|today|time|date)/i.test(text)) {
    return {
      id: createToolCallId(),
      name: "getCurrentTime",
      arguments: { locale: "zh-CN" },
    };
  }

  const expression = extractMathExpression(text);
  if (expression) {
    return {
      id: createToolCallId(),
      name: "calculator",
      arguments: { expression },
    };
  }

  const noteQuery = extractNoteQuery(text);
  if (noteQuery) {
    return {
      id: createToolCallId(),
      name: "searchNotes",
      arguments: { query: noteQuery },
    };
  }

  return null;
}

async function executeToolCall(toolCall) {
  const tool = toolRegistry.get(toolCall.name);
  if (!tool) {
    return {
      ok: false,
      error: `Unknown tool: ${toolCall.name}`,
    };
  }

  try {
    const data = await tool.execute(toolCall.arguments);
    return {
      ok: true,
      data,
    };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

function synthesizeAnswer(userInput, toolCall, toolResult) {
  if (!toolResult.ok) {
    return `我调用 ${toolCall.name} 时失败了：${toolResult.error}`;
  }

  if (toolCall.name === "getCurrentTime") {
    return `现在是 ${toolResult.data.localTime}，时区是 ${toolResult.data.timeZone}。`;
  }

  if (toolCall.name === "calculator") {
    return `${toolResult.data.expression} 的计算结果是 ${toolResult.data.result}。`;
  }

  if (toolCall.name === "searchNotes") {
    const { matches, query } = toolResult.data;
    if (matches.length === 0) {
      return `我在本地笔记里没有找到和「${query}」相关的内容。`;
    }

    const renderedMatches = matches
      .map((match) => `《${match.title}》：${match.content}`)
      .join("\n");
    return `我在本地笔记里找到了这些内容：\n${renderedMatches}`;
  }

  return `工具 ${toolCall.name} 已完成调用，但我还没有针对这个工具写最终回复模板。原始问题：${userInput}`;
}

function extractMathExpression(text) {
  const expressionPatterns = [
    /(?:算一下|计算|等于|calculate)\s*([0-9+\-*/%.()\s]+)/i,
    /([0-9][0-9+\-*/%.()\s]*[+\-*/%][0-9+\-*/%.()\s]*[0-9])/,
  ];

  for (const pattern of expressionPatterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return match[1].trim();
    }
  }

  return null;
}

function extractNoteQuery(text) {
  const lowerText = text.toLowerCase();
  const keywords = ["tool calling", "agent", "rag"];
  const matchedKeyword = keywords.find((keyword) => lowerText.includes(keyword));
  if (matchedKeyword) {
    return matchedKeyword;
  }

  if (/(是什么|什么意思|笔记|notes?|查一下|搜索)/i.test(text)) {
    const cleaned = text
      .replace(/是什么|什么意思|笔记|notes?|查一下|搜索|帮我|一下|？|\?/gi, "")
      .trim();

    return cleaned || null;
  }

  return null;
}

function createToolCallId() {
  return `call_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}
