# use agent_profile [NAME [SKILL ...]]: run Claude Code, Codex and OpenCode in this directory on the agent
# profile NAME (default: personal) instead of the global config, so they get none of the global skills, MCP
# servers or instructions, except the global SKILLs listed. Install by symlinking this file into
# ~/.config/direnv/lib/. See agent_profile.py.
use_agent_profile() {
  local name=${1:-personal}
  shift || true
  local root="$HOME/.config/agent-profiles/$name"
  local script
  script="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/agent_profile.py"
  python3 "$script" --profile "$name" --project "$PWD" --keep "$@" || return
  export CLAUDE_CONFIG_DIR="$root/claude"
  export ENABLE_CLAUDEAI_MCP_SERVERS=false
  export CODEX_HOME="$root/codex"
  export OPENCODE_CONFIG_DIR="$root/opencode"
  export OPENCODE_DISABLE_CLAUDE_CODE=1
  PATH_add "$root/bin"
  watch_dir "$HOME/.agents/skills"
  watch_dir "$HOME/.claude/skills"
}
