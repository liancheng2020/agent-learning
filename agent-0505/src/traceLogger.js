import fs from "node:fs";
import path from "node:path";

export class TraceLogger {
  constructor({ filePath }) {
    this.filePath = filePath;
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, "");
  }

  event(type, payload = {}) {
    const record = {
      ts: new Date().toISOString(),
      type,
      ...payload,
    };

    fs.appendFileSync(this.filePath, `${JSON.stringify(record)}\n`);
    return record;
  }
}

export function readJsonl(filePath) {
  if (!fs.existsSync(filePath)) {
    return [];
  }

  return fs
    .readFileSync(filePath, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}
