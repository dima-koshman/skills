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
SKIPPED=0
PAIRS=()
while [ "$#" -gt 0 ]; do
	SRC="$1"
	DEST="$2"
	shift 2

	# A missing source is informational, not fatal: pairs are supplied by static VS Code
	# task definitions, so a file deleted from the repo (or a stale synced copy of
	# tasks.json still naming it) would otherwise abort every remaining pair too.
	if [ ! -f "$SRC" ]; then
		echo "skipped: source file not found: $SRC"
		SKIPPED=$((SKIPPED + 1))
		continue
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

SKIPPED_NOTE=""
if [ "$SKIPPED" -gt 0 ]; then
	SKIPPED_NOTE=" (${SKIPPED} skipped: source missing)"
fi

if [ "$CHANGED" -eq 0 ]; then
	echo "Nothing to do; all destinations are already up to date.${SKIPPED_NOTE}"
	exit 0
fi

if [ "$APPLY" != true ]; then
	echo "Dry run: ${CHANGED} file(s) would be overwritten.${SKIPPED_NOTE} Nothing was written."
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
echo "Applied ${CHANGED} file(s).${SKIPPED_NOTE}"
