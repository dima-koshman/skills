#!/bin/bash
set -euo pipefail

BRANCH="${1:?Usage: $0 <branch-name> [dir]}"
NORMALIZED="${BRANCH//\//-}"

# All worktrees live under <main-worktree>/.worktrees/, regardless of which
# worktree the script is invoked from.
MAIN_ROOT="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"
WORKTREES_DIR="${MAIN_ROOT}/.worktrees"

if [ -n "${2:-}" ]; then
	DEST="$2"
else
	DEST="${NORMALIZED}"
fi
mkdir -p "${WORKTREES_DIR}"
DEST="$(cd "${WORKTREES_DIR}" && python3 -c "import os,sys; print(os.path.abspath(sys.argv[1]))" "$DEST")"

echo "Creating worktree at ${DEST} for branch ${BRANCH}..."
git worktree add -- "${DEST}" "${BRANCH}"

# Copy .env if it exists
if [ -f "${MAIN_ROOT}/.env" ]; then
	echo "Copying .env..."
	cp "${MAIN_ROOT}/.env" "${DEST}/.env"
fi

# Run setup commands in destination
(
	cd "${DEST}"
	echo "Running setup commands..."
	if command -v direnv >/dev/null 2>&1; then
		direnv allow || true
	fi
	if command -v pre-commit >/dev/null 2>&1; then
		pre-commit install || true
	fi
	if command -v uv >/dev/null 2>&1; then
		uv sync || true
	fi
)

# Launch IDE
echo "Launching IDE..."
if command -v ide >/dev/null 2>&1; then
	ide "${DEST}"
else
	echo "Warning: 'ide' command not found."
fi
