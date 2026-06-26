---
name: macos-disk-cleanup
description: >
  Use when the user is running low on disk space on macOS and wants to find and remove
  large files, caches, unused Homebrew packages, Docker resources, and app leftovers.
  Covers scanning all major space consumers (Homebrew, Docker, npm, uv, IDE caches,
  Application Support directories, system caches) and provides safe cleanup commands
  with reclaim estimates. Run commands with SafeToAutoRun only for read-only scans;
  deletion commands require user approval.
---

# macOS Disk Cleanup

## Quick assessment

Start by checking disk usage, then scan the major space consumers in parallel:

```bash
df -h /
```

## Scanning commands (all read-only, safe to auto-run)

### Homebrew — casks and formulae

```bash
# Cask sizes (GUI apps installed via brew)
du -sh /opt/homebrew/Caskroom/* 2>/dev/null | sort -rh | head -20

# Formula sizes (CLI tools)
du -sh /opt/homebrew/Cellar/* 2>/dev/null | sort -rh | head -30

# Homebrew download cache
du -sh ~/Library/Caches/Homebrew 2>/dev/null

# List installed packages with versions
brew list --cask --versions 2>/dev/null
brew list --formula --versions 2>/dev/null
```

### Docker

```bash
# Overall disk usage (images, volumes, build cache, containers)
docker system df

# Detailed per-image and per-volume sizes
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | sort -k2 -rh
docker volume ls -q | xargs -I{} docker volume inspect {} --format '{{.Name}} {{.Mountpoint}}'
```

### Package manager caches

```bash
# uv (Python) — often the biggest, can be 10+ GB
du -sh ~/.cache/uv 2>/dev/null
du -sh ~/.cache/uv/* 2>/dev/null | sort -rh | head -10

# npm
du -sh ~/.npm 2>/dev/null

# pip
du -sh ~/Library/Caches/pip 2>/dev/null

# pre-commit
du -sh ~/.cache/pre-commit 2>/dev/null

# node-gyp
du -sh ~/Library/Caches/node-gyp 2>/dev/null
```

### IDE and editor caches

These accumulate in `~/Library/Application Support/` and can be several GB each:

```bash
# All Application Support directories, sorted by size
du -sh ~/Library/Application\ Support/* 2>/dev/null | sort -rh | head -20

# Individual IDE cache subdirectories (safe to delete, rebuild on launch)
du -sh ~/Library/Application\ Support/Code/{Cache,CachedExtensionVSIXs,WebStorage,CachedData} 2>/dev/null
du -sh ~/Library/Application\ Support/Windsurf/{Cache,CachedData,WebStorage} 2>/dev/null
du -sh ~/Library/Application\ Support/Devin/{Cache,WebStorage} 2>/dev/null
du -sh ~/Library/Application\ Support/Antigravity/{CachedExtensionVSIXs,logs,CachedData,Cache} 2>/dev/null
du -sh ~/Library/Application\ Support/Antigravity\ IDE/{CachedExtensionVSIXs,WebStorage,CachedData,Cache} 2>/dev/null
```

### System and app caches

```bash
# All Library/Caches directories, sorted by size
du -sh ~/Library/Caches/* 2>/dev/null | sort -rh | head -20

# Common large ones
du -sh ~/Library/Caches/SiriTTS 2>/dev/null
du -sh ~/Library/Caches/ms-playwright-go 2>/dev/null
du -sh ~/Library/Caches/antigravity-updater 2>/dev/null
```

### Applications

```bash
du -sh /Applications/* 2>/dev/null | sort -rh | head -20
```

### Other common locations

```bash
# Xcode derived data and simulators (can be 10+ GB)
du -sh ~/Library/Developer/Xcode/DerivedData 2>/dev/null
du -sh ~/Library/Developer/CoreSimulator 2>/dev/null

# Docker data
du -sh ~/.docker 2>/dev/null
du -sh ~/.orbstack 2>/dev/null

# Local share data
du -sh ~/.local/share/* 2>/dev/null | sort -rh | head -10

# Claude Desktop VM bundles (can be 7+ GB)
du -sh ~/Library/Application\ Support/Claude/vm_bundles 2>/dev/null

# Leftover app data (app uninstalled but data remains)
# CrossOver, Steam, etc.
du -sh ~/Library/Application\ Support/CrossOver 2>/dev/null
du -sh ~/Library/Application\ Support/Steam 2>/dev/null
```

### Finding leftover data from uninstalled apps

When an app is deleted but its support data remains, find it:

```bash
mdfind "kMDItemFSName == 'AppName.app'" 2>/dev/null
du -sh ~/Library/Application\ Support/AppName 2>/dev/null
```

