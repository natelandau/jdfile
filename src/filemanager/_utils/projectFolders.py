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
        self.relative = f"{self.path.relative_to(self.root.parents[0])}"

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


def populate_project_folders(config: dict, project_name: str) -> list[Folder]:
    """Populate the list of Project objects (deepest level available for filing).

    Args:
        config: (dict) Configuration dictionary.
        project_name: (str) The project name to index.

    Returns:
        list[str]: List of Projects.

    """
    project_path = find_root_dir(config, project_name)

    available_folders = []

    areas = [
        area
        for area in project_path.iterdir()
        if area.is_dir() and re.match(r"^\d{2}-\d{2}[- _]", area.name)
    ]

    for area in areas:
        categories = [
            category
            for category in area.iterdir()
            if category.is_dir() and re.match(r"^\d{2}[- _]", category.name)
        ]

        if len(categories) == 0:
            available_folders.append(Folder(area, 1, project_path, project_name))
        else:
            for category in categories:
                subcategories = [
                    subcategory
                    for subcategory in category.iterdir()
                    if subcategory.is_dir() and re.match(r"^\d{2}\.\d{2}[- _]", subcategory.name)
                ]

                if len(subcategories) == 0:
                    available_folders.append(Folder(category, 2, project_path, project_name))
                else:
                    for subcategory in subcategories:
                        available_folders.append(Folder(subcategory, 3, project_path, project_name))

    log.trace("Populated project folders")
    return available_folders


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


def find_root_dir(config: dict, project_name: str) -> Path:
    """Find a valid root directory for the specified project.

    Args:
        config: (dict) Configuration dictionary.
        project_name: (str) The project name to index.

    Returns:
        Path: Path to a valid root directory.

    Raises:
        Abort: If a project folder is not found.
    """
    try:
        if config["projects"]:
            for project in config["projects"]:
                if project_name.lower() == config["projects"][project]["name"].lower():
                    project_path = Path(config["projects"][project]["path"]).expanduser().resolve()
                    break

            if project_path.exists() is False:
                log.error(f"'Config variable 'project_path': '{project_path}' does not exist.")
                raise Abort()

        else:
            log.error("No projects found in the configuration file")
            raise Abort()  # noqa: TC301
    except KeyError as e:
        log.error(f"{e} is not defined in the config file.")
        raise Abort() from e
    except UnboundLocalError as e:
        log.error(f"'{project_name}' is not defined in the config file.")
        raise Abort() from e

    return project_path
