export function summarize({ startedAt, findings, patch }) {
  const latencyMs = Date.now() - startedAt;
  const estimatedTokens = Math.ceil(JSON.stringify({ findings, patch }).length / 4);
  return { latencyMs, estimatedTokens, estimatedCostUsd: Math.round(estimatedTokens * 0.000002 * 1000000) / 1000000, findingCount: findings.length };
}
