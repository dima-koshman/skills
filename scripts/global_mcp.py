#!/usr/bin/env python3
"""Install the MCP servers of a Claude-style .mcp.json into every harness's GLOBAL MCP config.

No harness reads another's MCP file, and each has its own schema, so the file is rendered per harness with the
${VAR} references resolved:

    ~/.claude.json                     Claude Code   top-level "mcpServers" (user scope)
    ~/.codex/config.toml               Codex         [mcp_servers.<name>] tables in a block marked with the source
    ~/.config/opencode/opencode.json   OpenCode v2   "mcp.servers"; the file holds nothing else (opencode merges it
                                                     with the hand-kept opencode.jsonc, whose servers are never touched)
    ~/.gemini/config/mcp_config.json   Antigravity   IDE and agy CLI ("serverUrl")

Several projects can each sync their own .mcp.json. --mode merge (default) adds or updates the file's servers and
leaves every other server alone, so a server deleted from the file stays installed. --mode override makes each
harness's server set exactly the file: it also drops servers the file doesn't define, including other projects'
and ones this script never installed (e.g. openwiki).

Values come only from --env-file (a dotenv file parsed with `direnv dotenv json`) and --var NAME=VALUE. The process
environment is ignored, so a stale token direnv exported into the shell is never installed. Remote specs use
url/headers; local stdio specs use command/args. Other keys (e.g. "type", "description", "auth") are not written.
Written files are 0600: they may hold tokens. Re-run `sync` after rotating a token or editing the file.

Only harnesses whose config dir exists are touched.

Usage: global_mcp.py {sync,status} [--mcp-json PATH] [--env-file PATH] [--var NAME=VALUE ...] [--mode {merge,override}]
       global_mcp.py remove [--mcp-json PATH]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

CLAUDE = Path.home() / ".claude.json"
CODEX = Path.home() / ".codex/config.toml"
OPENCODE = Path.home() / ".config/opencode/opencode.json"
ANTIGRAVITY = Path.home() / ".gemini/config/mcp_config.json"

# Codex block markers name the source file (a path without spaces).
CODEX_MARKER = re.compile(r"# (BEGIN|END) global_mcp\.py (\S+)")


def load_env(env_file: Path | None) -> dict[str, str]:
    if env_file is None:
        return {}
    if not env_file.is_file():
        sys.exit(f"env file not found: {env_file}")
    out = subprocess.run(
        ["direnv", "dotenv", "json", str(env_file)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(out.stdout or "{}")


def load_servers(mcp_json: Path, env: dict[str, str]) -> dict[str, dict]:
    """The file's servers with every ${VAR} resolved; exits naming the missing variables (never their values)."""
    raw = mcp_json.read_text()
    missing = sorted(
        {name for name in re.findall(r"\$\{(\w+)\}", raw) if not env.get(name)}
    )
    if missing:
        sys.exit(
            f"missing variables (set them in --env-file or with --var): {', '.join(missing)}"
        )
    resolved = re.sub(r"\$\{(\w+)\}", lambda m: json.dumps(env[m.group(1)])[1:-1], raw)
    return json.loads(resolved)["mcpServers"]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def write_private(path: Path, text: str) -> None:
    """Atomically replace the file the path resolves to (symlinks stay symlinks), mode 0600."""
    path = path.resolve()
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def json_text(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def compare(current: dict, desired: dict, exact: bool) -> str:
    """absent / outdated / current; with exact, servers outside `desired` also make it outdated."""
    present = [name for name in desired if name in current]
    if not present:
        return "absent"
    if exact and set(current) != set(desired):
        return "outdated"
    return (
        "current"
        if all(current.get(name) == spec for name, spec in desired.items())
        else "outdated"
    )


def state(target, servers, override: bool) -> str:
    return compare(target.current(), target.desired(servers), exact=override)


class JsonUpsert:
    """A JSON file whose "mcpServers" map we share with other entries: merge upserts our names, override replaces
    the map."""

    def __init__(self, path: Path, harness_dir: Path, convert):
        self.path, self.harness_dir, self.convert = path, harness_dir, convert

    def installed(self) -> bool:
        return self.harness_dir.exists()

    def current(self) -> dict:
        return read_json(self.path).get("mcpServers", {})

    def desired(self, servers):
        return {name: self.convert(spec) for name, spec in servers.items()}

    def sync(self, servers, override: bool) -> None:
        data = read_json(self.path)
        if override:
            data["mcpServers"] = self.desired(servers)
        else:
            data.setdefault("mcpServers", {}).update(self.desired(servers))
        write_private(self.path, json_text(data))

    def remove(self, names) -> None:
        if not self.path.exists():
            return
        data = read_json(self.path)
        for name in names:
            data.get("mcpServers", {}).pop(name, None)
        write_private(self.path, json_text(data))


def claude_server(spec: dict) -> dict:
    if "command" in spec:
        return {"command": spec["command"]} | (
            {"args": spec["args"]} if "args" in spec else {}
        )

    return {"type": "http", "url": spec["url"]} | (
        {"headers": spec["headers"]} if "headers" in spec else {}
    )


def antigravity_server(spec: dict) -> dict:
    if "command" in spec:
        return {"command": spec["command"]} | (
            {"args": spec["args"]} if "args" in spec else {}
        )

    return {"serverUrl": spec["url"]} | (
        {"headers": spec["headers"]} if "headers" in spec else {}
    )


def mcp_server_name(header: str) -> str | None:
    """The server a TOML table header like [mcp_servers."jira"] or [mcp_servers.jira.env] belongs to."""
    servers = tomllib.loads(header).get("mcp_servers")
    return next(iter(servers)) if isinstance(servers, dict) and servers else None


def drop_mcp_tables(text: str, drop) -> str:
    """Remove the [mcp_servers.<name>] tables (and subtables) whose name `drop` selects, with the comment lines
    hugging them (e.g. openwiki's START/END markers); everything else is kept as written."""
    chunks = [[]]
    for line in text.splitlines(keepends=True):
        if re.match(r"\s*\[\[?[^\[\]]+\]\]?\s*(#.*)?$", line):
            chunks.append([])
        chunks[-1].append(line)
    kept = [chunks[0]]
    for chunk in chunks[1:]:
        name = mcp_server_name(chunk[0])
        if name is None or not drop(name):
            kept.append(chunk)
            continue
        while kept[-1] and kept[-1][-1].lstrip().startswith("#"):
            kept[-1].pop()
        body = [
            i
            for i, line in enumerate(chunk)
            if line.strip() and not line.lstrip().startswith("#")
        ]
        end = body[-1] + 1
        while end < len(chunk) and chunk[end].lstrip().startswith("#"):
            end += 1
        kept.append(chunk[end:])
    return "".join(line for chunk in kept for line in chunk)


class Codex:
    """config.toml: a source's [mcp_servers.*] tables are written at the end of the file between BEGIN/END comments
    naming the source. Codex inserts tables it adds later (e.g. [hooks.state.*]) before the trailing END comment, so
    the markers are only informational: tables are found by their headers, and anything else inside them is kept."""

    path = CODEX

    def __init__(self, source: str):
        self.source = source

    def installed(self) -> bool:
        return self.path.parent.exists()

    def current(self) -> dict:
        return (
            tomllib.loads(self.path.read_text()).get("mcp_servers", {})
            if self.path.exists()
            else {}
        )

    def rest(self, drop, all_markers: bool = False) -> str:
        """The config without this source's marker lines (every source's with all_markers) and without the
        [mcp_servers.<name>] tables `drop` selects."""

        def marker(line: str) -> bool:
            match = CODEX_MARKER.match(line)
            return bool(match) and (all_markers or match.group(2) == self.source)

        text = self.path.read_text() if self.path.exists() else ""
        text = "".join(
            line for line in text.splitlines(keepends=True) if not marker(line)
        )
        text = re.sub(r"\n{3,}", "\n\n", drop_mcp_tables(text, drop))
        return text.rstrip("\n") + "\n" if text.strip() else ""

    def block(self, servers) -> str:
        lines = [
            f"# BEGIN global_mcp.py {self.source} (managed by ~/Projects/dima/scripts/global_mcp.py: edit that file)"
        ]
        for name, spec in servers.items():
            lines += ["", f"[mcp_servers.{json.dumps(name)}]"]
            if "command" in spec:
                lines.append(f"command = {json.dumps(spec['command'])}")
                if "args" in spec:
                    lines.append(f"args = {json.dumps(spec['args'])}")
            else:
                lines.append(f"url = {json.dumps(spec['url'])}")
                if "headers" in spec:
                    headers = ", ".join(
                        f"{json.dumps(k)} = {json.dumps(v)}"
                        for k, v in spec["headers"].items()
                    )
                    lines.append(f"http_headers = {{ {headers} }}")

        return "\n".join(lines + [f"# END global_mcp.py {self.source}"]) + "\n"

    def desired(self, servers):
        return tomllib.loads(self.block(servers))["mcp_servers"]

    def sync(self, servers, override: bool) -> None:
        rest = self.rest(lambda name: override or name in servers, all_markers=override)
        text = rest + ("\n" if rest else "") + self.block(servers)
        tomllib.loads(text)  # refuse to write a config Codex can't parse
        write_private(self.path, text)

    def remove(self, names) -> None:
        if self.path.exists():
            write_private(self.path, self.rest(lambda name: name in names))


class OpenCode:
    """opencode.json holds only our "mcp" key; opencode deep-merges it with the hand-kept opencode.jsonc. Written in the
    v2 shape (`mcp.servers`; v2 reads v1's flat `mcp` map too, but normalizes it to this)."""

    path = OPENCODE

    def installed(self) -> bool:
        return self.path.parent.exists()

    def desired(self, servers):
        desired = {}
        for name, spec in servers.items():
            if "command" in spec:
                desired[name] = {
                    "type": "local",
                    "command": [spec["command"], *spec.get("args", [])],
                }
            else:
                desired[name] = {"type": "remote", "url": spec["url"]} | (
                    {"headers": spec["headers"]} if "headers" in spec else {}
                )

        return desired

    def check_owned(self) -> dict:
        data = read_json(self.path)
        if set(data) - {"$schema", "mcp"}:
            sys.exit(
                f"{self.path} has keys this script doesn't own ({', '.join(sorted(set(data) - {'$schema', 'mcp'}))}); move them to opencode.jsonc"
            )
        return data

    def current(self) -> dict:
        mcp = self.check_owned().get("mcp", {})
        return dict(mcp.get("servers", {}) if "servers" in mcp else mcp)

    def write(self, servers: dict) -> None:
        if servers:
            write_private(self.path, json_text({"mcp": {"servers": servers}}))
        else:
            self.path.unlink(missing_ok=True)

    def sync(self, servers, override: bool) -> None:
        self.write(
            self.desired(servers)
            if override
            else self.current() | self.desired(servers)
        )

    def remove(self, names) -> None:
        self.write(
            {name: spec for name, spec in self.current().items() if name not in names}
        )


def targets(source: str) -> list:
    return [
        JsonUpsert(CLAUDE, CLAUDE, claude_server),
        Codex(source),
        OpenCode(),
        JsonUpsert(ANTIGRAVITY, ANTIGRAVITY.parent, antigravity_server),
    ]


def display(path: Path) -> str:
    """The path with the home directory as ~, so markers don't depend on who reads them."""
    home = str(Path.home())
    return (
        "~" + str(path)[len(home) :]
        if str(path).startswith(home + os.sep)
        else str(path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install the MCP servers of a .mcp.json into the global harness configs."
    )
    parser.add_argument("command", choices=["sync", "status", "remove"])
    parser.add_argument(
        "--mcp-json",
        default=".mcp.json",
        help="Claude-style file with an mcpServers map (default ./.mcp.json)",
    )
    parser.add_argument(
        "--env-file",
        help="dotenv file with the values for its ${VAR} references (sync, status)",
    )
    parser.add_argument(
        "--var",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="a ${VAR} value; overrides --env-file (repeatable)",
    )
    parser.add_argument(
        "--mode",
        choices=["merge", "override"],
        default="merge",
        help="merge: add/update the file's servers, keep the rest; override: also drop servers not in the file",
    )
    args = parser.parse_args()
    cmd = args.command
    override = args.mode == "override"
    mcp_json = Path(args.mcp_json).expanduser().resolve()
    if not mcp_json.is_file():
        sys.exit(f"MCP file not found: {mcp_json}")
    names = list(json.loads(mcp_json.read_text())["mcpServers"])
    servers = None
    if cmd != "remove":
        env_file = Path(args.env_file).expanduser() if args.env_file else None
        variables = dict(var.split("=", 1) for var in args.var)
        servers = load_servers(mcp_json, load_env(env_file) | variables)
        print(
            f"MCP file: {mcp_json}\nenv file: {env_file or '-'}\nvariables: {', '.join(variables) or '-'}\n"
            f"mode: {args.mode}\nservers: {', '.join(names)}"
        )
    for target in targets(display(mcp_json)):
        path = target.path
        if not target.installed():
            print(f"{'no harness':<10} {path}")
            continue
        if cmd == "remove":
            target.remove(names)
            print(f"{'removed':<10} {path}")
            continue
        extra = ", ".join(sorted(set(target.current()) - set(names)))
        before = state(target, servers, override)
        if cmd == "status":
            print(
                f"{before:<10} {path}" + (f"  (not in file: {extra})" if extra else "")
            )
        elif before == "current":
            print(
                f"{'ok':<10} {path}"
                + (f"  (kept, not in file: {extra})" if extra else "")
            )
        else:
            target.sync(servers, override)
            note = (
                f"  ({'dropped' if override else 'kept, not in file'}: {extra})"
                if extra
                else ""
            )
            print(f"{'added' if before == 'absent' else 'updated':<10} {path}{note}")


if __name__ == "__main__":
    main()
