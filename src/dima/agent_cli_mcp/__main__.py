"""Run the agent conversation server over MCP stdio."""

import argparse
import json
import pathlib
import typing

import platformdirs

from .models import Source
from .server import create_server
from .service import Service
from .sources import default_sources


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search and read local agent chats through MCP stdio"
    )
    _ = parser.add_argument(
        "--index",
        type=pathlib.Path,
        default=platformdirs.user_cache_path("dima-agent-cli-mcp") / "index.sqlite3",
        help="Rebuildable SQLite/FTS5 index path",
    )
    _ = parser.add_argument(
        "--home",
        type=pathlib.Path,
        help="Discover harness data under this home directory instead of the current user's home",
    )
    _ = parser.add_argument(
        "--config",
        type=pathlib.Path,
        help="JSON array of sources, each with harness and path; overrides discovery",
    )
    args = parser.parse_args()
    index = typing.cast(pathlib.Path, args.index)
    home = typing.cast(pathlib.Path | None, args.home)
    config = typing.cast(pathlib.Path | None, args.config)
    if config:
        values = typing.cast(object, json.loads(config.read_text()))
        if not isinstance(values, list):
            parser.error("--config must contain a JSON array of sources")
        sources = [
            Source.model_validate(value) for value in typing.cast(list[object], values)
        ]
    else:
        sources = default_sources(home)
    with Service(index_path=index.expanduser(), sources=sources) as service:
        create_server(service).run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
