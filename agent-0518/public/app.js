const $ = (selector) => document.querySelector(selector);
const diff = $("#diff");
const code = $("#code");
const profile = $("#profile");
const status = $("#status");
let sampleInput;

$("#run").addEventListener("click", runReview);
$("#load-sample").addEventListener("click", () => {
  if (sampleInput) fillInput(sampleInput);
});

async function load() {
  try {
    const report = await request("/api/report");
    sampleInput = report.input;
    fillInput(report.input);
    render(report);
  } catch (error) { setStatus(error.message, true); }
}

async function runReview() {
  setStatus("审查中…");
  try {
    const report = await request("/api/review", {
      method: "POST",
      body: JSON.stringify({ diffText: diff.value, code: code.value, profile: profile.value }),
    });
    render(report);
    setStatus("审查完成");
  } catch (error) { setStatus(error.message, true); }
}

async function approve(actionId) {
  setStatus("正在记录审批…");
  try {
    const report = await request(`/api/approvals/${encodeURIComponent(actionId)}`, {
      method: "POST",
      body: JSON.stringify({ reviewer: "dashboard-reviewer" }),
    });
    render(report);
    setStatus("补丁已批准；本项目不会自动写入文件。");
  } catch (error) { setStatus(error.message, true); }
}

function render(data) {
  const run = data.latest;
  profile.value = run.profile;
  $("#metrics").innerHTML = [
    metric("Findings", run.review.findings.length),
    metric("Latency", `${run.metrics.latencyMs}ms`),
    metric("Estimated tokens", run.metrics.estimatedTokens),
    metric("Estimated cost", `$${run.metrics.estimatedCostUsd}`),
  ].join("");
  $("#findings").innerHTML = run.review.findings.length
    ? run.review.findings.map((finding) => `<article class="finding severity-${escapeHtml(finding.severity)}"><div class="finding-title">${escapeHtml(finding.severity)} · ${escapeHtml(finding.category)}</div><div class="muted">${escapeHtml(finding.file)}:${finding.line}</div><p>${escapeHtml(finding.message)}</p><p class="suggestion">${escapeHtml(finding.suggestion)}</p></article>`).join("")
    : empty("未发现符合当前规则的新增风险。");
  $("#plan").innerHTML = run.patch.plan.steps.length
    ? run.patch.plan.steps.map((step) => `<article class="finding"><strong>${escapeHtml(step.category)}</strong><p>${escapeHtml(step.action)}</p><p class="muted">${escapeHtml(step.reason)}</p></article>`).join("")
    : empty("没有需要生成的修复计划。");
  $("#sources").innerHTML = run.sources.length
    ? run.sources.map((source) => `<article class="source"><strong>${escapeHtml(source.title)}</strong><p>${escapeHtml(source.text)}</p><span>${escapeHtml(source.id)} · score ${source.score}</span></article>`).join("")
    : empty("未检索到匹配的本地规范。");
  $("#patch").textContent = run.patch.patch;
  $("#trace").innerHTML = data.trace.map((event) => `<article class="event"><strong>${escapeHtml(event.type)}</strong><span class="muted">${escapeHtml(new Date(event.ts).toLocaleTimeString())}</span><pre>${escapeHtml(JSON.stringify(event, null, 2))}</pre></article>`).join("");
  $("#capabilities").innerHTML = `<p><strong>Tools:</strong> ${data.capabilities.tools.map((tool) => escapeHtml(tool.name)).join(", ")}</p><p><strong>Resources:</strong> ${data.capabilities.resources.map((resource) => escapeHtml(resource.id)).join(", ")}</p><p><strong>Runs:</strong> ${data.aggregate.runs} · 成功率 ${data.aggregate.successRate} · P95 ${data.aggregate.p95LatencyMs}ms · 累计估算成本 $${data.aggregate.totalEstimatedCostUsd}</p>`;
  renderApproval(run.approval);
}

function renderApproval(approval) {
  if (!approval) { $("#approval").innerHTML = ""; return; }
  const action = approval.status === "needs_approval"
    ? `<button id="approve">批准此补丁计划</button>`
    : `<span class="approved">已由 ${escapeHtml(approval.reviewer)} 批准</span>`;
  $("#approval").innerHTML = `<div><strong>人工审批：</strong>${escapeHtml(approval.status)}<span class="muted"> action ${escapeHtml(approval.actionId)}</span></div>${action}`;
  $("#approve")?.addEventListener("click", () => approve(approval.actionId));
}

function fillInput(input) {
  if (!input) return;
  diff.value = input.diffText;
  code.value = input.code;
}
function metric(label, value) { return `<div class="metric"><strong>${escapeHtml(String(value))}</strong><span>${escapeHtml(label)}</span></div>`; }
function empty(text) { return `<p class="muted">${escapeHtml(text)}</p>`; }
function setStatus(message, isError = false) { status.textContent = message; status.className = isError ? "error-text" : ""; }
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char])); }
async function request(url, options = {}) {
  const response = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "请求失败");
  return data;
}

load();
