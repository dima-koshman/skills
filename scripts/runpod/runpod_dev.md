# Runpod GPU workspace

Run **Tasks: Run Task → Runpod: GPU workspace** from the Command Palette.
Choose the GPU (default: **NVIDIA GeForce RTX 4090**) and **VS Code Remote Tunnels**
(default) or **Direct SSH** in the pickers. The task creates a Pod with the selected GPU
in the network volume's data center, checks CUDA and PyTorch, then opens `/workspace`
in a new desktop VS Code window using the selected method. A saved Pod from an
interrupted session can be reused with the same GPU and connection method. Tunnels
need no direct SSH access or public port; SSH requires a network that permits the
Pod's assigned TCP port.

Requirements: Python 3.11+, `runpodctl`, and the `code` CLI on PATH. Install the
local VS Code extension for the selected method: **Remote - Tunnels**
(`ms-vscode.remote-server`) or **Remote - SSH** (`ms-vscode-remote.remote-ssh`).
For tunnels, both ends need outbound access to Microsoft's tunnel service;
corporate policy can still restrict this traffic.

On first use, follow the GitHub device sign-in URL and code printed in the task
terminal. Use the same GitHub account in VS Code's **Remote Tunnels: Connect to
Tunnel…** command if the new window asks you to sign in. Startup allows 15 minutes
for image startup and device sign-in. The task also prints a `vscode.dev` URL for
browser access. A CLI exit alone proves the open request was sent; successful
editor attachment still needs verification in the new window.

The CLI, saved login, and VS Code server data live under
`/workspace/.runpod-dev`, so they survive Pod deletion. Repositories and Python
virtual environments should also live under `/workspace`. The tunnel uses the
VS Code server license terms, accepted by the startup command.

Keep the task running while working. **Ctrl+C in its terminal**, or
**Tasks: Terminate Task**, requests deletion of the Pod. Closing the remote editor
window alone does not end the task. Startup failures also trigger deletion.
Cleanup is verified by reading the Pod back and checking that it is gone.

The network volume `gpe8lh1zzb` (`dima-gpu-dev-workspace`, 10 GB, EU-RO-1) is
always retained and continues to incur storage charges. Keep repositories,
virtual environments, model downloads, and checkpoints under `/workspace`.
Container filesystem changes outside `/workspace` are lost when the Pod is
deleted; packages installed there need reinstalling or inclusion in an image.
The task prints the current catalog GPU price before provisioning; container
disk and network storage are additional charges.

## Credentials and customization

The script reads `RUNPOD_API_KEY` from
`~/.config/direnv/env/runpod.env` if that file exists. Otherwise it uses
`runpodctl`'s `~/.runpod/config.toml`. It ignores inherited `RUNPOD_API_KEY` and
runs the CLI outside the project so a project `.env` cannot select an unintended
account. API response bodies and credentials are not printed.

Run `python3 scripts/runpod/runpod_dev.py --help` for options. The task passes the picker
values to `--gpu`, `--connection`, and `--remote-path` (accepts `/workspace`, an absolute path
under `/workspace`, or a relative subpath); direct script calls retain
`--gpu "NVIDIA GeForce RTX 4090"`, `--connection ssh`, and `--remote-path /workspace` as defaults.
SSH mode uses the task's existing key `~/.runpod/ssh/RunPod-Key-Go`, registers its
public key, updates the `runpod-devbox` alias, and requires Microsoft's
Remote - SSH extension. Use a network that permits SSH.
Explicit `--adopt-pod-id` is supported for SSH mode and authorizes deleting that
Pod when the task ends; volume and GPU must match. Tunnel mode creates its own
Pod with the startup bootstrap. Clean up a saved SSH session before switching
connection mode. Use a different state directory and tunnel name for independent
sessions.

## Recovery

For tunnel startup failures, inspect the container output printed in the task
terminal. A GitHub device code means sign-in is still pending. A relay connection
error can mean the network blocks the tunnel service. Startup timeout or failure
deletes the Pod; the persistent volume and saved login remain.

For optional SSH mode, a timeout **during banner exchange** happens before
key authentication. If Runpod and `ssh -vv -T -o ConnectTimeout=8 -p 443
git@ssh.github.com` both time out before the banner, check SSH policy with the
network administrator.

If cleanup fails, run **Runpod: cleanup GPU workspace** when connectivity returns.
The journal in `~/.local/state/dima/runpod-dev/session.json` records the Pod ID
or unique creation name. A process lock prevents two tasks from owning it.
An ambiguous creation response blocks further provisioning until the original
request can be reconciled, avoiding duplicate Pods. If the console confirms
that a pending request never created a Pod, remove that journal manually before
starting again.

No local script can guarantee cleanup after SIGKILL, forced editor shutdown,
power loss, or a prolonged API outage. In those cases, use the cleanup task or
delete the recorded Pod in the Runpod console. Signal handling waits for an
in-flight API request (up to 40 seconds) before cleanup, so allow the terminal
time to finish. Keep the journal until deletion is confirmed.
