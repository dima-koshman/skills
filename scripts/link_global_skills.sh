#!/usr/bin/env bash
# Publish skills globally by SYMLINK instead of copy — the live-editing alternative to
# `npx skills add <dir> --global`. Same layout npx produces, so every harness finds them:
#
#   ~/.agents/skills/<name>  -> <skill dir>             (OpenCode, Codex, Cursor, Antigravity, …)
#   ~/.claude/skills/<name>  -> ../../.agents/skills/<name>   (Claude Code)
#
# Edits in the source repo apply everywhere with no re-run; re-run only to add or remove a skill.
# An existing copy of the same skill (e.g. an earlier npx install, recognised by the same
# `name:` in its SKILL.md) is replaced; anything else in the way is refused, never clobbered.
# Switching back to npx: run with --unlink first, so npx does not write through the link.
#
# Usage: link_global_skills.sh [--unlink | --status] <skill-dir>...
#
# Takes explicit skill directories so it works for any repo when on PATH.
set -euo pipefail

AGENTS_DIR="$HOME/.agents/skills"
CLAUDE_DIR="$HOME/.claude/skills"

mode=link
case "${1:-}" in
    --unlink) mode=unlink; shift ;;
    --status) mode=status; shift ;;
esac
if [ $# -eq 0 ]; then
    echo "Usage: $0 [--unlink | --status] <skill-dir>..." >&2
    exit 2
fi

skill_name() { sed -n 's/^name:[[:space:]]*//p' "$1/SKILL.md" 2>/dev/null | head -1 | tr -d '"'"'"; }

# 0 when $1 is a real directory holding a copy of skill $2.
is_copy_of() { [ -d "$1" ] && [ ! -L "$1" ] && [ "$(skill_name "$1")" = "$2" ]; }

# Point $1 at $2 unless something unrelated is there. Prints what happened.
place_link() {
    local dest="$1" target="$2" name="$3"
    if [ -L "$dest" ]; then
        if [ "$(readlink "$dest")" = "$target" ]; then
            echo "already linked  $dest"
            return 0
        fi
        rm "$dest"
        ln -s "$target" "$dest"
        echo "relinked        $dest -> $target"
    elif is_copy_of "$dest" "$name"; then
        rm -rf "$dest"
        ln -s "$target" "$dest"
        echo "replaced copy   $dest -> $target"
    elif [ -e "$dest" ]; then
        echo "Refusing: $dest exists and is not a copy of skill '$name'." >&2
        return 1
    else
        ln -s "$target" "$dest"
        echo "linked          $dest -> $target"
    fi
}

mkdir -p "$AGENTS_DIR" "$CLAUDE_DIR"
failed=0

for arg in "$@"; do
    if [ ! -f "$arg/SKILL.md" ]; then
        echo "Refusing: $arg has no SKILL.md." >&2
        failed=1
        continue
    fi
    dir="$(cd "$arg" && pwd)"
    name="$(basename "$dir")"
    agents_link="$AGENTS_DIR/$name"
    claude_link="$CLAUDE_DIR/$name"

    case "$mode" in
        link)
            place_link "$agents_link" "$dir" "$name" || { failed=1; continue; }
            place_link "$claude_link" "../../.agents/skills/$name" "$name" || failed=1
            ;;
        unlink)
            if [ -L "$agents_link" ] && [ "$(readlink "$agents_link")" = "$dir" ]; then
                rm "$agents_link"
                echo "unlinked        $agents_link"
                if [ -L "$claude_link" ] && [ "$(readlink "$claude_link")" = "../../.agents/skills/$name" ]; then
                    rm "$claude_link"
                    echo "unlinked        $claude_link"
                fi
            else
                echo "not linked here $agents_link"
            fi
            ;;
        status)
            if [ -L "$agents_link" ] && [ "$(readlink "$agents_link")" = "$dir" ]; then
                state=linked
            elif is_copy_of "$agents_link" "$name"; then
                state=copy
            elif [ -e "$agents_link" ] || [ -L "$agents_link" ]; then
                state=other
            else
                state=missing
            fi
            printf '%-30s %-8s %s\n' "$name" "$state" "$dir"
            ;;
    esac
done

exit "$failed"
