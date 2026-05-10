const docs = [
  { id: "agent", text: "Agent uses tools, memory, workflow, and evaluation to complete tasks." },
  { id: "rag", text: "RAG chunks documents, embeds chunks, retrieves top matches, and cites sources." },
  { id: "mcp", text: "MCP exposes tools resources and prompts to connect agents with systems." }
];

export function chunkDocs(size = 80) {
  return docs.flatMap((doc) => {
    const chunks = [];
    for (let i = 0; i < doc.text.length; i += size) chunks.push({ id: `${doc.id}:${chunks.length}`, docId: doc.id, text: doc.text.slice(i, i + size) });
    return chunks;
  });
}

export function embed(text) {
  const vector = Array(16).fill(0);
  for (const token of tokenize(text)) {
    let hash = 0;
    for (const ch of token) hash = (hash * 31 + ch.charCodeAt(0)) % 997;
    vector[hash % vector.length] += 1;
  }
  return vector;
}

export function search(query, topK = 2) {
  const qv = embed(query);
  return chunkDocs().map((chunk) => ({ ...chunk, score: cosine(qv, embed(chunk.text)) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}

export function answer(query) {
  const hits = search(query).filter((hit) => hit.score > 0);
  if (!hits.length) return { answer: "没有检索到可靠来源。", sources: [] };
  return { answer: `${hits.map((h) => h.text).join(" ")}\nSources: ${hits.map((h) => h.id).join(", ")}`, sources: hits };
}

export function evaluateRetrieval(cases) {
  return cases.map((c) => {
    const hits = search(c.query, 3);
    return { query: c.query, expected: c.expectedDocId, hit: hits.some((h) => h.docId === c.expectedDocId), top: hits[0]?.docId };
  });
}

function tokenize(text) { return String(text).toLowerCase().match(/[a-z0-9]+|[\u4e00-\u9fa5]+/g) || []; }
function cosine(a, b) {
  const dot = a.reduce((sum, value, i) => sum + value * b[i], 0);
  const na = Math.sqrt(a.reduce((sum, value) => sum + value * value, 0));
  const nb = Math.sqrt(b.reduce((sum, value) => sum + value * value, 0));
  return na && nb ? dot / (na * nb) : 0;
}
