"""Utilities for working with Johnny Decimal folders."""
import re
from collections.abc import Generator
from pathlib import Path

import rich.repr
from plumbum import FG, CommandNotFound, ProcessExecutionError, local
from rich import print
from typer import Abort

from filemanager._utils.alerts import logger as log


@rich.repr.auto
class JDProject:
    """Class defining a Johnny Decimal project."""

    def __init__(
        self,
        root: str,
        name: str,
    ) -> None:
        """Initialize JohnnyDecimalFolder object.

        Args:
            root: (Path) Root directory of the project.
            name: (str) Name of the project.
        """
        self.root = Path(root).expanduser().resolve()
        self.name = name
        self.category_dict: dict[str, dict[str, str | Path | dict]] = _build_categories(self.root)

    def __rich_repr__(
        self,
    ) -> Generator[tuple[str, str | Path | dict], None, None]:
        """Rich representation of the Category object."""
        yield "root", self.root
        yield "name", self.name
        yield "categories", self.category_dict

    def print_tree(self) -> None:  # pragma: no cover
        """Print the project tree.

        Raises:
            Abort: If the project tree is empty.
        """
        try:
            tree = local["tree"]
            grep = local["grep"]
            print(str(self.root))
            showtree = (
                tree["-d", "-L", "3", "--noreport", self.root] | grep["--color=never", "[0-9]"]
            )
            showtree & FG
        except CommandNotFound as e:
            log.error("Nomad binary is not installed")
            raise Abort() from e
        except ProcessExecutionError as e:
            log.error(e)
            raise Abort() from e


@rich.repr.auto
class Project:
    """Class defining Johnny Decimal project folder available for moving files into."""

    def __init__(
        self,
        path: Path,
        level: int,
    ) -> None:
        """Initialize Project object.

        Args:
            path: (Path) Path to the folder.
            level: (int) Johnny decimal level of the folder. (1: top level, 2: sub-level, 3: sub-sub-level)
        """
        self.path: Path = path
        self.level: int = level

        if self.level == 3:
            self.name: str = re.sub(r"^\d{2}\.\d{2}[- _]", "", str(self.path.name)).strip()
            self.number: str = re.match(r"(^\d{2}\.\d{2})[- _]", str(self.path.name)).group(1).strip()  # type: ignore[union-attr]
        elif self.level == 2:
            self.name = re.sub(r"^\d{2}[- _]", "", str(self.path.name)).strip()
            self.number = re.match(r"(^\d{2})[- _]", str(self.path.name)).group(1).strip()  # type: ignore[union-attr]
        elif self.level == 1:
            self.name = re.sub(r"^\d{2}-\d{2}[- _]", "", str(self.path.name)).strip()
            self.number = re.match(r"^(\d{2}-\d{2})[- _]", str(self.path.name)).group(1).strip()  # type: ignore[union-attr]
        else:
            self.name = "None"
            self.number = "None"

        self.terms: list[str] = [self.name]

        if Path(self.path, ".filemanager").exists():
            content = Path(self.path, ".filemanager").read_text().splitlines()
            for line in content:
                if line.startswith("#"):
                    continue
                else:
                    self.terms.append(line)

    def __rich_repr__(
        self,
    ) -> Generator[tuple[str, str | Path | list | int], None, None]:
        """Rich representation of the Category object."""
        yield "path", self.path
        yield "level", self.level
        yield "name", self.name
        yield "number", self.number
        yield "terms", self.terms


def _build_categories(folder: Path) -> dict[str, dict[str, str | Path | dict]]:
    """Build the folder tree from files matching the Johnny Decimal System.

    Args:
        folder: (Path) Root folder of the tree.

    Returns:
        dict: Dictionary of categories, subcategories, and areas.
    """

    def _build_areas(folder: Path) -> dict:
        """Build the areas in the folder tree.

        Args:
            folder: (Path) Folder to build categories from.

        Returns:
            dict: Areas in the category.
        """
        areas: dict[Path, Path] = {}
        for area in folder.iterdir():
            if area.is_dir() and re.match(r"^\d{2}\.\d{2}[- _]", area.name):
                areas[area] = area
        return areas

    def _build_subcategories(folder: Path) -> dict:
        """Build the categories in the folder tree.

        Args:
            folder: (Path) Folder to build categories from.

        Returns:
            dict: Subcategories in the folder.
        """
        subcategories: dict[str, dict[str, Path | str | dict]] = {}
        for subcategory in folder.iterdir():
            if subcategory.is_dir() and re.match(r"^\d{2}[- _]", subcategory.name):
                subcategories[subcategory.name] = {
                    "path": subcategory,
                    "areas": _build_areas(subcategory),
                }
        return subcategories

    categories: dict[str, dict[str, str | Path | dict]] = {}
    for category in folder.iterdir():
        if category.is_dir() and re.match(r"^\d{2}-\d{2}[- _]", category.name):
            categories[category.name] = {
                "path": category,
                "subcategories": _build_subcategories(category),
            }

    return categories
