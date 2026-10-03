#!/usr/bin/env python3
"""Build the "Ask Claude" Siri shortcut, sign it, and open the Shortcuts import dialog.

The shortcut is a spoken conversation loop: dictate, pass the text to voice_chat.sh (which
runs Claude Code headlessly), speak the reply, repeat. voice_chat.sh prints nothing when the
user says "stop" or stays silent, and the shortcut then says goodbye and ends — Shortcuts' If
action can only test a shell script result for having a value, not for specific text.

The `shortcuts` CLI cannot create shortcuts, but it can sign a hand-built one, and opening a
signed file imports it after one click. Stdlib-only, so it runs under any interpreter.
Usage: python3 scripts/install_ask_claude_shortcut.py
"""

import pathlib
import plistlib
import subprocess
import tempfile
import uuid


def build_workflow() -> dict[str, object]:
    """Return the shortcut as Shortcuts' (undocumented) workflow plist structure."""
    repeat, dictate, shell, condition = (_new_id() for _ in range(4))
    reply = _output_of(shell, "Shell Script Result")
    actions = [
        _action(
            "repeat.count",
            GroupingIdentifier=repeat,
            WFControlFlowMode=0,
            WFRepeatCount=20,
        ),
        _action("dictatetext", UUID=dictate, WFDictateTextStopListening="After Pause"),
        _action(
            "runshellscript",
            UUID=shell,
            Shell="/bin/zsh",
            InputMode="to stdin",
            Script='"$HOME/.local/bin/voice_chat.sh"',
            Input=_attachment(_output_of(dictate, "Dictated Text")),
        ),
        _action(
            "conditional",
            GroupingIdentifier=condition,
            WFControlFlowMode=0,
            WFCondition=101,  # "does not have any value"
            WFInput={"Type": "Variable", "Variable": _attachment(reply)},
        ),
        _action("speaktext", WFText=_text("Goodbye."), WFSpeakTextWait=True),
        _action("exit"),
        _action("conditional", GroupingIdentifier=condition, WFControlFlowMode=2),
        _action("speaktext", WFText=_text_of(reply), WFSpeakTextWait=True),
        _action("repeat.count", GroupingIdentifier=repeat, WFControlFlowMode=2),
    ]
    return {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "2607.0.2",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 4282601983,
            "WFWorkflowIconGlyphNumber": 59511,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": [],
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowTypes": [],
        "WFQuickActionSurfaces": [],
        "WFWorkflowHasShortcutInputVariables": False,
    }


def main() -> None:
    # Not cleaned up: the import dialog reads the file after `open` has already returned.
    directory = pathlib.Path(tempfile.mkdtemp(prefix="ask-claude-shortcut-"))
    unsigned = directory / "unsigned.shortcut"
    # The imported shortcut takes its name, and so its Siri phrase, from this file name.
    signed = directory / "Ask Claude.shortcut"
    with unsigned.open("wb") as file:
        plistlib.dump(build_workflow(), file, fmt=plistlib.FMT_BINARY)

    _ = subprocess.run(
        ["shortcuts", "sign", "--input", str(unsigned), "--output", str(signed)],
        check=True,
    )
    _ = subprocess.run(["open", str(signed)], check=True)
    print('Click "Add Shortcut" in the Shortcuts dialog.')
    print(
        'If an "Ask Claude" shortcut already exists, delete it and rename the import to "Ask Claude".'
    )


def _new_id() -> str:
    return str(uuid.uuid4()).upper()


def _action(identifier: str, **params: object) -> dict[str, object]:
    return {
        "WFWorkflowActionIdentifier": f"is.workflow.actions.{identifier}",
        "WFWorkflowActionParameters": params,
    }


def _output_of(action_id: str, name: str) -> dict[str, str]:
    return {"Type": "ActionOutput", "OutputUUID": action_id, "OutputName": name}


def _attachment(variable: dict[str, str]) -> dict[str, object]:
    return {"Value": variable, "WFSerializationType": "WFTextTokenAttachment"}


def _text(string: str) -> dict[str, object]:
    return {
        "Value": {"string": string, "attachmentsByRange": {}},
        "WFSerializationType": "WFTextTokenString",
    }


def _text_of(variable: dict[str, str]) -> dict[str, object]:
    # U+FFFC is the placeholder character a variable occupies inside a text field.
    return {
        "Value": {"string": "￼", "attachmentsByRange": {"{0, 1}": variable}},
        "WFSerializationType": "WFTextTokenString",
    }


if __name__ == "__main__":
    main()
