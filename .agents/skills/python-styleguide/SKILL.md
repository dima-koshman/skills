---
name: python-styleguide
description: Shared Python style rules for all internal projects — imports, visibility, naming, Pydantic, FastAPI, enums, and more. Use when writing or reviewing Python code.
---

# Python Style Guide

Shared style rules for all internal Python projects. Follow the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) as the
base; the rules below override or extend it.

## Imports

Import packages or modules, not individual names from builtins or third-party packages.
Project-internal classes and functions may be imported directly.

```python
# Good
import collections
import asyncio
import contextlib
import concurrent.futures
import functools
import logging
import re

import httpx
import pydantic
import bidict

from sanitizer.codec import EntityTypeCodec          # own code — ok
from sanitizer.pipeline.base import DetectedEntity   # own code — ok

# Bad
from collections import defaultdict
from asyncio import Semaphore
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from httpx import AsyncClient, Timeout
```

Import every namespace you use directly, unless the parent already exposes it; never rely
on a child to expose the parent.

```python
# Good — only the namespaces actually referenced are imported
import presidio_analyzer
import presidio_analyzer.nlp_engine

engine = presidio_analyzer.AnalyzerEngine()
spacy_engine = presidio_analyzer.nlp_engine.SpacyNlpEngine()

# Bad — a.b is imported but never referenced directly
import presidio_analyzer
import presidio_analyzer.nlp_engine
import presidio_analyzer.nlp_engine.spacy_nlp_engine  # only used as presidio_analyzer.nlp_engine.SpacyNlpEngine
```

All imports must be at the top of the module. The only exception is optional/heavy
dependencies that should not be imported at module load time (e.g. `transformers`,
`lingua`) — those may be imported inside the function that uses them, with a comment
explaining why.

Exceptions: `from __future__ import annotations` and `from typing import ...` are fine
(type-annotation helpers with no meaningful module to import).

### Relative vs absolute imports

Use relative imports only for sibling or child modules — those living in the same directory
as the importing module. Everything else, including any module reached by going *up* the
package tree (`..` or higher), uses an absolute import from the project root.

Exception: modules at the project root itself (directly under `src/project_name/`) use
absolute imports for everything, including their siblings and children. Relative imports
start one level below the root.

```python
# In src/project_name/servers/gitlab/tools.py

# Good — siblings/children of tools.py use relative imports
from .annotations import BranchType, ProjectPathOrUrlType
from .utils import GitLabUrl, MergeRequest

# Good — anything outside gitlab/ uses an absolute import
from project_name.core import BuiltinMcpName, SecretName
from project_name.servers.core import BaseAhttpxMcp
from project_name.servers.atlassian.jira.utils import collect_jira_issue_keys_in_text

# Bad — reaching up the tree with a relative import
from ..core import BaseAhttpxMcp
from ..atlassian.jira.utils import collect_jira_issue_keys_in_text

# In src/project_name/core.py (a root module)

# Good — root modules use absolute imports even for siblings/children
from project_name.utils import filter_dict_by_keys

# Bad — relative import in a root module
from .utils import filter_dict_by_keys
```

## Module size

Keep modules small. As a rule of thumb, stay under 500 lines, and preferably well below
that. The number is a smell detector, not a hard limit: a module whose contents are tightly
coupled — one class and the helpers only it uses, a state machine whose cases must be read
together — is fine at 600 lines, while a 300-line module holding three unrelated concerns is
already too big. Modules are bound by logical or functional cohesion, not by line count;
splitting one along an arbitrary line boundary produces two modules that import each other
constantly and is worse than the original.

When a module has genuinely grown past what it should own, the ways to shrink it, in
rough order of preference:

- **Split into sibling modules.** The most common fix: one concern per file, side by side
    in the same package.
