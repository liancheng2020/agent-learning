export function summarizeRun({ startedAt, findings, patch, toolErrors = 0 }) {
  const latencyMs = Date.now() - startedAt;
  const estimatedTokens = Math.ceil(JSON.stringify({ findings, patch }).length / 4);
  return {
    latencyMs,
    estimatedTokens,
    estimatedCostUsd: round(estimatedTokens * 0.000002),
    findingCount: findings.length,
    toolErrors,
  };
}

export function aggregateRuns(runs) {
  const metrics = runs.map((run) => run.metrics).filter(Boolean);
  if (metrics.length === 0) {
    return { runs: 0, successRate: 0, avgLatencyMs: 0, p95LatencyMs: 0, totalEstimatedCostUsd: 0, toolErrors: 0 };
  }

  const latencies = metrics.map((item) => item.latencyMs).sort((a, b) => a - b);
  return {
    runs: runs.length,
    successRate: round(runs.filter((run) => run.ok).length / runs.length),
    avgLatencyMs: Math.round(latencies.reduce((sum, value) => sum + value, 0) / latencies.length),
    p95LatencyMs: latencies[Math.min(latencies.length - 1, Math.ceil(latencies.length * 0.95) - 1)],
    totalEstimatedCostUsd: round(metrics.reduce((sum, item) => sum + item.estimatedCostUsd, 0)),
    toolErrors: metrics.reduce((sum, item) => sum + item.toolErrors, 0),
  };
}

function round(value) { return Math.round(value * 1_000_000) / 1_000_000; }
