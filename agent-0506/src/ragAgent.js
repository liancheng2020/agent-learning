import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const docsPath = join(__dirname, "../data/docs.json");
const docs = JSON.parse(readFileSync(docsPath, "utf8"));

export function retrieve(query, limit = 2) {
  const terms = tokenize(query);
  return docs
    .map((doc) => ({ doc, score: score(doc, terms) }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((item) => ({ ...item.doc, score: item.score }));
}

export function answerWithRag(query) {
  const sources = retrieve(query);
  if (sources.length === 0) {
    return { ok: false, answer: "资料库里没有找到相关内容，我不能基于当前知识库回答。", sources: [] };
  }

  const answer = sources
    .map((source) => `${source.title}: ${source.text}`)
    .join("\n");

  return {
    ok: true,
    answer: `${answer}\n\nSources: ${sources.map((source) => source.id).join(", ")}`,
    sources
  };
}

function tokenize(text) {
  return String(text).toLowerCase().match(/[a-z0-9]+|[\u4e00-\u9fa5]+/g) || [];
}

function score(doc, terms) {
  const haystack = `${doc.title} ${doc.text}`.toLowerCase();
  return terms.reduce((total, term) => total + (haystack.includes(term) ? 1 : 0), 0);
}
