"""Filesystem-backed substitutes for paid/network tools in Runpod lifecycle tests."""

import json
import os
import pathlib
import sys
import time


def main() -> None:
    root = pathlib.Path(os.environ["FAKE_RUNPOD_ROOT"])
    tool = pathlib.Path(sys.argv[0]).name
    args = sys.argv[1:]
    path = root / "account.json"
    account = json.loads(path.read_text())
    mode = (root / "mode").read_text()
    if tool in ("code", "ide"):
        (root / "opened.json").write_text(json.dumps(args))
        sys.exit(1 if mode == "code-fails" else 0)
    if tool == "ssh":
        if mode == "ssh-fails":
            print(
                "ssh: connect to host 192.0.2.10 port 22022: Connection refused",
                file=sys.stderr,
            )
            sys.exit(255)
        if mode == "gpu-fails":
            print("GPU 0: NVIDIA GeForce RTX 4090")
            print("ModuleNotFoundError: No module named 'torch'", file=sys.stderr)
            sys.exit(1)
        print("GPU check: CUDA True")
        return
    if args[:2] == ["network-volume", "get"]:
        result = {"id": "volume", "dataCenterId": "EU-RO-1", "size": 10}
    elif args[:2] == ["gpu", "list"]:
        availability = (
            []
            if mode == "no-stock"
            else [{"dataCenterId": "EU-RO-1", "stockStatus": "Low"}]
        )
        result = [
            {
                "gpuId": "NVIDIA GeForce RTX 4090",
                "securePricePerHr": 0.89,
                "dataCenterAvailability": availability,
            },
            {
                "gpuId": "NVIDIA RTX A5000",
                "securePricePerHr": 0.27,
                "dataCenterAvailability": availability,
            },
        ]
    elif args[:2] == ["template", "get"]:
        result = {"imageName": "runpod/pytorch:pinned-cu128", "isServerless": False}
    elif args[:2] == ["ssh", "list-keys"]:
        result = {
            "keys": [
                {"key": key}
                for key in account.get("keys", ["ssh-ed25519 AAAATEST local"])
            ]
        }
    elif args[:2] == ["ssh", "add-key"]:
        account["keys"].append(
            pathlib.Path(args[args.index("--key-file") + 1]).read_text()
        )
        path.write_text(json.dumps(account))
        result = {}
    elif args[:2] == ["pod", "list"]:
        result = list(account["pods"].values())
        if mode == "lost-invisible":
            result = [pod for pod in result if pod["id"] != "created"]
    elif args[:2] == ["pod", "create"]:
        (root / "create-args.json").write_text(json.dumps(args))
        (root / "creating").touch()
        if mode == "slow-create":
            time.sleep(0.8)
        pod = {
            "id": "created",
            "name": args[args.index("--name") + 1],
            "networkVolumeId": "volume",
            "desiredStatus": "RUNNING",
            "gpuId": args[args.index("--gpu-id") + 1],
        }
        account["pods"]["created"] = pod
        path.write_text(json.dumps(account))
        if mode in ("lost-response", "lost-invisible"):
            print(
                json.dumps({"code": "network_error", "error": "response lost"}),
                file=sys.stderr,
            )
            sys.exit(1)
        result = pod
    elif args[:2] == ["pod", "get"]:
        if args[2] not in account["pods"]:
            print(
                json.dumps({"code": "not_found", "error": "pod missing"}),
                file=sys.stderr,
            )
            sys.exit(1)
        result = account["pods"][args[2]]
    elif args[:2] == ["pod", "logs"]:
        first_timeout = root / "log-timeout"
        if mode == "logs-not-ready" and not first_timeout.exists():
            first_timeout.touch()
            print(
                json.dumps({"code": "timeout", "error": "stream not ready"}),
                file=sys.stderr,
            )
            sys.exit(1)
        lines = ["DIMA_GPU_READY torch=2.8.0 CUDA=True"]
        if mode == "tunnel-fails":
            lines.append("DIMA_TUNNEL_FAILED: relay connection refused")
        elif mode == "tunnel-login":
            lines.append(
                "To grant access, visit https://github.com/login/device and use code FAKE-CODE"
            )
        else:
            lines.append(
                "Open this link in your browser https://vscode.dev/tunnel/dima-gpu-dev"
            )
        for i, line in enumerate(lines):
            print(json.dumps({"source": "container", "line": line, "ts": str(i)}))
        return
    elif args[:2] == ["pod", "delete"]:
        if mode == "delete-fails":
            print(
                json.dumps({"code": "network_error", "error": "offline"}),
                file=sys.stderr,
            )
            sys.exit(1)
        account["pods"].pop(args[2], None)
        path.write_text(json.dumps(account))
        result = {}
    elif args[:2] == ["pod", "start"]:
        account["pods"][args[2]]["desiredStatus"] = "RUNNING"
        path.write_text(json.dumps(account))
        result = account["pods"][args[2]]
    elif args[:2] == ["ssh", "info"]:
        result = {
            "ip": "192.0.2.10",
            "port": 22022,
            "ssh_key": {"path": str(root / "home/.ssh/key"), "in_account": True},
        }
    else:
        raise RuntimeError(f"Unexpected command: {tool} {args}")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