- **Promote it to a package** (a directory with an `__init__.py` — a *subpackage* when it
    sits inside another package). Turn `pipeline.py` into `pipeline/` with `base.py`,
    `stages.py`, `runner.py`, and re-export the public names from `pipeline/__init__.py`
    following [Public API in `__init__.py`](#public-api-in-__init__py).
- **Move standalone helpers to `utils`.** Functions in the module that don't depend on its
    subject matter — string munging, dict filtering, retry wrappers — belong in a shared
    utils module, not next to the domain logic that happens to call them first.
- **Use the framework's own decomposition.** Most libraries already offer a seam designed
    for this, and using it splits the code without inventing a structure: FastAPI
    `APIRouter`s defined per resource and mounted onto the app with `include_router`,
    Pydantic models composed from nested field models defined elsewhere, PyTorch
    `nn.Module`s assembled from smaller `nn.Module`s, Click/Typer sub-commands, pytest
    fixtures in `conftest.py`. Reach for the seam the package gives you before hand-rolling
    one.

Splitting is also a visibility exercise: whatever survives the move as importable becomes
the module's contract, so apply the [Visibility](#visibility) rules to the pieces as you
separate them.

## Visibility

A module-level name gets a leading underscore (`_helper`, `_Internal`) when it is part of
the module's implementation rather than its contract. The rule of thumb: "would I be okay
with another module importing this?" If no → underscore.

Apply consistently — drift here makes future refactors painful, because callers end up
depending on names that were never meant to be stable.

Underscore when:

- The name is only referenced inside the same file.
- The name exists solely to be a building block of another name in the same file
    (sentinel classes, helper builders, internal Pydantic config wrappers).
- The name is a single-use Pydantic schema for a route's request/response body.

Do **not** underscore when:

- The name is the return type, parameter type, or raised exception of a public function.
    It is part of that function's contract whether or not other code currently imports it.
- The name is used by a sibling module in the same package, even if no caller outside the
    package uses it. Package boundaries are the visibility boundary; re-export the name
    from `package/__init__.py` only when callers outside the package should use it.
- The name is a utility intentionally offered for ad-hoc use (one-off scripts, notebooks,
    internal tooling) even if no production caller exists.

Tests reaching into module internals do **not** make a name public. Tests are trusted
insiders and may import underscored names; the underscore still communicates "this is not
an API" to humans reading the code.

Use a single leading underscore. Double-leading underscores (`__name`) trigger Python's
name mangling and are appropriate only for instance attributes shielded from subclass
collisions — never for module-level names.

## Declaration order

Define private functions and classes **after** all public ones in the module. Readers
scanning a file top-to-bottom should encounter the public API first; implementation
details follow.

```python
# Good
class PublicClass:
    ...

def public_function() -> Result:
    return _helper()

class _InternalHelper:
    ...

def _helper() -> Result:
    ...

# Bad — private names before the public API they serve
def _helper() -> Result:
    ...

class _InternalHelper:
    ...

class PublicClass:
    ...

def public_function() -> Result:
    return _helper()
```

## Methods that don't use `self` or `cls`

When a method's body never references `self` or `cls`, it does not belong to the class —
make it a module-level function instead of a `@staticmethod`. A method that ignores the
instance is not really a method; keeping it on the class implies a dependency on instance
or class state that isn't there, and forces every caller to route through an instance to
reach pure logic. A free function states plainly "this is standalone," is directly
testable and importable without constructing the class, and reuses the module's existing
public/private layout rather than adding a second visibility axis inside the class.

Prefer a module-level function over `@staticmethod`. A `@staticmethod` is still namespaced
under the class and reachable only via it, carrying the same "belongs to this class"
implication with none of the access to state that would justify it. Reach for
`@staticmethod` only when an external contract requires the callable to live on the class
(e.g. a framework that looks it up as an attribute, or an override of a base-class
staticmethod).

Give the extracted function module-private visibility (a leading underscore) when it is
only an implementation detail of the module, following the [Visibility](#visibility) rules,
and place it after the public API following [Declaration order](#declaration-order). Update
call sites from `self._helper(...)` to `_helper(...)`.

Two cases are **not** violations, even though the body ignores `self`:

- **Interface methods.** A base-class default (`return []`) or an `@override` whose body
    happens not to touch `self` is fixed by the polymorphic contract — the signature must
    stay an instance method so subclasses and callers can rely on it.
- **Registered callables.** A method exposed to a framework by binding (an MCP tool, a
    route handler) must stay a method even if its current body is a stub or a pure wrapper,
    because the framework registers the bound attribute.

```python
# Good — pure helper is a module-private function, placed after the public class
class DashboardTools(BaseMcp):
    async def get_panels(self) -> dict:
        panels = _flatten_dashboard_panels(await self.fetch())
        ...

def _flatten_dashboard_panels(dashboard: dict) -> list[dict]:
    ...

# Bad — method that never uses self; a staticmethod would still be class-namespaced
class DashboardTools(BaseMcp):
    async def get_panels(self) -> dict:
        panels = self._flatten_dashboard_panels(await self.fetch())
        ...

    def _flatten_dashboard_panels(self, dashboard: dict) -> list[dict]:
        ...
```

## Blank lines

Add a blank line after the end of an indented block (`for`, `while`, `if`, `with`, `try`)
when the next statement is at the outer indentation level.

```python
# Good
for item in items:
    process(item)

return result

# Bad
for item in items:
    process(item)
return result
```

## Naming

Use American English spelling in all identifiers, docstrings, and comments.
Prefer `normalize` over `normalise`, `color` over `colour`, `serialize` over `serialise`, etc.

Avoid single-letter or two-letter variable names except in the simplest comprehension
patterns (e.g. `[x * 2 for x in values]`). Use descriptive names as soon as the
comprehension body is non-trivial or references multiple attributes.

```python
# Good
[EntitySummary(text=entity.text, ...) for entity in entities]

# Bad
[EntitySummary(text=e.text, ...) for e in entities]
```

## Logging

Use `logging` for diagnostics, runtime events, warnings, errors, and anything that should
be filterable, redirectable, or useful after the fact. Use `print` only when stdout output
is the user-facing result itself: CLI output, one-off scripts, notebooks, demos, or
human-readable inspection while debugging.

When `rich` is an available dependency and the output is meant for humans in a terminal,
prefer `rich.print(...)` over built-in `print(...)`. Keep built-in `print` or write to
`sys.stdout` directly for machine-readable stdout, exact byte/text protocols, tests that
assert literal output, or places where Rich markup, color detection, wrapping, or pretty
rendering would be surprising.

```python
# Good — human-facing CLI output
import json

import rich

rich.print({"status": "ok", "items": 3})

# Fine — stdout is the command's stable machine-readable output
print(json.dumps(payload, sort_keys=True))

# Bad — diagnostics should be log records
print(f"Sample failed: {result}")
```

Use `logging` directly rather than a per-module `logger = logging.getLogger(__name__)`.
Since the formatter already includes location info (`%(filename)s`, `%(lineno)d`), named
loggers add no practical benefit for an app.

```python
# Good
logging.warning(f"Sample failed: {result}")

# Bad
logger = logging.getLogger(__name__)
logger.warning(f"Sample failed: {result}")
```

For command-line apps and other entry points that own console logging setup, prefer Rich's
logging handler for readable terminal logs and rich tracebacks. Configure this once in the
entry point, not at library import time.

```python
# Good
import logging

import rich.logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[rich.logging.RichHandler(rich_tracebacks=True)],
)

# Bad — plain console formatting when Rich is already available
logging.basicConfig(level=logging.INFO)
```

Pin the Rich console width only when there is no tty, for services that run in containers.
Rich detects the terminal width from the attached tty (and re-detects on every render, so it
tracks live resizes); when there is none (Kubernetes/ArgoCD, Docker, any piped stdout) it
cannot, and falls back to 80 columns, wrapping log lines and tracebacks too tightly. A fixed
`Console(width=...)` fixes the container case but also overrides auto-detection on a real
terminal — so gate it on `sys.stdout.isatty()`: leave `width=None` (the auto-detecting
default) on a tty, and pin a wider value only off-tty. Rich also emits no ANSI color into a
non-tty by default, so container logs stay plain unless you set `force_terminal=True` —
usually undesirable, since most log viewers (e.g. the ArgoCD logs tab) show raw escape codes
rather than rendering them.

```python
import sys

# Good — auto-detects on a local terminal; pins 120 in a container (where it would else be 80)
handlers=[
    rich.logging.RichHandler(
        rich_tracebacks=True,
        console=rich.console.Console(width=None if sys.stdout.isatty() else 120),
    ),
]

# Bad — a fixed width overrides auto-detection everywhere, including local terminals
console=rich.console.Console(width=120)
```

Override RichHandler's timestamp format. Its default is `[%x %X]`, a locale date and time —
`[07/29/26 13:46:30]`, ambiguous between day-first and month-first readings, and with no
timezone at all. Print an ISO-ordered date and the UTC offset instead, so a log line can be
correlated with traces and with logs from other machines.

This has to be a **callable**, not a format string: RichHandler renders the timestamp from
`datetime.fromtimestamp(record.created)`, which is naive local time, so `%z` and `%Z` in a
format string both render empty. `astimezone()` attaches the system zone — UTC in a container,
the developer's zone locally — which makes the offset printable. Prefer `%z` (`+0400`) over
`%Z`, since `astimezone()` on a fixed-offset local zone yields a tzname like `"+04"` anyway.

```python
import datetime

import rich.text

# Good — ISO-ordered date, explicit offset: [2026-07-29 13:46:30 +0400]
def _format_rich_log_time(log_time: datetime.datetime) -> rich.text.Text:
    return rich.text.Text(log_time.astimezone().strftime("[%Y-%m-%d %H:%M:%S %z]"))

handlers=[rich.logging.RichHandler(log_time_format=_format_rich_log_time)]

# Bad — %z is silently empty, because the datetime handed over is naive
log_time_format="[%Y-%m-%d %H:%M:%S %z]"
```

Two things that quietly defeat it:

- **A formatter with a `datefmt`.** `RichHandler.render` prefers `self.formatter.datefmt` over
    the `log_time_format` passed to the constructor. The usual `logging.Formatter("%(message)s")`
    leaves `datefmt` as `None`, so the callable wins — but setting a `datefmt` on that formatter
    overrides the timestamp format with no error.
- **A library logger with its own handlers.** A logger that sets `propagate = False` and installs
    its own RichHandlers (FastMCP does both, on the `fastmcp` logger) never reaches the root
    handler, so its records keep the default format and the two sinks disagree. Pass the format
    into that library's own logging setup too — FastMCP's `configure_logging` splats
    `**rich_kwargs` into each RichHandler it builds, so `log_time_format=...` reaches both.

Beware double-logging when Rich shares the root logger with another sink that also renders to
the console. Notably, `logfire.configure()` enables its own console exporter by default, which
prints every record to stderr in its own format — on top of the RichHandler output — so each
line appears twice. Pass `console=False` to `logfire.configure(...)` (or the equivalent for
any other handler) so exactly one sink owns console rendering.

## String formatting

Prefer f-strings over `%`-style or `.format()` formatting, including in logging calls.

```python
# Good
logging.warning(f"Sample failed: {result}")

# Bad
logging.warning("Sample failed: %s", result)
```

## Docstrings

Use Google-style docstrings: first line is a single summary sentence, then a blank line,
then details. For multiline docstrings, the closing `"""` goes on its own line. Use
4-space indentation for continuation lines.

```python
# Good
def foo(self) -> str:
    """Short summary.

    Longer description with details:
        item one
        item two
    """

# Bad
def foo(self) -> str:
    """Short summary.
    Pattern: something  ← flush with summary, not 4-indented continuation
    """
```

## FastAPI

Do not specify `response_model` in route decorators when it duplicates the return type
annotation — FastAPI infers it automatically. Only use `response_model` when you need to
override the serialized type (e.g. returning a subclass but serializing as the base).

## Health endpoints

Web apps and long-running services must expose two health endpoints:

- `GET /livez` — liveness: the process is up. Keep it dependency-free (no DB, models, or
    downstream calls) so it stays green as long as the process itself is alive, and have it
    return the project version (see [Package version](#package-version)).
- `GET /readyz` — readiness: the app is ready to serve traffic. Check what a real request
    needs — database connections, loaded models, warmed caches — and return a non-200
    status until they are all ready.

Splitting the two lets an orchestrator restart a genuinely dead process (liveness) without
pulling a slow-to-warm but healthy instance out of rotation (readiness).

```python
import fastapi

import myapp  # exposes myapp.__version__

app = fastapi.FastAPI()

@app.get("/livez")
def livez() -> dict:
    return {"status": "ok", "version": myapp.__version__}

@app.get("/readyz")
def readyz(response: fastapi.Response) -> dict:
    if not model_is_loaded():
        response.status_code = fastapi.status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable"}

    return {"status": "ok"}
```

## Pydantic fields

Do not use the `...` (Ellipsis) sentinel in `pydantic.Field()`. Fields without a default
are required by default; just use keyword arguments.

```python
# Good
class Foo(pydantic.BaseModel):
    name: str = pydantic.Field(description="The name")

# Bad
class Foo(pydantic.BaseModel):
    name: str = pydantic.Field(..., description="The name")
```

Always pass the default as the `default=` keyword, never as the first positional argument.
Type checkers infer a `pydantic.Field()` with a positional default as having no default, so
they wrongly flag `Foo()` as missing a required argument.

```python
# Good
class Foo(pydantic.BaseModel):
    retries: int = pydantic.Field(default=3, description="Retry count")

# Bad — type checker thinks `retries` is required
class Foo(pydantic.BaseModel):
    retries: int = pydantic.Field(3, description="Retry count")
```

## Multiline strings

For multiline strings whose content spans several lines (e.g. a `description=` in
`pydantic.Field`, tool/field help text, prompts), use `inspect.cleandoc("""...""")` rather
than parenthesized per-line string concatenation. The triple-quoted form is far easier for
humans to edit: no per-line quotes to balance and no trailing spaces to hand-manage at each
line break. `cleandoc` strips the common leading indentation and the leading/trailing blank
lines, so the block can be indented to match its surroundings.

```python
# Good
description=inspect.cleandoc("""
    The ID of the transition to perform.
    Use the get_transitions tool to find available transition IDs.
""")

# Bad — quotes and trailing spaces to juggle on every line
description=(
    "The ID of the transition to perform. "
    "Use the get_transitions tool to find available transition IDs."
)
```

This applies to strings with genuinely multiple lines of content. A single sentence that
merely wraps to satisfy the line-length limit is not a multiline string — leave it as one
string literal (parenthesized if needed for wrapping); do not split a single sentence into a
`cleandoc` block just because it is long.

## Regular expressions

Prefer `re2` (the `google-re2` package) over the stdlib `re` for **critical** regex code:
patterns applied to untrusted or user/LLM-supplied input, or complex patterns where
catastrophic backtracking (ReDoS) or edge-case reliability matters. RE2 guarantees
linear-time matching and cannot blow up on a pathological pattern or input.

For **simple, fixed, internal** patterns, the stdlib `re` is good enough — reach for `re2`
where the reliability guarantee actually buys something, not everywhere by reflex. Both are
acceptable for simple cases; using `re2` there is fine but not required.

Import the module (`import re2`), consistent with the imports rule. A few API differences
from `re` to keep in mind:

- No `flags=` argument and no `re.IGNORECASE` / `re.DOTALL` constants. Use inline flags at
    the start of the pattern instead: `(?i)` for case-insensitive, `(?s)` for dotall.
- A compiled pattern's `.sub()` is `sub(repl, text, count=0)` — there is no `string=` keyword.
- No backreferences *within the pattern* and no lookahead/lookbehind (RE2's design). A
    numbered backreference in the *replacement* string (`r"**\1**"`) is fine.

```python
# Good — untrusted pattern from a tool argument, so RE2's linear-time guarantee matters
import re2

def filter_lines(lines: list[str], user_pattern: str) -> list[str]:
    return [line for line in lines if re2.search(user_pattern, line)]

# Good — inline (?i) replaces the flags= argument
forbidden = re2.compile(r"(?i)\b(DROP|DELETE|TRUNCATE)\b")

# Fine — a simple, fixed, internal pattern; stdlib re is good enough here
import re

issue_keys = re.findall(r"[A-Z]+-\d+", text)
```

## Return statements

Prefer inline construction in `return` over assigning to a named variable first, but only
for simple value objects (dataclasses, Pydantic models) where the constructor arguments
are self-documenting. A variable named after its type adds no information.

```python
# Good — constructor args document the return value
return Dataset(samples=samples, name="synthetic", description="...")

# Bad — variable name adds nothing
dataset = Dataset(samples=samples, name="synthetic", description="...")
return dataset
```

Assign first when the value requires intermediate steps or conditional logic.

## `__init__` return annotations

Do not annotate `__init__` with `-> None`. Python guarantees `__init__` returns `None`
(`TypeError` is raised at construction otherwise), so the annotation adds noise without
information.

```python
# Good
class Foo:
    def __init__(self, x: int):
        self.x = x

# Bad
class Foo:
    def __init__(self, x: int) -> None:
        self.x = x
```

## Override decorator

Always add `@override` from `typing` to every method that overrides a base class method,
including `__call__`, other dunder methods, and `@classmethod` overrides.

```python
# Good
from typing import override

class Foo(Base):
    @override
    def __call__(self) -> dict: ...

    @override
    @classmethod
    def settings_customise_sources(cls, ...) -> ...: ...

# Bad
class Foo(Base):
    def __call__(self) -> dict: ...
```

## Constants

Avoid module-level and class-level constants unless they are genuinely shared across
multiple call sites. Prefer computing values inline or in `__init__` where they are used.
Magic numbers that are parameters should be taken as constructor arguments with defaults,
not frozen as class constants.

## Enums

Prefer an enum over bare string literals whenever the same string identity appears in more
than one place (dispatch keys, dataset/model names, status values, config modes). A free-form
string repeated across modules drifts silently when one copy is renamed; an enum gives a single
source of truth, find-all-references, and type-checker coverage. The moment you write the same
literal a second time, reach for an enum.

For string enums, use `enum.StrEnum` with `enum.auto()` — `auto()` sets each value to the
lowercased member name, so the member is the single source of truth and the value can't drift
out of sync with it. Only assign explicit values when an external contract requires a specific
string that differs from the member name (e.g. a wire format or third-party API), and add a
comment saying so.

```python
# Good — member name is the value, no duplication
class DatasetName(enum.StrEnum):
    composite = enum.auto()       # "composite"
    edge_cases = enum.auto()      # "edge_cases"
    json_structure = enum.auto()

# Acceptable — explicit value pinned by an external contract
class Provider(enum.StrEnum):
    open_ai = "openai"  # value fixed by the vendor's API

# Bad — value hand-typed to match the member name, free to drift
class DatasetName(enum.StrEnum):
    composite = "composite"
    edge_cases = "edge_cases"
```

`StrEnum` members are `str` subclasses, so they compare and hash equal to their string value —
they work as dict keys looked up by plain strings and in `==` checks against strings, including
values deserialized from JSON or read from files.

## Exhaustive match statements

When matching on an enum or a closed union of types, end with `case _: assert_never(value)`
to make the match exhaustive. Pyright/mypy will then flag a type error if a new variant is
added without a corresponding case — turning a silent fallthrough into a static check.

Pass the matched value to `assert_never()` so the type checker can verify the narrowed
type is `Never`. A bare `assert_never()` still raises at runtime but doesn't give the
type checker anything to verify.

```python
# Good
match quantization:
    case Quantization.fp32: ...
    case Quantization.fp16: ...
    case Quantization.bf16: ...
    case Quantization.int8: ...
    case _:
        assert_never(quantization)

# Bad — type checker can't verify exhaustiveness
match quantization:
    case Quantization.fp32: ...
    case Quantization.fp16: ...
    case _:
        assert_never()
```

## Sentinel defaults for None-vs-unset disambiguation

When a function argument is genuinely `T | None` and the caller may pass `None`
explicitly with different meaning from "not passed", use `...` (Ellipsis) as the default
sentinel rather than introducing a module-level `_UNSET = object()`. Import `EllipsisType`
from `types` for the annotation.

`...` is a built-in singleton, so no extra object needs to be allocated or named, and
`is ...` reads naturally at the call site. No package in practice passes `...` as a
legitimate argument value, so collision risk is nil.

```python
# Good
from types import EllipsisType

def build_pipeline(
    self,
    device: str | None | EllipsisType = ...,
) -> Pipeline:
    return pipeline(device=self.device if device is ... else device)

# Bad — extra named sentinel adds ceremony with no benefit
_UNSET = object()

def build_pipeline(self, device=_UNSET) -> Pipeline:
    return pipeline(device=self.device if device is _UNSET else device)
```

Don't use this pattern when the argument's type already excludes `None` — a plain
`device: str = self.device`-style default (or a fresh argument with no default at all)
is simpler. The sentinel is only justified when both `None` and "not passed" are
meaningful, distinct states.

## Public API in `__init__.py`

Everything imported or defined in an `__init__.py` is treated as the package's public API
by convention. Do not use `__all__`, and do not use `import x as x` re-export aliases.

Reasoning:

- `__all__` is a string-based duplicate of the import list, not directly connected to the
    symbols it names, so it drifts silently when symbols are renamed or removed.
- `import x as x` is visually noisy and still duplicates the name. Its only real benefit
    is signalling intent to type checkers, which we get more cheaply via the `F401` ignore
    in `pyproject.toml` (`per-file-ignores = { "__init__.py" = ["F401"] }`).

Trade-off: non-standard, so if another project ever consumes this code as a library their
type checker won't inherit the `F401` suppression. Acceptable for now; fix mechanically
later by rewriting to `import x as x` form if needed.

Only import a name in `__init__.py` if it is actually referenced by code outside the
package (i.e. imported via `from package import Name`), or if the package is consumed as
a library and the name is part of its intentional public surface. Do not import names
simply because they exist in a child module — that bloats the public API and creates
misleading re-exports that no caller uses.

```python
# Good — only names that outside callers actually import
from .main import Config, ProvidedConfig, UserConfigStoreName
from .tool_exposure import ToolExposureMode

# Bad — Stage and CodeModeConfig are internal to the config package;
#       no parent module imports them
from .main import Config, ProvidedConfig, Stage, UserConfigStoreName
from .tool_exposure import CodeModeConfig, SearchType, ToolExposureMode, ToolSearchConfig
```

## Package version

Declare the package version in the project root `__init__.py` by reading it from the
installed distribution metadata rather than hardcoding a literal:

```python
import importlib.metadata

__version__ = importlib.metadata.version(__name__)
```

Inside the root `__init__.py`, `__name__` is already the package name, so passing it keeps
a single source of truth (`pyproject.toml`) and stays correct if the package is renamed —
no duplicated magic string. `importlib.metadata.version()` looks up a *distribution* name,
so this only works when the distribution name equals the import name. Keep them identical:
the `[project] name` in `pyproject.toml` must match the importable package name.

```toml
# pyproject.toml — distribution name matches the src/<package> import name
[project]
name = "myapp"      # -> importlib.metadata.version("myapp"), i.e. version(__name__)
```

```python
# Bad — hardcoded string drifts from pyproject and duplicates the name
__version__ = importlib.metadata.version("myapp")

# Bad — self-import to recover the name; __name__ already is it
import myapp
__version__ = importlib.metadata.version(myapp.__name__)
```

## Multiline function arguments

Always wrap multiline expressions used as function arguments in parentheses. This makes it
unambiguous where each argument ends, since all continuation lines are clearly enclosed.

```python
# Good
result = foo(
    x=(
        value_if_true
        if condition
        else value_if_false
    ),
)

# Bad — hard to tell where the argument ends
result = foo(
    x=value_if_true
    if condition
    else value_if_false,
)
```

## ExceptionGroup and TaskGroup

A function that owns an `asyncio.TaskGroup` (or otherwise produces an `ExceptionGroup`)
must not let the group leak out of its public API. Unwrap inside the function and re-raise
a single, concrete exception that callers can match with plain `except`.

Rationale:

- The use of `TaskGroup` is an implementation detail. Leaking `ExceptionGroup` couples
    every caller to that choice.
- Plain `except SomeError` does not match an `ExceptionGroup` containing `SomeError`.
    Leaked groups silently bypass framework handlers (FastAPI exception handlers,
    `tenacity.retry_if_exception_type`, `pytest.raises`) and end up in the catch-all 500
    path.
- `TaskGroup` can wrap exceptions in nested groups when multiple tasks fail. Picking
    `eg.exceptions[0]` is unsafe — that element may itself be a group. Walk the tree to
    collect leaf exceptions before deciding what to re-raise.

```python
# Good — group is unwrapped at the boundary; callers use plain except
async def fetch_all(endpoints: list[str]) -> list[Result]:
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(_fetch(endpoint)) for endpoint in endpoints]
    except* httpx.HTTPError as eg:
        leaves = _flatten_exception_group(eg)
        for exc in leaves:
            logging.warning(f"Endpoint failed: {exc!r}")
        raise leaves[0] from eg

    return [task.result() for task in tasks]

# Bad — caller's ``except httpx.HTTPError`` will not match
async def fetch_all(endpoints: list[str]) -> list[Result]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(_fetch(endpoint)) for endpoint in endpoints]

    return [task.result() for task in tasks]
```

Exception: a function whose contract is "do N things and report all failures" (form
validation, batch processing where partial results matter) may legitimately return or raise
an `ExceptionGroup`. Document that explicitly in the docstring so callers know to use
`except*`.

## Assertions

Use `assert` only in tests and for debugging invariants that should never be violated in
correct code. Never use `assert` to validate user input, API responses, or any runtime
condition that can legitimately fail in production — `assert` statements are stripped when
Python runs with the `-O` flag, so they provide no safety guarantee in optimized builds.

```python
# Good — assert guards an internal invariant; a bug elsewhere is the only cause
def _process(items: list[str]) -> None:
    assert items, "caller must ensure items is non-empty"
    ...

# Bad — user input or external data must be validated with a real exception
def process(items: list[str]) -> None:
    assert items, "items must not be empty"  # silently skipped with -O
    ...

# Good — raise explicitly for runtime validation
def process(items: list[str]) -> None:
    if not items:
        raise ValueError("items must not be empty")
    ...
```

## Test guidelines

- Keep failures actionable — state what resource or config is missing, naming the exact
    env var or fixture to set.
- In **unit tests**, never `pytest.skip`. They have no external prerequisites, so a skip
    can only mean the test was written to dodge its own setup.
- In **integration tests**, prefer `pytest.fail(...)` — but `pytest.skip(...)` is
    acceptable for an optional capability the deployment may genuinely not use.

The distinction is whether the missing thing *should* be there:

- **Fail** when absence indicates a misconfiguration or a broken fixture — the resource
    exists in any healthy environment. A repository always has files and commits; a
    Confluence instance always has pages. If those come back empty, something is wrong and
    you want to hear about it.
- **Skip** when absence is a legitimate deployment choice. A team that tracks work in Jira
    may never open a GitLab issue, so `get_issue` has nothing to exercise. That is not a
    defect, and failing the suite over it trains people to ignore red.

```python
# Good — the feature may legitimately be unused in this deployment
if issue_iid is None:
    pytest.skip("No GitLab issue found; set TEST_GITLAB_ISSUE_IID")

# Bad — every non-empty repository has commits, so this hides a broken fixture
if commit_sha is None:
    pytest.skip("No commit SHA available")
```

**A skip must never absorb flakiness.** If a resource is normally present and the call
occasionally returns nothing, skipping converts an intermittent backend failure into a
silent green — the worst outcome, because the suite reports success while coverage quietly
drops. When unsure, re-run the test several times: if it passes consistently and skipped
once, the skip is masking instability and belongs as a failure.

Skip the narrowest thing possible. A `pytest.skip` partway through a test also discards the
assertions that already passed, so the report cannot distinguish "two of three tools
verified" from "nothing ran". If only the tail of a test is conditional, split it out.

Because a skip is easy to stop noticing, make it visible and explain it:

- Set `addopts = "-ra"` in `[tool.pytest.ini_options]` so every skip prints its reason in
    the summary. Without it a skip is a bare `s` in the progress line and reads like a pass.
- Comment any skip that is an exception to the surrounding file's convention, saying why,
    so it is not later "fixed" into a failure by someone applying this guide literally.
