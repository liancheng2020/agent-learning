export function estimateCost({ inputTokens, outputTokens, inputPrice = 0.000001, outputPrice = 0.000004 }) {
  return inputTokens * inputPrice + outputTokens * outputPrice;
}

export function recordRun(input) {
  const started = Date.now();
  const inputTokens = roughTokens(input);
  const output = `answer for ${input}`;
  const outputTokens = roughTokens(output);
  return {
    input,
    output,
    latencyMs: Date.now() - started,
    inputTokens,
    outputTokens,
    costUsd: estimateCost({ inputTokens, outputTokens }),
    ok: true
  };
}

export function summarize(records) {
  return {
    runs: records.length,
    okRate: records.filter((r) => r.ok).length / records.length,
    totalCostUsd: round(records.reduce((sum, r) => sum + r.costUsd, 0)),
    avgLatencyMs: Math.round(records.reduce((sum, r) => sum + r.latencyMs, 0) / records.length)
  };
}

function roughTokens(text) { return Math.ceil(String(text).length / 4); }
function round(n) { return Math.round(n * 1000000) / 1000000; }
