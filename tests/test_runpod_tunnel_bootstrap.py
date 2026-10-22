"""Execute the remote bootstrap with filesystem-backed GPU/CLI substitutes."""

import importlib.util
import io
import json
import os
import pathlib
import subprocess
import sys
import tarfile

import pytest


def test_bootstrap_installs_cli_and_reuses_persistent_login(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_bootstrap()
    root = tmp_path / "workspace"
    binary = tmp_path / "bin"
    binary.mkdir()
    nvidia = binary / "nvidia-smi"
    nvidia.write_text("#!/bin/sh\necho 'GPU 0: fake GPU'\n")
    nvidia.chmod(0o700)
    (tmp_path / "torch.py").write_text(
        "__version__ = 'test'\n"
        "class cuda:\n"
        " @staticmethod\n"
        " def is_available(): return True\n"
        "class Tensor:\n"
        " def sum(self): return self\n"
        " def item(self): return 3\n"
        "def ones(count, device): return Tensor()\n"
    )
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    monkeypatch.setenv("DIMA_TUNNEL_NAME", "test-gpu")
    payload = (
        f"#!{sys.executable}\n"
        + """
import json, pathlib, sys
args = sys.argv[1:]
directory = pathlib.Path(args[args.index('--cli-data-dir') + 1])
token = directory / 'login'
if args[-2:] == ['user', 'show']:
    sys.exit(0 if token.exists() else 1)
if 'login' in args:
    token.write_text('persistent login')
    sys.exit(0)
(directory / 'tunnel-args.json').write_text(json.dumps(args))
sys.exit(17)
"""
    ).encode()
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as bundle:
        member = tarfile.TarInfo("code")
        member.size = len(payload)
        bundle.addfile(member, io.BytesIO(payload))

    monkeypatch.setattr(
        module.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(archive.getvalue()),
    )
    with pytest.raises(subprocess.CalledProcessError):
        module.main(root)

    saved_login = root / "vscode-cli/login"
    assert saved_login.read_text() == "persistent login"
    tunnel_args = json.loads((root / "vscode-cli/tunnel-args.json").read_text())
    assert tunnel_args[tunnel_args.index("--name") + 1] == "test-gpu"
    assert tunnel_args[tunnel_args.index("--server-data-dir") + 1] == str(
        root / "vscode-server"
    )
    assert "--accept-server-license-terms" in tunnel_args
    assert root.stat().st_mode & 0o777 == 0o700

    # Neither a new download nor device login should be needed in the next Pod.
    saved_login.write_text("existing session")
    monkeypatch.setattr(module.urllib.request, "urlopen", _unexpected_download)
    with pytest.raises(subprocess.CalledProcessError):
        module.main(root)

    assert saved_login.read_text() == "existing session"


def test_bootstrap_refuses_missing_cuda_before_installing_tunnel(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_bootstrap()
    binary = tmp_path / "bin"
    binary.mkdir()
    nvidia = binary / "nvidia-smi"
    nvidia.write_text("#!/bin/sh\nexit 1\n")
    nvidia.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ["PATH"])
    root = tmp_path / "workspace"
    monkeypatch.setattr(module.urllib.request, "urlopen", _unexpected_download)
    with pytest.raises(subprocess.CalledProcessError):
        module.main(root)

    assert not (root / "code").exists()


def _unexpected_download(*_args: object, **_kwargs: object) -> None:
    pytest.fail("CLI download was attempted despite a saved binary or missing CUDA")


def _load_bootstrap():
    path = pathlib.Path(__file__).parent.parent / "scripts/runpod_tunnel_bootstrap.py"
    spec = importlib.util.spec_from_file_location("runpod_tunnel_bootstrap", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
