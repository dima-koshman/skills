#!/bin/bash
set -euo pipefail

BRANCH="${1:?Usage: $0 <branch-name> [dir]}"
NORMALIZED="${BRANCH//\//-}"
REPO_PARENT="$(dirname "$PWD")"

if [ -n "${2:-}" ]; then
  DEST="$2"
else
  DEST="../$(basename "$PWD")-${NORMALIZED}"
fi
DEST="$(cd "$REPO_PARENT" && python3 -c "import os,sys; print(os.path.abspath(sys.argv[1]))" "$DEST")"

echo "Creating worktree at ${DEST} for branch ${BRANCH}..."
git worktree add "${DEST}" "${BRANCH}"

# Copy .env if it exists
if [ -f .env ]; then
  echo "Copying .env..."
  cp .env "${DEST}/.env"
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
