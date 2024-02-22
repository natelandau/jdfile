"""Model for the project directory."""

import functools
import re
from pathlib import Path
from typing import Any

import rich.repr
import typer

from jdfile._config import Config
from jdfile.constants import FolderType
from jdfile.utils import alerts
from jdfile.utils.alerts import logger as log


@rich.repr.auto
class Folder:
    """Representation of a folder that is available for content to be filed to.

    Attributes:
        area: (Path) Path to the area folder, if the folder is a category or subcategory.
        category: (Path) Path to the category folder, if the folder is a subcategory.
        name: (str) Name of the folder.
        number: (str) Number of the folder.
        path: (Path) Path to the folder.
        relative: (str) Path relative to the parent folder of the project
        terms: (list[str]) List of terms in the folder name and .jdfile files.
        type: (FolderType) Type of the folder.

    """

    def __init__(
        self,
        path: str,
        folder_type: FolderType,
        area: Path | None = None,
        category: Path | None = None,
    ) -> None:
        self.path = Path(path).expanduser().resolve()
        self.type = folder_type
        self.area = area
        self.category = category

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover  # noqa: PLW3201
        """Rich representation of the Folder object."""
        yield "area", self.area
        yield "category", self.category
        yield "name", self.name
        yield "number", self.number
        yield "path", self.path
        yield "terms", self.terms
        yield "type", self.type

    @functools.cached_property
    def name(self) -> str:
        """Name of the folder."""
        if self.type == FolderType.AREA:
            return re.sub(r"^\d{2}-\d{2}[- _]", "", str(self.path.name)).strip()

        if self.type == FolderType.CATEGORY:
            return re.sub(r"^\d{2}[- _]", "", str(self.path.name)).strip()

        if self.type == FolderType.SUBCATEGORY:
            return re.sub(r"^\d{2}\.\d{2}[- _]", "", str(self.path.name)).strip()

        return None

    @functools.cached_property
    def number(self) -> str:
        """Johnny Decimal number of the folder."""
        if self.type == FolderType.AREA:
            return re.match(r"^(\d{2}-\d{2})[- _]", str(self.path.name)).group(0).strip("- _")

        if self.type == FolderType.CATEGORY:
            return re.match(r"^(\d{2})[- _]", str(self.path.name)).group(0).strip("- _")

        if self.type == FolderType.SUBCATEGORY:
            return re.match(r"^(\d{2}\.\d{2})[- _]", str(self.path.name)).group(0).strip("- _")

        return None

    @functools.cached_property
    def terms(self) -> list[str]:
        """Terms used to match the folder."""
        terms = [word for word in re.split(r"[- _]", self.name) if word]
        if Path(self.path, ".jdfile").exists():
            content = Path(self.path, ".jdfile").read_text().splitlines()
            for line in content:
                if line.startswith("#"):
                    continue
                terms.append(line)

        return terms


