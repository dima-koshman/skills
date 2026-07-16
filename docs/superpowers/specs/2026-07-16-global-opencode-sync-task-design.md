# Global OpenCode Sync Task Design

## Goal

Add a VS Code task that explicitly copies selected project OpenCode files into the user's global OpenCode configuration.

## Behavior

The task creates `~/.config/opencode/plugins` and `~/.config/opencode/schemas` when needed, then copies these files exactly:

- `.opencode/opencode.jsonc` to `~/.config/opencode/opencode.jsonc`
- `.opencode/tui.json` to `~/.config/opencode/tui.json`
- `.opencode/dcp.jsonc` to `~/.config/opencode/dcp.jsonc`
- `.opencode/plugins/load-mcp-json.js` to `~/.config/opencode/plugins/load-mcp-json.js`
- `.opencode/schemas/claude-mcp.schema.json` to `~/.config/opencode/schemas/claude-mcp.schema.json`

The command uses `${workspaceFolder}` for source paths and chains operations with `&&`, so a failed operation prevents subsequent copies. Existing destination versions of these five files are overwritten. Other global files, including notifier state, package files, and plugins, remain unchanged.

## Runtime Behavior

When globally installed, `load-mcp-json.js` uses OpenCode's active `worktree` or `directory` value to locate `.mcp.json`. It therefore reads `.mcp.json` from the active project rather than from `~/.config/opencode`.

The project-local plugin remains in place. Within this project, OpenCode may discover both copies; the plugin's MCP configuration merge is idempotent for identical input, although keeping both copies is redundant.

## Verification

Validate `.vscode/tasks.json`, run the new task, compare all five source and destination files byte-for-byte, and run the MCP plugin test. Restart OpenCode after synchronization because configuration and plugins are loaded at startup.
