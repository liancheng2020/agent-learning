import { MemoryStore } from "./memoryStore.js";

export function createMemoryAgent(store = new MemoryStore()) {
  return {
    run(input) {
      const text = input.trim();
      const remember = text.match(/记住[:：]\s*(.+?)\s*=\s*(.+)/);
      if (remember) {
        store.remember(remember[1].trim(), remember[2].trim(), ["user"]);
        return { action: "remember", answer: `已记住：${remember[1].trim()} = ${remember[2].trim()}` };
      }

      const found = store.search(text);
      if (found.length > 0) {
        return {
          action: "recall",
          answer: `我找到了相关记忆：\n${found.map((fact) => `- ${fact.key}: ${fact.value}`).join("\n")}`
        };
      }

      return { action: "answer", answer: "没有找到相关记忆。你可以用“记住: key = value”写入记忆。" };
    }
  };
}
