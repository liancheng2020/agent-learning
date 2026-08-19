import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { runReviewAgent } from "./agent.js";
import { ApprovalStore } from "./approvals.js";
import { PreferenceMemory } from "./memory.js";
import { aggregateRuns } from "./metrics.js";
import { listResources } from "./rag.js";
import { sampleCode, sampleDiff } from "./sampleDiff.js";
import { eventsForRun, readTrace, Trace } from "./trace.js";
import { listTools } from "./tools.js";

const port = Number(process.env.PORT || 5118);
const publicDir = path.resolve("public");
const tracePath = path.resolve("data/trace.jsonl");
const trace = new Trace(tracePath);
const approvals = new ApprovalStore();
const memory = new PreferenceMemory();
const runs = new Map();
const inputs = new Map();
let latest;
latest = createRun({ diffText: sampleDiff, code: sampleCode, profile: memory.get("reviewProfile") });

http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://localhost:${port}`);
    if (url.pathname === "/api/report" && req.method === "GET") return json(res, reportFor(url.searchParams.get("runId")));
    if (url.pathname === "/api/runs" && req.method === "GET") return json(res, { runs: [...runs.values()].map(runSummary), metrics: aggregateRuns([...runs.values()]) });
    if (url.pathname === "/api/capabilities" && req.method === "GET") return json(res, { tools: listTools(), resources: listResources(), prompts: ["frontend-review"] });
    if (url.pathname === "/api/memory" && req.method === "GET") return json(res, memory.all());
    if (url.pathname === "/api/memory" && req.method === "POST") return updateMemory(req, res);
    if (url.pathname === "/api/review" && req.method === "POST") return createReview(req, res);
    if (url.pathname.startsWith("/api/approvals/") && req.method === "POST") return approvePatch(req, res, url.pathname.split("/").at(-1));
    if (url.pathname.startsWith("/api/")) return error(res, 404, "unknown API endpoint");
    return serveStatic(url.pathname, res);
  } catch (cause) {
    return error(res, 500, cause instanceof Error ? cause.message : "unexpected server error");
  }
}).listen(port, () => console.log(`Frontend Review Agent Pro: http://localhost:${port}`));

function createRun({ diffText, code, profile }) {
  const result = runReviewAgent({ diffText, code, profile, trace, approvalStore: approvals });
  runs.set(result.runId, result);
  inputs.set(result.runId, { diffText, code });
  latest = result;
  return result;
}

async function createReview(req, res) {
  const body = await readJson(req);
  const diffText = String(body.diffText || "").trim();
  const code = String(body.code || "");
  const profile = validProfile(body.profile) ? body.profile : memory.get("reviewProfile");
  if (!diffText || !code) return error(res, 400, "diffText and code are required");
  return json(res, reportFor(createRun({ diffText, code, profile }).runId));
}

async function approvePatch(req, res, actionId) {
  const body = await readJson(req);
  const run = [...runs.values()].find((item) => item.approval?.actionId === actionId);
  if (!run) return error(res, 404, "approval request not found");
  const approval = approvals.approve(actionId, { reviewer: String(body.reviewer || "local-reviewer"), patch: run.patch.patch });
  run.approval = approval;
  trace.event("approval.completed", { runId: run.runId, actionId, reviewer: approval.reviewer });
  return json(res, reportFor(run.runId));
}

async function updateMemory(req, res) {
  const body = await readJson(req);
  if (!validProfile(body.reviewProfile)) return error(res, 400, "reviewProfile must be minimal, balanced, or strict");
  return json(res, { memory: memory.set("reviewProfile", body.reviewProfile) });
}

function reportFor(runId) {
  const run = runId ? runs.get(runId) : latest;
  if (!run) throw new Error("run not found");
  return { latest: run, input: inputs.get(run.runId), trace: eventsForRun(readTrace(tracePath), run.runId), aggregate: aggregateRuns([...runs.values()]), capabilities: { tools: listTools(), resources: listResources() } };
}

function runSummary(run) { return { runId: run.runId, ok: run.ok, profile: run.profile, findingCount: run.review.findings.length, approval: run.approval?.status || "not_required", metrics: run.metrics }; }
function validProfile(value) { return ["minimal", "balanced", "strict"].includes(value); }

async function readJson(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 500_000) throw new Error("request body is too large");
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}"); } catch { throw new Error("request body must be JSON"); }
}

function serveStatic(urlPath, res) {
  const relativePath = urlPath === "/" ? "index.html" : urlPath.replace(/^\/+/, "");
  const file = path.resolve(publicDir, relativePath);
  if (!file.startsWith(`${publicDir}${path.sep}`) || !fs.existsSync(file) || !fs.statSync(file).isFile()) return error(res, 404, "not found");
  res.writeHead(200, { "Content-Type": contentType(file) });
  res.end(fs.readFileSync(file));
}

function json(res, data) { res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" }); res.end(JSON.stringify(data)); }
function error(res, status, message) { res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" }); res.end(JSON.stringify({ error: message })); }
function contentType(file) { if (file.endsWith(".js")) return "application/javascript"; if (file.endsWith(".css")) return "text/css"; return "text/html; charset=utf-8"; }
