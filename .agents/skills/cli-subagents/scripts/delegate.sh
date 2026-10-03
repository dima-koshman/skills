#!/usr/bin/env bash
# Run another coding-agent CLI headlessly as a subagent and print only its final answer.
#
# Usage: delegate.sh <claude|opencode|agy> [--write] [--model MODEL] [--resume ID] [--cd DIR] < task
#
# Reads the task prompt from stdin. Read-only by default (claude plan mode, opencode's plan
# agent, agy plan mode); --write lets the subagent edit files. Prints the final answer, then a
# "[delegate]" footer with the session ID to pass to --resume, plus any permissions the
# subagent was denied. Exits non-zero, with the error on stderr, when the run fails.
set -euo pipefail

usage() {
	sed -n '4,4p' "$0" | sed 's/^# //' >&2
	exit 2
}

CLI="${1:-}"
case "$CLI" in claude | opencode | agy) shift ;; *) usage ;; esac

WRITE=false
MODEL=""
RESUME=""
while [ "$#" -gt 0 ]; do
	case "$1" in
	--write) WRITE=true && shift ;;
	--model) MODEL="${2:?--model needs a value}" && shift 2 ;;
	--resume) RESUME="${2:?--resume needs a session ID}" && shift 2 ;;
	--cd) cd "${2:?--cd needs a directory}" && shift 2 ;;
	*) usage ;;
	esac
done

for tool in "$CLI" jq; do
	command -v "$tool" >/dev/null || {
		echo "delegate.sh: $tool is not installed" >&2
		exit 127
	}
done

TASK="$(cat)"
[ -n "$TASK" ] || usage

# A fresh session gets the ground rules; a resumed one already has them.
PROMPT="$TASK"
if [ -z "$RESUME" ]; then
	PROMPT="You are running as a non-interactive subagent: another coding agent invoked you through \
a headless CLI, and nobody can answer questions during this run. Make reasonable assumptions and \
state them. Do not hand this task on to another agent CLI. End with a concise final report of \
what you found or changed.

$TASK"
fi

OUT="$(mktemp)"
ERR="$(mktemp)"
trap 'rm -f "$OUT" "$ERR"' EXIT
STATUS=0

case "$CLI" in
claude)
	args=(-p "$PROMPT" --output-format json)
	if $WRITE; then args+=(--permission-mode acceptEdits); else args+=(--permission-mode plan); fi
	[ -n "$MODEL" ] && args+=(--model "$MODEL")
	[ -n "$RESUME" ] && args+=(--resume "$RESUME")
	claude "${args[@]}" </dev/null >"$OUT" 2>"$ERR" || STATUS=$?
	ANSWER="$(jq -r '.result // empty' "$OUT" 2>/dev/null || true)"
	SESSION="$(jq -r '.session_id // empty' "$OUT" 2>/dev/null || true)"
	FAILED="$(jq -r 'if .is_error then (.result // "claude reported an error") else empty end' "$OUT" 2>/dev/null || true)"
	DENIED="$(jq -r '[.permission_denials[]?.tool_name] | unique | join(", ")' "$OUT" 2>/dev/null || true)"
	;;
opencode)
	args=(run --format json)
	# Without an agent, opencode runs its build agent, which may edit files and run shell commands.
	$WRITE || args+=(--agent plan)
	[ -n "$MODEL" ] && args+=(--model "$MODEL")
	[ -n "$RESUME" ] && args+=(--session "$RESUME")
	opencode "${args[@]}" "$PROMPT" </dev/null >"$OUT" 2>"$ERR" || STATUS=$?
	# The output is one JSON event per line; the answer is the last text part.
	ANSWER="$(jq -rs '[.[] | select(.type == "text")] | last | .part.text // empty' "$OUT" 2>/dev/null || true)"
	SESSION="$(jq -rs '[.[].sessionID // empty] | first // empty' "$OUT" 2>/dev/null || true)"
	FAILED="$(jq -rs '[.[] | select(.type == "error") | .error.message] | join("; ")' "$OUT" 2>/dev/null || true)"
	# Headless opencode auto-rejects "ask" permissions and only says so on stderr.
	DENIED="$(sed -n 's/.*permission requested: \([^ ]*\).*auto-rejecting.*/\1/p' "$ERR" | sort -u | paste -sd, - | sed 's/,/, /g')"
	;;
agy)
	args=(-p "$PROMPT" --output-format json)
	if $WRITE; then args+=(--mode accept-edits); else args+=(--mode plan); fi
	[ -n "$MODEL" ] && args+=(--model "$MODEL")
	[ -n "$RESUME" ] && args+=(--conversation "$RESUME")
	agy "${args[@]}" </dev/null >"$OUT" 2>"$ERR" || STATUS=$?
	ANSWER="$(jq -r '.response // empty' "$OUT" 2>/dev/null || true)"
	SESSION="$(jq -r '.conversation_id // empty' "$OUT" 2>/dev/null || true)"
	FAILED="$(jq -r 'if .status == "ERROR" then (.error // "agy reported an error") else empty end' "$OUT" 2>/dev/null || true)"
	DENIED="$(jq -r '[.denied_actions[]?.action] | unique | join(", ")' "$OUT" 2>/dev/null || true)"
	;;
esac

if [ "$STATUS" -ne 0 ] || [ -n "$FAILED" ]; then
	echo "delegate.sh: $CLI failed (exit $STATUS)${FAILED:+: $FAILED}" >&2
	[ -s "$ERR" ] && tail -n 20 "$ERR" >&2
	[ -n "$ANSWER" ] && printf '%s\n' "$ANSWER" >&2
	exit 1
fi

printf '%s\n\n' "${ANSWER:-(no answer text)}"
echo "[delegate] cli=$CLI session=${SESSION:-unknown}"
[ -z "$DENIED" ] || echo "[delegate] denied: $DENIED"
