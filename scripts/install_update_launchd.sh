#!/usr/bin/env bash
# Install a launchd LaunchAgent that runs the daily package-manager update
#
#     brew update && brew upgrade --yes && npm update -g
#
# once a day. launchd is used instead of cron because macOS cron silently
# drops any job whose time passes while the Mac is asleep, whereas launchd
# runs a missed StartCalendarInterval job the moment the machine next wakes.
# So on a laptop that sleeps through midnight, this still runs — at wake, not
# at 00:00. It does NOT wake the Mac; for true at-midnight execution add a
# `sudo pmset repeat wake MTWRFSU 23:58:00` (commented at the bottom).
#
# A user LaunchAgent (~/Library/LaunchAgents), not a system LaunchDaemon: the
# job needs the user's Homebrew and npm, and must never run as root.
#
# Usage:
#   install_update_launchd.sh              install/refresh the agent
#   install_update_launchd.sh --uninstall  remove it
#
# Idempotent: reinstalling replaces the plist and reloads.
set -euo pipefail

LABEL="local.dima.brew-npm-update"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
LOG="$HOME/Library/Logs/brew-npm-update.log"
HOUR=0
MINUTE=0

DOMAIN="gui/$(id -u)"

uninstall() {
    # bootout is best-effort: it errors if the label was never loaded.
    launchctl bootout "${DOMAIN}/${LABEL}" 2>/dev/null || true
    if [ -f "${PLIST}" ]; then
        rm -f "${PLIST}"
        echo "Removed ${PLIST} and unloaded ${LABEL}."
    else
        echo "Nothing to remove: ${PLIST} does not exist."
    fi
}

if [ "${1:-}" = "--uninstall" ]; then
    uninstall
    exit 0
fi

if [ "${1:-}" != "" ]; then
    echo "Unknown argument: $1 (use --uninstall or no argument)." >&2
    exit 2
fi

# brew must exist at install time: we bake its bin into the job's PATH because
# launchd starts jobs with a bare PATH that omits /opt/homebrew and any npm.
if ! command -v brew >/dev/null 2>&1; then
    echo "Refusing: brew is not on PATH; nothing to schedule." >&2
    exit 1
fi
BREW_PREFIX="$(brew --prefix)"
JOB_PATH="${BREW_PREFIX}/bin:${BREW_PREFIX}/sbin:/usr/bin:/bin:/usr/sbin:/sbin"

mkdir -p "$(dirname "${PLIST}")" "$(dirname "${LOG}")"

# StartCalendarInterval with only Hour+Minute set fires daily at that time.
# StandardOut/ErrorPath capture output so a background failure is visible in
# the log rather than lost. RunAtLoad is omitted so installing (or logging in)
# does not itself trigger a run.
cat > "${PLIST}" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>-lc</string>
        <string>brew update &amp;&amp; brew upgrade --yes &amp;&amp; npm update -g</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>${JOB_PATH}</string>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>${HOUR}</integer>
        <key>Minute</key>
        <integer>${MINUTE}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${LOG}</string>
    <key>StandardErrorPath</key>
    <string>${LOG}</string>
</dict>
</plist>
PLIST_EOF

# Reload cleanly: bootout any previous instance (ignore "not loaded"), then
# bootstrap the freshly written plist. This is the modern replacement for the
# deprecated `launchctl load -w`.
launchctl bootout "${DOMAIN}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "${DOMAIN}" "${PLIST}"

printf 'Installed %s\n' "${LABEL}"
printf '  runs daily at %02d:%02d (or at next wake if asleep then)\n' "${HOUR}" "${MINUTE}"
printf '  command: brew update && brew upgrade --yes && npm update -g\n'
printf '  logs to: %s\n' "${LOG}"
printf '  run now to test: launchctl kickstart -k %s/%s\n' "${DOMAIN}" "${LABEL}"
printf '  remove with:     %s --uninstall\n' "$0"

# For true at-midnight execution even while the Mac sleeps, schedule a wake a
# couple of minutes before the job (needs sudo, persists across reboots):
#   sudo pmset repeat wake MTWRFSU 23:58:00
