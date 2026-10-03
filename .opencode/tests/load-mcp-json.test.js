import { expect, test } from "bun:test"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"

import LoadMcpJson from "../plugins/load-mcp-json.js"

// Stands in for the opencode v2 host: hands the plugin an MCP editor backed by a Map
// (the MCPEditor shape from @opencode/plugin) and returns what the plugin registered.
async function setupWith(mcpServers, existing = {}) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "load-mcp-json-"))
  fs.writeFileSync(path.join(directory, ".mcp.json"), JSON.stringify({ mcpServers }))
  const servers = new Map(Object.entries(existing))
  const editor = {
    list: () => [...servers.entries()],
    get: (name) => servers.get(name),
    set: (name, config) => servers.set(name, config),
    update: (name, update) => update(servers.get(name)),
    remove: (name) => servers.delete(name),
  }
  const context = {
    location: { directory, project: { directory } },
    mcp: {
      transform: async (callback) => {
        callback(editor)
        return { dispose: async () => {} }
      },
    },
  }
  try {
    await LoadMcpJson.setup(context)
  } finally {
    fs.rmSync(directory, { recursive: true, force: true })
  }
  return Object.fromEntries(servers)
}

test("expands environment references while importing remote headers", async () => {
  const variable = "OPENCODE_TEST_MCP_AUTH_HEADER"
  const previous = process.env[variable]

  try {
    process.env[variable] = "encoded-test-credential"
    const servers = await setupWith({
      remote: {
        type: "streamable-http",
        url: "https://example.test/mcp",
        headers: { Authorization: `Basic \${${variable}}` },
      },
    })

    expect(servers.remote).toEqual({
      type: "remote",
      url: "https://example.test/mcp",
      headers: { Authorization: "Basic encoded-test-credential" },
    })
  } finally {
    if (previous === undefined) delete process.env[variable]
    else process.env[variable] = previous
  }
})

test("imports a stdio server as a local command array", async () => {
  const servers = await setupWith({
    playwright: { type: "stdio", command: "npx", args: ["-y", "@playwright/mcp@latest"], env: { DEBUG: "1" } },
  })

  expect(servers.playwright).toEqual({
    type: "local",
    command: ["npx", "-y", "@playwright/mcp@latest"],
    environment: { DEBUG: "1" },
  })
})

test("leaves servers already defined in opencode config untouched", async () => {
  const configured = { type: "remote", url: "https://configured.test/mcp" }
  const servers = await setupWith(
    { shared: { type: "http", url: "https://from-mcp-json.test/mcp" } },
    { shared: configured },
  )

  expect(servers.shared).toBe(configured)
})
