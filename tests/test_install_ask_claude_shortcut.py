import importlib.util
import pathlib
import typing

import pytest


@pytest.fixture
def workflow() -> dict[str, object]:
    return _load_generator().build_workflow()


def test_loop_listens_runs_voice_chat_and_speaks_the_reply(
    workflow: dict[str, object],
) -> None:
    identifiers = [
        _identifier(workflow, index) for index in range(len(_actions(workflow)))
    ]

    assert identifiers == [
        "repeat.count",
        "dictatetext",
        "runshellscript",
        "conditional",
        "speaktext",
        "exit",
        "conditional",
        "speaktext",
        "repeat.count",
    ]


def test_shell_script_reads_the_dictated_text_on_stdin(
    workflow: dict[str, object],
) -> None:
    assert "voice_chat.sh" in str(_param(workflow, 2, "Script"))
    assert _param(workflow, 2, "InputMode") == "to stdin"
    assert _param(workflow, 2, "Input", "Value", "OutputUUID") == _param(
        workflow, 1, "UUID"
    )


def test_empty_reply_says_goodbye_and_stops(workflow: dict[str, object]) -> None:
    assert _param(workflow, 3, "WFCondition") == 101  # "does not have any value"
    assert _param(workflow, 3, "WFInput", "Variable", "Value", "OutputUUID") == _param(
        workflow, 2, "UUID"
    )
    assert _param(workflow, 4, "WFText", "Value", "string") == "Goodbye."
    assert _identifier(workflow, 5) == "exit"


def test_reply_is_spoken_after_the_end_check(workflow: dict[str, object]) -> None:
    spoken = _param(
        workflow, 7, "WFText", "Value", "attachmentsByRange", "{0, 1}", "OutputUUID"
    )

    assert spoken == _param(workflow, 2, "UUID")
    assert _param(workflow, 7, "WFSpeakTextWait") is True


class _Generator(typing.Protocol):
    def build_workflow(self) -> dict[str, object]: ...


def _load_generator() -> _Generator:
    path = (
        pathlib.Path(__file__).parent.parent / "scripts/install_ask_claude_shortcut.py"
    )
    spec = importlib.util.spec_from_file_location("install_ask_claude_shortcut", path)
    assert spec and spec.loader, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return typing.cast(_Generator, typing.cast(object, module))


def _actions(workflow: dict[str, object]) -> list[object]:
    actions = workflow["WFWorkflowActions"]
    assert isinstance(actions, list)
    return typing.cast(list[object], actions)


def _identifier(workflow: dict[str, object], index: int) -> str:
    identifier = _at(_actions(workflow)[index], "WFWorkflowActionIdentifier")
    return str(identifier).removeprefix("is.workflow.actions.")


def _param(workflow: dict[str, object], index: int, *keys: str) -> object:
    return _at(_actions(workflow)[index], "WFWorkflowActionParameters", *keys)


def _at(value: object, *keys: str) -> object:
    for key in keys:
        assert isinstance(value, dict), f"expected a dict at {key!r}, got {value!r}"
        value = typing.cast(dict[str, object], value)[key]

    return value
