import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { Trace, readTrace } from "./trace.js";
import { runReviewAgent } from "./agent.js";
import { sampleCode, sampleDiff } from "./sampleDiff.js";

const port = Number(process.env.PORT || 5118);
const publicDir = path.resolve("public");
const tracePath = path.resolve("data/trace.jsonl");
let latest = runReviewAgent({ diffText: sampleDiff, code: sampleCode, trace: new Trace(tracePath) });

http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${port}`);
  if (url.pathname === "/api/report") return json(res, { latest, trace: readTrace(tracePath) });
  if (url.pathname === "/api/rerun") { latest = runReviewAgent({ diffText: sampleDiff, code: sampleCode, trace: new Trace(tracePath) }); return json(res, { latest, trace: readTrace(tracePath) }); }
  const file = path.join(publicDir, url.pathname === "/" ? "index.html" : url.pathname);
  if (!file.startsWith(publicDir) || !fs.existsSync(file)) { res.writeHead(404); res.end("not found"); return; }
  res.writeHead(200, { "Content-Type": type(file) });
  res.end(fs.readFileSync(file));
}).listen(port, () => console.log(`Frontend Review Agent Pro: http://localhost:${port}`));

function json(res, data) { res.writeHead(200, { "Content-Type": "application/json" }); res.end(JSON.stringify(data)); }
function type(file) { if (file.endsWith(".js")) return "application/javascript"; if (file.endsWith(".css")) return "text/css"; return "text/html"; }