If `mdfind` returns nothing but `Application Support/AppName` exists, the app was
uninstalled and the data is safe to delete.

## Cleanup commands

### Tier 1 — Safe caches (re-download on demand, no data loss)

```bash
# Homebrew cache — downloaded bottles/packages
brew cleanup --prune=all

# uv cache — Python package cache
uv cache clean

# npm cache
npm cache clean --force

# pip cache
pip cache purge

# pre-commit cache (re-clones hooks on next run)
rm -rf ~/.cache/pre-commit

# node-gyp cache
rm -rf ~/Library/Caches/node-gyp

# Playwright browser cache (re-downloads on next run)
rm -rf ~/Library/Caches/ms-playwright-go
```

### Tier 2 — IDE/editor caches (rebuild on launch, no project data lost)

```bash
# VS Code
rm -rf ~/Library/Application\ Support/Code/{Cache,CachedExtensionVSIXs,WebStorage,CachedData}

# Windsurf
rm -rf ~/Library/Application\ Support/Windsurf/{Cache,CachedData,WebStorage}

# Devin
rm -rf ~/Library/Application\ Support/Devin/{Cache,WebStorage}

# Antigravity
rm -rf ~/Library/Application\ Support/Antigravity/{CachedExtensionVSIXs,logs,CachedData,Cache}

# Antigravity IDE
rm -rf ~/Library/Application\ Support/Antigravity\ IDE/{CachedExtensionVSIXs,WebStorage,CachedData,Cache}
```

### Tier 3 — Docker (large reclaim, loses unused images/volumes)

```bash
# Remove unused images, stopped containers, build cache, and unused volumes
docker system prune -a --volumes

# More targeted options:
docker image prune -a          # unused images only
docker volume prune            # unused volumes only
docker builder prune -a        # build cache only
```

### Tier 4 — Homebrew package removal (loses the tool)

```bash
# Uninstall a formula (CLI tool)
brew uninstall <name>

# Uninstall a cask (GUI app)
brew uninstall --cask <name>

# Also remove data directories for database packages
rm -rf /opt/homebrew/var/<name>
```

### Tier 5 — App removal (largest reclaim, loses the app)

```bash
# Remove app from Applications
rm -rf /Applications/AppName.app

# Remove leftover support data (check app isn't installed first!)
rm -rf ~/Library/Application\ Support/AppName

# Remove leftover caches
rm -rf ~/Library/Caches/AppName
```

### Tier 6 — Claude Desktop VM bundle (7+ GB, re-downloads if needed)

```bash
rm -rf ~/Library/Application\ Support/Claude/vm_bundles
```

## Workflow

1. Run `df -h /` to check current free space.
2. Run the scanning commands in parallel to identify all space consumers.
3. Present findings sorted by size, grouped by category (Docker, caches, brew, apps).
4. For each item, note: size, what it is, whether it's safe to delete, and whether it
   re-downloads/rebuilds automatically.
5. Let the user decide what to remove — never delete without explicit approval.
6. After cleanup, run `df -h /` again to confirm the reclaimed space.

## Key targets on this machine

Known large space consumers from the initial scan on 2025-06-26:

| Target | Size | Cleanup command |
|--------|------|-----------------|
| Docker images + volumes + build cache | ~43 GB | `docker system prune -a --volumes` |
| `~/.cache/uv` | ~11 GB | `uv cache clean` |
| Claude VM bundle | ~7.7 GB | `rm -rf ~/Library/Application\ Support/Claude/vm_bundles` |
| `~/.npm` | ~2.3 GB | `npm cache clean --force` |
| Homebrew cache | ~1.5 GB | `brew cleanup --prune=all` |
| Windsurf caches | ~1.7 GB | `rm -rf ~/Library/Application\ Support/Windsurf/{Cache,CachedData,WebStorage}` |
| Devin caches | ~1.1 GB | `rm -rf ~/Library/Application\ Support/Devin/{Cache,WebStorage}` |
| `~/.cache/pre-commit` | ~626 MB | `rm -rf ~/.cache/pre-commit` |
| VS Code caches | ~870 MB | `rm -rf ~/Library/Application\ Support/Code/{Cache,CachedExtensionVSIXs,WebStorage,CachedData}` |
| SiriTTS cache | ~484 MB | `rm -rf ~/Library/Caches/SiriTTS` |
| antigravity-updater cache | ~304 MB | `rm -rf ~/Library/Caches/antigravity-updater` |
| CrossOver leftover data | ~3.3 GB | `rm -rf ~/Library/Application\ Support/CrossOver` |
| Xcode | ~4.6 GB | `rm -rf /Applications/Xcode.app` |
