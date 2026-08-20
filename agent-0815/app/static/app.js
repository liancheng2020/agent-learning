const $ = selector => document.querySelector(selector);
const diff = $("#diff");
const timeline = $("#timeline");
const sample = `diff --git a/src/LoginButton.jsx b/src/LoginButton.jsx
--- a/src/LoginButton.jsx
+++ b/src/LoginButton.jsx
@@ -1,4 +1,7 @@
+const result = await api.login();
+localStorage.setItem("token", result.token);
+return <img src="/avatar.png" />;`;
let eventCount = 0;

diff.value = sample;
$("#sample").addEventListener("click", () => { diff.value = sample; });
$("#run").addEventListener("click", run);

async function run() {
  eventCount = 0;
  timeline.innerHTML = "";
  setConnection("Streaming", true);
  $("#run").disabled = true;
  try {
    const response = await fetch("/review/stream", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ diff_text: diff.value }) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    await parseSse(response.body, handleEvent);
  } catch (error) {
    addStep("请求失败", error.message, "error");
    setConnection("Error", false);
  } finally {
    $("#run").disabled = false;
  }
}

async function parseSse(body, onEvent) {
  const reader = body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() || "";
    for (const block of blocks) {
      const type = block.match(/^event: (.+)$/m)?.[1];
      const payload = block.match(/^data: (.+)$/m)?.[1];
      if (type && payload) onEvent(type, JSON.parse(payload));
    }
  }
}

function handleEvent(type, data) {
  eventCount += 1;
  $("#step-count").textContent = `${eventCount} events`;
  if (data.traceId) $("#trace-id").textContent = data.traceId;
  if (type === "phase") addStep(data.label, data.stage, "phase");
  if (type === "tool") addStep(data.tool, data.status, data.status === "running" ? "running" : "completed");
  if (type === "error") { addStep(data.code, data.message, "error"); setConnection("Error", false); }
  if (type === "final") { renderResult(data.result); setConnection("Complete", false); }
}

function addStep(title, detail, state) {
  timeline.insertAdjacentHTML("beforeend", `<article class="step ${state}"><span class="step-icon"></span><div><strong>${escapeHtml(title)}</strong><small>${escapeHtml(detail)}</small></div></article>`);
  timeline.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function renderResult(result) {
  $("#metrics").innerHTML = [metric(result.findings.length, "Findings"), metric(result.patch_plan.risk, "Risk"), metric(result.tool_calls.length, "Tools"), metric(result.provider, "Provider")].join("");
  $("#findings").innerHTML = result.findings.length ? result.findings.map(item => `<article class="finding ${item.severity}"><div><strong>${escapeHtml(item.category)}</strong><span>${escapeHtml(item.severity)}</span></div><small>${escapeHtml(item.file)}:${item.line}</small><p>${escapeHtml(item.message)}</p><p class="suggestion">${escapeHtml(item.suggestion)}</p></article>`).join("") : '<p class="muted">未发现问题</p>';
  $("#plan").innerHTML = result.patch_plan.steps.length ? result.patch_plan.steps.map((item, index) => `<article class="plan"><span>${index + 1}</span><div><strong>${escapeHtml(item.category)}</strong><p>${escapeHtml(item.action)}</p><small>${escapeHtml(item.reason)}</small></div></article>`).join("") : '<p class="muted">无需生成修复计划</p>';
  $("#sources").innerHTML = result.sources.length ? result.sources.map(item => `<article class="source"><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.text)}</p><small>${escapeHtml(item.id)} · score ${item.score}</small></article>`).join("") : '<p class="muted">未检索到来源</p>';
}

function metric(value, label) { return `<div><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>`; }
function setConnection(label, active) { $("#connection").textContent = label; $("#dot").classList.toggle("active", active); }
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]); }

