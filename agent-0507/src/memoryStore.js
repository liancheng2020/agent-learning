import fs from "node:fs";
import path from "node:path";

export class MemoryStore {
  constructor(filePath = "data/memory.json") {
    this.filePath = filePath;
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    if (!fs.existsSync(filePath)) fs.writeFileSync(filePath, JSON.stringify({ facts: [] }, null, 2));
  }

  all() {
    return JSON.parse(fs.readFileSync(this.filePath, "utf8")).facts;
  }

  remember(key, value, tags = []) {
    const data = { facts: this.all().filter((fact) => fact.key !== key) };
    data.facts.push({ key, value, tags, updatedAt: new Date().toISOString() });
    fs.writeFileSync(this.filePath, JSON.stringify(data, null, 2));
  }

  search(query) {
    const q = String(query).toLowerCase();
    return this.all().filter((fact) => {
      return `${fact.key} ${fact.value} ${fact.tags.join(" ")}`.toLowerCase().includes(q);
    });
  }
}
