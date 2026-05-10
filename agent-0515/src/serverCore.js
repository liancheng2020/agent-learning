const resources = { "project://package": '{"name":"demo"}', "docs://rules": "Only read files under allowed roots." };
const tools = {
  echo(args) { return args; },
  getPackageInfo() { return { name: "agent-0515-real-mcp-server", runtime: "node" }; }
};

export function handleRpc(request) {
  const { id, method, params = {} } = request;
  try {
    if (method === "tools/list") return ok(id, Object.keys(tools).map((name) => ({ name })));
    if (method === "tools/call") return ok(id, callTool(params.name, params.arguments || {}));
    if (method === "resources/list") return ok(id, Object.keys(resources).map((uri) => ({ uri })));
    if (method === "resources/read") return ok(id, { uri: params.uri, text: resources[params.uri] });
    return err(id, `unknown method: ${method}`);
  } catch (error) {
    return err(id, error.message);
  }
}

function callTool(name, args) {
  if (!tools[name]) throw new Error(`unknown tool: ${name}`);
  return tools[name](args);
}
function ok(id, result) { return { jsonrpc: "2.0", id, result }; }
function err(id, message) { return { jsonrpc: "2.0", id, error: { message } }; }
