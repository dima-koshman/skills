#!/bin/bash
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <branch-name>" >&2
  exit 1
fi

BRANCH="$1"
SAFE_BRANCH="${BRANCH//\//-}"
REPO_NAME=$(basename "$PWD")
DESTINATION="../${REPO_NAME}-${SAFE_BRANCH}"

echo "Creating worktree at ${DESTINATION} for branch ${BRANCH}..."
git worktree add "${DESTINATION}" "${BRANCH}"

# Copy .env if it exists
if [ -f .env ]; then
  echo "Copying .env..."
  cp .env "${DESTINATION}/.env"
fi

# Run setup commands in destination
(
  cd "${DESTINATION}"
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
  ide "${DESTINATION}"
else
  echo "Warning: 'ide' command not found."
fi
