const notes = [
  {
    title: "Tool Calling",
    content: "Tool calling lets an Agent use external capabilities through structured arguments.",
  },
  {
    title: "Structured Output",
    content: "Structured output makes Agent responses testable, parseable, and reusable.",
  },
  {
    title: "Eval",
    content: "Eval measures whether an Agent chooses the right action and produces acceptable output.",
  },
];

export const tools = {
  calculator: {
    name: "calculator",
    execute({ expression }) {
      const normalized = String(expression).replace(/\s+/g, "");
      if (!/^[\d+\-*/%.()]+$/.test(normalized)) {
        throw new Error("unsupported math expression");
      }

      return {
        expression,
        result: Function(`"use strict"; return (${normalized});`)(),
      };
    },
  },
  searchNotes: {
    name: "searchNotes",
    execute({ query }) {
      const keyword = String(query).toLowerCase();
      const matches = notes.filter((note) => {
        return `${note.title} ${note.content}`.toLowerCase().includes(keyword);
      });

      return {
        query,
        matches,
      };
    },
  },
  createChecklist: {
    name: "createChecklist",
    execute({ topic }) {
      return {
        topic,
        items: [
          `明确 ${topic} 的输入和输出`,
          `实现 ${topic} 的最小可运行版本`,
          `为 ${topic} 添加至少 2 条 eval 用例`,
          `记录 ${topic} 的 trace 日志`,
        ],
      };
    },
  },
};
