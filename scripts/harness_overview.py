#!/usr/bin/env python3
"""Build a browsable HTML overview of what every coding-agent harness on this machine can do and how it is told to
behave: MCP servers (connection status, tools, token cost), skills, plugins, config files, instruction text, tool
search and subscription usage.

    Claude Code  `claude mcp list` (health-checked), `claude plugin list --json`, `claude -p /usage`, skills and
                 CLAUDE.md files on disk, ENABLE_TOOL_SEARCH from settings/env
    Codex        `codex mcp list --json`, `codex plugin list --json`, `codex features list`, `codex debug
                 prompt-input` (the exact model-visible prompt), rate limits from `codex app-server` (account/rateLimits/read)
    OpenCode     v2 server API (`opencode api GET /api/{config,agent,mcp,skill,plugin}`), `opencode stats`, AGENTS.md
    Antigravity  ~/.gemini/config/mcp_config.json, its skill roots, `agy plugin list`, `agy -p /quota`, GEMINI.md

Scope: `global` (default) runs every harness from an empty directory outside any project, so the page shows only
global configuration; `project` runs them from --project, adding that project's MCP servers, skills and instructions.

Every MCP server whose config this script can read is probed with `initialize` + `tools/list` (once per distinct
config, shared across harnesses, after the harnesses' own health checks) for its tools. Token counts use tiktoken's
o200k_base when it is importable (the VS Code task runs this with `uv run --with tiktoken`), else chars/4; they are
estimates for every harness. explorer.html browses servers' tools, skills, plugins and config files in one tree.

Secrets never reach the page: headers and env are not recorded, every value from ~/.config/direnv/env/**/*.env is
redacted, token-like strings are masked, and the output is deleted if a known value still slips through.

Output (default <repo>/dev/harness-overview/, git-ignored): index.html, explorer.html, style.css, data/*.js.

Usage: harness_overview.py [--scope global|project] [--project DIR] [--out DIR] [--no-usage] [--open]
"""

import argparse
import hashlib
import json
import os
import re
import selectors
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True  # no scripts/__pycache__ for the sibling import below
import llm_capture  # noqa: E402  # sibling import after disabling bytecode writes

HOME = Path.home()
REPO = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "harness_overview_assets"
GLOBAL_CWD = (
    HOME / ".cache/harness-overview/global"
)  # empty, outside any project: what a harness sees with no project
ENV_DIR = HOME / ".config/direnv/env"
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
SECRET_PATTERNS = [
    (re.compile(r"\b(Bearer|Basic|Token)\s+[^\s\"',]+", re.I), r"\1 ***"),
    (
        re.compile(
            r"\b([\w-]*(?:token|secret|password|passwd|api[_-]?key)[\w-]*)(\"?\s*[=:]\s*\"?)[^\s\"',&]+",
            re.I,
        ),
        r"\1\2***",
    ),
    (re.compile(r"(://)[^/\s:@\"]+:[^@\s/\"]+@"), r"\1***@"),
]
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_FILE_BYTES = 400_000
MAX_FILES = 300
PROBE_TIMEOUT = 20
SECTIONS = {
    "mcp": "MCP servers",
    "skill": "Skills",
    "plugin": "Plugins",
    "config": "Config files",
}

SECRET_VALUES: list[str] = []
CAPTURE = True  # --no-capture turns off the mock-API request captures
# Each subscription's own usage page. None of the CLIs expose the OpenCode workspace id (only an API key is stored),
# so its link defaults to the console root; pass --opencode-console (or OPENCODE_CONSOLE_URL) for the workspace page.
USAGE_PAGES = {
    "claude": "https://claude.ai/new#settings/usage",
    "codex": "https://chatgpt.com/settings/usage?tab=overview",
    "opencode": os.environ.get("OPENCODE_CONSOLE_URL") or "https://opencode.ai/console",
    "agy": "https://gemini.google.com/usage",
}

try:
    import tiktoken

    _ENCODING = tiktoken.get_encoding("o200k_base")
    TOKENIZER = "o200k_base"

    def count_tokens(text: str) -> int:
        return len(_ENCODING.encode(text, disallowed_special=()))
except Exception:  # noqa: BLE001  # not installed, or the encoding can't be downloaded
    TOKENIZER = "chars/4"

    def count_tokens(text: str) -> int:
        return round(len(text) / 4)


def known_secrets() -> list[str]:
    """Values from every env file (as written and JSON-escaped), longest first; plain URLs and paths are not secrets."""
    values: set[str] = set()
    for env_file in ENV_DIR.glob("**/*.env"):
        try:
            out = subprocess.run(
                ["direnv", "dotenv", "json", str(env_file)],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            env = json.loads(out.stdout or "{}")
        except Exception:  # noqa: BLE001, S112  # skip unreadable or malformed env files
            continue
        for value in env.values():
            if (
                len(value) >= 12
                and not re.fullmatch(r"https?://[^@\s]*", value)
                and not value.startswith(("/", "~"))
            ):
                values |= {value, json.dumps(value)[1:-1]}
    return sorted(values, key=len, reverse=True)


def mask(text: str) -> str:
    for value in SECRET_VALUES:
        text = text.replace(value, "***")
    for pattern, repl in SECRET_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def tilde(path: Path | str) -> str:
    return str(path).replace(str(HOME), "~", 1)


def local_time(value: float | str | None) -> str:
    if value in (None, ""):
        return ""
    try:
        dt = (
            datetime.fromtimestamp(float(value))
            if isinstance(value, (int, float))
            else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        )
        return dt.astimezone().strftime("%b %d %H:%M")
    except (ValueError, OSError):
        return str(value)


@dataclass
class Server:
    name: str
    target: str
    status: str = "not probed"  # connected | failed | needs auth | pending | disabled | not probed
    detail: str = ""
    tools: int | None = None
    tokens: int | None = None
    tools_ref: str | None = None


@dataclass
class Skill:
    name: str
    description: str
    source: str
    ref: str | None = None
    tokens: int = (
        0  # name + description: what sits in context before the skill is loaded
    )


@dataclass
class Plugin:
    name: str
    version: str = ""
    enabled: bool | None = None
    detail: str = ""
    ref: str | None = None
    url: str = ""


@dataclass
class Hook:
    event: str
    label: str  # short: matcher and command
    source: str  # the file that defines it
    detail: str  # the hook's full definition, masked


@dataclass
class Prompt:
    title: str
    path: str
    text: str
    tokens: int = 0


@dataclass
class RequestPart:
    kind: str  # system | tools | context
    title: str
    text: str
    tokens: int = 0


@dataclass
class Harness:
    key: str
    name: str
    version: str = ""
    model: str = ""
    models: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)
    config_ref: str | None = None
    servers: list[Server] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    plugins: list[Plugin] = field(default_factory=list)
    prompts: list[Prompt] = field(default_factory=list)
    hooks: list[Hook] = field(default_factory=list)
    request: dict = field(
        default_factory=dict
    )  # {source, note, parts: [RequestPart]}: what one model call carries
    tool_search: dict = field(
        default_factory=dict
    )  # {state: on|off|per model|unsupported, detail}
    usage: dict = field(
        default_factory=dict
    )  # {source, as_of, rows: [{label, used, resets}], raw}
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------- helpers


