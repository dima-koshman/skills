#!/bin/bash
# Sample the macOS paging rate over N seconds (default 10).
#
# vm_stat counters are cumulative since boot, so a single reading proves nothing about
# what is happening now. Sustained tens of MB/s in both directions means the VM system
# is thrashing, which is what shows up as kernel_task CPU.
set -euo pipefail

secs="${1:-10}"

snap() {
  vm_stat | tr -d '.' | awk '
    /Swapins/  {a=$2}
    /Swapouts/ {b=$2}
    END        {print a, b}'
}

read -r si1 so1 <<< "$(snap)"
sleep "$secs"
read -r si2 so2 <<< "$(snap)"

printf 'Over %ss:\n' "$secs"
printf '  swapins : %8d pages  ~%d MB/s\n' "$((si2 - si1))" "$(((si2 - si1) * 4096 / secs / 1048576))"
printf '  swapouts: %8d pages  ~%d MB/s\n' "$((so2 - so1))" "$(((so2 - so1) * 4096 / secs / 1048576))"
