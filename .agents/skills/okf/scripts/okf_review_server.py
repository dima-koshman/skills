"""Serve an OKF bundle's HTML reader with review actions and auto-reload.

Usage:
    python okf_review_server.py [bundle-dir] [-o output.html] [--reviewer human:<id>]
                                [--host 127.0.0.1] [--port 8765] [--open]

The reader that ``okf_site.py`` writes is a static page. Served by this script, the
same page also shows a Review panel on each concept:

* Promote (a button beside the draft pill): removes ``status: draft`` and
  appends a ``verified`` event by the reviewer.
* Comment: appends ``{by, at, text}`` to the concept's ``review_comments`` and
  keeps it a draft. Agents address the comments and then remove them.

Edits change only the affected frontmatter keys; the rest of the file stays as
it was. After an edit, and whenever a file in the bundle changes, the server
regenerates ``index.md`` and the HTML, and open pages reload themselves.

It listens on localhost only and serves just the page and files inside the bundle.
"""

from __future__ import annotations

import argparse
import datetime
import getpass
import http.server
import json
import mimetypes
import os
import pathlib
import re
import sys
import tempfile
import threading
import time
import urllib.parse
import webbrowser

import okf_index
import okf_site
import yaml

_RESERVED_FILENAMES = frozenset({"index.md", "log.md"})
_DRAFT_LINE = re.compile(r"^status:[ \t]*(['\"]?)draft\1[ \t]*(?:#.*)?\n", re.MULTILINE)
_MAX_BODY_BYTES = 64 * 1024


class ReviewError(ValueError):
    """A review action that cannot be applied; the message is shown to the reviewer."""


def promote(
    bundle_root: pathlib.Path,
    concept_id: str,
    reviewer: str,
    at: str,
) -> None:
    """Remove ``status: draft`` and record ``reviewer``'s review in ``verified``."""
    path = _concept_path(bundle_root, concept_id)
    head, rest = _split_frontmatter(path.read_text(encoding="utf-8"))
    if str(_load(head).get("status") or "").strip() != "draft":
        raise ReviewError(f"{concept_id} is not a draft")
    new_head, count = _DRAFT_LINE.subn("", head, count=1)
    if count != 1:
        raise ReviewError(f"{concept_id}: cannot find its 'status: draft' line")
    new_head = _append_to_list(new_head, "verified", {"by": reviewer, "at": at})
    _write_checked(path, head, new_head, rest, changed={"status", "verified"})


def add_comment(
    bundle_root: pathlib.Path, concept_id: str, author: str, at: str, text: str
) -> None:
    """Append a review comment to the concept's ``review_comments``."""
    if not text or not text.strip():
        raise ReviewError("the comment is empty")
    path = _concept_path(bundle_root, concept_id)
    head, rest = _split_frontmatter(path.read_text(encoding="utf-8"))
    comment = {"by": author, "at": at, "text": text.strip()}
    new_head = _append_to_list(head, "review_comments", comment)
    _write_checked(path, head, new_head, rest, changed={"review_comments"})


