#!/usr/bin/env python3
"""Capture the exact request a coding-agent harness sends to its model, without calling a model.

A local mock API (Anthropic Messages and OpenAI Chat Completions, streaming or not) records every request
body and answers "ok"; the harness runs one prompt pointed at it with a dummy API key, so no real
credentials or tokens are spent. The recorded request holds the built-in system prompt, the tool
definitions and the messages exactly as sent.

    Claude Code  `claude -p` with ANTHROPIC_BASE_URL=<mock>, ANTHROPIC_API_KEY=<dummy>, ENABLE_TOOL_SEARCH=true
                 (a non-Anthropic base URL would otherwise turn tool search off and change the request)
    OpenCode v2  `opencode run --standalone` with OPENCODE_CONFIG_CONTENT adding an openai-compatible "capture"
                 provider whose model id equals the default model's, so OpenCode picks the same base prompt

Usage: llm_capture.py claude|opencode [--cwd DIR] [--out FILE]   (prints a size summary; --out saves the request)
"""

import argparse
import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DUMMY_KEY = "capture-dummy-key-not-a-secret"


class MockAPI:
    """Records POST bodies; replies like the Anthropic or OpenAI API would, with the text "ok"."""

    def __init__(self):
        self.requests: list[dict] = []
        api = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(
                self,
                body: dict | None = None,
                sse: list[str] | None = None,
                status: int = 200,
            ):
                self.send_response(status)
                if sse is not None:
                    self.send_header("Content-Type", "text/event-stream")
                    self.end_headers()
                    for chunk in sse:
                        self.wfile.write(chunk.encode())
                else:
                    data = json.dumps(body or {}).encode()
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)

            def do_GET(self):
                self.reply({"data": [], "object": "list", "has_more": False})

            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
                try:
                    body = json.loads(raw or b"{}")
                except json.JSONDecodeError:
                    body = {"_raw": raw.decode(errors="replace")}
                api.requests.append({"path": self.path, "body": body})
                model = body.get("model", "capture")
                if self.path.endswith("/count_tokens"):
                    return self.reply({"input_tokens": 1})
                if "/messages" in self.path:
                    return self.anthropic(model, body.get("stream"))
                return self.openai(model, body.get("stream"))

            def anthropic(self, model, stream):
                message = {
                    "id": "msg_capture",
                    "type": "message",
                    "role": "assistant",
                    "model": model,
                    "content": [],
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": {"input_tokens": 1, "output_tokens": 1},
                }
                if not stream:
                    return self.reply(
                        message
                        | {
                            "content": [{"type": "text", "text": "ok"}],
                            "stop_reason": "end_turn",
                        }
                    )
                events = [
                    ("message_start", {"type": "message_start", "message": message}),
                    (
                        "content_block_start",
                        {
                            "type": "content_block_start",
                            "index": 0,
                            "content_block": {"type": "text", "text": ""},
                        },
                    ),
                    (
                        "content_block_delta",
                        {
                            "type": "content_block_delta",
                            "index": 0,
                            "delta": {"type": "text_delta", "text": "ok"},
                        },
                    ),
                    ("content_block_stop", {"type": "content_block_stop", "index": 0}),
                    (
                        "message_delta",
                        {
                            "type": "message_delta",
                            "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                            "usage": {"output_tokens": 1},
                        },
                    ),
                    ("message_stop", {"type": "message_stop"}),
                ]
                self.reply(
                    sse=[
                        f"event: {name}\ndata: {json.dumps(data)}\n\n"
                        for name, data in events
                    ]
                )

            def openai(self, model, stream):
                if not stream:
                    return self.reply(
                        {
                            "id": "chatcmpl-capture",
                            "object": "chat.completion",
                            "created": 0,
                            "model": model,
                            "choices": [
                                {
                                    "index": 0,
                                    "message": {"role": "assistant", "content": "ok"},
                                    "finish_reason": "stop",
                                }
                            ],
                            "usage": {
                                "prompt_tokens": 1,
                                "completion_tokens": 1,
                                "total_tokens": 2,
                            },
                        }
                    )
                base = {
                    "id": "chatcmpl-capture",
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": model,
                }
                chunks = [
                    base
                    | {
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"role": "assistant", "content": "ok"},
                                "finish_reason": None,
                            }
                        ]
                    },
                    base
                    | {
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                        "usage": {
                            "prompt_tokens": 1,
                            "completion_tokens": 1,
                            "total_tokens": 2,
                        },
                    },
                ]
                self.reply(
                    sse=[f"data: {json.dumps(c)}\n\n" for c in chunks]
                    + ["data: [DONE]\n\n"]
                )

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def __enter__(self):
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()


def main_request(requests: list[dict]) -> dict | None:
    """The agent's own call: the largest request that carries tools (side calls such as titles are small)."""
    candidates = [
        r for r in requests if isinstance(r["body"], dict) and r["body"].get("tools")
    ] or requests
    return max(candidates, key=lambda r: len(json.dumps(r["body"])), default=None)


def capture_claude(cwd: Path, timeout: int = 180) -> dict | None:
    with MockAPI() as api:
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN")
        }
        env |= {
            "ANTHROPIC_BASE_URL": api.url,
            "ANTHROPIC_API_KEY": DUMMY_KEY,
            "ENABLE_TOOL_SEARCH": "true",
            "DISABLE_TELEMETRY": "1",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "TRACE_TO_LANGSMITH": "false",
        }
        subprocess.run(
            ["claude", "-p", "hi"],
            check=False,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
        return main_request(api.requests)


def capture_opencode(cwd: Path, model_id: str, timeout: int = 180) -> dict | None:
    with MockAPI() as api:
        provider = {
            "capture": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "capture",
                "options": {"baseURL": f"{api.url}/v1", "apiKey": DUMMY_KEY},
                "models": {model_id: {"name": model_id}},
            }
        }
        env = os.environ | {
            "OPENCODE_CONFIG_CONTENT": json.dumps({"provider": provider})
        }
        subprocess.run(
            ["opencode", "run", "--standalone", "--model", f"capture/{model_id}", "hi"],
            check=False,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
        return main_request(api.requests)


def summarize(request: dict | None) -> str:
    if not request:
        return "no request captured"
    body = request["body"]
    system = body.get("system")
    system_text = system if isinstance(system, str) else json.dumps(system or "")
    messages = body.get("messages") or []
    if not system and messages and messages[0].get("role") == "system":
        system_text = json.dumps(messages[0].get("content"))
    return (
        f"{request['path']}: model={body.get('model')} system={len(system_text)} chars, "
        f"tools={len(body.get('tools') or [])} ({len(json.dumps(body.get('tools') or []))} chars), messages={len(messages)}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Capture a harness's model request through a local mock API."
    )
    parser.add_argument("harness", choices=["claude", "opencode"])
    parser.add_argument(
        "--cwd", default=str(Path.home() / ".cache/harness-overview/global")
    )
    parser.add_argument(
        "--model", default="gpt-5.6-sol", help="opencode: the model id to impersonate"
    )
    parser.add_argument(
        "--out",
        help="save the captured request as JSON (it may contain your instructions; no secrets are sent)",
    )
    args = parser.parse_args()
    cwd = Path(args.cwd).expanduser()
    req = (
        capture_claude(cwd)
        if args.harness == "claude"
        else capture_opencode(cwd, args.model)
    )
    print(summarize(req))
    if args.out and req:
        Path(args.out).write_text(json.dumps(req, indent=2, ensure_ascii=False))
