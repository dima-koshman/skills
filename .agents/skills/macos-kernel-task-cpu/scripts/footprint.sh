#!/bin/bash
# Total memory footprint grouped by process-name pattern.
#
# Uses top's MEM column rather than ps RSS: under memory pressure RSS excludes
# compressed and swapped-out pages, badly understating the real consumers.
#
# Caveat: Electron helpers share memory, so group totals double-count. Read this as a
# ranking of consumers, not as an absolute byte count.
#
# Usage: ./footprint.sh Devin OrbStack claude
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: $(basename "$0") PATTERN [PATTERN ...]" >&2
  exit 64
fi

top -l 1 -n 300 -o mem -stats command,mem 2>/dev/null |
  awk -v pats="$*" '
    BEGIN { n = split(pats, p, " ") }
    {
      m = $NF
      if (m !~ /^[0-9]/) next
      v = m + 0
      if (m ~ /G/) v *= 1024
      else if (m ~ /K/) v /= 1024
      else if (m !~ /M/) next
      for (i = 1; i <= n; i++) if (index($0, p[i])) { tot[p[i]] += v; next }
      tot["(unmatched)"] += v
    }
    END { for (k in tot) printf "%-14s %8.2f GB\n", k, tot[k] / 1024 }' |
  sort -k2 -rn
