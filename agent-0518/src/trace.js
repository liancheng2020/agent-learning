import fs from "node:fs";
import path from "node:path";

export class Trace {
  constructor(filePath, { reset = false } = {}) {
    this.filePath = filePath;
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    if (reset || !fs.existsSync(filePath)) fs.writeFileSync(filePath, "");
  }

  event(type, payload = {}) {
    const record = { ts: new Date().toISOString(), type, ...payload };
    fs.appendFileSync(this.filePath, `${JSON.stringify(record)}\n`);
    return record;
  }
}

export class MemoryTrace {
  constructor() { this.records = []; }
  event(type, payload = {}) {
    const record = { ts: new Date().toISOString(), type, ...payload };
    this.records.push(record);
    return record;
  }
}

export function readTrace(filePath) {
  if (!fs.existsSync(filePath)) return [];
  return fs.readFileSync(filePath, "utf8")
    .split("\n")
    .filter(Boolean)
    .flatMap((line) => {
      try { return [JSON.parse(line)]; } catch { return []; }
    });
}

export function eventsForRun(records, runId) {
  return records.filter((record) => record.runId === runId);
}
