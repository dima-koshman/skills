#!/usr/bin/env bash

printf '%-8s %s\n' 'PID' 'WORKING DIRECTORY'

ps -axo pid=,comm= |
    while read -r pid command; do
        [ "${command##*/}" = opencode ] || continue

        output=$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null || true)
        cwd='<unavailable>'
        if [[ "$output" == *$'\n'n* ]]; then
            cwd=${output##*$'\n'n}
        fi

        printf '%-8s %s\n' "$pid" "$cwd"
    done
