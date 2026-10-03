#!/usr/bin/env bash
# One turn of a spoken conversation with Claude Code, for the "Ask Claude" Shortcut.
#
# Usage: printf '%s' "<dictated text>" | voice_chat.sh
#
# Prints the reply to speak, stripped of markdown. Turns less than VOICE_CHAT_RESUME_MINUTES
# (default 10) apart continue one Claude session, so a conversation survives between Siri
# invocations. "New conversation" starts over; "stop", "goodbye" or silence print nothing,
# which the Shortcut treats as the end of the conversation (its If action can only test a
# shell script result for having a value).
#
# Claude runs headlessly from $HOME in auto mode: it may run commands and edit files, and its
# safety classifier blocks risky actions. VOICE_CHAT_MODEL picks the model (default sonnet,
# for latency).
set -euo pipefail

# Shortcuts runs scripts with a minimal PATH that lacks Homebrew and ~/.local/bin.
export PATH="$PATH:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin"

STATE_DIR="${VOICE_CHAT_STATE_DIR:-$HOME/.cache/voice-chat}"
SESSION_FILE="$STATE_DIR/session"
RESUME_MINUTES="${VOICE_CHAT_RESUME_MINUTES:-10}"
MODEL="${VOICE_CHAT_MODEL:-sonnet}"
mkdir -p "$STATE_DIR"

TEXT="$(cat)"
# Dictation capitalizes, punctuates and may use a curly apostrophe; match phrases without those.
COMMAND="$(printf '%s' "$TEXT" | tr '[:upper:]' '[:lower:]' |
	sed -E -e "s/’/'/g" -e 's/[.,!?;:]//g' -e 's/^[[:space:]]+|[[:space:]]+$//g')"

case "$COMMAND" in
"" | stop | goodbye | "that's all" | "never mind" | nevermind)
	exit 0
	;;
"new conversation" | "start over")
	rm -f "$SESSION_FILE"
	echo "Okay, starting a new conversation."
	exit 0
	;;
esac

VOICE_PROMPT="You are talking with the user by voice. Their messages come from speech-to-text and \
may contain transcription errors, and your reply will be read aloud. Answer in one to three short \
spoken sentences, without markdown, lists, code or URLs. If a request is ambiguous or may have \
been misheard, ask a short clarifying question instead of acting. Before anything that deletes, \
sends, installs or changes settings, say what you are about to do and ask the user to confirm in \
their next message."

args=(-p "$TEXT" --output-format json --permission-mode auto --model "$MODEL"
	--append-system-prompt "$VOICE_PROMPT")
if [ -n "$(find "$SESSION_FILE" -mmin "-$RESUME_MINUTES" 2>/dev/null)" ]; then
	args+=(--resume "$(cat "$SESSION_FILE")")
fi

cd "$HOME"
if ! OUT="$(claude "${args[@]}" </dev/null 2>"$STATE_DIR/last-error.log")"; then
	echo "Sorry, Claude failed. The error is in $STATE_DIR/last-error.log."
	exit 0
fi

REPLY="$(printf '%s' "$OUT" | jq -r '.result // empty')"
SESSION="$(printf '%s' "$OUT" | jq -r '.session_id // empty')"
[ -z "$SESSION" ] || printf '%s' "$SESSION" >"$SESSION_FILE"

if [ "$(printf '%s' "$OUT" | jq -r '.is_error')" = "true" ] || [ -z "$REPLY" ]; then
	echo "Sorry, that went wrong. ${REPLY}"
	exit 0
fi

# Markdown reads badly aloud: keep link text, drop emphasis, code ticks and heading marks.
printf '%s\n' "$REPLY" | sed -E \
	-e 's/\[([^]]*)\]\([^)]*\)/\1/g' \
	-e 's/[*`]//g' \
	-e 's/^#+ *//'
