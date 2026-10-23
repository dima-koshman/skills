import importlib.util
import json
import os
import pathlib
import stat
import subprocess
import tomllib
from typing import final

import pytest

_SCRIPT = pathlib.Path(__file__).parent.parent / "scripts/global_mcp.py"
_SPEC = importlib.util.spec_from_file_location("global_mcp", _SCRIPT)
assert _SPEC and _SPEC.loader
global_mcp = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(global_mcp)

LOCAL_SERVER = {"command": "uv", "args": ["run", "python", "-m", "dima.agent_cli_mcp"]}
REMOTE_SERVER = {
    "type": "http",
    "url": "https://mcp.example.com/mcp",
    "headers": {"Authorization": "Bearer token"},
}


def test_claude_and_antigravity_keep_stdio_shape() -> None:
    assert global_mcp.claude_server(LOCAL_SERVER) == LOCAL_SERVER
    assert global_mcp.antigravity_server(LOCAL_SERVER) == LOCAL_SERVER


def test_codex_uses_command_and_args() -> None:
    assert global_mcp.Codex("src").desired({"local": LOCAL_SERVER}) == {
        "local": LOCAL_SERVER
    }


def test_opencode_combines_command_and_args() -> None:
    assert global_mcp.OpenCode().desired({"local": LOCAL_SERVER}) == {
        "local": {
            "type": "local",
            "command": ["uv", "run", "python", "-m", "dima.agent_cli_mcp"],
        }
    }


def test_remote_shapes() -> None:
    assert global_mcp.claude_server(REMOTE_SERVER) == REMOTE_SERVER
    assert global_mcp.antigravity_server(REMOTE_SERVER) == {
        "serverUrl": "https://mcp.example.com/mcp",
        "headers": {"Authorization": "Bearer token"},
    }
    assert global_mcp.Codex("src").desired({"remote": REMOTE_SERVER}) == {
        "remote": {
            "url": "https://mcp.example.com/mcp",
            "http_headers": {"Authorization": "Bearer token"},
        }
    }
    assert global_mcp.OpenCode().desired({"remote": REMOTE_SERVER}) == {
        "remote": {
            "type": "remote",
            "url": "https://mcp.example.com/mcp",
            "headers": {"Authorization": "Bearer token"},
        }
    }


@pytest.fixture
def env(tmp_path: pathlib.Path) -> "_Env":
    return _Env(tmp_path)


def test_sync_resolves_env_file_and_vars_and_keeps_other_servers(env: "_Env") -> None:
    mcp_json = env.mcp_json(
        "a.json",
        {
            "local": LOCAL_SERVER,
            "remote": {
                "type": "http",
                "url": "${BASE_URL}/mcp",
                "headers": {"Authorization": "Bearer ${TOKEN}"},
                "description": "not written",
            },
        },
    )
    env_file = env.home / "a.env"
    _ = env_file.write_text("TOKEN=dummy-token\n")

    _ = env.run(
        "sync",
        "--mcp-json",
        str(mcp_json),
        "--env-file",
        str(env_file),
        "--var",
        "BASE_URL=https://x.invalid",
    )

    remote = {
        "type": "http",
        "url": "https://x.invalid/mcp",
        "headers": {"Authorization": "Bearer dummy-token"},
    }
    assert env.claude()["local"] == LOCAL_SERVER
    assert env.claude()["remote"] == remote
    assert env.claude()["unmanaged"] == {"command": "keep"}
    assert env.codex()["remote"] == {
        "url": remote["url"],
        "http_headers": remote["headers"],
    }
    assert set(env.codex()) == {"unmanaged", "local", "remote"}
    assert set(env.opencode()) == {"local", "remote"}
    assert env.antigravity()["remote"] == {
        "serverUrl": remote["url"],
        "headers": remote["headers"],
    }
    assert env.antigravity()["unmanaged"] == {"command": "keep"}
    for path in env.configs:
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
    status = env.run(
        "status",
        "--mcp-json",
        str(mcp_json),
        "--env-file",
        str(env_file),
        "--var",
        "BASE_URL=x",
    )
    assert status.count("outdated") == 4  # BASE_URL differs from what was synced


def test_missing_variable_names_the_variable(env: "_Env") -> None:
    mcp_json = env.mcp_json("a.json", {"remote": {"url": "${BASE_URL}/mcp"}})

    result = env.run("sync", "--mcp-json", str(mcp_json), check=False)

    assert "BASE_URL" in result
    assert set(env.claude()) == {"unmanaged"}


