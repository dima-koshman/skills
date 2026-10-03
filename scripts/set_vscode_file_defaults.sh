#!/usr/bin/env bash
# Make VS Code the default app (Finder double-click, `open <file>`) for
# coding-related file extensions. Requires duti (`brew install duti`).
#
# Deliberately left out, so they keep their usual handler:
#   .html/.htm  browser — double-clicking one usually means "preview it"
#   .csv        spreadsheet app
#   .txt/.log   TextEdit/Console — plain text and logs, not code
#
# Two mechanisms, because Launch Services resolves extensions two ways:
#
#   1. An extension some app maps to a real UTI (.py -> public.python-script)
#      is set with `duti -s`, which assigns a handler to that UTI.
#   2. An extension apps only list by name (.go, .rs, .tf ...) has a dynamic
#      UTI, and Launch Services rejects handlers for those (duti: error -50).
#      Finder's "Change All..." handles these by storing an LSHandlers entry
#      keyed on the extension itself; this script writes the same entry, then
#      restarts lsd so it is picked up. Without it, whichever editor declares
#      the extension with the highest rank wins (e.g. Antigravity IDE).
#
# Every extension is read back with `duti -x` at the end, and the run fails if
# any does not resolve to VS Code. Idempotent: re-running replaces this
# script's own extension entries instead of appending duplicates.
#
# Usage: set_vscode_file_defaults.sh
set -euo pipefail

BUNDLE_ID="com.microsoft.VSCode"
LS_DOMAIN="com.apple.LaunchServices/com.apple.launchservices.secure"

EXTENSIONS=(
    # Python
    py pyi pyw ipynb
    # JavaScript / TypeScript / web
    js mjs cjs jsx ts mts cts tsx vue svelte css scss sass less svg
    # Data and config
    json jsonc json5 jsonl yaml yml toml ini cfg conf env properties xml
    lock editorconfig gitignore gitattributes dockerfile
    # Shell
    sh bash zsh fish ps1 bat cmd
    # Systems and JVM languages
    c h cc cpp cxx hpp m mm go rs java kt kts scala swift dart gradle
    # Scripting languages
    rb php lua pl r
    # Query, schema and infra
    sql graphql gql proto tf tfvars hcl cmake mk
    # Docs and diffs
    md markdown mdx rst patch diff
)

if ! command -v duti >/dev/null 2>&1; then
    echo "duti not found; install it with: brew install duti" >&2
    exit 1
fi

if ! osascript -e "id of app id \"${BUNDLE_ID}\"" >/dev/null 2>&1; then
    echo "No app with bundle id ${BUNDLE_ID} is installed." >&2
    exit 1
fi

# Line 3 of `duti -x` is the handler's bundle id.
handler() { duti -x "$1" 2>/dev/null | sed -n 3p || true; }

# Indexed arrays only, and every "${arr[@]}" guarded by a length check: macOS's
# stock bash 3.2 has no associative arrays and treats an empty array as unset
# under -u.
before=()
dynamic=()
failed=()

for ext in "${EXTENSIONS[@]}"; do
    prev=$(duti -x "${ext}" 2>/dev/null | head -1 || true)
    before+=("${prev:-<none>}")
    if err=$(duti -s "${BUNDLE_ID}" ".${ext}" all 2>&1); then
        :
    elif [[ ${err} == *"dyn."* ]]; then
        dynamic+=("${ext}")
    else
        echo ".${ext}: ${err}" >&2
        failed+=("${ext}")
    fi
done

if [ "${#dynamic[@]}" -gt 0 ]; then
    # Round-trip through `defaults` rather than editing the plist file, so
    # cfprefsd's cached copy cannot overwrite the change.
    defaults export "${LS_DOMAIN}" - | /usr/bin/python3 -c '
import plistlib, sys
bundle_id, exts = sys.argv[1].lower(), sys.argv[2:]
prefs = plistlib.loads(sys.stdin.buffer.read())
tag_class = "public.filename-extension"
handlers = [
    h for h in prefs.get("LSHandlers", [])
    if not (h.get("LSHandlerContentTagClass") == tag_class
            and h.get("LSHandlerContentTag") in exts)
]
handlers += [
    {
        "LSHandlerContentTag": ext,
        "LSHandlerContentTagClass": tag_class,
        "LSHandlerRoleAll": bundle_id,
        "LSHandlerPreferredVersions": {"LSHandlerRoleAll": "-"},
    }
    for ext in exts
]
prefs["LSHandlers"] = handlers
plistlib.dump(prefs, sys.stdout.buffer, fmt=plistlib.FMT_XML)
' "${BUNDLE_ID}" "${dynamic[@]}" | defaults import "${LS_DOMAIN}" -
    # lsd only reads these entries at startup; launchd respawns it on demand.
    killall lsd 2>/dev/null || true
fi

# Launch Services applies changes asynchronously, so a read-back can show the
# old handler for several seconds. Verify after the whole batch, with retries.
for ((i = 0; i < ${#EXTENSIONS[@]}; i++)); do
    ext=${EXTENSIONS[i]}
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        [ "$(handler "${ext}")" = "${BUNDLE_ID}" ] && break
        sleep 1
    done
    now=$(handler "${ext}")
    if [ "${now}" = "${BUNDLE_ID}" ]; then
        printf '%-14s %s -> Visual Studio Code\n' ".${ext}" "${before[i]}"
    else
        printf '%-14s FAILED (now: %s)\n' ".${ext}" "${now:-<none>}" >&2
        failed+=("${ext}")
    fi
done

if [ "${#failed[@]}" -gt 0 ]; then
    echo "Could not set ${#failed[@]} extension(s): ${failed[*]}" >&2
    exit 1
fi
echo "Done: all ${#EXTENSIONS[@]} extensions open in VS Code."
