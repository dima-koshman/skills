import { expect, test } from "bun:test"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"

import { LoadMcpJson } from "./load-mcp-json.js"

test("expands environment references while importing remote headers", async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "load-mcp-json-"))
  const variable = "OPENCODE_TEST_MCP_AUTH_HEADER"
  const previous = process.env[variable]

  try {
    process.env[variable] = "encoded-test-credential"
    fs.writeFileSync(
      path.join(directory, ".mcp.json"),
      JSON.stringify({
        mcpServers: {
          remote: {
            type: "streamable-http",
            url: "https://example.test/mcp",
            headers: { Authorization: `Basic \${${variable}}` },
          },
        },
      }),
    )

    const hooks = await LoadMcpJson({ worktree: directory, directory })
    const config = {}
    await hooks.config(config)

    expect(config.mcp.remote.headers.Authorization).toBe("Basic encoded-test-credential")
  } finally {
    if (previous === undefined) delete process.env[variable]
    else process.env[variable] = previous
    fs.rmSync(directory, { recursive: true, force: true })
  }
})
