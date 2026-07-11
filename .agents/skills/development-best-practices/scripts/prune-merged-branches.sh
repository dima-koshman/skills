#!/usr/bin/env bash
# Delete local branches whose upstream was merged and deleted on the remote.
#
# After a PR/MR is squash-merged and its branch deleted on the host, `git fetch
# --prune` drops the remote-tracking ref, leaving the local branch with a "[gone]"
# upstream. `git branch --merged` does NOT catch squash-merges (no ancestry link),
# so we key off the "[gone]" marker instead, which is the reliable signal.
#
# Host-agnostic: relies only on git plumbing (fetch --prune + the "[gone]" marker
# that git itself sets). No `gh`/`glab`/API calls, so it works with GitHub, GitLab,
# Bitbucket, or any remote unchanged.
#
# Usage:
#   prune-merged-branches.sh            # delete gone branches
#   prune-merged-branches.sh --dry-run  # just list what would be deleted
set -euo pipefail

dry_run=0
[ "${1:-}" = "--dry-run" ] && dry_run=1

echo ">> git fetch --prune"
git fetch --prune

# Never delete the branch we're on.
current="$(git branch --show-current)"

gone="$(git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads/ \
  | awk '$2=="[gone]" {print $1}' \
  | grep -vx "$current" || true)"

if [ -z "$gone" ]; then
  echo "Nothing to prune — no branches with a gone upstream."
  exit 0
fi

echo ">> branches whose upstream is gone:"
echo "$gone" | sed 's/^/   /'

if [ "$dry_run" = "1" ]; then
  echo "(dry run — nothing deleted)"
  exit 0
fi

echo "$gone" | xargs -n1 git branch -D
git worktree prune -v
