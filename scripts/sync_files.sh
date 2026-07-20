#!/bin/bash
# Copy source files over destination files, showing a diff first.
#
# Usage: sync_files.sh [--confirm=<value>] <src> <dest> [<src> <dest> ...]
#
# Without --confirm=yes this is a dry run: it only prints the diff of what
# would change. Pass --confirm=yes to actually overwrite the destinations.
set -euo pipefail

CONFIRM=""
if [[ "${1:-}" == --confirm=* ]]; then
	CONFIRM="${1#--confirm=}"
	shift
elif [ "${1:-}" == "--yes" ]; then
	CONFIRM="yes"
	shift
fi

if [ "$#" -lt 2 ] || [ $(("$#" % 2)) -ne 0 ]; then
	echo "Usage: $0 [--confirm=<value>] <src> <dest> [<src> <dest> ...]" >&2
	exit 2
fi

APPLY=false
if [ "$(printf '%s' "$CONFIRM" | tr '[:upper:]' '[:lower:]')" == "yes" ]; then
	APPLY=true
fi

CHANGED=0
PAIRS=()
while [ "$#" -gt 0 ]; do
	SRC="$1"
	DEST="$2"
	shift 2

	if [ ! -f "$SRC" ]; then
		echo "Error: source file not found: $SRC" >&2
		exit 1
	fi

	if [ -f "$DEST" ] && cmp -s "$SRC" "$DEST"; then
		echo "unchanged: $DEST"
		continue
	fi

	CHANGED=$((CHANGED + 1))
	PAIRS+=("$SRC" "$DEST")

	if [ -f "$DEST" ]; then
		echo "=== modified: $DEST ==="
		diff -u --label "$DEST (current)" --label "$SRC (new)" "$DEST" "$SRC" || true
	else
		echo "=== created: $DEST ==="
	fi
	echo
done

if [ "$CHANGED" -eq 0 ]; then
	echo "Nothing to do; all destinations are already up to date."
	exit 0
fi

if [ "$APPLY" != true ]; then
	echo "Dry run: ${CHANGED} file(s) would be overwritten. Nothing was written."
	echo "Re-run with --confirm=yes to apply."
	exit 0
fi

set -- "${PAIRS[@]}"
while [ "$#" -gt 0 ]; do
	SRC="$1"
	DEST="$2"
	shift 2
	mkdir -p "$(dirname "$DEST")"
	cp -f "$SRC" "$DEST"
	echo "wrote: $DEST"
done
echo "Applied ${CHANGED} file(s)."
