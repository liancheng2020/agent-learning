import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const publicDir = path.resolve("public");
const dataDir = path.resolve("data");
const port = Number(process.env.PORT || 5110);

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${port}`);
  if (url.pathname === "/api/trace") {
    const tracePath = path.join(dataDir, "trace.jsonl");
    const body = fs.existsSync(tracePath) ? parseJsonl(fs.readFileSync(tracePath, "utf8")) : [];
    return json(res, body);
  }

  const filePath = path.join(publicDir, url.pathname === "/" ? "index.html" : url.pathname);
  if (!filePath.startsWith(publicDir) || !fs.existsSync(filePath)) {
    res.writeHead(404);
    res.end("not found");
    return;
  }

  res.writeHead(200, { "Content-Type": contentType(filePath) });
  res.end(fs.readFileSync(filePath));
});

server.listen(port, () => {
  console.log(`Agent dashboard: http://localhost:${port}`);
});

function parseJsonl(text) {
  return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function json(res, data) {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function contentType(filePath) {
  if (filePath.endsWith(".css")) return "text/css";
  if (filePath.endsWith(".js")) return "application/javascript";
  return "text/html";
}