def test_two_sources_merge_side_by_side(env: "_Env") -> None:
    a = env.mcp_json("a.json", {"a1": LOCAL_SERVER})
    b = env.mcp_json("b.json", {"b1": LOCAL_SERVER})

    _ = env.run("sync", "--mcp-json", str(a))
    _ = env.run("sync", "--mcp-json", str(b))
    _ = env.run("sync", "--mcp-json", str(a))

    for servers in (env.claude(), env.codex(), env.antigravity()):
        assert set(servers) == {"unmanaged", "a1", "b1"}
    assert set(env.opencode()) == {"a1", "b1"}
    codex_text = env.codex_path.read_text()
    assert codex_text.count("# BEGIN global_mcp.py") == 2
    assert codex_text.count("# END global_mcp.py") == 2

    _ = env.run("remove", "--mcp-json", str(a))

    for servers in (env.claude(), env.codex(), env.antigravity()):
        assert set(servers) == {"unmanaged", "b1"}
    assert set(env.opencode()) == {"b1"}


def test_merge_keeps_and_override_drops_servers_not_in_file(env: "_Env") -> None:
    a = env.mcp_json("a.json", {"a1": LOCAL_SERVER, "stale": LOCAL_SERVER})
    _ = env.run("sync", "--mcp-json", str(a))
    # Codex appends its own tables before the trailing END marker; they must survive rewrites.
    _ = env.codex_path.write_text(
        env.codex_path.read_text().replace(
            "# END", '[hooks.state."x"]\nhash = "h"\n# END'
        )
    )
    a = env.mcp_json("a.json", {"a1": {"command": "new"}})

    merged = env.run("sync", "--mcp-json", str(a))

    assert "kept, not in file: stale, unmanaged" in merged
    assert set(env.claude()) == {"unmanaged", "a1", "stale"}

    overridden = env.run("sync", "--mcp-json", str(a), "--mode", "override")

    assert "dropped: stale, unmanaged" in overridden
    for servers in (env.claude(), env.codex(), env.antigravity(), env.opencode()):
        assert set(servers) == {"a1"}
    codex = tomllib.loads(env.codex_path.read_text())
    assert codex["model"] == "keep"
    assert codex["hooks"]["state"]["x"] == {"hash": "h"}
    assert "OPENWIKI" not in env.codex_path.read_text()
    assert "ok" in env.run("sync", "--mcp-json", str(a), "--mode", "override")


@final
class _Env:
    def __init__(self, tmp_path: pathlib.Path) -> None:
        self.home = tmp_path
        self.codex_path = tmp_path / ".codex/config.toml"
        self.configs = [
            tmp_path / ".claude.json",
            self.codex_path,
            tmp_path / ".config/opencode/opencode.json",
            tmp_path / ".gemini/config/mcp_config.json",
        ]
        _ = self.configs[0].write_text(
            json.dumps({"mcpServers": {"unmanaged": {"command": "keep"}}})
        )
        self.codex_path.parent.mkdir()
        _ = self.codex_path.write_text(
            'model = "keep"\n\n# OPENWIKI:MCP:START\n[mcp_servers.unmanaged]\ncommand = "keep"\n# OPENWIKI:MCP:END\n'
        )
        self.configs[2].parent.mkdir(parents=True)
        self.configs[3].parent.mkdir(parents=True)
        _ = self.configs[3].write_text(
            json.dumps({"mcpServers": {"unmanaged": {"command": "keep"}}})
        )

    def mcp_json(self, name: str, servers: dict[str, object]) -> pathlib.Path:
        path = self.home / name
        _ = path.write_text(json.dumps({"mcpServers": servers}))
        return path

    def run(self, *args: str, check: bool = True) -> str:
        environment = {"HOME": str(self.home), "PATH": os.environ["PATH"]}
        result = subprocess.run(
            ["python3", str(_SCRIPT), *args],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        if check:
            assert result.returncode == 0, result.stderr
        return result.stdout + result.stderr

    def claude(self) -> dict[str, object]:
        return json.loads(self.configs[0].read_text())["mcpServers"]

    def codex(self) -> dict[str, object]:
        return tomllib.loads(self.codex_path.read_text()).get("mcp_servers", {})

    def opencode(self) -> dict[str, object]:
        path = self.configs[2]
        return json.loads(path.read_text())["mcp"]["servers"] if path.exists() else {}

    def antigravity(self) -> dict[str, object]:
        return json.loads(self.configs[3].read_text())["mcpServers"]
