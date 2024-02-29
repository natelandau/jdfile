"""Common utility functions for jdfile."""

import re
from pathlib import Path

import typer
from loguru import logger

from jdfile.constants import ALWAYS_IGNORE_FILES, SPINNER
from jdfile.models import Project

from .config import AppConfig
from .console import console


def get_file_list(files: list[Path], depth: int, project: Project = None) -> list[Path]:
    """Build and return a sorted list of processable files from the given paths.

    This function considers both individual files and directories in the input list. For directories,
    it recursively searches for files up to the specified depth. It filters out files based on ignore patterns,
    dotfiles, and specific ignore rules defined either in the Project object or the application's default configuration.

    Args:
        files: A list of files or directories to process.
        depth: The depth to search for files within directories.
        project: An optional project configuration that specifies files to ignore.

    Returns:
        A sorted list of Path objects representing files to be processed.
    """
    # Determine files to ignore and regex patterns based on project or default configuration
    config: Project | AppConfig = project if project else AppConfig()
    files_to_ignore = ALWAYS_IGNORE_FILES + config.ignored_files
    ignore_file_regex = config.ignore_file_regex or "^$"
    ignore_dotfiles = config.ignore_dotfiles

    def is_ignored_file(file: Path) -> bool:
        """Determine if a file should be ignored based on its name or path."""
        return (
            (ignore_dotfiles and file.name.startswith("."))
            or (file.name in files_to_ignore)
            or re.search(ignore_file_regex, file.name) is not None
        )

    # Filter out ignored files and separate files from directories
    processable_files = [f for f in files if f.is_file() and not is_ignored_file(f)]
    directories = [f for f in files if f.is_dir() and not is_ignored_file(f)]

    # Process directories
    with console.status(
        "Processing Files...  [dim](Can take a while for large directory trees)[/]",
        spinner=SPINNER,
    ):
        for _dir in directories:
            for f in _dir.rglob("*"):
                depth_of_file = len(f.relative_to(_dir).parts)
                if (
                    depth_of_file <= depth
                    and f.is_file()
                    and not is_ignored_file(f)
                    and f not in processable_files
                ):
                    processable_files.append(f)

    logger.debug(f"{len(processable_files)} files to process")
    return sorted(processable_files)


def get_project(
    project_name: str | None, exit_on_fail: bool = True, verbosity: int = 0
) -> Project | None:
    """Attempt to instantiate a Project object based on the provided project name.

    This function looks up the project name in the application's configuration. If the project name is not provided, or if the specified project does not exist in the configuration, the function either returns `None` or exits the application based on the `exit_on_fail` flag.

    Args:
        project_name: The name of the project to instantiate, or `None` if no project name is provided.
        exit_on_fail: Whether to exit the application with an error code if the project cannot be instantiated. Defaults to `True`.
        verbosity: Verbosity level for logging.

    Returns:
        An instance of `Project` if the project is found, otherwise `None`, depending on `exit_on_fail`.

    Raises:
        typer.Exit: If the project is not found and `exit_on_fail` is `True`.
    """
    if not project_name:
        msg = "No project specified"
        if exit_on_fail:
            logger.error(msg)
            raise typer.Exit(code=1)

        logger.trace(msg)
        return None

    if project_name not in AppConfig().projects:
        msg = f"Project not found: {project_name}"
        logger.error(msg)
        if exit_on_fail:
            raise typer.Exit(code=1)
        return None

    logger.debug(f"Project '{project_name}' loaded successfully.")
    return Project(project_name, verbosity=verbosity)
