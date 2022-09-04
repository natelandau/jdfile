"""Utilities for working with files."""
from enum import Enum
from pathlib import Path


def create_unique_filename(original: Path, separator: Enum, append_integer: bool = False) -> Path:
    """Create a unique filename by creating a unique integer and adding it to the filename.

    Args:
        original (Path): The original filename.
        separator (Enum): The separator to use.
        append_integer (bool, optional): If True, append an integer to the filename. If false, places unique integer before file extensions. Defaults to False.

    Returns:
        Path: The unique filename.

    """
    if separator == "underscore":
        sep = "_"
    elif separator == "dash":
        sep = "-"
    elif separator == "space":
        sep = " "
    else:
        sep = "-"

    if original.exists():
        parent: Path = original.parent
        stem: str = str(original)[: str(original).rfind("".join(original.suffixes))].replace(
            f"{str(parent)}/", ""
        )
        suffixes: list[str] = original.suffixes

        unique_integer = 1
        if append_integer:
            new_path = Path(parent / f"{stem}{''.join(suffixes)}.{unique_integer}")
        else:
            new_path = Path(parent / f"{stem}{sep}{unique_integer}{''.join(suffixes)}")

        while new_path.exists():
            unique_integer += 1
            if append_integer:
                new_path = Path(parent / f"{stem}{''.join(suffixes)}.{unique_integer}")
            else:
                new_path = Path(parent / f"{stem}{sep}{unique_integer}{''.join(suffixes)}")

        return new_path

    else:
        return original
