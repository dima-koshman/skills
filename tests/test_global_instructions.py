import os
import pathlib
import subprocess

_SCRIPT = pathlib.Path(__file__).parent.parent / "scripts/global_instructions.py"


def _run(home: pathlib.Path, *args: str) -> str:
    environment = {"HOME": str(home), "PATH": os.environ["PATH"]}
    result = subprocess.run(
        ["python3", str(_SCRIPT), *args],
        capture_output=True,
        text=True,
        env=environment,
        check=True,
    )
    return result.stdout


def test_two_sources_sync_update_and_remove_independently(
    tmp_path: pathlib.Path,
) -> None:
    (tmp_path / ".claude").mkdir()
    claude = tmp_path / ".claude/CLAUDE.md"
    _ = claude.write_text("# Mine\n\nkeep me\n")
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    _ = a.write_text("A one\n")
    _ = b.write_text("B one\n")

    _ = _run(tmp_path, "sync", "--instructions-file", str(a))
    _ = _run(tmp_path, "sync", "--instructions-file", str(b))
    _ = a.write_text("A two\n")

    assert "outdated" in _run(tmp_path, "status", "--instructions-file", str(a))
    assert "updated" in _run(tmp_path, "sync", "--instructions-file", str(a))
    assert "ok" in _run(tmp_path, "sync", "--instructions-file", str(a))
    text = claude.read_text()
    assert text.startswith("# Mine\n\nkeep me\n")
    assert "A two" in text and "A one" not in text and "B one" in text
    assert "<!-- BEGIN global_instructions.py ~/a.md " in text
    assert not (tmp_path / ".codex/AGENTS.md").exists()  # harness not installed

    _ = _run(tmp_path, "remove", "--instructions-file", str(a))

    assert "A two" not in claude.read_text()
    assert "B one" in claude.read_text()

    _ = _run(tmp_path, "remove", "--instructions-file", str(b))

    assert claude.read_text() == "# Mine\n\nkeep me\n"
