#!/usr/bin/env bash
# Replace .claude/skills with a symlink to .agents/skills.
#
# Claude Code only scans .claude/skills/, while OpenCode reads .agents/skills/
# directly. Linking the directory (rather than each skill) means newly added
# skills need no re-run.
#
# Refuses to act if .agents/skills is missing (the link would dangle), or if
# .claude/skills holds a real entry that has no counterpart in .agents/skills
# and would therefore be lost.
#
# Usage: link_claude_skills.sh [project-dir]
#
# Acts on the current directory by default, so this works in any project when
# the script is on PATH — never on the repo the script itself lives in.
set -euo pipefail

PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR"

if [ ! -d .agents/skills ]; then
    echo "Refusing: $PROJECT_DIR/.agents/skills does not exist; the symlink would dangle." >&2
    exit 1
fi

if [ -L .claude/skills ]; then
    echo "Already a symlink: .claude/skills -> $(readlink .claude/skills)"
    exit 0
fi

if [ -d .claude/skills ]; then
    orphans=()
    for entry in .claude/skills/*; do
        # Guard against the literal glob when .claude/skills is empty.
        [ -e "$entry" ] || [ -L "$entry" ] || continue
        name=$(basename "$entry")
        if [ ! -L "$entry" ] && [ ! -e ".agents/skills/$name" ]; then
            orphans+=("$name")
        fi
    done

    if [ "${#orphans[@]}" -gt 0 ]; then
        echo "Refusing: .claude/skills holds entries absent from .agents/skills: ${orphans[*]}" >&2
        exit 1
    fi
fi

rm -rf .claude/skills
mkdir -p .claude
ln -s ../.agents/skills .claude/skills
echo 'Linked .claude/skills -> ../.agents/skills'
