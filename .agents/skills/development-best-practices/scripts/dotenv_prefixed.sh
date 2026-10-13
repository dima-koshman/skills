# direnv helper: symlink into ~/.config/direnv/lib/ so every .envrc can call it — direnv
# sources ~/.config/direnv/lib/*.sh before each .envrc (see the development-best-practices
# skill, "Load several environments side by side").

# dotenv_prefixed PREFIX FILE: load FILE's variables as PREFIX_<NAME>, without exporting
# the unprefixed names. Lets several env files that share variable names (e.g. one per
# environment under ~/.config/direnv/env/) load side by side:
#
#   dotenv_prefixed PROD ~/.config/direnv/env/openwebui.env
#   dotenv_prefixed DEV  ~/.config/direnv/env/openwebui-dev.env
#
# direnv parses the file (same rules as dotenv); a subshell keeps the plain names local,
# and %q re-quotes each value for the eval. A missing file is skipped, like
# dotenv_if_exists, and edits to the file trigger a reload via watch_file.
dotenv_prefixed() {
  local prefix=$1 file=$2
  [[ -f "$file" ]] || return 0
  watch_file "$file"
  eval "$(
    eval "$("${direnv:-direnv}" dotenv bash "$file")"
    sed -n -E 's/^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)=.*/\2/p' "$file" |
      while IFS= read -r name; do
        printf 'export %s_%s=%q\n' "$prefix" "$name" "${!name}"
      done
  )"
}
