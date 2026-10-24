"""Bootstrap and connect to a GPU Pod using VS Code Remote Tunnels."""

import argparse
import base64
import pathlib
import re
import shlex
import subprocess
import threading
import time
from collections.abc import Callable
from typing import Any


def docker_args() -> str:
    source = pathlib.Path(__file__).with_name("runpod_tunnel_bootstrap.py").read_bytes()
    payload = base64.b64encode(source).decode("ascii")
    # NVIDIA's image entrypoint still runs; no nginx/SSH/Jupyter startup is needed.
    setup = (
        "import base64; "
        f"exec(compile(base64.b64decode('{payload}'), 'runpod_tunnel_bootstrap.py', 'exec'))"
    )
    return shlex.join(["python3", "-u", "-c", setup])


def connect(
    args: argparse.Namespace,
    cli: Callable[..., Any],
    check_cancel: Callable[[], None],
    stop: threading.Event,
    pod_id: str,
    env: dict[str, str],
) -> None:
    deadline = time.monotonic() + args.ready_timeout
    seen: set[tuple[str, str]] = set()
    gpu_ready = False
    tunnel_name = None
    print(f"Pod {pod_id}: waiting for CUDA and VS Code Remote Tunnels...", flush=True)
    while time.monotonic() < deadline:
        check_cancel()
        records = cli(
            "pod",
            "logs",
            pod_id,
            "--source",
            "container",
            "--tail",
            "1000",
            "--max-wait",
            "1s",
        )
        for record in records:
            line = str(record.get("line", ""))
            identity = (str(record.get("ts", "")), line)
            if identity in seen:
                continue
            seen.add(identity)
            print(line, flush=True)
            if "DIMA_TUNNEL_FAILED:" in line:
                raise RuntimeError(line)
            if "DIMA_GPU_READY " in line:
                gpu_ready = True
            match = re.search(r"https://vscode\.dev/tunnel/([a-zA-Z0-9_-]+)", line)
            if match:
                tunnel_name = match[1]
        if gpu_ready and tunnel_name:
            check_cancel()
            result = subprocess.run(
                [
                    "code",
                    "--new-window",
                    "--remote",
                    f"tunnel+{tunnel_name}",
                    "/workspace",
                ],
                env=env,
                timeout=30,
                start_new_session=True,
                check=False,
            )
            if result.returncode:
                raise RuntimeError("VS Code failed to open the remote window.")
            print(
                f"Browser alternative: https://vscode.dev/tunnel/{tunnel_name}/workspace",
                flush=True,
            )
            return
        stop.wait(args.poll_interval)
    check_cancel()
    raise RuntimeError(
        f"Pod {pod_id}: tunnel readiness timed out. Complete the device sign-in shown above "
        "and check whether this network permits VS Code Remote Tunnels."
    )