@rich.repr.auto
class Project:
    """Representation of a project directory.

    Attributes:
        all_folders: (dict[str, dict[str, Any]]) All folders in the project.
        config: (dict[str, Any]) Configuration for the project.
        exists: (bool) Whether the project exists.
        name: (str) Name of the project.
        path: (Path) Path to the project.
        usable_folders: (dict[str, dict[str, Any]]) Johnny Decimal folders that can be used for filing.
    """

    def __init__(
        self,
        config: Config = None,
    ) -> None:
        """Initialize the project folder."""
        self.config = config
        if (
            self.config is None
            or self.config.project_name is None
            or self.config.project_path is None
        ):
            self.path = None
            self.name = None
            self.exists = False
            self.all_folders = {}
        else:
            self.path = self._validate_project_path(self.config.project_path)
            self.name = self.config.project_name
            self.exists = self.path.exists()
            self.all_folders = self._find_folders()

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover  # noqa: PLW3201
        """Rich representation of the Project object."""
        yield "exists", self.exists
        yield "name", self.name
        yield "path", self.path

    def _find_folders(self) -> dict[str, dict[str, Any]]:
        """Find all areas (top level folders) in the project.

        Returns:
            list[Path]: List of paths to areas.
        """
        area_dict = {}
        for area in self.path.iterdir():
            if area.is_dir() and re.match(r"^\d{2}-\d{2}[- _]", area.name):
                area_dict[area.name] = {
                    "path": area,
                    "categories": self._find_categories(area),
                }
        return dict(sorted(area_dict.items()))

    def _find_categories(self, area: Path) -> dict[str, dict[str, Any]]:
        """Find all categories in the project.

        Args:
            area: (Path) Path to the area.

        Returns:
            Dict[str, list[Path] | Path]: Dictionary of categories and subcategories.
        """
        category_dict = {}
        for category in area.iterdir():
            if category.is_dir() and re.match(r"^\d{2}[- _]", category.name):
                category_dict[category.name] = {
                    "path": category,
                    "subcategories": self._find_subcategories(category),
                }
        return dict(sorted(category_dict.items()))

    @staticmethod
    def _find_subcategories(category: Path) -> list[Path]:
        """Find all subcategories in the project.

        Args:
            category: (Path) Path to the category.

        Returns:
            list[Path]: List of paths to subcategories.
        """
        return sorted(
            [
                subcategory
                for subcategory in category.iterdir()
                if subcategory.is_dir() and re.match(r"^\d{2}\.\d{2}[- _]", subcategory.name)
            ]
        )

    @staticmethod
    def _validate_project_path(path: Path) -> Path:
        """Assign the project path after validating it exists.

        Args:
            path: (Path) Path to the project.

        Returns:
            bool: Whether the path is valid.
        """
        path = Path(path).expanduser().resolve()

        if not path.exists():
            alerts.error(f"Specified project path does not exist: {path}")
            raise typer.Abort()

        if not path.is_dir():
            alerts.error(f"Specified project path is not a directory: {path}")
            raise typer.Abort()

        return path

    @functools.cached_property
    def usable_folders(self) -> list[Folder]:
        """Create property for usable folders.

        Returns:
            list[Folder]: List of paths to usable folders.
        """
        if not self.exists:
            return []

        usable_folders: list[Folder] = []
        for _area in self.all_folders:
            if (
                self.all_folders[_area]["categories"] == {}
                or Path(self.all_folders[_area]["path"] / ".jdfile").exists()
            ):
                usable_folders.append(
                    Folder(
                        self.all_folders[_area]["path"],
                        FolderType.AREA,
                        area=self.all_folders[_area]["path"],
                    )
                )

            if self.all_folders[_area]["categories"] != {}:
                for _category in self.all_folders[_area]["categories"]:
                    if (
                        self.all_folders[_area]["categories"][_category]["subcategories"] == []
                        or Path(
                            self.all_folders[_area]["categories"][_category]["path"] / ".jdfile"
                        ).exists()
                    ):
                        usable_folders.append(
                            Folder(
                                self.all_folders[_area]["categories"][_category]["path"],
                                FolderType.CATEGORY,
                                area=self.all_folders[_area]["path"],
                                category=self.all_folders[_area]["categories"][_category]["path"],
                            )
                        )

                    if len(self.all_folders[_area]["categories"][_category]["subcategories"]) > 0:
                        for _subcategory in self.all_folders[_area]["categories"][_category][
                            "subcategories"
                        ]:
                            usable_folders.append(  # noqa: PERF401
                                Folder(
                                    _subcategory,
                                    FolderType.SUBCATEGORY,
                                    area=self.all_folders[_area]["path"],
                                    category=self.all_folders[_area]["categories"][_category][
                                        "path"
                                    ],
                                ),
                            )
        log.trace(f"Populated {len(usable_folders)} folders")
        return sorted(usable_folders, key=lambda x: x.path)

    def tree(self) -> None:
        """Print a tree of the project."""
        pipe = "│"
        branch = "├──"
        space = "   "
        elbow = "└──"

        if self.exists is False:
            alerts.warning("No Johnny Decimal project found.")
            return
        if self.exists:
            print(self.path)  # noqa: T201
            print("│")  # noqa: T201
            for _n, _area in enumerate(self.all_folders):
                if _n < len(self.all_folders) - 1:
                    print(branch, _area)  # noqa: T201
                    last_area = False
                else:
                    print(elbow, _area)  # noqa: T201
                    last_area = True
                for _nn, _category in enumerate(self.all_folders[_area]["categories"]):
                    area_pipe = space if last_area else pipe
                    if _nn < len(self.all_folders[_area]["categories"]) - 1:
                        print(area_pipe, space, branch, _category)  # noqa: T201
                        last_cat = False
                    else:
                        print(area_pipe, space, elbow, _category)  # noqa: T201
                        last_cat = True

                    for _nnn, _subcategory in enumerate(
                        self.all_folders[_area]["categories"][_category]["subcategories"]
                    ):
                        cat_pipe = space if last_cat else pipe
                        if (
                            _nnn
                            < len(self.all_folders[_area]["categories"][_category]["subcategories"])
                            - 1
                        ):
                            print(area_pipe, space, cat_pipe, space, branch, _subcategory.name)  # noqa: T201
                        else:
                            print(area_pipe, space, cat_pipe, space, elbow, _subcategory.name)  # noqa: T201
