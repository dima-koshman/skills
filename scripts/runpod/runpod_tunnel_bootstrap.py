"""Run inside the GPU container; persist the VS Code installation and login."""

import os
import pathlib
import subprocess
import sys
import tarfile
import tempfile
import urllib.request


def main(root: pathlib.Path = pathlib.Path("/workspace/.runpod-dev")) -> None:
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    subprocess.run(["nvidia-smi", "-L"], check=True)
    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import torch\n"
                "if not torch.cuda.is_available(): raise RuntimeError('CUDA is unavailable')\n"
                "if torch.ones(3, device='cuda').sum().item() != 3: raise RuntimeError('CUDA tensor check failed')\n"
                "print('DIMA_GPU_READY torch=' + torch.__version__, flush=True)"
            ),
        ],
        check=True,
    )
    code = root / "code"
    if not code.exists():
        print("Downloading the VS Code Linux CLI...", flush=True)
        with tempfile.TemporaryFile() as archive:
            with urllib.request.urlopen(
                "https://update.code.visualstudio.com/latest/cli-linux-x64/stable",
                timeout=120,
            ) as response:
                while block := response.read(1024 * 1024):
                    archive.write(block)
            archive.seek(0)
            with tarfile.open(fileobj=archive, mode="r:gz") as bundle:
                member = next(
                    item
                    for item in bundle.getmembers()
                    if item.isfile() and pathlib.PurePosixPath(item.name).name == "code"
                )
                binary = bundle.extractfile(member)
                if binary is None:
                    raise RuntimeError("VS Code archive has no CLI executable")
                staging = root / "code.download"
                with staging.open("wb") as output:
                    while block := binary.read(1024 * 1024):
                        output.write(block)
                staging.chmod(0o700)
                staging.replace(code)
    cli_data = root / "vscode-cli"
    cli_data.mkdir(mode=0o700, exist_ok=True)
    command = [str(code), "--cli-data-dir", str(cli_data), "tunnel"]
    login = subprocess.run([*command, "user", "show"], check=False)
    if login.returncode:
        subprocess.run([*command, "user", "login", "--provider", "github"], check=True)
    subprocess.run(
        [
            *command,
            "--accept-server-license-terms",
            "--name",
            os.environ["DIMA_TUNNEL_NAME"],
            "--server-data-dir",
            str(root / "vscode-server"),
        ],
        check=True,
    )
    raise RuntimeError("VS Code tunnel exited unexpectedly")


if __name__ == "__main__":
    try:
        main()
    except (
        OSError,
        ValueError,
        RuntimeError,
        StopIteration,
        tarfile.TarError,
        subprocess.SubprocessError,
    ) as error:
        print(f"DIMA_TUNNEL_FAILED: {error}", flush=True)
        sys.exit(1)
