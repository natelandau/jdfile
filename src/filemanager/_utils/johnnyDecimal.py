"""Utilities for working with Johnny Decimal folders."""
import re
from collections.abc import Generator
from pathlib import Path

import rich.repr
from plumbum import FG, CommandNotFound, ProcessExecutionError, local
from rich import print
from typer import Abort

from filemanager._utils.alerts import logger as log


def show_tree(project: Path) -> None:  # pragma: no cover
    """Print the project tree.

    Args:
        project: (Path) Project to print.

    Raises:
        Abort: If the project tree is empty.
    """
    try:
        tree = local["tree"]
        grep = local["grep"]
        print(str(project))
        showtree = tree["-d", "-L", "3", "--noreport", project] | grep["--color=never", "[0-9]"]
        showtree & FG
    except CommandNotFound as e:
        log.error("Nomad binary is not installed")
        raise Abort() from e
    except ProcessExecutionError as e:
        log.error(e)
        raise Abort() from e


@rich.repr.auto
class Folder:
    """Class defining Johnny Decimal project folder available for moving files into."""

    def __init__(
        self,
        path: Path,
        level: int,
        project: Path,
        project_name: str,
    ) -> None:
        """Initialize Project object.

        Args:
            path: (Path) Path to the folder.
            level: (int) Johnny decimal level of the folder. (1: top level, 2: sub-level, 3: sub-sub-level)
            project: (Path) Path to the root of the project.
            project_name: (str) Name of the project.
        """
        self.path: Path = path
        self.level: int = level
        self.root: Path = project
        self.project_name: str = project_name

        if self.level == 3:
            self.name: str = re.sub(r"^\d{2}\.\d{2}[- _]", "", str(self.path.name)).strip()
            self.number: str = re.match(r"(^\d{2}\.\d{2})[- _]", str(self.path.name)).group(1).strip()  # type: ignore[union-attr]
            self.tree: str = str(self.path).replace(str(self.root), "")
        elif self.level == 2:
            self.name = re.sub(r"^\d{2}[- _]", "", str(self.path.name)).strip()
            self.number = re.match(r"(^\d{2})[- _]", str(self.path.name)).group(1).strip()  # type: ignore[union-attr]
            self.tree = str(self.path).replace(str(self.root), "")
        elif self.level == 1:
            self.name = re.sub(r"^\d{2}-\d{2}[- _]", "", str(self.path.name)).strip()
            self.number = re.match(r"^(\d{2}-\d{2})[- _]", str(self.path.name)).group(1).strip()  # type: ignore[union-attr]
            self.tree = str(self.path).replace(str(self.root), "")
        else:  # pragma: no cover
            self.name = "None"
            self.number = "None"
            self.tree = "None"

        self.tree = re.sub(r"/\d{2}-\d{2}[- _]|/\d{2}[- _]|/\d{2}\.\d{2}[- _]", "/", self.tree)

        self.terms: list[str] = [word for word in re.split(r"[- _]", self.name) if word]

        if Path(self.path, ".filemanager").exists():
            content = Path(self.path, ".filemanager").read_text().splitlines()
            for line in content:
                if line.startswith("#"):
                    continue
                else:
                    self.terms.append(line)

    def __rich_repr__(
        self,
    ) -> Generator[tuple[str, str | Path | list | int], None, None]:  # pragma: no cover
        """Rich representation of the Category object."""
        yield "path", self.path
        yield "level", self.level
        yield "name", self.name
        yield "number", self.number
        yield "terms", self.terms
