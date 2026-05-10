const summary = document.querySelector("#summary");
const timeline = document.querySelector("#timeline");
document.querySelector("#refresh").addEventListener("click", loadTrace);

async function loadTrace() {
  const records = await fetch("/api/trace").then((response) => response.json());
  const runs = new Set(records.map((record) => record.runId).filter(Boolean));
  const tools = records.filter((record) => record.type === "tool.selected").length;
  const completed = records.filter((record) => record.type === "run.completed" && record.ok).length;

  summary.innerHTML = [
    metric("Records", records.length),
    metric("Runs", runs.size),
    metric("Tool Calls", tools),
    metric("Completed", completed),
  ].join("");

  timeline.innerHTML = records.map((record) => {
    return `<article class="event">
      <div>
        <div class="type">${record.type}</div>
        <div>${new Date(record.ts).toLocaleTimeString()}</div>
      </div>
      <pre>${escapeHtml(JSON.stringify(record, null, 2))}</pre>
    </article>`;
  }).join("");
}

function metric(label, value) {
  return `<div class="metric"><strong>${value}</strong><span>${label}</span></div>`;
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[char]));
}

loadTrace();