class ReviewServer:
    """The reader for one bundle, served on localhost with the review API."""

    def __init__(
        self,
        bundle_root: pathlib.Path,
        output_path: pathlib.Path,
        reviewer: str,
        host: str = "127.0.0.1",
        port: int = 8765,
    ) -> None:
        self.bundle_root = bundle_root.resolve()
        self.output_path = output_path.resolve()
        self.reviewer = reviewer
        # Asset links in the page are relative to the output file, so serve from the
        # directory that holds both the page and the bundle.
        self.site_root = pathlib.Path(
            os.path.commonpath([self.output_path.parent, self.bundle_root])
        )
        self._lock = threading.RLock()
        self._snapshot: dict[str, int] = {}
        self.rebuild()
        self.httpd = http.server.ThreadingHTTPServer((host, port), _Handler)
        self.httpd.review = self  # type: ignore[attr-defined]
        self.host = host
        self.port = self.httpd.server_address[1]

    @property
    def page_url(self) -> str:
        page = self.output_path.relative_to(self.site_root).as_posix()
        return f"http://{self.host}:{self.port}/{urllib.parse.quote(page)}"

    def version(self) -> str:
        try:
            return str(self.output_path.stat().st_mtime_ns)
        except FileNotFoundError:
            return ""

    def rebuild(self) -> None:
        """Regenerate index.md and the HTML reader."""
        with self._lock:
            concepts, warnings = okf_index._collect_concepts(self.bundle_root)
            for warning in warnings:
                print(f"warning: {warning}", file=sys.stderr)
            if concepts:
                okf_index._write_root_catalog(self.bundle_root, concepts)
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            okf_site.render(self.bundle_root, self.output_path)
            self._snapshot = self._bundle_snapshot()

    def refresh_if_changed(self) -> bool:
        """Rebuild when a bundle file changed since the last build; return whether it did."""
        with self._lock:
            if self._bundle_snapshot() == self._snapshot:
                return False
            self.rebuild()
            return True

    def apply(self, action: str, payload: dict) -> None:
        concept_id = str(payload.get("id") or "")
        at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        with self._lock:
            if action == "promote":
                promote(self.bundle_root, concept_id, self.reviewer, at)
            elif action == "comment":
                add_comment(
                    self.bundle_root,
                    concept_id,
                    self.reviewer,
                    at,
                    str(payload.get("text") or ""),
                )
            else:
                raise ReviewError(f"unknown action: {action}")
            self.rebuild()
        print(f"{action}: {concept_id}")

    def watch(self, interval: float) -> None:
        """Poll the bundle and rebuild on change; runs until the process exits."""
        while True:
            time.sleep(interval)
            try:
                if self.refresh_if_changed():
                    print("bundle changed: re-rendered")
            except Exception as error:  # noqa: BLE001 - any render failure; keep serving, the next change retries
                print(f"error: re-render failed: {error}", file=sys.stderr)

    def static_file(self, url_path: str) -> pathlib.Path | None:
        """The file to serve for ``url_path``: the page itself or a file in the bundle."""
        relative = urllib.parse.unquote(url_path).lstrip("/")
        path = (self.site_root / relative).resolve()
        if path == self.output_path:
            return path
        if path.is_relative_to(self.bundle_root) and path.is_file():
            return path
        return None

    def _bundle_snapshot(self) -> dict[str, int]:
        snapshot = {}
        for path in self.bundle_root.rglob("*"):
            if (
                path.name == "index.md"
                or path == self.output_path
                or not path.is_file()
            ):
                continue
            snapshot[path.relative_to(self.bundle_root).as_posix()] = (
                path.stat().st_mtime_ns
            )
        return snapshot


