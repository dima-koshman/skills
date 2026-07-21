#!/usr/bin/env python3
"""Print every installed package of the running interpreter's environment, by size.

Stdlib-only, so it can run under any interpreter. Run it with the interpreter whose
environment you want to inspect, e.g. `uv run python scripts/get_venv_packages_size.py`.
"""

import importlib.metadata
import pathlib


def main() -> None:
    packages: list[tuple[str, int]] = []
    for dist in importlib.metadata.distributions():
        size = 0
        if dist.files:
            for file in dist.files:
                full_path = pathlib.Path(str(dist.locate_file(file)))
                if full_path.exists():
                    size += full_path.stat().st_size

        packages.append((dist.name, size))

    packages.sort(key=lambda x: x[1])
    for name, size in packages:
        print(f"{size / 1024 / 1024:>8.2f} MB  {name}")


if __name__ == "__main__":
    main()
