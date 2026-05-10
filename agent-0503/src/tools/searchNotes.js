const notes = [
  {
    title: "Agent",
    content: "Agent = LLM plus tools, memory, planning, and feedback loops.",
  },
  {
    title: "Tool Calling",
    content: "Tool calling lets a model request structured actions instead of only generating text.",
  },
  {
    title: "RAG",
    content: "RAG means retrieval augmented generation: retrieve relevant context, then answer with it.",
  },
];

export const searchNotesTool = {
  name: "searchNotes",
  description: "Search local learning notes by keyword.",
  parameters: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Keyword or phrase to search in local notes.",
      },
    },
    required: ["query"],
    additionalProperties: false,
  },
  execute({ query }) {
    if (typeof query !== "string" || query.trim() === "") {
      throw new Error("query must be a non-empty string");
    }

    const normalizedQuery = query.trim().toLowerCase();
    const matches = notes.filter((note) => {
      const haystack = `${note.title} ${note.content}`.toLowerCase();
      return haystack.includes(normalizedQuery);
    });

    return {
      query,
      matches,
    };
  },
};
