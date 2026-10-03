import inspect
import json
import os
import pathlib
import subprocess
import time
from typing import final

import pytest


@pytest.fixture
def voice(tmp_path: pathlib.Path) -> "_VoiceChat":
    return _VoiceChat(tmp_path)


def test_replies_with_claude_result_in_auto_mode(voice: "_VoiceChat") -> None:
    voice.claude_replies("It is sunny.", session_id="ses-1")

    result = voice.say("What's the weather?")

    assert result.stdout.strip() == "It is sunny."
    assert "--permission-mode\nauto" in "\n".join(voice.claude_args())
    assert (
        voice.claude_args()[voice.claude_args().index("-p") + 1]
        == "What's the weather?"
    )


def test_resumes_a_recent_session(voice: "_VoiceChat") -> None:
    voice.claude_replies("Sure.", session_id="ses-1")
    _ = voice.say("Remember the word pelican.")

    _ = voice.say("Which word?")

    assert "--resume\nses-1" in "\n".join(voice.claude_args())


def test_starts_a_new_session_once_the_last_turn_is_old(voice: "_VoiceChat") -> None:
    voice.claude_replies("Sure.", session_id="ses-1")
    _ = voice.say("Remember the word pelican.")
    voice.age_session(minutes=30)

    _ = voice.say("Which word?")

    assert "--resume" not in voice.claude_args()


def test_stop_phrase_prints_nothing_without_calling_claude(voice: "_VoiceChat") -> None:
    result = voice.say("Stop.")

    assert result.stdout == ""
    assert not voice.args_file.exists()


def test_silence_ends_the_conversation(voice: "_VoiceChat") -> None:
    result = voice.say("  ")

    assert result.stdout == ""
    assert not voice.args_file.exists()


def test_new_conversation_forgets_the_session(voice: "_VoiceChat") -> None:
    voice.claude_replies("Sure.", session_id="ses-1")
    _ = voice.say("Remember the word pelican.")
    _ = voice.say("New conversation.")

    _ = voice.say("Which word?")

    assert "--resume" not in voice.claude_args()


def test_reply_is_stripped_of_markdown_for_speech(voice: "_VoiceChat") -> None:
    voice.claude_replies(
        "**Done.** See [the docs](https://example.test) and run `ls`.",
        session_id="ses-1",
    )

    result = voice.say("Do it.")

    assert result.stdout.strip() == "Done. See the docs and run ls."


def test_claude_failure_is_spoken_as_an_apology(voice: "_VoiceChat") -> None:
    voice.claude_fails()

    result = voice.say("Do it.")

    assert result.returncode == 0
    assert result.stdout.startswith("Sorry")


@final
class _VoiceChat:
    """Runs voice_chat.sh against a stub `claude` on PATH, with an isolated HOME and state dir."""

    def __init__(self, root: pathlib.Path):
        self.root: pathlib.Path = root
        self.bin: pathlib.Path = root / "bin"
        self.home: pathlib.Path = root / "home"
        self.state: pathlib.Path = root / "state"
        self.args_file: pathlib.Path = root / "claude-args"
        self.bin.mkdir()
        self.home.mkdir()

    def claude_replies(self, result: str, session_id: str) -> None:
        output = json.dumps(
            {
                "type": "result",
                "is_error": False,
                "result": result,
                "session_id": session_id,
            }
        )
        self._install_claude(output, exit_code=0)

    def claude_fails(self) -> None:
        self._install_claude("", exit_code=1)

    def say(self, text: str) -> subprocess.CompletedProcess[str]:
        env = {
            **os.environ,
            "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}",
            "HOME": str(self.home),
            "VOICE_CHAT_STATE_DIR": str(self.state),
        }
        return subprocess.run(
            ["bash", str(_VOICE_CHAT)],
            input=text,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def claude_args(self) -> list[str]:
        return self.args_file.read_text().splitlines()

    def age_session(self, minutes: int) -> None:
        old = time.time() - minutes * 60
        os.utime(self.state / "session", (old, old))

    def _install_claude(self, output: str, exit_code: int) -> None:
        _ = (self.root / "claude.out").write_text(output)
        script = self.bin / "claude"
        _ = script.write_text(
            inspect.cleandoc(f"""
                #!/bin/bash
                printf "%s\\n" "$@" > "{self.args_file}"
                cat "{self.root}/claude.out"
                exit {exit_code}
            """)
        )
        script.chmod(0o755)


_VOICE_CHAT = pathlib.Path(__file__).parent.parent / "scripts/voice_chat.sh"
