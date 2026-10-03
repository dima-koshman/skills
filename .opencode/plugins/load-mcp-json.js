import fs from "node:fs"
import path from "node:path"

function expandEnvReferences(value) {
  if (typeof value !== "string") return value
  return value.replace(/\$\{([^}]+)\}/g, (_, name) => process.env[name] ?? "")
}

function expandStringRecord(record) {
  if (!record || typeof record !== "object" || Array.isArray(record)) return undefined
  return Object.fromEntries(
    Object.entries(record)
      .filter((entry) => typeof entry[1] === "string")
      .map(([key, value]) => [key, expandEnvReferences(value)]),
  )
}

// opencode v2 inverts `enabled` into `disabled` and splits one timeout into phases. A
// .mcp.json `timeout` bounds tool calls (Claude Code's per-server meaning), so it maps to
// the execution phase.
function convertCommonFields(server) {
  const fields = {}
  if (server.enabled !== undefined) fields.disabled = !server.enabled
  if (typeof server.timeout === "number") fields.timeout = { execution: server.timeout }
  return fields
}

function convertServer(server) {
  if (!server || typeof server !== "object" || Array.isArray(server)) return undefined

  if (typeof server.url === "string") {
    const converted = {
      type: "remote",
      url: expandEnvReferences(server.url),
    }
    Object.assign(converted, convertCommonFields(server))
    const headers = expandStringRecord(server.headers)
    if (headers) converted.headers = headers
    return converted
  }

  if (typeof server.command === "string") {
    const args = Array.isArray(server.args) ? server.args.map(expandEnvReferences) : []
    const converted = {
      type: "local",
      command: [expandEnvReferences(server.command), ...args],
    }
    Object.assign(converted, convertCommonFields(server))
    if (typeof server.cwd === "string") converted.cwd = expandEnvReferences(server.cwd)
    const environment = expandStringRecord(server.env ?? server.environment)
    if (environment) converted.environment = environment
    return converted
  }

  return undefined
}

function readServers(directory) {
  const file = path.join(directory, ".mcp.json")
  if (!fs.existsSync(file)) return {}

  const parsed = JSON.parse(fs.readFileSync(file, "utf8"))
  const servers = parsed.mcpServers ?? parsed.servers
  if (!servers || typeof servers !== "object" || Array.isArray(servers)) return {}

  return Object.fromEntries(
    Object.entries(servers)
      .map(([name, server]) => [name, convertServer(server)])
      .filter((entry) => entry[1]),
  )
}

// opencode v2 plugin: a default export with an `id` and `setup(ctx)`. The shape is what
// Plugin.define from @opencode/plugin returns (it is an identity function), so the file
// needs no dependency and can be copied into ~/.config/opencode/plugins/ on its own.
export default {
  id: "load-mcp-json",
  async setup(ctx) {
    const servers = readServers(ctx.location.project?.directory ?? ctx.location.directory)
    if (Object.keys(servers).length === 0) return

    await ctx.mcp.transform((editor) => {
      for (const [name, server] of Object.entries(servers)) {
        // Servers defined in opencode config win over .mcp.json ones of the same name.
        if (!editor.get(name)) editor.set(name, server)
      }
    })
  },
}
