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

For multiline strings (e.g. `description=` in `pydantic.Field`), use
`inspect.cleandoc("""...""")` rather than parenthesized string concatenation.

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

- Do **not** use `pytest.skip` in tests. If a prerequisite is missing, fail the test with
    a clear message using `pytest.fail(...)` or an assertion stating what
    resource/config is missing.
- Keep failures actionable — state what resource or config is missing.

## Security

- `.claude/`, `.mcp.json`, and skill files are version-controlled and must **never**
    contain secrets.
- Use environment-variable references (e.g. `${LOGFIRE_READ_TOKEN}`) instead of
    hardcoded tokens anywhere that is committed to git.
- Review with `git diff` before committing changes to these files.
