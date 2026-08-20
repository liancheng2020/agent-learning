const diff = document.querySelector("#diff");
const timeline = document.querySelector("#timeline");
const connection = document.querySelector("#connection");
const sample = `diff --git a/src/Login.jsx b/src/Login.jsx
--- a/src/Login.jsx
+++ b/src/Login.jsx
@@ -1,2 +1,4 @@
+const result = await api.login();
+return <img src="/avatar.png" />;`;

document.querySelector("#sample").addEventListener("click", () => { diff.value = sample; });
document.querySelector("#run").addEventListener("click", run);
diff.value = sample;

async function run() {
  timeline.innerHTML = "";
  connection.textContent = "Streaming";
  const response = await fetch("/review/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ diff_text: diff.value }),
  });
  if (!response.ok) { connection.textContent = "Error"; return; }
  await parseSse(response.body, handleEvent);
  connection.textContent = "Complete";
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
      const data = block.match(/^data: (.+)$/m)?.[1];
      if (type && data) onEvent(type, JSON.parse(data));
    }
  }
}

function handleEvent(type, data) {
  if (type === "phase") addStep(data.label, data.stage, "phase");
  if (type === "tool") addStep(data.tool, data.status, "tool");
  if (type === "final") renderResult(data.result);
}

function addStep(title, status, kind) {
  timeline.insertAdjacentHTML("beforeend", `<article class="step ${kind}"><span></span><div><strong>${escapeHtml(title)}</strong><small>${escapeHtml(status)}</small></div></article>`);
}

function renderResult(result) {
  document.querySelector("#findings").innerHTML = result.findings.length
    ? result.findings.map(item => `<article class="finding ${item.severity}"><strong>${escapeHtml(item.category)}</strong><span>${escapeHtml(item.file)}:${item.line}</span><p>${escapeHtml(item.message)}</p><small>${escapeHtml(item.suggestion)}</small></article>`).join("")
    : '<p class="muted">未发现问题</p>';
  document.querySelector("#plan").innerHTML = `<p><strong>风险：</strong>${escapeHtml(result.patch_plan.risk)}</p>${result.patch_plan.steps.map(item => `<article class="plan"><strong>${escapeHtml(item.category)}</strong><p>${escapeHtml(item.action)}</p></article>`).join("")}<code>${escapeHtml(result.trace_id)}</code>`;
}

function escapeHtml(value) { return String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]); }

