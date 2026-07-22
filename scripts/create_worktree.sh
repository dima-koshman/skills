#!/bin/bash
set -euo pipefail

BRANCH="${1:?Usage: $0 <branch-name> [dir]}"
NORMALIZED="${BRANCH//\//-}"

MAIN_ROOT="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"
CURRENT_ROOT="$(git rev-parse --show-toplevel)"

# Invoked from the main worktree: nest new worktrees under .worktrees/.
# Invoked from a linked worktree: put the new one beside it, so worktrees kept
# outside .worktrees/ stay grouped where they already live.
if [ "${CURRENT_ROOT}" = "${MAIN_ROOT}" ]; then
	BASE_DIR="${MAIN_ROOT}/.worktrees"
else
	BASE_DIR="$(dirname "${CURRENT_ROOT}")"
fi

DEST="${2:-${NORMALIZED}}"
case "${DEST}" in
/*) ;;
*) DEST="${BASE_DIR}/${DEST}" ;;
esac
mkdir -p "$(dirname "${DEST}")"

# An existing branch is checked out as-is. An unknown one is created off the main
# worktree's HEAD — normally main — so a new branch starts from the integration
# branch even when this runs from a worktree sitting on unrelated work.
if git rev-parse --verify --quiet "refs/heads/${BRANCH}" >/dev/null; then
	echo "Creating worktree at ${DEST} for existing branch ${BRANCH}..."
	git worktree add -- "${DEST}" "${BRANCH}"
else
	START_POINT="$(git -C "${MAIN_ROOT}" rev-parse HEAD)"
	echo "Creating worktree at ${DEST} for new branch ${BRANCH} (from ${MAIN_ROOT} @ ${START_POINT:0:12})..."
	git worktree add -b "${BRANCH}" -- "${DEST}" "${START_POINT}"
fi

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
