import inspect
import json
import os
import pathlib
import subprocess
from typing import final

import pytest


@pytest.fixture
def stubs(tmp_path: pathlib.Path) -> "_Stubs":
    return _Stubs(tmp_path)


def test_claude_read_only_runs_in_plan_mode_and_prints_result(stubs: "_Stubs") -> None:
    stubs.install("claude", json.dumps(_CLAUDE_RESULT))

    result = stubs.run("claude")

    assert result.returncode == 0
    assert "--permission-mode\nplan" in "\n".join(stubs.args())
    assert result.stdout.startswith("The plugin bridges .mcp.json into opencode.")
    assert "session=b45014ad-claude" in result.stdout


def test_claude_write_accepts_edits(stubs: "_Stubs") -> None:
    stubs.install("claude", json.dumps(_CLAUDE_RESULT))

    _ = stubs.run("claude", "--write")

    assert "--permission-mode\nacceptEdits" in "\n".join(stubs.args())


def test_resume_passes_session_and_sends_task_without_preamble(stubs: "_Stubs") -> None:
    stubs.install("claude", json.dumps(_CLAUDE_RESULT))

    _ = stubs.run("claude", "--resume", "b45014ad-claude", task="And the tests?")

    args = stubs.args()
    assert "--resume\nb45014ad-claude" in "\n".join(args)
    assert args[args.index("-p") + 1] == "And the tests?"


def test_opencode_read_only_uses_plan_agent_and_prints_last_text(
    stubs: "_Stubs",
) -> None:
    stubs.install("opencode", _OPENCODE_EVENTS)

    result = stubs.run("opencode")

    assert "--agent\nplan" in "\n".join(stubs.args())
    assert result.stdout.startswith("Final answer.")
    assert "Looking." not in result.stdout
    assert "session=ses_opencode" in result.stdout


def test_opencode_write_uses_default_build_agent(stubs: "_Stubs") -> None:
    stubs.install("opencode", _OPENCODE_EVENTS)

    _ = stubs.run("opencode", "--write")

    assert "--agent" not in stubs.args()


def test_opencode_reports_auto_rejected_permissions(stubs: "_Stubs") -> None:
    stubs.install(
        "opencode",
        _OPENCODE_EVENTS,
        stderr="! permission requested: external_directory (/elsewhere/*); auto-rejecting\n",
    )

    result = stubs.run("opencode")

    assert "denied: external_directory" in result.stdout


def test_agy_reports_denied_actions(stubs: "_Stubs") -> None:
    denied = {
        **_AGY_RESULT,
        "response": "",
        "denied_actions": [{"action": "write_file"}],
    }
    stubs.install("agy", json.dumps(denied))

    result = stubs.run("agy", "--write")

    assert "--mode\naccept-edits" in "\n".join(stubs.args())
    assert "denied: write_file" in result.stdout


def test_agy_error_exits_nonzero_with_message(stubs: "_Stubs") -> None:
    error = {
        "conversation_id": "",
        "status": "ERROR",
        "response": "",
        "error": "model not recognized",
    }
    stubs.install("agy", json.dumps(error), exit_code=1)

    result = stubs.run("agy")

    assert result.returncode == 1
    assert "model not recognized" in result.stderr


@final
class _Stubs:
    """Fake agent CLIs on PATH that record their arguments and replay canned output."""

    def __init__(self, root: pathlib.Path):
        self.root: pathlib.Path = root
        self.bin: pathlib.Path = root / "bin"
        self.args_file: pathlib.Path = root / "args"
        self.bin.mkdir()

    def install(
        self, cli: str, stdout: str, stderr: str = "", exit_code: int = 0
    ) -> None:
        _ = (self.root / f"{cli}.out").write_text(stdout)
        _ = (self.root / f"{cli}.err").write_text(stderr)
        script = self.bin / cli
        _ = script.write_text(
            inspect.cleandoc(f"""
                #!/bin/bash
                printf "%s\\n" "$@" > "{self.args_file}"
                cat "{self.root}/{cli}.out"
                cat "{self.root}/{cli}.err" >&2
                exit {exit_code}
            """)
        )
        script.chmod(0o755)

    def args(self) -> list[str]:
        return self.args_file.read_text().splitlines()

    def run(
        self, *args: str, task: str = "Explain the plugin."
    ) -> subprocess.CompletedProcess[str]:
        env = {**os.environ, "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}"}
        return subprocess.run(
            ["bash", str(_DELEGATE), *args],
            input=task,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )


_DELEGATE = (
    pathlib.Path(__file__).parent.parent
    / ".agents/skills/cli-subagents/scripts/delegate.sh"
)

# Output shapes captured from real headless runs (claude 2.1.288, opencode 2.0.20, agy 1.2.16).
_CLAUDE_RESULT: dict[str, object] = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "session_id": "b45014ad-claude",
    "result": "The plugin bridges .mcp.json into opencode.",
    "permission_denials": [],
}
_OPENCODE_EVENTS = "\n".join(
    json.dumps(event)
    for event in [
        {"type": "step_start", "sessionID": "ses_opencode"},
        {
            "type": "text",
            "sessionID": "ses_opencode",
            "part": {"type": "text", "text": "Looking."},
        },
        {"type": "tool_use", "sessionID": "ses_opencode"},
        {
            "type": "text",
            "sessionID": "ses_opencode",
            "part": {"type": "text", "text": "Final answer."},
        },
        {"type": "step_finish", "sessionID": "ses_opencode"},
    ]
)
_AGY_RESULT: dict[str, object] = {
    "conversation_id": "conv-agy",
    "status": "SUCCESS",
    "response": "Done.\n",
}
