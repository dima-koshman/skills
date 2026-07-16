# Global OpenCode Sync Task Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a VS Code task that copies the project's selected OpenCode configuration files to the user's global OpenCode directory.

**Architecture:** Extend the existing `.vscode/tasks.json` task list with one shell task. The command creates the global plugin and schema directories and explicitly copies five files, preserving every unrelated global file.

**Tech Stack:** VS Code tasks 2.0.0, POSIX shell, macOS `mkdir`, `cp`, and `cmp`, Bun test runner

## Global Constraints

- Copy `.opencode/opencode.jsonc`, `.opencode/tui.json`, `.opencode/dcp.jsonc`, `.opencode/plugins/load-mcp-json.js`, and `.opencode/schemas/claude-mcp.schema.json` exactly.
- Use `${workspaceFolder}` for every source path.
- Overwrite only the corresponding five global destination files.
- Do not copy `node_modules`, package files, plugin tests, unrelated schemas, or notifier state.
- Chain shell operations with `&&` so execution stops after the first failure.
- Do not commit changes unless the user explicitly requests a commit.

---

### Task 1: Add and verify the global sync task

**Files:**
- Modify: `.vscode/tasks.json:11-89`
- Verify: `.opencode/plugins/load-mcp-json.test.js`

**Interfaces:**
- Consumes: VS Code `${workspaceFolder}` variable and the five source files listed in Global Constraints.
- Produces: VS Code task `Sync OpenCode config globally` and matching files under `$HOME/.config/opencode`.

- [ ] **Step 1: Add the task definition**

Insert this object into the existing `tasks` array:

```json
{
    "label": "Sync OpenCode config globally",
    "detail": "Copy this project's OpenCode, TUI, and DCP configs plus the .mcp.json loader and schema to ~/.config/opencode",
    "command": "mkdir -p \"$HOME/.config/opencode/plugins\" \"$HOME/.config/opencode/schemas\" && cp -f \"${workspaceFolder}/.opencode/opencode.jsonc\" \"$HOME/.config/opencode/opencode.jsonc\" && cp -f \"${workspaceFolder}/.opencode/tui.json\" \"$HOME/.config/opencode/tui.json\" && cp -f \"${workspaceFolder}/.opencode/dcp.jsonc\" \"$HOME/.config/opencode/dcp.jsonc\" && cp -f \"${workspaceFolder}/.opencode/plugins/load-mcp-json.js\" \"$HOME/.config/opencode/plugins/load-mcp-json.js\" && cp -f \"${workspaceFolder}/.opencode/schemas/claude-mcp.schema.json\" \"$HOME/.config/opencode/schemas/claude-mcp.schema.json\""
}
```

- [ ] **Step 2: Validate the VS Code task file as JSON**

Run:

```bash
python3 -m json.tool .vscode/tasks.json >/dev/null
```

Expected: exit status 0 with no output.

- [ ] **Step 3: Run the exact synchronization command**

Run:

```bash
mkdir -p "$HOME/.config/opencode/plugins" "$HOME/.config/opencode/schemas" && cp -f "$PWD/.opencode/opencode.jsonc" "$HOME/.config/opencode/opencode.jsonc" && cp -f "$PWD/.opencode/tui.json" "$HOME/.config/opencode/tui.json" && cp -f "$PWD/.opencode/dcp.jsonc" "$HOME/.config/opencode/dcp.jsonc" && cp -f "$PWD/.opencode/plugins/load-mcp-json.js" "$HOME/.config/opencode/plugins/load-mcp-json.js" && cp -f "$PWD/.opencode/schemas/claude-mcp.schema.json" "$HOME/.config/opencode/schemas/claude-mcp.schema.json"
```

Expected: exit status 0 with no output.

- [ ] **Step 4: Verify exact destination contents**

Run:

```bash
cmp -s .opencode/opencode.jsonc "$HOME/.config/opencode/opencode.jsonc" && cmp -s .opencode/tui.json "$HOME/.config/opencode/tui.json" && cmp -s .opencode/dcp.jsonc "$HOME/.config/opencode/dcp.jsonc" && cmp -s .opencode/plugins/load-mcp-json.js "$HOME/.config/opencode/plugins/load-mcp-json.js" && cmp -s .opencode/schemas/claude-mcp.schema.json "$HOME/.config/opencode/schemas/claude-mcp.schema.json"
```

Expected: exit status 0 with no output.

- [ ] **Step 5: Run the MCP loader test**

Run:

```bash
npx --yes bun test ./.opencode/plugins/load-mcp-json.test.js
```

Expected: one test passes and the command exits with status 0.

- [ ] **Step 6: Inspect the final diff and status**

Run:

```bash
git diff -- .vscode/tasks.json docs/superpowers/specs/2026-07-16-global-opencode-sync-task-design.md docs/superpowers/plans/2026-07-16-global-opencode-sync-task.md
```

Expected: the new task is the only `.vscode/tasks.json` change; the new design and plan documents are untracked; the pre-existing `.opencode/opencode.jsonc` modification remains untouched.
