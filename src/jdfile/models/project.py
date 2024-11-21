"""Project model."""

import functools
import re
from collections.abc import Generator
from pathlib import Path

import typer
from loguru import logger
from rich.tree import Tree

from jdfile import settings
from jdfile.constants import FolderType, ProjectType
from jdfile.utils import console, match_pattern


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
        path: Path,
        folder_type: FolderType,
        area: Path | None = None,
        category: Path | None = None,
    ) -> None:
        self.path = Path(path).expanduser().resolve()
        self.type = folder_type
        self.area = area
        self.category = category

    def __str__(self) -> str:  # pragma: no cover
        """String representation of the folder.

        Returns:
            str: String representation of the folder.
        """
        return f"FOLDER: {self.path.name} ({self.type.value}): {self.path}"

    @property
    def name(self) -> str:
        """Name of the folder."""
        if self.type == FolderType.AREA:
            return re.sub(r"^\d{2}-\d{2}[- _]", "", str(self.path.name)).strip()

        if self.type == FolderType.CATEGORY:
            return re.sub(r"^\d{2}[- _]", "", str(self.path.name)).strip()

        if self.type == FolderType.SUBCATEGORY:
            return re.sub(r"^\d{2}\.\d{2}[- _]", "", str(self.path.name)).strip()

        return self.path.name

    @property
    def number(self) -> str | None:
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
            content = Path(self.path, ".jdfile").read_text(encoding="utf-8").splitlines()
            for line in content:
                if line.startswith("#") or line in terms:
                    continue
                terms.append(line)

        return terms


class Project:
    """Represents a project directory, encapsulating its configuration, path, and folder structure."""

    def __init__(self) -> None:
        """Initializes the Project instance by loading its configuration and determining usable folders."""
        self.name = settings.project_name

        # Validate and assign the project path
        self.path = self._validate_project_path(settings.path)

        # Identify usable folders within the project
        self.usable_folders = (
            self._find_jd_folders()
            if settings.project_type == ProjectType.JD
            else self._find_non_jd_folders()
        )

    def __repr__(self) -> str:
        """String representation of the project.

        Returns:
            str: String representation of the project.
        """
        return f"PROJECT: {self.name}: {self.path} {len(self.usable_folders)} usable folders"

    def _find_non_jd_folders(self) -> list[Folder]:
        """Find and categorize all non-Johnny Decimal folders within the project up to the specified depth.

        Returns:
            List[Folder]: A sorted list of Folder objects categorized by their hierarchy.
        """

        def traverse_directory(directory: Path, depth: int) -> Generator[Folder, None, None]:
            for item in directory.iterdir():
                if item.is_dir() and item.name[0] != ".":  # Exclude hidden folders
                    yield Folder(path=item, folder_type=FolderType.OTHER)
                    if depth < settings.project_depth:
                        yield from traverse_directory(item, depth + 1)

        non_jd_folders = list(traverse_directory(self.path, 0))
        logger.trace(f"{len(non_jd_folders)} non-JD folders indexed in project: {self.name}")
        return sorted(non_jd_folders, key=lambda folder: folder.path)

    def _find_jd_folders(self) -> list[Folder]:
        """Find and categorize all relevant folders within the project according to their hierarchy.

        This method categorizes folders into areas, categories, and subcategories based on their naming convention. It also accounts for special `.jdfile` markers to include specific folders directly.

        Returns:
            List[Folder]: A sorted list of Folder objects categorized by their hierarchy.
        """

        def create_folders(
            directory: Path,
            folder_type: FolderType,
            parent_area: Path | None = None,
            parent_category: Path | None = None,
        ) -> list[Folder]:
            pattern = {
                FolderType.AREA: r"^\d{2}-\d{2}[- _]",
                FolderType.CATEGORY: r"^\d{2}[- _]",
                FolderType.SUBCATEGORY: r"^\d{2}\.\d{2}[- _]",
            }[folder_type]

            return [
                Folder(
                    path=item,
                    folder_type=folder_type,
                    area=parent_area or item,
                    category=parent_category or item,
                )
                for item in directory.iterdir()
                if item.is_dir() and match_pattern(item.name, pattern)
            ]

        areas = create_folders(self.path, FolderType.AREA)
        categories = [
            folder
            for area in areas
            for folder in create_folders(area.path, FolderType.CATEGORY, parent_area=area.path)
        ]
        subcategories = [
            folder
            for category in categories
            for folder in create_folders(
                category.path,
                FolderType.SUBCATEGORY,
                parent_area=category.area,
                parent_category=category.path,
            )
        ]

        # Filtering to avoid duplicates and include folders with .jdfile
        all_folders: list[Folder] = []
        for folder_list in (areas, categories, subcategories):
            for folder in folder_list:
                if (
                    not any(existing.path == folder.path for existing in all_folders)
                    or Path(folder.path / ".jdfile").exists()
                ):
                    logger.debug(f"PROJECT: Add '{folder.path.name}'")
                    all_folders.append(folder)

        logger.trace(f"{len(all_folders)} folders indexed in project: {self.name}")
        return sorted(all_folders, key=lambda folder: folder.path)

    @staticmethod
    def _validate_project_path(path: str) -> Path:
        """Validates the provided path for the project, ensuring it exists and is accessible.

        Args:
            path (str): The path to validate.

        Returns:
            Path: The validated path as a Path object.

        Raises:
            typer.Exit: If the path is not valid or does not exist.
        """
        path_to_validate = Path(path).expanduser().resolve()

        if not path_to_validate.exists():
            logger.error(f"Specified project path does not exist: {path}")
            raise typer.Exit(code=1)

        if not path_to_validate.is_dir():
            logger.error(f"Specified project path is not a directory: {path}")
            raise typer.Exit(code=1)

        return path_to_validate

    def _walk_directory(self, directory: Path, tree: Tree) -> None:
        """Recursively build a Tree with directory contents, excluding hidden files and sorting directories before files.

        Args:
            directory (Path): The directory to walk through.
            tree (Tree): The Tree object to which the directory structure will be added.
        """
        # Sort dirs first then by filename
        paths = sorted(
            Path(directory).iterdir(),
            key=lambda path: (path.is_file(), path.name.lower()),
        )

        for path in paths:
            if path.name.startswith(".") or not path.is_dir():
                continue

            branch = tree.add(f"{path.name}")
            self._walk_directory(path, branch)

    def tree(self) -> None:
        """Print a tree representation of the project directory to the console."""
        tree = Tree(
            f":open_file_folder: [link file://{self.path}]{self.path}",
            guide_style="dim",
        )
        self._walk_directory(Path(self.path), tree)
        console.print(tree)
