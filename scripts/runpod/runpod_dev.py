#!/usr/bin/env python3
"""Own a Runpod GPU development session until Ctrl+C or task termination.

Requires Python 3.11+, runpodctl, and code with the selected remote extension.
Credentials: --env-file (RUNPOD_API_KEY only), otherwise ~/.runpod/config.toml.
The Pod is deleted on normal cancellation or failure; the network volume is retained.
SIGKILL, power loss, and unavailable APIs require recovery with --cleanup.
"""

import argparse
import contextlib
import fcntl
import ipaddress
import json
import os
import pathlib
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from typing import Any

# This executable intentionally loads its sibling from the script directory.
import runpod_tunnel  # pyright: ignore[reportImplicitRelativeImport]


def main() -> int:
    args = _arguments()
    try:
        return _Session(args).run()
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Runpod: {error}", file=sys.stderr, flush=True)
        return 1


class _ToolError(RuntimeError):
    def __init__(self, code: str, action: str):
        super().__init__(f"{action} failed ({code})")
        self.code = code


class _Cancelled(Exception):
    pass


class _Session:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.directory = pathlib.Path(args.state_dir).expanduser().resolve()
        self.state_path = self.directory / "session.json"
        self.state: dict[str, Any] = {}
        self.stop = threading.Event()
        self.env = dict(os.environ)
        # Use an explicit credential source, not a stale direnv value or project .env.
        self.env.pop("RUNPOD_API_KEY", None)
        env_file = pathlib.Path(args.env_file).expanduser()
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.strip().startswith(
                    ("RUNPOD_API_KEY=", "export RUNPOD_API_KEY=")
                ):
                    values = shlex.split(line.partition("=")[2], comments=True)
                    if len(values) != 1:
                        raise ValueError(f"Invalid RUNPOD_API_KEY in {env_file}")
                    self.env["RUNPOD_API_KEY"] = values[0]

    def run(self) -> int:
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (self.directory / "session.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError(
                    "A GPU workspace task already owns this session."
                ) from error
            for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                signal.signal(sig, self._signal)
            if self.state_path.exists():
                self.state = json.loads(self.state_path.read_text())
                if self.state.get("volume_id") != self.args.volume_id:
                    raise RuntimeError(
                        "Saved session uses another volume; use its original --volume-id to clean up."
                    )
            status = 0
            try:
                self._prepare()
                if not self.args.cleanup:
                    self._connect()
                    print(
                        "GPU workspace ready. Keep this task running; Ctrl+C deletes its Pod.",
                        flush=True,
                    )
                    self.stop.wait()
            except _Cancelled:
                print("Cancellation received; cleaning up.", flush=True)
            except (OSError, ValueError, RuntimeError) as error:
                print(f"Runpod: {error}", file=sys.stderr, flush=True)
                status = 1
            finally:
                if not self._cleanup():
                    status = 1
            return status

    def _signal(self, _sig: int, _frame: object) -> None:
        # Do not raise inside create: its response carries the ID needed for cleanup.
        self.stop.set()

    def _check_cancel(self) -> None:
        if self.stop.is_set():
            raise _Cancelled()

    def _cli(self, *args: str) -> Any:
        try:
            result = subprocess.run(
                ["runpodctl", *args],
                check=False,
                capture_output=True,
                text=True,
                cwd=self.directory,
                env=self.env,
                timeout=40,
                start_new_session=True,
            )
        except subprocess.TimeoutExpired as error:
            if args[:2] == ("pod", "logs"):
                return []
            raise _ToolError("network_timeout", " ".join(args[:2])) from error
        # CLI responses can contain credentials; never print raw stdout/stderr.
        if result.returncode:
            code = "cli_error"
            for line in result.stderr.splitlines():
                with contextlib.suppress(json.JSONDecodeError):
                    code = json.loads(line).get("code", code)
            if args[:2] == ("pod", "logs") and code in (
                "timeout",
                "network_timeout",
                "not_ready",
            ):
                return []
            raise _ToolError(code, " ".join(args[:2]))
        try:
            if args[:2] == ("pod", "logs"):
                return [
                    json.loads(line)
                    for line in result.stdout.splitlines()
                    if line.strip()
                ]
            data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError as error:
            raise _ToolError("invalid_response", " ".join(args[:2])) from error
        if isinstance(data, dict) and "error" in data:
            raise _ToolError(data.get("code", "cli_error"), " ".join(args[:2]))
        return data

    def _pod(self, pod_id: str) -> dict[str, Any] | None:
        try:
            return self._cli("pod", "get", pod_id)
        except _ToolError as error:
            if error.code == "not_found":
                return None
            raise

    def _save(self) -> None:
        _atomic_write(self.state_path, json.dumps(self.state, indent=2) + "\n", 0o600)

    def _validate_pod(self, pod: dict[str, Any]) -> None:
        expected_gpu = (
            self.state.get("gpu", self.args.gpu) if self.args.cleanup else self.args.gpu
        )
        if (
            pod.get("networkVolumeId") != self.args.volume_id
            or pod.get("gpuId") != expected_gpu
        ):
            raise RuntimeError(
                f"Pod {pod['id']} does not match the requested volume/GPU; refusing to adopt it."
            )

    def _recover_create(self) -> None:
        if not self.state.get("request_name") or self.state.get("pod_id"):
            return
        pods = self._cli("pod", "list", "--all")
        matches = [pod for pod in pods if pod.get("name") == self.state["request_name"]]
        if len(matches) > 1:
            raise RuntimeError(
                "Multiple Pods match saved creation intent; manual inspection required."
            )
        if matches:
            pod = self._cli("pod", "get", matches[0]["id"])
            self._validate_pod(pod)
            self.state["pod_id"] = pod["id"]
            self._save()
        else:
            raise RuntimeError(
                "Creation outcome is unresolved; retaining the journal. Retry cleanup after checking the console."
            )

    def _prepare(self) -> None:
        self._recover_create()
        pod = self._pod(self.state["pod_id"]) if self.state.get("pod_id") else None
        if not pod and self.args.adopt_pod_id:
            pod = self._pod(self.args.adopt_pod_id)
            if pod:
                self._validate_pod(pod)
                self.state = {
                    "pod_id": pod["id"],
                    "volume_id": self.args.volume_id,
                    "gpu": self.args.gpu,
                }
                self._save()
        if self.args.cleanup:
            return
        if pod and self.state.get("connection", "ssh") != self.args.connection:
            raise RuntimeError(
                "Saved Pod uses another connection mode; run cleanup first."
            )
        for binary in (
            "runpodctl",
            *(["ssh"] if self.args.connection == "ssh" else []),
        ):
            if not shutil.which(binary):
                raise RuntimeError(f"Required command is missing: {binary}")
        self.editor = _editor_binary()
        volume = self._cli("network-volume", "get", self.args.volume_id)
        if self.args.connection == "ssh":
            self._register_key()
        self._check_cancel()
        if pod:
            self._validate_pod(pod)
            print(f"Using Pod {pod['id']} (deleted when this task ends).", flush=True)
            if pod.get("desiredStatus") != "RUNNING":
                self._cli("pod", "start", pod["id"])
                if self._pod(pod["id"]) is None:
                    raise RuntimeError("Pod disappeared after start.")
            return
        dc = volume["dataCenterId"]
        gpus = self._cli("gpu", "list", "--include-unavailable")
        gpu = next((gpu for gpu in gpus if gpu.get("gpuId") == self.args.gpu), None)
        if (
            not gpu
            or gpu.get("securePricePerHr") is None
            or not any(
                item["dataCenterId"] == dc
                and item["stockStatus"].lower()
                in ("low", "medium", "high", "available")
                for item in gpu.get("dataCenterAvailability", [])
            )
        ):
            raise RuntimeError(f"No {self.args.gpu} stock in {dc}; no Pod created.")
        template = self._cli("template", "get", self.args.template)
        image = template.get("imageName")
        if not image or template.get("isServerless"):
            raise RuntimeError("Template did not return a Pod image.")
        print(
            f"Creating {self.args.gpu} in {dc}: ${gpu['securePricePerHr']}/hour plus disk storage.",
            flush=True,
        )
        self._check_cancel()
        self.state = {
            "volume_id": self.args.volume_id,
            "gpu": self.args.gpu,
            "connection": self.args.connection,
            "request_name": f"dima-gpu-dev-{uuid.uuid4().hex[:12]}",
        }
        self._save()
        connection_args = (
            ["--ssh=false", "--docker-args", runpod_tunnel.docker_args()]
            if self.args.connection == "tunnel"
            else ["--ports", "22/tcp", "--ssh"]
        )
        pod = self._cli(
            "pod",
            "create",
            "--name",
            self.state["request_name"],
            "--image",
            image,
            "--gpu-id",
            self.args.gpu,
            "--gpu-count",
            "1",
            "--cloud-type",
            "SECURE",
            "--min-cuda-version",
            self.args.min_cuda,
            "--data-center-ids",
            dc,
            "--network-volume-id",
            self.args.volume_id,
            "--volume-mount-path",
            "/workspace",
            "--container-disk-in-gb",
            "30",
            *connection_args,
            "--env",
            json.dumps(
                {
                    "HF_HOME": "/workspace/.cache/huggingface",
                    "UV_CACHE_DIR": "/workspace/.cache/uv",
                    "PIP_CACHE_DIR": "/workspace/.cache/pip",
                    **(
                        {"DIMA_TUNNEL_NAME": self.args.tunnel_name}
                        if self.args.connection == "tunnel"
                        else {}
                    ),
                }
            ),
        )
        self.state["pod_id"] = pod["id"]
        self._save()
        if self._pod(pod["id"]) is None:
            raise RuntimeError("Created Pod was not found on read-back.")

    def _register_key(self) -> None:
        key = pathlib.Path(self.args.ssh_key).expanduser()
        if not key.exists():
            key.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            subprocess.run(
                ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
                check=True,
            )
        public = pathlib.Path(str(key) + ".pub")
        if not public.exists():
            raise RuntimeError(f"SSH public key is missing: {public}")
        wanted = public.read_text().split()[:2]
        keys = self._cli("ssh", "list-keys")["keys"]
        if not any(item["key"].split()[:2] == wanted for item in keys):
            self._cli("ssh", "add-key", "--key-file", str(public))
            keys = self._cli("ssh", "list-keys")["keys"]
            if not any(item["key"].split()[:2] == wanted for item in keys):
                raise RuntimeError("SSH key registration did not persist.")

    def _connect(self) -> None:
        if self.args.connection == "tunnel":
            runpod_tunnel.connect(
                self.args,
                self._cli,
                self._check_cancel,
                self.stop,
                self.state["pod_id"],
                self.env,
                self.editor,
            )
            return
        deadline = time.monotonic() + self.args.ready_timeout
        last_error = "SSH address is not assigned yet"
        pod_id = self.state["pod_id"]
        reported_error = ""
        endpoint = ""
        while time.monotonic() < deadline:
            self._check_cancel()
            try:
                info = self._cli("ssh", "info", pod_id)
                ipaddress.ip_address(info["ip"])
                port = int(info["port"])
                if not 1 <= port <= 65535:
                    raise ValueError("Invalid SSH port")
                self._configure_ssh(info["ip"], port)
                current_endpoint = f"{info['ip']}:{port}"
                if current_endpoint != endpoint:
                    endpoint = current_endpoint
                    print(
                        f"Pod {pod_id}: checking SSH/CUDA at root@{endpoint}...",
                        flush=True,
                    )
                result = subprocess.run(
                    [
                        "ssh",
                        "-T",
                        "-o",
                        "BatchMode=yes",
                        "-o",
                        "ConnectTimeout=8",
                        self.args.host,
                        (
                            "nvidia-smi -L && python3 -c 'import torch; assert torch.cuda.is_available(); "
                            'print(torch.__version__, torch.ones(3, device="cuda").sum().item())\' && test -d /workspace'
                        ),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    start_new_session=True,
                    check=False,
                )
                if result.returncode == 0:
                    print(result.stdout.strip(), flush=True)
                    self._check_cancel()
                    result = subprocess.run(
                        [
                            self.editor,
                            "--new-window",
                            "--remote",
                            f"ssh-remote+{self.args.host}",
                            self.args.remote_path,
                        ],
                        env=self.env,
                        timeout=30,
                        start_new_session=True,
                        check=False,
                    )
                    if result.returncode:
                        raise RuntimeError("VS Code failed to open the remote window.")
                    return
                detail = (
                    result.stderr.strip() or result.stdout.strip() or "No output"
                )[-2000:]
                last_error = f"SSH/CUDA probe exited {result.returncode}: {detail}"
            except (
                _ToolError,
                ValueError,
                KeyError,
                subprocess.TimeoutExpired,
            ) as error:
                last_error = str(error)
            if last_error != reported_error:
                print(f"Waiting for readiness: {last_error}", flush=True)
                reported_error = last_error
            if self.stop.wait(self.args.poll_interval):
                raise _Cancelled()
        raise RuntimeError(f"Pod {pod_id} did not become usable: {last_error}")

    def _configure_ssh(self, host: str, port: int) -> None:
        path = pathlib.Path("~/.ssh/config").expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        existing = path.read_text() if path.exists() else ""
        # Remove this alias's own Host block; do not absorb neighbouring Host/Match blocks.
        lines = existing.splitlines(keepends=True)
        start = None
        end = len(lines)
        for index, line in enumerate(lines):
            if re.match(r"^\s*(Host|Match)\s", line, re.IGNORECASE):
                if start is not None:
                    end = index
                    break
                words = shlex.split(line, comments=True)
                if words[0].lower() == "host" and self.args.host in words[1:]:
                    if words[1:] != [self.args.host]:
                        raise RuntimeError(
                            "SSH alias is part of a shared Host block; choose another --host."
                        )
                    start = index
        block = (
            f"Host {self.args.host}\n    HostName {host}\n    User root\n    Port {port}\n"
            f'    IdentityFile "{pathlib.Path(self.args.ssh_key).expanduser()}"\n'
            "    IdentitiesOnly yes\n    StrictHostKeyChecking accept-new\n"
            "    ServerAliveInterval 30\n    ServerAliveCountMax 3\n"
        )
        remaining = existing if start is None else "".join(lines[:start] + lines[end:])
        remaining = remaining.lstrip("\n").removeprefix("Host *\n")
        # SSH uses the first assigned value. Put our alias before wildcard defaults
        # and restore all-host scope for the original global prelude (e.g. Include).
        updated = block + "\nHost *\n" + remaining
        _atomic_write(
            path, updated, path.stat().st_mode & 0o777 if path.exists() else 0o600
        )

    def _cleanup(self) -> bool:
        if not self.state:
            return True
        try:
            self._recover_create()
            pod_id = self.state.get("pod_id")
            if pod_id:
                for attempt in range(3):
                    try:
                        if self._pod(pod_id) is not None:
                            self._cli("pod", "delete", pod_id)
                        if self._pod(pod_id) is not None:
                            raise RuntimeError("Pod still exists after deletion.")
                        print(
                            f"Deleted Pod {pod_id}; network volume retained.",
                            flush=True,
                        )
                        break
                    except (OSError, RuntimeError):
                        if attempt == 2:
                            raise
                        time.sleep(0.5 * (attempt + 1))
            self.state_path.unlink(missing_ok=True)
            return True
        except (OSError, ValueError, RuntimeError) as error:
            print(
                f"CLEANUP FAILED: {error}. Pod may still be billing. State retained: {self.state_path}. "
                "Run the Runpod cleanup task or delete the recorded Pod in the console.",
                file=sys.stderr,
                flush=True,
            )
            return False


def _editor_binary() -> str:
    for name in ("code", "ide"):
        if found := shutil.which(name):
            return found
    for candidate in (
        pathlib.Path("~/.local/bin/ide").expanduser(),
        pathlib.Path(
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
        ),
    ):
        if os.access(candidate, os.X_OK):
            return str(candidate)
    raise RuntimeError("Required command is missing: code (or ide)")


def _atomic_write(path: pathlib.Path, text: str, mode: int) -> None:
    name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, delete=False
        ) as file:
            name = file.name
            os.chmod(name, mode)
            file.write(text)
        os.replace(name, path)
    finally:
        if name:
            pathlib.Path(name).unlink(missing_ok=True)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--volume-id",
        required=True,
        help="Existing network volume; never deleted by this script",
    )
    parser.add_argument(
        "--adopt-pod-id",
        help="Explicit existing development Pod to reuse AND delete when the task ends",
    )
    parser.add_argument("--gpu", default="NVIDIA GeForce RTX 4090")
    parser.add_argument("--template", default="runpod-torch-v280")
    parser.add_argument("--min-cuda", default="12.8")
    parser.add_argument("--host", default="runpod-devbox")
    parser.add_argument("--connection", choices=("ssh", "tunnel"), default="ssh")
    parser.add_argument(
        "--remote-path",
        default="/workspace",
        help="Remote directory or subpath under /workspace to open in VS Code",
    )
    parser.add_argument("--tunnel-name", default="dima-gpu-dev")
    parser.add_argument("--ssh-key", default="~/.ssh/runpod_dev_ed25519")
    parser.add_argument("--state-dir", default="~/.local/state/dima/runpod-dev")
    parser.add_argument("--env-file", default="~/.config/direnv/env/runpod.env")
    parser.add_argument(
        "--ready-timeout",
        type=float,
        default=300,
        help="Seconds before deleting an unusable Pod",
    )
    parser.add_argument("--poll-interval", type=float, default=5)
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete only the saved/adopted session Pod and exit",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.host):
        parser.error("--host must be a plain SSH alias")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,59}", args.tunnel_name):
        parser.error("--tunnel-name must be 3–60 lowercase letters, digits or hyphens")
    raw_remote = args.remote_path.strip()
    remote = (
        pathlib.PurePosixPath("/workspace")
        if not raw_remote
        else pathlib.PurePosixPath(raw_remote)
        if raw_remote.startswith("/")
        else pathlib.PurePosixPath("/workspace") / raw_remote
    )
    if ".." in remote.parts or not remote.is_relative_to("/workspace"):
        parser.error("--remote-path must be /workspace or a path inside /workspace")
    args.remote_path = str(remote)
    if args.connection == "tunnel" and args.adopt_pod_id and not args.cleanup:
        parser.error(
            "Tunnel mode requires a Pod created with the tunnel bootstrap; omit --adopt-pod-id"
        )
    if args.ready_timeout <= 0 or args.poll_interval <= 0:
        parser.error("timeouts must be positive")
    return args


if __name__ == "__main__":
    sys.exit(main())
