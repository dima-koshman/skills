"""Fixtures shared across test modules."""

import json
import pathlib
import sqlite3
from collections.abc import Callable

import pytest


@pytest.fixture
def opencode_database() -> Callable[[pathlib.Path], sqlite3.Connection]:
    """Build a legacy OpenCode SQLite store with one session, message and part."""
    return _opencode_database


def _opencode_database(path: pathlib.Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    _ = connection.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE session(id TEXT PRIMARY KEY,title TEXT,directory TEXT,parent_id TEXT,time_created INTEGER,time_updated INTEGER,time_archived INTEGER);
        CREATE TABLE message(id TEXT,session_id TEXT,data TEXT,time_created INTEGER,time_updated INTEGER);
        CREATE TABLE part(id TEXT,message_id TEXT,session_id TEXT,data TEXT,time_created INTEGER,time_updated INTEGER);
        INSERT INTO session VALUES('s','Native title','/repo',NULL,1700000000000,1700000000000,NULL);
    """)
    _ = connection.execute(
        "INSERT INTO message VALUES(?,?,?,?,?)",
        (
            "m",
            "s",
            json.dumps({"role": "user", "time": {"created": 1700000000000}}),
            1,
            1,
        ),
    )
    _ = connection.execute(
        "INSERT INTO part VALUES(?,?,?,?,?,?)",
        ("p", "m", "s", json.dumps({"type": "text", "text": "first"}), 1, 1),
    )
    connection.commit()
    return connection
