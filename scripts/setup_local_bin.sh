#!/usr/bin/env bash
# Make this repo's VSCode tasks work on a fresh clone, by symlinking into
# ~/.local/bin the two things those tasks assume already exist:
#
#   1. the scripts they invoke by bare name
#   2. `ide`, the editor launcher create_worktree.sh opens the new worktree with
#
# Symlinks rather than copies, so editing a script in the clone takes effect
# everywhere with no re-run. The tradeoff is that links dangle if the clone
# moves — re-run this to repoint them.
#
# `ide` cannot be a shell alias: aliases live only in the interactive shell that
# defines them, so a script running under bash never sees one.
#
# Usage: setup_local_bin.sh [target-dir]
#
# Invoke by path, not by bare name — this is what puts the bare names on PATH.
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$HOME/.local/bin}"

# Deliberately curated, not a glob over scripts/. These are the cross-project
# tools tasks call by bare name; repo-internal tooling like sync_files.sh is
# invoked by explicit path and has no business on PATH.
SCRIPTS=(
    create_worktree.sh
    get_venv_packages_size.py
    link_claude_md.sh
    link_claude_skills.sh
    list_opencode_processes.sh
)

# First hit wins. Add bundles here as needed.
IDE_CANDIDATES=(
    "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    "/Applications/Cursor.app/Contents/Resources/app/bin/cursor"
    "/Applications/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide"
    "/Applications/Windsurf.app/Contents/Resources/app/bin/windsurf"
    "/Applications/Devin.app/Contents/Resources/app/bin/devin-desktop"
)

mkdir -p "${TARGET_DIR}"

# Replace only our own symlinks; a real file at the destination belongs to
# something else and is never silently clobbered.
link() {
    local src="$1" dest="$2" label="$3"
    if [ -e "${dest}" ] && [ ! -L "${dest}" ]; then
        echo "Skipping ${label}: ${dest} exists and is not a symlink." >&2
        return 1
    fi
    ln -sfn "${src}" "${dest}"
    echo "Linked ${label} -> ${src}"
}

failed=0

for name in "${SCRIPTS[@]}"; do
    src="${SCRIPTS_DIR}/${name}"
    if [ ! -x "${src}" ]; then
        echo "Skipping ${name}: ${src} is missing or not executable." >&2
        failed=$((failed + 1))
        continue
    fi
    link "${src}" "${TARGET_DIR}/${name}" "${name}" || failed=$((failed + 1))
done

LAUNCHER=""
for candidate in "${IDE_CANDIDATES[@]}"; do
    if [ -x "${candidate}" ]; then
        LAUNCHER="${candidate}"
        break
    fi
done

# A missing IDE does not fail the run: the scripts above are still linked, and
# only create_worktree.sh's final step needs `ide`.
if [ -z "${LAUNCHER}" ]; then
    echo "Warning: found no editor launcher; 'ide' not linked. Tried:" >&2
    printf '  %s\n' "${IDE_CANDIDATES[@]}" >&2
    failed=$((failed + 1))
else
    link "${LAUNCHER}" "${TARGET_DIR}/ide" "ide" || failed=$((failed + 1))
fi

case ":${PATH}:" in
*":${TARGET_DIR}:"*) ;;
*)
    echo "Warning: ${TARGET_DIR} is not on PATH; these links are unreachable." >&2
    echo "Add to your shell rc: export PATH=\"${TARGET_DIR}:\$PATH\"" >&2
    failed=$((failed + 1))
    ;;
esac

if [ "${failed}" -gt 0 ]; then
    echo "Finished with ${failed} problem(s); see warnings above." >&2
    exit 1
fi
echo "All tools linked into ${TARGET_DIR}."
