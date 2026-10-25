"""Exercise real processes/signals and files; substitute only external paid tools."""

import json
import os
import pathlib
import signal
import subprocess
import sys
import time
from collections.abc import Iterator
from typing import Any

import pytest


@pytest.fixture
def workspace(tmp_path: pathlib.Path) -> Iterator["_Workspace"]:
    value = _Workspace(tmp_path)
    try:
        yield value
    finally:
        value.close()


@pytest.mark.parametrize("sig", [signal.SIGINT, signal.SIGTERM, signal.SIGHUP])
def test_signal_deletes_session_pod_and_retains_volume(
    workspace: "_Workspace", sig: int
) -> None:
    process = workspace.start()
    workspace.wait_for("GPU workspace ready", process)
    process.send_signal(sig)
    process.wait(timeout=10)
    assert "created" not in workspace.account()["pods"]
    assert "unrelated" in workspace.account()["pods"]
    assert workspace.account()["volumes"] == ["volume"]
    assert not workspace.state.exists()


def test_cancel_during_create_waits_for_pod_id_then_deletes_it(
    workspace: "_Workspace",
) -> None:
    workspace.mode("slow-create")
    process = workspace.start()
    workspace.wait_for_file("creating", process)
    os.killpg(process.pid, signal.SIGTERM)
    process.wait(timeout=10)
    assert "created" not in workspace.account()["pods"]
    assert not (workspace.root / "opened.json").exists()


@pytest.mark.parametrize("mode", ["ssh-fails", "code-fails"])
def test_setup_failure_deletes_pod(workspace: "_Workspace", mode: str) -> None:
    workspace.mode(mode)
    process = workspace.start()
    assert process.wait(timeout=10) != 0
    assert "created" not in workspace.account()["pods"]
    assert "unrelated" in workspace.account()["pods"]
    assert "Deleted Pod created" in workspace.output()


def test_lost_create_response_is_reconciled_before_cleanup(
    workspace: "_Workspace",
) -> None:
    workspace.mode("lost-response")
    process = workspace.start()
    assert process.wait(timeout=10) != 0
    assert "created" not in workspace.account()["pods"]
    assert "Deleted Pod created" in workspace.output()


@pytest.mark.parametrize(
    "mode, detail",
    [
        ("ssh-fails", "Connection refused"),
        ("gpu-fails", "ModuleNotFoundError: No module named 'torch'"),
    ],
)
def test_setup_failure_reports_underlying_ssh_or_gpu_error(
    workspace: "_Workspace",
    mode: str,
    detail: str,
) -> None:
    workspace.mode(mode)
    process = workspace.start()
    assert process.wait(timeout=10) != 0
    assert detail in workspace.output()
    assert "192.0.2.10:22022" in workspace.output()
    assert "created" not in workspace.account()["pods"]


@pytest.mark.parametrize("status", ["RUNNING", "EXITED"])
def test_adopts_only_explicit_pod_and_refreshes_ssh_config(
    workspace: "_Workspace",
    status: str,
) -> None:
    account = workspace.account()
    account["pods"]["existing"] = {
        "id": "existing",
        "name": "dev",
        "networkVolumeId": "volume",
        "gpuId": "NVIDIA GeForce RTX 4090",
        "desiredStatus": status,
    }
    workspace.write_account(account)
    process = workspace.start("--adopt-pod-id", "existing")
    workspace.wait_for("GPU workspace ready", process)
    assert workspace.account()["pods"]["existing"]["desiredStatus"] == "RUNNING"
    config = (workspace.root / "home/.ssh/config").read_text()
    assert "Host other" in config
    assert "HostName 192.0.2.10" in config
    assert "Port 22022" in config
    assert json.loads((workspace.root / "opened.json").read_text()) == [
        "--new-window",
        "--remote",
        "ssh-remote+runpod-devbox",
        "/workspace",
    ]
    process.send_signal(signal.SIGINT)
    process.wait(timeout=10)
    assert "existing" not in workspace.account()["pods"]
    assert "created" not in workspace.account()["pods"]


def test_unresolved_creation_keeps_journal_and_prevents_duplicate_pods(
    workspace: "_Workspace",
) -> None:
    workspace.mode("lost-invisible")
    process = workspace.start()
    assert process.wait(timeout=10) != 0
    assert workspace.state.exists()
    intent = workspace.state.read_text()
    retry = workspace.start(log_name="retry.log")
    assert retry.wait(timeout=10) != 0
    assert workspace.state.read_text() == intent
    workspace.mode("ok")
    recovery = workspace.start("--cleanup", log_name="recovery.log")
    assert recovery.wait(timeout=10) == 0
    assert "created" not in workspace.account()["pods"]
    assert not workspace.state.exists()


def test_rejects_adoption_of_pod_using_another_volume(workspace: "_Workspace") -> None:
    process = workspace.start("--adopt-pod-id", "unrelated")
    assert process.wait(timeout=10) != 0
    assert "unrelated" in workspace.account()["pods"]
    assert not workspace.state.exists()