def run(cmd: list[str], cwd: Path, timeout: int = 180) -> str:
    """stdout of cmd (ANSI stripped). Goes through a temp file: opencode truncates output written to a pipe."""
    with tempfile.TemporaryFile("w+") as out:
        proc = subprocess.run(
            cmd,
            check=False,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        out.seek(0)
        stdout = out.read()
    if proc.returncode != 0 and not stdout.strip():
        raise RuntimeError(
            f"`{' '.join(cmd)}` exited {proc.returncode}: {mask(proc.stderr.strip()[-300:])}"
        )
    return ANSI.sub("", stdout)


def attempt(harness: Harness, what: str, fn) -> None:
    try:
        fn()
    except Exception as e:  # noqa: BLE001  # one failing source must not hide the rest of the page
        harness.errors.append(f"{what}: {mask(str(e))}")


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return None


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def frontmatter(text: str) -> dict[str, str]:
    """name/description from a SKILL.md header; handles plain, quoted and folded (>, |) values."""
    if not text.startswith("---"):
        return {}
    header = text.split("\n---", 1)[0].splitlines()[1:]
    out: dict[str, str] = {}
    i = 0
    while i < len(header):
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", header[i])
        i += 1
        if not m:
            continue
        key, value = m.groups()
        if value in (">", "|", ">-", "|-", ""):
            parts = []
            while i < len(header) and (
                header[i].startswith((" ", "\t")) or not header[i].strip()
            ):
                parts.append(header[i].strip())
                i += 1
            value = " ".join(p for p in parts if p)
        out[key] = value.strip().strip("'\"")
    return out


def dirs_up(project: Path) -> list[Path]:
    """project and its parents below $HOME, outermost first (the order harnesses concatenate instruction files in)."""
    return [
        d
        for d in reversed([project, *project.parents])
        if d != HOME and HOME in d.parents
    ]


def add_prompt(harness: Harness, title: str, path: Path) -> None:
    text = read_text(path)
    if text is not None and text.strip():
        harness.prompts.append(
            Prompt(title, tilde(path), mask(text), count_tokens(text))
        )


def part(kind: str, title: str, text: str) -> dict:
    text = mask(text)
    return asdict(RequestPart(kind, title, text, count_tokens(text)))


def content_text(content) -> str:
    """A message's content as text: strings joined, other blocks as JSON."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n\n".join(
            c.get("text")
            if isinstance(c, dict) and isinstance(c.get("text"), str)
            else json.dumps(c, ensure_ascii=False)
            for c in content
        )
    return json.dumps(content, ensure_ascii=False)


def captured_request(req: dict | None, source: str) -> dict:
    """Split a captured Anthropic or OpenAI chat request into system prompt, tool definitions and context."""
    if not req:
        return {"source": source, "note": "nothing was captured", "parts": []}
    body, parts = req["body"], []
    system = body.get("system")
    for i, block in enumerate(
        system if isinstance(system, list) else ([{"text": system}] if system else [])
    ):
        parts.append(
            part(
                "system",
                f"system block {i + 1}",
                block.get("text", "") if isinstance(block, dict) else str(block),
            )
        )
    for message in body.get("messages", []):
        kind = (
            "system"
            if message.get("role") in ("system", "developer") and not system
            else "context"
        )
        parts.append(
            part(
                kind,
                f"{message.get('role')} message",
                content_text(message.get("content")),
            )
        )
    if tools := body.get("tools"):
        parts.append(
            part(
                "tools",
                f"{len(tools)} tool definitions",
                json.dumps(tools, indent=1, ensure_ascii=False),
            )
        )
    return {
        "source": source,
        "note": f'model {body.get("model")}; the prompt was "hi"',
        "parts": parts,
    }


def existing(*paths: Path) -> list[Path]:
    return [p for p in paths if p.is_file()]


def doc_url(root: Path) -> str:
    """homepage or repository from a plugin/package manifest under root."""
    for rel in (
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        "plugin.json",
        "package.json",
    ):
        meta = read_json(root / rel)
        repo = meta.get("repository")
        url = meta.get("homepage") or (
            repo.get("url") if isinstance(repo, dict) else repo
        )
        if isinstance(url, str) and url.startswith(("http", "git+http")):
            return re.sub(r"\.git$", "", url.removeprefix("git+"))
    return ""


# ---------------------------------------------------------------- explorer pages
# One tree in explorer.html: <section>/<page>/<item>. A page's ref is its URL-encoded "<section>/<page name>";
# its content goes to data/<id>.js, the tree (without content) to data/explorer-index.js.


class Explorers:
    def __init__(self):
        self.pages: dict[str, dict] = {}
        self.by_key: dict[str, str] = {}
        self.names: dict[str, set[str]] = {}
        self.lock = threading.Lock()

    def add(
        self,
        key: str,
        kind: str,
        title: str,
        subtitle: str,
        items_fn,
        hint: str = "",
        meta: dict | None = None,
    ) -> str:
        """Register a page once per key (e.g. a skill dir shared by several harnesses); items_fn builds its items.
        A second page with the same title in a section is told apart by hint."""
        with self.lock:
            if key in self.by_key:
                return self.by_key[key]
            taken = self.names.setdefault(kind, set())
            name, n = title, 2
            if name in taken:
                hint = hint or subtitle
                name = f"{title} ({hint if len(hint) <= 40 else '…' + hint[-39:]})"
            while name in taken:
                name, n = f"{title} ({n})", n + 1
            taken.add(name)
            ref = f"{urllib.parse.quote(SECTIONS[kind], safe='')}/{urllib.parse.quote(name, safe='')}"
            page_id = f"{kind}-{re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:40]}-{hashlib.sha1(key.encode()).hexdigest()[:8]}"
            self.by_key[key] = ref
            self.pages[ref] = {
                "ref": ref,
                "id": page_id,
                "kind": kind,
                "name": name,
                "subtitle": subtitle,
                "meta": meta or {},
                "harnesses": [],
                "items": [],
            }
        self.pages[ref]["items"] = items_fn()
        return ref

    def used_by(self, ref: str | None, harness: str) -> None:
        if ref in self.pages and harness not in self.pages[ref]["harnesses"]:
            self.pages[ref]["harnesses"].append(harness)


EXPLORERS = Explorers()


def file_item(path: Path, label: str) -> dict:
    item = {"path": label, "href": path.resolve().as_uri()}
    try:
        size = path.stat().st_size
    except OSError as e:
        return item | {"note": str(e)}
    if path.suffix.lower() in IMAGE_EXT:
        return item | {"kind": "image"}
    if size > MAX_FILE_BYTES:
        return item | {"note": f"{size // 1024} KB, too large to embed"}
    raw = path.read_bytes()
    try:
        text = raw.decode()
    except UnicodeDecodeError:
        text = None
    if text is None or "\0" in text[:4096]:
        return item | {"note": "binary file"}
    kind = "md" if path.suffix.lower() in (".md", ".markdown", ".mdc") else "code"
    return item | {
        "kind": kind,
        "lang": path.suffix.lstrip(".").lower(),
        "text": mask(text),
        "tokens": count_tokens(text),
    }


def walk(root: Path):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=True):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name != ".DS_Store":
                yield Path(dirpath) / name
                count += 1
                if count >= MAX_FILES:
                    return


def dir_explorer(
    kind: str, title: str, root: Path, meta: dict | None = None
) -> str | None:
    """A page with every file under root (or just root, if it is a file); SKILL.md / README.md first."""
    if not root.exists():
        return None
    root = root.resolve()

    def items():
        if root.is_file():
            return [file_item(root, root.name)]
        files = [(p, p.relative_to(root).as_posix()) for p in walk(root)]
        files.sort(
            key=lambda f: (
                f[1] != "SKILL.md",
                f[1].lower() != "readme.md",
                f[1].count("/"),
                f[1].lower(),
            )
        )
        return [file_item(p, rel) for p, rel in files]

    return EXPLORERS.add(
        f"dir:{root}",
        kind,
        title,
        tilde(root),
        items,
        hint=tilde(root.parent),
        meta=meta,
    )


def files_explorer(key: str, title: str, paths: list[Path]) -> str | None:
    if not paths:
        return None
    return EXPLORERS.add(
        key,
        "config",
        title,
        ", ".join(tilde(p) for p in paths),
        lambda: [file_item(p, tilde(p)) for p in paths],
    )


def tool_tokens(tool: dict) -> int:
    """Approximate context cost of one tool definition: name, description and input schema as compact JSON."""
    spec = {
        "name": tool.get("name"),
        "description": tool.get("description", ""),
        "input_schema": tool.get("inputSchema", {}),
    }
    return count_tokens(json.dumps(spec, separators=(",", ":"), ensure_ascii=False))


def tools_explorer(server: Server, tools: list[dict]) -> str:
    tools = [
        json.loads(mask(json.dumps(t, ensure_ascii=False)))
        for t in sorted(tools, key=lambda t: t.get("name", ""))
    ]
    items = [
        {
            "path": t.get("name", "?"),
            "kind": "tool",
            "tool": t,
            "tokens": tool_tokens(t),
            "text": json.dumps(t, indent=2, ensure_ascii=False),
        }
        for t in tools
    ]
    server.tokens = sum(i["tokens"] for i in items)
    meta = {"target": server.target, "tools": len(items), "tokens": server.tokens}
    # Keyed by name + definitions: one server reached through different targets (openwiki --host claude/codex/...) is one page.
    digest = hashlib.sha1(json.dumps(tools, sort_keys=True).encode()).hexdigest()
    return EXPLORERS.add(
        f"tools:{server.name}:{digest}",
        "mcp",
        server.name,
        f"{server.target} · {len(items)} tools",
        lambda: items,
        hint=server.target,
        meta=meta,
    )


def skill(name: str, description: str, source: str, root: Path | None) -> Skill:
    description = mask(description)
    tokens = count_tokens(f"- {name}: {description}")
    ref = (
        dir_explorer(
            "skill", name, root, {"description": description, "tokens": tokens}
        )
        if root
        else None
    )
    return Skill(name, description, tilde(source), ref, tokens)


def scan_skills(root: Path, source: str, prefix: str = "") -> list[Skill]:
    if not root.is_dir():
        return []
    out = []
    for skill_md in sorted(root.glob("*/SKILL.md")):
        meta = frontmatter(read_text(skill_md) or "")
        out.append(
            skill(
                prefix + (meta.get("name") or skill_md.parent.name),
                meta.get("description", ""),
                f"{source}: {skill_md}",
                skill_md.parent,
            )
        )
    return out


# ---------------------------------------------------------------- MCP probing


def jsonrpc(method: str, id_: int | None = None, params: dict | None = None) -> dict:
    msg: dict = {"jsonrpc": "2.0", "method": method}
    if id_ is not None:
        msg["id"] = id_
    if params is not None:
        msg["params"] = params
    return msg


INIT = {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {"name": "harness-overview", "version": "1"},
}


def server_info(init: dict) -> str:
    info = init.get("result", {}).get("serverInfo", {})
    return f"{info.get('name', '')} {info.get('version', '')}".strip()


def http_call(
    url: str, headers: dict, msg: dict, session: str | None
) -> tuple[dict | None, str | None]:
    hdrs = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    } | headers
    if session:
        hdrs["Mcp-Session-Id"] = session
    req = urllib.request.Request(
        url, data=json.dumps(msg).encode(), headers=hdrs, method="POST"
    )
    with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as resp:
        session = resp.headers.get("Mcp-Session-Id") or session
        if "id" not in msg:
            return None, session
        if "text/event-stream" in resp.headers.get("Content-Type", ""):
            for raw in resp:
                line = raw.decode(errors="replace").strip()
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip() or "{}")
                    if data.get("id") == msg["id"]:
                        return data, session
            return None, session
        return json.loads(resp.read() or b"{}"), session


def probe_http(url: str, headers: dict) -> tuple[str, str, list | None]:
    try:
        init, session = http_call(url, headers, jsonrpc("initialize", 1, INIT), None)
        if not init or "error" in init:
            return (
                "failed",
                str((init or {}).get("error", "no initialize response")),
                None,
            )
        http_call(url, headers, jsonrpc("notifications/initialized"), session)
        tools, cursor, n = [], None, 2
        while n < 20:
            res, session = http_call(
                url,
                headers,
                jsonrpc("tools/list", n, {"cursor": cursor} if cursor else {}),
                session,
            )
            result = (res or {}).get("result", {})
            tools += result.get("tools", [])
            cursor, n = result.get("nextCursor"), n + 1
            if not cursor:
                break
        return "connected", server_info(init), tools
    except urllib.error.HTTPError as e:
        return (
            ("needs auth" if e.code in (401, 403) else "failed"),
            f"HTTP {e.code} {e.reason}",
            None,
        )
    except urllib.error.URLError as e:
        return "failed", str(e.reason), None
    except Exception as e:  # noqa: BLE001
        return "failed", f"{type(e).__name__}: {e}", None


def probe_stdio(
    command: str, args: list[str], env: dict, cwd: str | None
) -> tuple[str, str, list | None]:
    try:
        proc = subprocess.Popen(
            [command, *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=os.environ | env,
            cwd=cwd or GLOBAL_CWD,
        )
    except OSError as e:
        return "failed", str(e), None
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)

    def call(msg: dict) -> dict | None:
        proc.stdin.write((json.dumps(msg) + "\n").encode())
        proc.stdin.flush()
        if "id" not in msg:
            return None
        while sel.select(timeout=PROBE_TIMEOUT):
            line = proc.stdout.readline()
            if not line:
                return None
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("id") == msg["id"]:
                return data
        raise TimeoutError(f"no response within {PROBE_TIMEOUT}s")

    try:
        init = call(jsonrpc("initialize", 1, INIT))
        if not init or "error" in init:
            return "failed", str((init or {}).get("error", "process exited")), None
        call(jsonrpc("notifications/initialized"))
        res = call(jsonrpc("tools/list", 2, {}))
        return (
            "connected",
            server_info(init),
            (res or {}).get("result", {}).get("tools", []),
        )
    except Exception as e:  # noqa: BLE001
        return "failed", f"{type(e).__name__}: {e}", None
    finally:
        proc.kill()
        proc.wait()


PROBE_POOL = ThreadPoolExecutor(max_workers=6)
PROBES: dict[str, Future] = {}
PROBE_LOCK = threading.Lock()
# Probes wait for the harnesses' own health checks: probing the same gateway concurrently got those checks 503s.
NATIVE_CHECKS = ["claude", "opencode"]
NATIVE_DONE = threading.Event()


def native_check_done(key: str) -> None:
    with PROBE_LOCK:
        if key in NATIVE_CHECKS:
            NATIVE_CHECKS.remove(key)
        if not NATIVE_CHECKS:
            NATIVE_DONE.set()


def after_native(fn, *args):
    NATIVE_DONE.wait(timeout=300)
    return fn(*args)


def probe(spec: dict) -> Future:
    """Probe a normalized spec ({url, headers} or {command, args, env, cwd}) once, however many harnesses share it."""
    key = json.dumps(spec, sort_keys=True)
    with PROBE_LOCK:
        if key not in PROBES:
            if "url" in spec:
                PROBES[key] = PROBE_POOL.submit(
                    after_native, probe_http, spec["url"], spec.get("headers") or {}
                )
            else:
                PROBES[key] = PROBE_POOL.submit(
                    after_native,
                    probe_stdio,
                    spec["command"],
                    spec.get("args", []),
                    spec.get("env") or {},
                    spec.get("cwd"),
                )
        return PROBES[key]


def expand(value: str, extra: dict) -> str:
    """${VAR} / ${VAR:-default} like Claude Code does; KeyError when a variable is unset (then the server isn't probed)."""

    def sub(m):
        name, default = m.group(1), m.group(3)
        resolved = extra.get(name, os.environ.get(name))
        if resolved is None:
            if default is None:
                raise KeyError(name)
            return default
        return resolved

    return re.sub(r"\$\{(\w+)(:-([^}]*))?\}", sub, value)


def normalize(spec: dict, extra: dict | None = None) -> dict | None:
    """A Claude/OpenCode/Antigravity server entry as a probe spec, or None (legacy SSE, unresolvable variables)."""
    extra = extra or {}
    try:
        url = spec.get("url") or spec.get("serverUrl") or spec.get("httpUrl")
        if url:
            if spec.get("type") == "sse":
                return None
            return {
                "url": expand(url, extra),
                "headers": {
                    k: expand(str(v), extra)
                    for k, v in (spec.get("headers") or {}).items()
                },
            }
        command = spec.get("command")
        args = spec.get("args") or []
        if isinstance(command, list):
            command, args = command[0], command[1:]
        if not command:
            return None
        env = spec.get("env") or spec.get("environment") or {}
        return {
            "command": expand(command, extra),
            "args": [expand(str(a), extra) for a in args],
            "env": {k: expand(str(v), extra) for k, v in env.items()},
            "cwd": spec.get("cwd"),
        }
    except KeyError:
        return None


def finish_probes(pending: list[tuple[Server, Future, bool]]) -> None:
    """Attach probe results: tools always; status too where the harness has no health check of its own."""
    for server, future, sets_status in pending:
        status, detail, tools = future.result()
        if sets_status:
            server.status, server.detail = status, mask(detail)
        if tools is not None:
            server.tools = len(tools)
            server.tools_ref = tools_explorer(server, tools)


# ---------------------------------------------------------------- hooks


def command_label(handler: dict) -> str:
    """A hook command shortened to its program, or to the script an interpreter runs plus its first arguments."""
    command = handler.get("command", "")
    words = (
        [command, *handler["args"]]
        if handler.get("args")
        else re.findall(r"'[^']*'|\"[^\"]*\"|\S+", command)
    )
    words = [w.strip("'\"") for w in words if w]
    if not words:
        return "?"
    if (
        Path(words[0]).name.startswith(
            ("python", "node", "bash", "sh", "zsh", "uv", "bun")
        )
        and len(words) > 1
    ):
        rest = [w for w in words[1:] if w not in ("run", "-c", "--no-project")]
        script = next((i for i, w in enumerate(rest) if not w.startswith("-")), 0)
        tail = [w for w in rest[script + 1 : script + 3] if not w.startswith("-")]
        return (
            " ".join([Path(rest[script]).name, *tail]) if rest else Path(words[0]).name
        )
    return Path(words[0]).name


def json_hooks(
    harness: Harness, path: Path, hooks: dict, source: str | None = None
) -> None:
    """Claude/Codex-style {event: [{matcher, hooks: [handler]}]} (agy's flat events have no matcher)."""
    for event, groups in (hooks or {}).items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            handlers = group.get("hooks", [group]) if isinstance(group, dict) else []
            for handler in handlers:
                matcher = group.get("matcher")
                label = (
                    f"{matcher} · " if matcher not in (None, "", "*", ".*") else ""
                ) + command_label(handler)
                harness.hooks.append(
                    Hook(
                        event,
                        mask(label),
                        source or tilde(path),
                        mask(
                            json.dumps(
                                {
                                    "event": event,
                                    "matcher": matcher,
                                    "handler": handler,
                                },
                                indent=2,
                                ensure_ascii=False,
                            )
                        ),
                    )
                )


def plugin_hooks(harness: Harness, path: Path, name: str) -> None:
    """OpenCode v2 hooks are registered in plugin code: ctx.<domain>.hook("<name>", ...)."""
    source = read_text(path) or ""
    for domain, hook in re.findall(r"ctx\.(\w+)\.hook\(\s*[\"'`]([^\"'`]+)", source):
        harness.hooks.append(
            Hook(
                f"{domain}.{hook}",
                name,
                tilde(path),
                f'registered by plugin {name} ({tilde(path)}):\n  ctx.{domain}.hook("{hook}", ...)',
            )
        )


# ---------------------------------------------------------------- Claude Code


def claude(cwd: Path, project: Path | None, usage: bool) -> Harness:
    h = Harness("claude", "Claude Code")
    global_files = existing(
        HOME / ".claude.json",
        HOME / ".claude/settings.json",
        HOME / ".claude/settings.local.json",
    )
    project_files = (
        existing(
            project / ".mcp.json",
            project / ".claude/settings.json",
            project / ".claude/settings.local.json",
        )
        if project
        else []
    )
    settings_files = [
        p for p in global_files + project_files if p.name.startswith("settings")
    ]
    h.config_files = [tilde(p) for p in global_files + project_files]
    h.config_ref = files_explorer(
        f"config:claude:{project}", "Claude Code", global_files + project_files
    )
    attempt(
        h,
        "version",
        lambda: setattr(h, "version", run(["claude", "--version"], cwd).strip()),
    )

    def model():
        for path in reversed(settings_files):
            if m := read_json(path).get("model"):
                h.model = m
                return
        h.model = "default"

    def tool_search():
        env = {}
        for (
            path
        ) in settings_files:  # later (project, local) settings override earlier ones
            env |= read_json(path).get("env", {})
        env |= {
            k: v
            for k, v in os.environ.items()
            if k in ("ENABLE_TOOL_SEARCH", "ANTHROPIC_BASE_URL")
        }
        value, base = env.get("ENABLE_TOOL_SEARCH"), env.get("ANTHROPIC_BASE_URL", "")
        third_party = bool(base) and "anthropic.com" not in base
        if value:
            state = "off" if value.lower() in ("false", "0", "off") else "on"
            h.tool_search = {
                "state": state,
                "upfront": "deferred until searched (ToolSearch)"
                if state == "on"
                else "sent with every request",
                "detail": f"ENABLE_TOOL_SEARCH={value} (true: always defer MCP tools; auto[:N]: "
                "defer once their definitions pass N% of the context)",
            }
        elif third_party:
            h.tool_search = {
                "state": "off",
                "upfront": "sent with every request",
                "detail": "ANTHROPIC_BASE_URL is not an Anthropic host; set ENABLE_TOOL_SEARCH to enable",
            }
        else:
            h.tool_search = {
                "state": "on",
                "upfront": "deferred until searched (ToolSearch)",
                "detail": "default: MCP tools are deferred and loaded through the ToolSearch tool",
            }

    def read_usage():
        raw = run(["claude", "-p", "/usage"], GLOBAL_CWD, timeout=90)
        rows = []
        for label, used, resets in re.findall(
            r"^(Current [^:]+): (\d+)% used(?: · resets (.+))?$", raw, re.M
        ):
            rows.append(
                {
                    "label": label.removeprefix("Current ").capitalize(),
                    "used": int(used),
                    "resets": resets,
                }
            )
        h.usage = {
            "source": "claude -p /usage",
            "as_of": "now",
            "rows": rows,
            "raw": mask(raw.strip()),
        }

    specs: dict[str, dict] = {}
    marketplaces = read_json(HOME / ".claude/plugins/known_marketplaces.json")

    def plugin_url(plugin_id: str, root: Path | None) -> str:
        """The marketplace entry's homepage, else the plugin's own manifest, else the marketplace's GitHub repo."""
        name, _, market = plugin_id.partition("@")
        manifest = read_json(
            HOME
            / ".claude/plugins/marketplaces"
            / market
            / ".claude-plugin/marketplace.json"
        )
        entry = next(
            (e for e in manifest.get("plugins", []) if e.get("name") == name), {}
        )
        if url := entry.get("homepage") or entry.get("repository"):
            return url
        if root and (url := doc_url(root)):
            return url
        repo = marketplaces.get(market, {}).get("source", {}).get("repo")
        return f"https://github.com/{repo}" if repo else ""

    def plugins():
        seen: dict[str, Plugin] = {}
        for p in json.loads(run(["claude", "plugin", "list", "--json"], cwd)):
            if p.get("scope") == "project" and project is None:
                continue
            root = Path(p["installPath"]) if p.get("installPath") else None
            plugin = seen.setdefault(
                p["id"],
                Plugin(
                    p["id"],
                    p.get("version", ""),
                    False,
                    "",
                    dir_explorer("plugin", p["id"], root) if root else None,
                    plugin_url(p["id"], root),
                ),
            )
            plugin.enabled = plugin.enabled or bool(p.get("enabled"))
            plugin.detail = ", ".join(filter(None, [plugin.detail, p.get("scope", "")]))
            if p.get("enabled") and root:
                plugin_name = p["id"].split("@")[0]
                for s in scan_skills(
                    root / "skills", f"plugin {p['id']}", f"{plugin_name}:"
                ):
                    if all(x.name != s.name for x in h.skills):
                        h.skills.append(s)
                mcp = read_json(root / ".mcp.json")
                for name, spec in (
                    mcp.get("mcpServers", mcp) if isinstance(mcp, dict) else {}
                ).items():
                    if isinstance(spec, dict) and (
                        norm := normalize(spec, {"CLAUDE_PLUGIN_ROOT": str(root)})
                    ):
                        specs[f"plugin:{plugin_name}:{name}"] = norm
        h.plugins = list(seen.values())

    def servers():
        cfg = read_json(HOME / ".claude.json")
        sources = [
            cfg.get("mcpServers", {}),
            cfg.get("projects", {}).get(str(cwd), {}).get("mcpServers", {}),
        ]
        if project:
            sources.append(read_json(project / ".mcp.json").get("mcpServers", {}))
        for source in sources:
            for name, spec in source.items():
                if norm := normalize(spec):
                    specs[name] = norm
        pending = []
        try:
            listing = run(["claude", "mcp", "list"], cwd)
        finally:
            native_check_done("claude")
        for line in listing.splitlines():
            if " - " not in line or ": " not in line:
                continue
            head, status = line.rsplit(" - ", 1)
            name, target = head.split(": ", 1)
            detail = status.split("—", 1)[1].strip() if "—" in status else ""
            state = (
                "connected"
                if "Connected" in status
                else "needs auth"
                if "auth" in status.lower()
                else "pending"
                if "Pending" in status
                else "failed"
            )
            server = Server(
                name.strip(),
                mask(re.sub(r"\s*\((HTTP|SSE|stdio)\)$", "", target.strip())),
                state,
                mask(detail),
            )
            h.servers.append(server)
            if name.strip() in specs:
                pending.append((server, probe(specs[name.strip()]), False))
        finish_probes(pending)

    def models():
        raw = run(["claude", "-p", "/model"], GLOBAL_CWD, timeout=90)
        if m := re.search(r"Available: (.+?)(?:, or a full model ID)?\.?$", raw, re.M):
            h.models = [x.strip() for x in m.group(1).split(",") if x.strip()]

    def capture():
        h.request = captured_request(
            llm_capture.capture_claude(cwd),
            "captured: claude -p against a local mock API (API-key mode; "
            "an interactive subscription session opens with a slightly different identity block)",
        )

    def hooks():
        for path in settings_files:
            json_hooks(h, path, read_json(path).get("hooks", {}))
        for p in json.loads(run(["claude", "plugin", "list", "--json"], cwd)):
            if (
                p.get("enabled")
                and p.get("installPath")
                and (project or p.get("scope") != "project")
            ):
                file = Path(p["installPath"]) / "hooks/hooks.json"
                if file.is_file() and all(
                    x.source != f"plugin {p['id']}" for x in h.hooks
                ):
                    json_hooks(
                        h, file, read_json(file).get("hooks", {}), f"plugin {p['id']}"
                    )

    def prompts():
        add_prompt(h, "global ~/.claude/CLAUDE.md", HOME / ".claude/CLAUDE.md")
        if not project:
            return
        for d in dirs_up(project):
            found = existing(
                d / "CLAUDE.md", d / ".claude/CLAUDE.md", d / "CLAUDE.local.md"
            )
            for path in found or existing(d / "AGENTS.md"):
                add_prompt(
                    h,
                    f"project {tilde(path)}"
                    + ("" if found else " (no CLAUDE.md there)"),
                    path,
                )
        slug = re.sub(r"[^A-Za-z0-9]", "-", str(project))
        add_prompt(
            h,
            "auto memory index",
            HOME / ".claude/projects" / slug / "memory/MEMORY.md",
        )

    attempt(h, "model", model)
    attempt(h, "claude -p /model", models)
    attempt(h, "tool search", tool_search)
    h.skills += scan_skills(HOME / ".claude/skills", "global")
    if project:
        h.skills += scan_skills(project / ".claude/skills", "project")
    attempt(h, "claude plugin list", plugins)
    attempt(h, "claude mcp list", servers)
    native_check_done("claude")
    attempt(h, "hooks", hooks)
    attempt(h, "instruction files", prompts)
    if usage:
        attempt(h, "claude -p /usage", read_usage)
    if CAPTURE:
        attempt(h, "request capture", capture)
    return h


# ---------------------------------------------------------------- Codex


def codex(cwd: Path, project: Path | None, usage: bool) -> Harness:
    h = Harness("codex", "Codex")
    files = existing(HOME / ".codex/config.toml", HOME / ".codex/hooks.json")
    if project:
        files += existing(project / ".codex/config.toml", project / ".codex/hooks.json")
    h.config_files = [tilde(p) for p in files]
    h.config_ref = files_explorer(f"config:codex:{project}", "Codex", files)
    attempt(
        h,
        "version",
        lambda: setattr(h, "version", run(["codex", "--version"], cwd).strip()),
    )
    attempt(
        h,
        "model",
        lambda: setattr(
            h,
            "model",
            tomllib.loads((HOME / ".codex/config.toml").read_text()).get(
                "model", "default"
            ),
        ),
    )

    def tool_search():
        flags = dict(
            re.findall(
                r"^(\S*tool_search\S*)\s+.*?\s(true|false)\s*$",
                run(["codex", "features", "list"], cwd),
                re.M,
            )
        )
        if flags.get("tool_search_always_defer_mcp_tools") == "true":
            h.tool_search = {
                "state": "on",
                "upfront": "deferred behind tool_search",
                "detail": "tool_search_always_defer_mcp_tools: MCP tools are always deferred behind tool_search",
            }
        else:
            h.tool_search = {
                "state": "off",
                "upfront": "sent with every request",
                "detail": "feature flags: "
                + ", ".join(f"{k}={v}" for k, v in flags.items()),
            }

    def read_usage():
        """Live limits from the app-server's account/rateLimits/read (the JSON-RPC API the IDE extensions use)."""
        proc = subprocess.Popen(
            ["codex", "app-server"],
            cwd=GLOBAL_CWD,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        sel = selectors.DefaultSelector()
        sel.register(proc.stdout, selectors.EVENT_READ)

        def call(msg: dict) -> dict:
            proc.stdin.write(json.dumps(msg) + "\n")
            proc.stdin.flush()
            while sel.select(timeout=30):
                line = proc.stdout.readline()
                if not line:
                    break
                reply = json.loads(line)
                if reply.get("id") == msg.get("id"):
                    if "error" in reply:
                        raise RuntimeError(
                            reply["error"].get("message", reply["error"])
                        )
                    return reply.get("result", {})
            raise TimeoutError("no reply from codex app-server")

        try:
            call(
                {
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "clientInfo": {"name": "harness-overview", "version": "1"}
                    },
                }
            )
            proc.stdin.write(json.dumps({"method": "initialized"}) + "\n")
            result = call({"id": 2, "method": "account/rateLimits/read"})
        finally:
            proc.kill()
            proc.wait()
        limits = result.get("rateLimits") or {}
        rows = []
        for key in ("primary", "secondary"):
            if w := limits.get(key):
                minutes = w.get("windowDurationMins") or 0
                label = (
                    "5-hour window"
                    if minutes == 300
                    else "Weekly"
                    if minutes == 10080
                    else f"{minutes // 60} h window"
                )
                rows.append(
                    {
                        "label": label,
                        "used": round(w.get("usedPercent", 0)),
                        "resets": local_time(w.get("resetsAt")),
                    }
                )
        credits = result.get("rateLimitResetCredits") or {}
        resets = [
            {
                "title": c.get("title") or "reset",
                "expires": local_time(c.get("expiresAt"))
                if c.get("expiresAt")
                else "never",
            }
            for c in sorted(
                credits.get("credits") or [],
                key=lambda c: c.get("expiresAt") or float("inf"),
            )
            if c.get("status") == "available"
        ]
        h.usage = {
            "source": "codex app-server: account/rateLimits/read",
            "as_of": "now",
            "plan": limits.get("planType") or "",
            "rows": rows,
            "resets_available": credits.get("availableCount"),
            "resets": resets,
            "raw": mask(
                json.dumps(
                    {k: v for k, v in result.items() if k != "accountId"}, indent=2
                )
            ),
        }

    def servers():
        pending = []
        for s in json.loads(run(["codex", "mcp", "list", "--json"], cwd)):
            t = s.get("transport", {})
            if t.get("type") == "stdio":
                server = Server(
                    s["name"],
                    mask(" ".join([t.get("command", ""), *t.get("args", [])])),
                )
                spec = {
                    "command": t.get("command", ""),
                    "args": t.get("args", []),
                    "env": t.get("env") or {},
                    "cwd": t.get("cwd"),
                }
            else:
                headers = dict(t.get("http_headers") or {})
                headers |= {
                    k: os.environ[v]
                    for k, v in (t.get("env_http_headers") or {}).items()
                    if v in os.environ
                }
                if (var := t.get("bearer_token_env_var")) and var in os.environ:
                    headers["Authorization"] = f"Bearer {os.environ[var]}"
                server = Server(s["name"], mask(t.get("url", "")))
                spec = {"url": t.get("url", ""), "headers": headers}
            h.servers.append(server)
            if not s.get("enabled", True):
                server.status, server.detail = (
                    "disabled",
                    s.get("disabled_reason") or "",
                )
            else:
                pending.append((server, probe(spec), True))
        finish_probes(pending)

    def prompt_input():
        for msg in json.loads(run(["codex", "debug", "prompt-input"], cwd)):
            for piece in msg.get("content", []):
                text = piece.get("text", "")
                if not text.strip():
                    continue
                tag = re.match(r"\s*<([\w ]+?)>", text)
                title = (
                    tag.group(1)
                    if tag
                    else text.strip().splitlines()[0][:80].lstrip("# ")
                )
                h.prompts.append(
                    Prompt(
                        f"{msg.get('role', '')}: {title}",
                        "codex debug prompt-input",
                        mask(text),
                        count_tokens(text),
                    )
                )
                if h.request is not None and "parts" in h.request:
                    kind = "system" if msg.get("role") == "developer" else "context"
                    h.request["parts"].append(
                        part(kind, f"{msg.get('role')}: {title}", text)
                    )
                if text.lstrip().startswith("<skills_instructions>"):
                    roots = dict(re.findall(r"^- `(r\d+)` = `([^`]+)`", text, re.M))
                    for name, desc, file in re.findall(
                        r"^- ([^:\n`]+): (.*) \(file: ([^)]+)\)$", text, re.M
                    ):
                        root, _, rest = file.partition("/")
                        path = Path(roots.get(root, root)) / rest
                        h.skills.append(
                            skill(name.strip(), desc, str(path), path.parent)
                        )

    def plugins():
        for p in json.loads(run(["codex", "plugin", "list", "--json"], cwd)).get(
            "installed", []
        ):
            root = (
                HOME
                / ".codex/plugins/cache"
                / p.get("marketplaceName", "")
                / p.get("name", "")
                / p.get("version", "")
            )
            url = (
                next(
                    (
                        u
                        for m in [root, *root.glob("*")]
                        if m.is_dir() and (u := doc_url(m))
                    ),
                    "",
                )
                if root.is_dir()
                else ""
            )
            h.plugins.append(
                Plugin(
                    p.get("pluginId") or p.get("name", ""),
                    p.get("version", ""),
                    p.get("enabled"),
                    p.get("installPolicy", ""),
                    dir_explorer("plugin", p.get("pluginId") or p["name"], root),
                    url,
                )
            )

    def hooks():
        for base in [HOME / ".codex", *([project / ".codex"] if project else [])]:
            json_hooks(
                h, base / "hooks.json", read_json(base / "hooks.json").get("hooks", {})
            )
            if (base / "config.toml").is_file():
                json_hooks(
                    h,
                    base / "config.toml",
                    tomllib.loads((base / "config.toml").read_text()).get("hooks", {}),
                )

    def models():
        catalog = json.loads(run(["codex", "debug", "models"], cwd)).get("models", [])
        h.models = [m["slug"] for m in catalog if m.get("visibility") == "list"]
        default = next((m for m in catalog if m.get("slug") == h.model), None)
        parts = (
            [
                part(
                    "system",
                    f"base instructions ({h.model})",
                    default["base_instructions"],
                )
            ]
            if default and default.get("base_instructions")
            else []
        )
        h.request = {
            "source": "assembled: the default model's base_instructions (codex debug models) + codex debug prompt-input",
            "note": "Codex's tool definitions are not exposed, so they are not counted",
            "parts": parts,
        }

    attempt(h, "hooks", hooks)
    attempt(h, "codex debug models", models)
    attempt(h, "codex features list", tool_search)
    attempt(h, "codex mcp list", servers)
    attempt(h, "codex debug prompt-input", prompt_input)
    attempt(h, "codex plugin list", plugins)
    if usage:
        attempt(h, "codex app-server rateLimits", read_usage)
    return h


# ---------------------------------------------------------------- OpenCode


def opencode(cwd: Path, project: Path | None, usage: bool) -> Harness:
    """OpenCode v2: everything comes from its background server's API (`opencode api GET /api/...`), scoped to cwd."""
    cfg_dir = HOME / ".config/opencode"
    h = Harness("opencode", "OpenCode")
    attempt(
        h,
        "version",
        lambda: setattr(h, "version", run(["opencode", "--version"], cwd).strip()),
    )

    def api(path: str):
        reply = json.loads(
            run(
                ["opencode", "api", "GET", path, "-H", f"x-opencode-directory:{cwd}"],
                cwd,
            )
        )
        return reply.get("data", reply) if isinstance(reply, dict) else reply

    servers_cfg: dict[str, dict] = {}

    def load_config():
        sources = api("/api/config")
        docs = [
            src for src in sources if src.get("type") == "document" and src.get("path")
        ]
        files = [Path(src["path"]) for src in docs if Path(src["path"]).is_file()]
        h.config_files = [tilde(f) for f in files]
        h.config_ref = files_explorer(f"config:opencode:{project}", "OpenCode", files)
        merged: dict = {}
        for src in docs:  # later documents (project) override earlier ones (global)
            info = src.get("info") or {}
            merged |= {k: v for k, v in info.items() if k != "mcp"}
            mcp = info.get("mcp") or {}
            servers_cfg.update(
                mcp.get(
                    "servers", {k: v for k, v in mcp.items() if isinstance(v, dict)}
                )
            )
        agents = api("/api/agent")
        default = next(
            (a for a in agents if a.get("id") == merged.get("default_agent")), None
        ) or next((a for a in agents if a.get("mode") == "primary"), {})
        m = default.get("model") or {}
        h.model = (
            f"{m.get('providerID')}/{m.get('id')}"
            + (f"#{m['variant']}" if m.get("variant") else "")
            if m
            else "default"
        )
        direct = [
            name for name, spec in servers_cfg.items() if spec.get("codemode") is False
        ]
        h.tool_search = {
            "state": "on",
            "upfront": "≈2k-token inline catalog of signatures; the rest via search()",
            "detail": "Code Mode: MCP tools run inside the `execute` tool; the prompt carries an inline "
            "catalog of signatures capped at ~2k tokens, the rest is found with search() (per-server `codemode: false` "
            "exposes tools directly"
            + (f"; set for {', '.join(direct)}" if direct else "")
            + ")",
        }

    def servers():
        try:
            listing = api("/api/mcp")
            for _ in range(
                10
            ):  # a just-started service answers [] until its servers are registered
                if listing or not servers_cfg:
                    break
                time.sleep(1)
                listing = api("/api/mcp")
        finally:
            native_check_done("opencode")
        pending = []
        for entry in listing:
            spec = servers_cfg.get(entry["name"], {})
            target = spec.get("url") or " ".join(spec.get("command") or [])
            status = entry.get("status", {})
            state = {
                "connected": "connected",
                "disabled": "disabled",
                "needs_auth": "needs auth",
                "needs_client_registration": "needs auth",
            }.get(status.get("status"), "failed")
            server = Server(
                entry["name"], mask(target), state, mask(status.get("error", ""))
            )
            h.servers.append(server)
            if spec and (norm := normalize(spec)):
                pending.append((server, probe(norm), False))
        finish_probes(pending)

    def skills():
        for s in api("/api/skill"):
            path = s.get("path", "")
            if path.startswith("/builtin/"):
                description = mask(s.get("description", ""))
                tokens = count_tokens(f"- {s['name']}: {description}")
                ref = EXPLORERS.add(
                    f"builtin:opencode:{s['id']}",
                    "skill",
                    s["name"],
                    f"OpenCode built-in {path}",
                    lambda s=s: [
                        {
                            "path": Path(s["path"]).name,
                            "kind": "md",
                            "text": mask(s.get("content", "")),
                            "tokens": count_tokens(s.get("content", "")),
                        }
                    ],
                    hint="OpenCode built-in",
                    meta={"description": description, "tokens": tokens},
                )
                h.skills.append(
                    Skill(s["name"], description, f"built-in {path}", ref, tokens)
                )
            else:
                h.skills.append(
                    skill(s["name"], s.get("description", ""), path, Path(path).parent)
                )

    def plugins():
        for p in api("/api/plugin"):
            src = p.get("source", {})
            state = p.get("state", {}).get("status", "")
            if src.get("type") == "local":
                path = Path(src["path"])
                plugin_hooks(h, path, p["id"])
                h.plugins.append(
                    Plugin(
                        p["id"],
                        enabled=state == "active",
                        detail=f"{tilde(path)} · {state}",
                        ref=dir_explorer("plugin", p["id"], path),
                    )
                )
            elif src.get("type") == "package":
                name = re.sub(r"(?<=.)@[^@/]*$", "", src.get("target", p["id"]))
                h.plugins.append(
                    Plugin(
                        src.get("target", p["id"]),
                        src.get("version", ""),
                        state == "active",
                        state,
                        url=f"https://www.npmjs.com/package/{name}",
                    )
                )

    def models():
        h.models = [
            line.strip()
            for line in run(["opencode", "models"], cwd).splitlines()
            if "/" in line and " " not in line.strip()
        ]

    def capture():
        model_id = h.model.split("/", 1)[-1].split("#", 1)[0]
        h.request = captured_request(
            llm_capture.capture_opencode(cwd, model_id),
            f"captured: opencode run --standalone with a mock provider impersonating {model_id}",
        )

    def read_usage():
        raw = run(["opencode", "stats", "--days", "7"], GLOBAL_CWD, timeout=90)
        h.usage = {
            "source": "opencode stats --days 7 (local token totals; the subscription's limits are not exposed)",
            "as_of": "now",
            "rows": [],
            "raw": mask(raw.strip()),
        }

    def prompts():
        if (cfg_dir / "AGENTS.md").is_file():
            add_prompt(h, "global ~/.config/opencode/AGENTS.md", cfg_dir / "AGENTS.md")
        else:
            add_prompt(
                h,
                "global ~/.claude/CLAUDE.md (OpenCode fallback)",
                HOME / ".claude/CLAUDE.md",
            )
        if project:
            for d in dirs_up(project):
                for path in existing(d / "AGENTS.md") or existing(d / "CLAUDE.md"):
                    add_prompt(h, f"project {tilde(path)}", path)

    attempt(h, "opencode api /api/config", load_config)
    attempt(h, "opencode api /api/mcp", servers)
    native_check_done("opencode")
    attempt(h, "opencode api /api/skill", skills)
    attempt(h, "opencode api /api/plugin", plugins)
    attempt(h, "opencode models", models)
    if CAPTURE:
        attempt(h, "request capture", capture)
    attempt(h, "instruction files", prompts)
    if usage:
        attempt(h, "opencode stats", read_usage)
    return h


# ---------------------------------------------------------------- Antigravity (IDE + agy CLI)


def antigravity(cwd: Path, project: Path | None, usage: bool) -> Harness:
    mcp_config = HOME / ".gemini/config/mcp_config.json"
    settings = HOME / ".gemini/antigravity-cli/settings.json"
    h = Harness("agy", "Antigravity (agy)")
    files = existing(mcp_config, HOME / ".gemini/config/skills.json", settings)
    h.config_files = [tilde(p) for p in files]
    h.config_ref = files_explorer("config:agy", "Antigravity", files)
    h.tool_search = {
        "state": "per model",
        "upfront": "deferred if the model supports it",
        "detail": "deferred tool loading is a server-side capability of each model "
        "(supports_deferred_tool_loading); nothing to configure locally",
    }
    attempt(
        h,
        "version",
        lambda: setattr(h, "version", run(["agy", "--version"], cwd).strip()),
    )
    attempt(
        h,
        "model",
        lambda: setattr(h, "model", read_json(settings).get("model", "default")),
    )

    def read_usage():
        raw = run(["agy", "-p", "/quota"], GLOBAL_CWD, timeout=90)
        rows = []
        for group, label, remaining, resets in re.findall(
            r"^([^\t\n]+)\t([^\t\n]+)\t(\d+)%\t(\S+)$", raw, re.M
        ):
            rows.append(
                {
                    "label": f"{group}: {label.replace(' Limit Remaining', '').lower()}",
                    "used": 100 - int(remaining),
                    "resets": local_time(resets),
                }
            )
        h.usage = {
            "source": "agy -p /quota",
            "as_of": "now",
            "rows": rows,
            "raw": mask(raw.strip()),
        }

    def servers():
        pending = []
        for name, s in read_json(mcp_config).get("mcpServers", {}).items():
            url = s.get("serverUrl") or s.get("httpUrl") or s.get("url")
            server = Server(
                name, mask(url or " ".join([s.get("command", ""), *s.get("args", [])]))
            )
            h.servers.append(server)
            if s.get("disabled"):
                server.status = "disabled"
            elif spec := normalize(s):
                pending.append((server, probe(spec), True))
        finish_probes(pending)

    def skills():
        for entry in read_json(HOME / ".gemini/config/skills.json").get("entries", []):
            h.skills.extend(scan_skills(Path(entry["path"]), "skills.json root"))
        h.skills.extend(scan_skills(HOME / ".gemini/antigravity-cli/skills", "global"))
        h.skills.extend(
            scan_skills(HOME / ".gemini/antigravity-cli/builtin/skills", "built-in")
        )
        if project:
            h.skills.extend(scan_skills(project / ".agents/skills", "project"))

    def models():
        h.models = [
            line.split("\t", 1)[0].strip()
            for line in run(["agy", "models"], GLOBAL_CWD).splitlines()
            if "\t" in line
        ]

    def plugins():
        for line in run(["agy", "plugin", "list"], cwd).splitlines():
            if line.strip() and "No imported plugins" not in line:
                h.plugins.append(Plugin(mask(line.strip())))

    def prompts():
        add_prompt(h, "global ~/.gemini/GEMINI.md", HOME / ".gemini/GEMINI.md")
        if not project:
            return
        for d in dirs_up(project):
            for path in existing(d / "GEMINI.md", d / "AGENTS.md"):
                add_prompt(h, f"project {tilde(path)}", path)
        for rule in sorted((project / ".agents/rules").glob("*.md")):
            add_prompt(h, f"project rule {rule.name}", rule)

    def hooks():
        for path in [
            HOME / ".gemini/config/hooks.json",
            *([project / ".agents/hooks.json"] if project else []),
        ]:
            for name, spec in read_json(path).items():
                if isinstance(spec, dict) and spec.get("enabled", True):
                    json_hooks(
                        h,
                        path,
                        {k: v for k, v in spec.items() if k != "enabled"},
                        f"{tilde(path)} ({name})",
                    )

    attempt(h, "hooks", hooks)
    attempt(h, "mcp_config.json", servers)
    attempt(h, "skills", skills)
    attempt(h, "agy plugin list", plugins)
    attempt(h, "agy models", models)
    h.request = {
        "source": "not available",
        "note": "Antigravity exposes neither its system prompt nor a way to point it at a mock API",
        "parts": [],
    }
    attempt(h, "instruction files", prompts)
    if usage:
        attempt(h, "agy -p /quota", read_usage)
    return h


# ---------------------------------------------------------------- output


def write_js(path: Path, statement: str) -> str:
    path.write_text(statement)
    return statement


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build an HTML overview of every harness's MCP servers, skills, plugins and instructions."
    )
    parser.add_argument(
        "--scope",
        choices=["global", "project"],
        default="global",
        help="global: only global config (default); project: as seen from --project",
    )
    parser.add_argument(
        "--project",
        default=".",
        help="project directory for --scope project (default: cwd)",
    )
    parser.add_argument(
        "--out",
        default=str(REPO / "dev/harness-overview"),
        help="output directory (default: <repo>/dev/harness-overview)",
    )
    parser.add_argument(
        "--no-usage", action="store_true", help="skip the subscription usage commands"
    )
    parser.add_argument(
        "--no-capture",
        action="store_true",
        help="skip capturing the model requests through a local mock API",
    )
    parser.add_argument(
        "--opencode-console",
        help="OpenCode console URL for the usage link, e.g. https://opencode.ai/console/<workspace>/go "
        "(default: $OPENCODE_CONSOLE_URL or the console root)",
    )
    parser.add_argument(
        "--open", action="store_true", help="open index.html when done (macOS `open`)"
    )
    args = parser.parse_args()

    SECRET_VALUES.extend(known_secrets())
    if args.opencode_console:
        USAGE_PAGES["opencode"] = args.opencode_console
    global CAPTURE
    CAPTURE = not args.no_capture
    project = (
        Path(args.project).expanduser().resolve() if args.scope == "project" else None
    )
    cwd = project or GLOBAL_CWD
    GLOBAL_CWD.mkdir(parents=True, exist_ok=True)

    collectors = {
        "Claude Code": claude,
        "Codex": codex,
        "OpenCode": opencode,
        "Antigravity": antigravity,
    }
    with ThreadPoolExecutor(max_workers=len(collectors)) as pool:
        futures = {
            name: pool.submit(fn, cwd, project, not args.no_usage)
            for name, fn in collectors.items()
        }
        harnesses = []
        for name, future in futures.items():
            h = future.result()
            for ref in [
                h.config_ref,
                *(s.tools_ref for s in h.servers),
                *(s.ref for s in h.skills),
                *(p.ref for p in h.plugins),
            ]:
                EXPLORERS.used_by(ref, h.name)
            print(
                f"{name:<12} {len(h.servers):>3} MCP  {len(h.skills):>3} skills  {len(h.plugins):>3} plugins  "
                f"{len(h.prompts):>2} instruction parts"
                + (f"  ({len(h.errors)} errors)" if h.errors else "")
            )
            h.usage["page"] = USAGE_PAGES.get(h.key, "")
            harnesses.append(asdict(h))
    PROBE_POOL.shutdown(wait=False, cancel_futures=True)

    out = Path(args.out).expanduser().resolve()
    data_dir = out / "data"
    shutil.rmtree(data_dir, ignore_errors=True)
    data_dir.mkdir(parents=True)
    for asset in ASSETS.iterdir():
        shutil.copy(asset, out / asset.name)
    overview = {
        "scope": args.scope,
        "project": tilde(project) if project else None,
        "home": str(HOME),
        "tokenizer": TOKENIZER,
        "generated": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"),
        "harnesses": harnesses,
    }
    sections = [
        {"kind": kind, "name": name, "pages": []} for kind, name in SECTIONS.items()
    ]
    for page in sorted(EXPLORERS.pages.values(), key=lambda p: p["name"].lower()):
        summary = {k: v for k, v in page.items() if k != "items"} | {
            "items": [
                {"path": i["path"], "tokens": i.get("tokens")} for i in page["items"]
            ]
        }
        next(s for s in sections if s["kind"] == page["kind"])["pages"].append(summary)
    written = [
        write_js(
            data_dir / "overview.js",
            f"window.OVERVIEW = {json.dumps(overview, ensure_ascii=False)};\n",
        ),
        write_js(
            data_dir / "explorer-index.js",
            f"window.EXPLORER_INDEX = {json.dumps({'tokenizer': TOKENIZER, 'sections': sections}, ensure_ascii=False)};\n",
        ),
    ]
    for page in EXPLORERS.pages.values():
        written.append(
            write_js(
                data_dir / f"{page['id']}.js",
                "(window.EXPLORER_PAGES = window.EXPLORER_PAGES || {})"
                f"[{json.dumps(page['ref'])}] = {json.dumps(page, ensure_ascii=False)};\n",
            )
        )

    if leaked := [v for v in SECRET_VALUES if any(v in text for text in written)]:
        shutil.rmtree(data_dir)
        raise SystemExit(
            f"refusing to keep the output: {len(leaked)} known secret value(s) were not redacted"
        )
    print(
        f"wrote {out}/index.html ({len(EXPLORERS.pages)} explorer pages, tokens: {TOKENIZER})"
    )
    if args.open:
        subprocess.run(["open", str(out / "index.html")], check=False)


if __name__ == "__main__":
    main()
