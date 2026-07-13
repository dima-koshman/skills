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

function convertServer(server) {
  if (!server || typeof server !== "object" || Array.isArray(server)) return undefined

  if (typeof server.url === "string") {
    const converted = {
      type: "remote",
      url: expandEnvReferences(server.url),
    }
    if (server.enabled !== undefined) converted.enabled = Boolean(server.enabled)
    if (server.timeout !== undefined) converted.timeout = server.timeout
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
    if (server.enabled !== undefined) converted.enabled = Boolean(server.enabled)
    if (server.timeout !== undefined) converted.timeout = server.timeout
    if (typeof server.cwd === "string") converted.cwd = expandEnvReferences(server.cwd)
    const environment = expandStringRecord(server.env ?? server.environment)
    if (environment) converted.environment = environment
    return converted
  }

  return undefined
}

export const LoadMcpJson = async ({ worktree, directory }) => ({
  config: async (config) => {
    const file = path.join(worktree || directory, ".mcp.json")
    if (!fs.existsSync(file)) return

    const parsed = JSON.parse(fs.readFileSync(file, "utf8"))
    const servers = parsed.mcpServers ?? parsed.servers
    if (!servers || typeof servers !== "object" || Array.isArray(servers)) return

    const converted = Object.fromEntries(
      Object.entries(servers)
        .map(([name, server]) => [name, convertServer(server)])
        .filter((entry) => entry[1]),
    )

    config.mcp = { ...converted, ...(config.mcp ?? {}) }
  },
})
