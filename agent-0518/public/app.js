const metrics = document.querySelector("#metrics");
const findings = document.querySelector("#findings");
const plan = document.querySelector("#plan");
const patch = document.querySelector("#patch");
const trace = document.querySelector("#trace");
document.querySelector("#rerun").addEventListener("click", () => load("/api/rerun"));

async function load(url = "/api/report") {
  const data = await fetch(url).then((res) => res.json());
  const latest = data.latest;
  metrics.innerHTML = [
    metric("Findings", latest.review.findings.length),
    metric("Latency", `${latest.metrics.latencyMs}ms`),
    metric("Tokens", latest.metrics.estimatedTokens),
    metric("Cost", `$${latest.metrics.estimatedCostUsd}`)
  ].join("");
  findings.innerHTML = latest.review.findings.map((f) => `<article class="finding"><div class="severity">${f.severity} · ${f.category}</div><div>${f.file}:${f.line}</div><p>${f.message}</p><p>${f.suggestion}</p></article>`).join("");
  plan.innerHTML = latest.patch.plan.steps.map((s) => `<article class="finding"><strong>${s.category}</strong><p>${s.action}</p><p>${s.reason}</p></article>`).join("");
  patch.textContent = latest.patch.patch;
  trace.innerHTML = data.trace.map((e) => `<article class="event"><strong>${e.type}</strong><pre>${escapeHtml(JSON.stringify(e, null, 2))}</pre></article>`).join("");
}

function metric(label, value) { return `<div class="metric"><strong>${value}</strong><span>${label}</span></div>`; }
function escapeHtml(text) { return text.replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[c])); }
load();
