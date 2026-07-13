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

    packages.sort(key=lambda x: x[1], reverse=True)
    for name, size in packages:
        print(f"{size / 1024 / 1024:>8.2f} MB  {name}")


if __name__ == "__main__":
    main()
