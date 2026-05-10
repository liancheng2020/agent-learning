import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const dataDir = join(__dirname, "../data");
const resources = readJson("resources.json");
const prompts = readJson("prompts.json");
const fileListings = readJson("fileListings.json");

const tools = {
  listFiles({ path = "." } = {}) {
    return { path, files: fileListings[path] || [] };
  },
  summarize({ text }) {
    return { summary: String(text).slice(0, 80) };
  }
};

export function listCapabilities() {
  return {
    resources: Object.keys(resources),
    prompts: Object.keys(prompts),
    tools: Object.keys(tools)
  };
}

export function readResource(uri) {
  if (!(uri in resources)) throw new Error(`unknown resource: ${uri}`);
  return { uri, text: resources[uri] };
}

export function getPrompt(name) {
  if (!(name in prompts)) throw new Error(`unknown prompt: ${name}`);
  return { name, template: prompts[name] };
}

export function callTool(name, args) {
  if (!(name in tools)) throw new Error(`unknown tool: ${name}`);
  return { name, result: tools[name](args) };
}

function readJson(fileName) {
  return JSON.parse(readFileSync(join(dataDir, fileName), "utf8"));
}