class _Handler(http.server.BaseHTTPRequestHandler):
    server_version = "okf-review"

    @property
    def review(self) -> ReviewServer:
        return self.server.review  # type: ignore[attr-defined]

    def do_GET(self) -> None:
        if not self._host_allowed():
            return self._json(403, {"error": "unexpected Host header"})
        path = urllib.parse.urlsplit(self.path).path
        if path == "/api/ping":
            return self._json(
                200,
                {
                    "okf_review": True,
                    "reviewer": self.review.reviewer,
                    "bundle": self.review.bundle_root.name,
                    "version": self.review.version(),
                },
            )
        if path == "/api/version":
            return self._json(200, {"version": self.review.version()})
        if path == "/":
            self.send_response(302)
            self.send_header("Location", self.review.page_url)
            self.end_headers()
            return
        file = self.review.static_file(path)
        if file is None:
            return self._json(404, {"error": "not found"})
        body = file.read_bytes()
        self.send_response(200)
        self.send_header(
            "Content-Type",
            mimetypes.guess_type(file.name)[0] or "application/octet-stream",
        )
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        # Browsers send Origin on cross-site POSTs, and a JSON body needs a CORS preflight
        # this server never answers, so other sites cannot drive these actions.
        if not self._host_allowed() or not self._origin_allowed():
            return self._json(403, {"error": "requests must come from the reader page"})
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("application/json"):
            return self._json(415, {"error": "send JSON"})
        length = int(self.headers.get("Content-Length") or 0)
        if length > _MAX_BODY_BYTES:
            return self._json(413, {"error": "request too large"})
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._json(400, {"error": "invalid JSON"})
        action = urllib.parse.urlsplit(self.path).path.removeprefix("/api/")
        try:
            self.review.apply(action, payload if isinstance(payload, dict) else {})
        except ReviewError as error:
            return self._json(400, {"error": str(error)})
        self._json(200, {"ok": True, "version": self.review.version()})

    def log_message(self, format: str, *args: object) -> None:
        if not self.path.startswith("/api/version"):
            super().log_message(format, *args)

    def _allowed_hosts(self) -> set[str]:
        port = self.review.port
        return {f"{self.review.host}:{port}", f"localhost:{port}", f"127.0.0.1:{port}"}

    def _host_allowed(self) -> bool:
        return self.headers.get("Host", "") in self._allowed_hosts()

    def _origin_allowed(self) -> bool:
        origin = self.headers.get("Origin")
        return origin is None or origin in {
            f"http://{h}" for h in self._allowed_hosts()
        }

    def _json(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def _concept_path(bundle_root: pathlib.Path, concept_id: str) -> pathlib.Path:
    root = bundle_root.resolve()
    relative = concept_id.strip().lstrip("/")
    path = (root / relative).resolve()
    if (
        not relative.endswith(".md")
        or path.name in _RESERVED_FILENAMES
        or not path.is_relative_to(root)
        or not path.is_file()
    ):
        raise ReviewError(f"not a concept in this bundle: {concept_id}")
    return path


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split into the frontmatter text (with its final newline) and everything from ``---`` on."""
    if not text.startswith("---\n"):
        raise ReviewError("the concept has no frontmatter")
    end = text.find("\n---", 3)
    if end < 0:
        raise ReviewError("the concept's frontmatter is not closed")
    return text[4 : end + 1], text[end + 1 :]


def _load(head: str) -> dict:
    try:
        frontmatter = yaml.safe_load(head)
    except yaml.YAMLError as error:
        raise ReviewError(f"cannot parse the frontmatter: {error}") from error
    if not isinstance(frontmatter, dict):
        raise ReviewError("the frontmatter is not a mapping")
    return frontmatter


def _append_to_list(head: str, key: str, item: dict) -> str:
    """Append ``item`` to the top-level list ``key``, rewriting only that key's lines."""
    lines = head.splitlines(keepends=True)
    start = next(
        (i for i, line in enumerate(lines) if line.startswith(f"{key}:")), None
    )
    if start is None:
        current, start, end = [], len(lines), len(lines)
    else:
        end = start + 1
        while end < len(lines) and lines[end][:1] in (" ", "-", "\t"):
            end += 1
        value = _load("".join(lines[start:end])).get(key)
        current = [value] if isinstance(value, dict) else list(value or [])
    block = yaml.safe_dump(
        {key: [*current, item]}, sort_keys=False, allow_unicode=True, width=110
    )
    return "".join(lines[:start]) + block + "".join(lines[end:])


def _write_checked(
    path: pathlib.Path, old_head: str, new_head: str, rest: str, changed: set[str]
) -> None:
    """Write the new frontmatter after checking that only ``changed`` keys differ."""
    old, new = _load(old_head), _load(new_head)
    if {k: v for k, v in old.items() if k not in changed} != {
        k: v for k, v in new.items() if k not in changed
    }:
        raise ReviewError("refusing an edit that would change other frontmatter keys")
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as handle:
        handle.write("---\n" + new_head + rest)
    os.replace(handle.name, path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Serve an OKF bundle's HTML reader with draft promotion and comments."
    )
    parser.add_argument(
        "bundle", nargs="?", default=".", help="OKF bundle root (default: .)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output HTML path (default: <bundle>/okf-site.html).",
    )
    parser.add_argument(
        "--reviewer",
        default=f"human:{getpass.getuser()}",
        help="Actor recorded on promotions and comments (default: human:<login>).",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Address to bind (default: 127.0.0.1)."
    )
    parser.add_argument("--port", type=int, default=8765, help="Port (default: 8765).")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between bundle checks (default: 1).",
    )
    parser.add_argument(
        "--open", action="store_true", help="Open the reader in a browser."
    )
    args = parser.parse_args()

    bundle_root = pathlib.Path(args.bundle).resolve()
    if not bundle_root.is_dir():
        print(f"error: bundle path is not a directory: {bundle_root}", file=sys.stderr)
        return 2
    if not args.reviewer.startswith("human:"):
        print("error: --reviewer must be a human:<id> actor", file=sys.stderr)
        return 2
    output = pathlib.Path(args.output) if args.output else bundle_root / "okf-site.html"

    try:
        server = ReviewServer(bundle_root, output, args.reviewer, args.host, args.port)
    except OSError as error:
        print(
            f"error: cannot listen on {args.host}:{args.port}: {error}", file=sys.stderr
        )
        return 1
    threading.Thread(target=server.watch, args=(args.interval,), daemon=True).start()
    print(f"Reviewing {bundle_root} as {args.reviewer} at {server.page_url}")
    print("Press Ctrl+C to stop.")
    if args.open:
        webbrowser.open(server.page_url)
    try:
        server.httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
