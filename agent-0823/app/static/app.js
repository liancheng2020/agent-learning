const $ = (selector) => document.querySelector(selector);
const sample = `+++ b/src/Profile.tsx
@@ -1 +1,5 @@
+const payload: any = response;
+localStorage.setItem("accessToken", payload.token);
+return <section dangerouslySetInnerHTML={{ __html: payload.bio }} />;
`;

$("#diff").value = sample;
$("#sample").addEventListener("click", () => { $("#diff").value = sample; });
$("#review").addEventListener("click", review);
$("#evaluate").addEventListener("click", evaluate);

async function review() {
  toggle("#review", true, "审查中...");
  try {
    const response = await fetch("/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ diff_text: $("#diff").value })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    render(await response.json());
  } catch (error) {
    $("#findings").innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  } finally {
    toggle("#review", false, "运行审查");
  }
}

async function evaluate() {
  toggle("#evaluate", true, "评测中...");
  try {
    const response = await fetch("/eval", { method: "POST" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    $("#metrics").textContent = [
      `Baseline hit: ${percent(data.baseline.hit_rate)}`,
      `Tuned hit:    ${percent(data.tuned.hit_rate)}`,
      `Citation:     ${percent(data.tuned.citation_accuracy)}`,
      `JSON valid:   ${percent(data.tuned.json_valid_rate)}`,
      `Tool success: ${percent(data.tuned.tool_success_rate)}`
    ].join("\n");
  } catch (error) {
    $("#metrics").textContent = error.message;
  } finally {
    toggle("#evaluate", false, "运行 Baseline / Tuned 评测");
  }
}

function render(data) {
  const citations = data.findings.reduce((count, item) => count + item.citations.length, 0);
  $("#finding-count").textContent = data.findings.length;
  $("#tool-count").textContent = data.tool_runs.length;
  $("#citation-count").textContent = citations;
  $("#version").textContent = data.prompt_version;
  $("#summary").textContent = data.summary;
  $("#findings").className = data.findings.length ? "" : "empty";
  $("#findings").innerHTML = data.findings.length ? data.findings.map((finding) => `
    <article class="finding">
      <div class="finding-head">
        <div><span class="severity ${finding.severity}">${escapeHtml(finding.severity)}</span><strong>${escapeHtml(finding.category)}</strong></div>
        <span>${escapeHtml(finding.topic)}</span>
      </div>
      <p>${escapeHtml(finding.message)}</p>
      <p class="suggestion">${escapeHtml(finding.suggestion)}</p>
      <div class="citations">
        ${finding.citations.map((citation) => `
          <blockquote>
            <strong>${escapeHtml(citation.title)}</strong>
            <p>${escapeHtml(citation.quote)}</p>
            <footer>${escapeHtml(citation.document_id)} · score ${citation.score.toFixed(3)}</footer>
          </blockquote>
        `).join("")}
      </div>
    </article>
  `).join("") : "未发现已覆盖规则的问题。";
}

function toggle(selector, disabled, label) {
  const button = $(selector);
  button.disabled = disabled;
  button.textContent = label;
}
function percent(value) { return `${(value * 100).toFixed(1)}%`; }
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]);
}
