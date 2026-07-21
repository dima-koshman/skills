#!/usr/bin/env bash
# Replace CLAUDE.md with a symlink to AGENTS.md, so Claude Code and other
# agents read one instruction file.
#
# Refuses to clobber a CLAUDE.md that holds its own content; only comments,
# blank lines and lines merely mentioning AGENTS.md count as disposable.
# Delete the file manually first if replacing real content is intended.
#
# Usage: link_claude_md.sh [project-dir]
#
# Acts on the current directory by default, so this works in any project when
# the script is on PATH — never on the repo the script itself lives in.
set -euo pipefail

PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR"

if [ ! -f AGENTS.md ]; then
    echo "Refusing: $PROJECT_DIR/AGENTS.md does not exist; the symlink would dangle." >&2
    exit 1
fi

if [ -L CLAUDE.md ]; then
    echo "CLAUDE.md is already a symlink -> $(readlink CLAUDE.md)"
    exit 0
fi

if [ -s CLAUDE.md ] && grep -vE '^\s*(#.*)?$' CLAUDE.md | grep -qivF 'AGENTS.md'; then
    echo 'Refusing: CLAUDE.md has its own content. Review and delete it first.' >&2
    exit 1
fi

rm -f CLAUDE.md
ln -s AGENTS.md CLAUDE.md
echo 'Linked CLAUDE.md -> AGENTS.md'