def test_ssh_alias_overrides_existing_wildcard_defaults(
    workspace: "_Workspace",
) -> None:
    config = workspace.root / "home/.ssh/config"
    config.write_text(
        "Host *\n    User developer\n    Port 22\nHost other\n    HostName other.example\n"
    )
    process = workspace.start()
    workspace.wait_for("GPU workspace ready", process)
    effective = subprocess.run(
        ["/usr/bin/ssh", "-G", "-F", str(config), "runpod-devbox"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "user root\n" in effective
    assert "port 22022\n" in effective
    assert "Host other" in config.read_text()


def test_registers_key_without_removing_existing_account_keys(
    workspace: "_Workspace",
) -> None:
    account = workspace.account()
    account["keys"] = ["ssh-ed25519 AAAAOTHER another-machine"]
    workspace.write_account(account)
    process = workspace.start()
    workspace.wait_for("GPU workspace ready", process)
    assert workspace.account()["keys"] == [
        "ssh-ed25519 AAAAOTHER another-machine",
        "ssh-ed25519 AAAATEST local",
    ]
    process.send_signal(signal.SIGTERM)
    assert process.wait(timeout=10) == 0


def test_no_local_gpu_stock_prevents_pod_creation(workspace: "_Workspace") -> None:
    workspace.mode("no-stock")
    process = workspace.start()
    assert process.wait(timeout=10) != 0
    assert not (workspace.root / "creating").exists()
    assert "unrelated" in workspace.account()["pods"]


def test_second_session_cannot_delete_first_sessions_pod(
    workspace: "_Workspace",
) -> None:
    first = workspace.start()
    workspace.wait_for("GPU workspace ready", first)
    second = workspace.start(log_name="second.log")
    assert second.wait(timeout=10) != 0
    assert first.poll() is None
    assert "created" in workspace.account()["pods"]
    first.send_signal(signal.SIGINT)
    first.wait(timeout=10)


def test_failed_cleanup_keeps_recovery_state(workspace: "_Workspace") -> None:
    process = workspace.start()
    workspace.wait_for("GPU workspace ready", process)
    workspace.mode("delete-fails")
    process.send_signal(signal.SIGTERM)
    assert process.wait(timeout=10) != 0
    assert workspace.state.exists()
    assert "created" in workspace.account()["pods"]
    workspace.mode("ok")
    recovery = workspace.start("--cleanup", log_name="recovery.log")
    assert recovery.wait(timeout=10) == 0
    assert "created" not in workspace.account()["pods"]
    assert not workspace.state.exists()


def test_tunnel_mode_bootstraps_without_ssh_and_opens_desktop(
    workspace: "_Workspace",
) -> None:
    workspace.mode("ssh-fails")
    process = workspace.start("--connection", "tunnel")
    workspace.wait_for("GPU workspace ready", process)
    args = json.loads((workspace.root / "create-args.json").read_text())
    assert (
        args[args.index("--ssh") + 1] == "false"
        if "--ssh" in args
        else "--ssh=false" in args
    )
    assert "22/tcp" not in args
    assert "--docker-args" in args
    assert json.loads((workspace.root / "opened.json").read_text()) == [
        "--new-window",
        "--remote",
        "tunnel+dima-gpu-dev",
        "/workspace",
    ]
    process.send_signal(signal.SIGINT)
    assert process.wait(timeout=10) == 0
    assert "created" not in workspace.account()["pods"]


def test_tunnel_waits_for_logs_while_container_initializes(
    workspace: "_Workspace",
) -> None:
    workspace.mode("logs-not-ready")
    process = workspace.start("--connection", "tunnel", "--ready-timeout", "2")
    workspace.wait_for("GPU workspace ready", process)
    assert (workspace.root / "log-timeout").exists()
    process.send_signal(signal.SIGINT)
    assert process.wait(timeout=10) == 0
    assert "created" not in workspace.account()["pods"]


def test_tunnel_login_is_shown_and_cancellation_deletes_pod(
    workspace: "_Workspace",
) -> None:
    workspace.mode("tunnel-login")
    process = workspace.start("--connection", "tunnel", "--ready-timeout", "10")
    workspace.wait_for("FAKE-CODE", process)
    assert "github.com/login/device" in workspace.output()
    assert not (workspace.root / "opened.json").exists()
    process.send_signal(signal.SIGTERM)
    assert process.wait(timeout=10) == 0
    assert "created" not in workspace.account()["pods"]


def test_tunnel_failure_deletes_pod_with_actionable_error(
    workspace: "_Workspace",
) -> None:
    workspace.mode("tunnel-fails")
    process = workspace.start("--connection", "tunnel")
    assert process.wait(timeout=10) != 0
    assert "relay connection refused" in workspace.output()
    assert "created" not in workspace.account()["pods"]


def test_custom_gpu_selection_and_cleanup_without_gpu_arg(
    workspace: "_Workspace",
) -> None:
    workspace.mode("lost-invisible")
    process = workspace.start("--gpu", "NVIDIA RTX A5000")
    assert process.wait(timeout=10) != 0
    args = json.loads((workspace.root / "create-args.json").read_text())
    assert args[args.index("--gpu-id") + 1] == "NVIDIA RTX A5000"
    assert workspace.state.exists()
    workspace.mode("ok")
    recovery = workspace.start("--cleanup", log_name="recovery.log")
    assert recovery.wait(timeout=10) == 0
    assert "created" not in workspace.account()["pods"]
    assert not workspace.state.exists()


@pytest.mark.parametrize("connection", ["ssh", "tunnel"])
def test_falls_back_to_ide_when_code_missing(
    workspace: "_Workspace", connection: str
) -> None:
    (workspace.root / "bin/code").rename(workspace.root / "bin/ide")
    process = workspace.start("--connection", connection)
    workspace.wait_for_file("opened.json", process)
    os.killpg(process.pid, signal.SIGTERM)
    assert process.wait(timeout=10) == 0


@pytest.mark.parametrize(
    ("connection", "remote_path", "expected_remote"),
    [
        ("ssh", "/workspace/project-a", "ssh-remote+runpod-devbox"),
        ("tunnel", "project-a", "tunnel+dima-gpu-dev"),
    ],
)
def test_custom_remote_path_opens_requested_folder(
    workspace: "_Workspace",
    connection: str,
    remote_path: str,
    expected_remote: str,
) -> None:
    process = workspace.start("--connection", connection, "--remote-path", remote_path)
    workspace.wait_for_file("opened.json", process)
    opened = json.loads((workspace.root / "opened.json").read_text())
    assert opened == [
        "--new-window",
        "--remote",
        expected_remote,
        "/workspace/project-a",
    ]
    os.killpg(process.pid, signal.SIGTERM)
    assert process.wait(timeout=10) == 0


class _Workspace:
    def __init__(self, root: pathlib.Path):
        self.root = root
        self.state = root / "state/session.json"
        self.processes: list[subprocess.Popen[bytes]] = []
        self.mode("ok")
        home = root / "home"
        (home / ".ssh").mkdir(parents=True)
        (home / ".ssh/key").write_text("fake private key")
        (home / ".ssh/key.pub").write_text("ssh-ed25519 AAAATEST local")
        (home / ".ssh/config").write_text("Host other\n    HostName other.example\n")
        self.write_account(
            {
                "pods": {"unrelated": {"id": "unrelated", "networkVolumeId": "other"}},
                "volumes": ["volume"],
            }
        )
        binary = root / "bin"
        binary.mkdir()
        helper = pathlib.Path(__file__).parent / "helpers/runpod_fake_tools.py"
        for name in ("runpodctl", "ssh", "code"):
            tool = binary / name
            tool.write_text(f"#!{sys.executable}\n" + helper.read_text())
            tool.chmod(0o755)

    def start(
        self, *args: str, log_name: str = "session.log"
    ) -> subprocess.Popen[bytes]:
        script = pathlib.Path(__file__).parent.parent / "scripts/runpod/runpod_dev.py"
        assert script.exists(), "Runpod workspace launcher has not been implemented"
        env = {
            "HOME": str(self.root / "home"),
            "PATH": f"{self.root / 'bin'}:{os.defpath}",
            "FAKE_RUNPOD_ROOT": str(self.root),
            "PYTHONUNBUFFERED": "1",
        }
        with (self.root / log_name).open("wb") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(script),
                    "--volume-id",
                    "volume",
                    "--state-dir",
                    str(self.root / "state"),
                    "--ssh-key",
                    str(self.root / "home/.ssh/key"),
                    "--ready-timeout",
                    "0.5",
                    "--poll-interval",
                    "0.05",
                    *args,
                ],
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        self.processes.append(process)
        return process

    def mode(self, value: str) -> None:
        (self.root / "mode").write_text(value)

    def account(self) -> dict[str, Any]:
        return json.loads((self.root / "account.json").read_text())

    def write_account(self, account: dict[str, Any]) -> None:
        (self.root / "account.json").write_text(json.dumps(account))

    def output(self) -> str:
        return (self.root / "session.log").read_text()

    def wait_for(self, value: str, process: subprocess.Popen[bytes]) -> None:
        deadline = time.monotonic() + 8
        while value not in self.output():
            assert process.poll() is None, self.output()
            assert time.monotonic() < deadline, self.output()
            time.sleep(0.02)

    def wait_for_file(self, name: str, process: subprocess.Popen[bytes]) -> None:
        deadline = time.monotonic() + 8
        while not (self.root / name).exists():
            assert process.poll() is None, self.output()
            assert time.monotonic() < deadline, self.output()
            time.sleep(0.02)

    def close(self) -> None:
        for process in self.processes:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
