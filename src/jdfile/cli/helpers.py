"""Helpers for the jdfile cli."""

import re
import shutil
from pathlib import Path

import typer
from confz import validate_all_configs
from loguru import logger
from pydantic import ValidationError
from rich.prompt import Confirm

from jdfile.utils import AppConfig, console  # isort: skip
from jdfile.constants import ALWAYS_IGNORE_FILES, CONFIG_PATH, SPINNER
from jdfile.models import File, Project
from jdfile.views import confirmation_table, skipped_file_table


def confirm_changes_to_files(
    file_list: list[File],
    confirm_changes_flag: bool,
    force: bool,
    project: Project,
    verbosity: int,
) -> bool:
    """Confirm changes."""
    if not force and confirm_changes_flag:
        logger.info("Confirm the changes below")
        table = confirmation_table(
            files=file_list,
            project_path=project.path if project else None,
            total_files=len(file_list),
            verbosity=verbosity,
        )
        console.print(table)
        return Confirm.ask("Commit changes?")

    return True


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


def load_configuration() -> None:
    """Load the configuration."""
    if not CONFIG_PATH.exists():  # pragma: no cover
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        default_config_file = Path(__file__).parent.parent.resolve() / "default_config.toml"
        shutil.copy(default_config_file, CONFIG_PATH)
        logger.info(f"Created default configuration file: {CONFIG_PATH}")

    # Load and validate configuration
    try:
        validate_all_configs()
    except ValidationError as e:  # pragma: no cover
        logger.error(f"Invalid configuration file: {CONFIG_PATH}")
        for error in e.errors():
            console.print(f"           [red]{error['loc'][0]}: {error['msg']}[/red]")
        raise typer.Exit(code=1) from e


def show_files_without_updates(
    file_list: list[File], project: Project, organize_files_flag: bool
) -> None:
    """Process files without updates."""
    files_without_new_parent = [x for x in file_list if not x.has_new_parent]
    if project and organize_files_flag and files_without_new_parent:
        table = skipped_file_table(files_without_new_parent)
        console.print(table)


def update_files(  # noqa: PLR0917
    files_to_process: list[File],
    clean_filenames: bool | None,
    organize_files: bool | None,
    project: Project | None,
    use_nltk_library: bool | None,
    terms: list[str],
    force: bool,
    verbosity: int = 0,
) -> tuple[list[File], list[File]]:
    """Process files."""
    files_with_no_updates = []
    files_with_updates = []
    with console.status(
        "Processing Files...  [dim](Can take a while for large directory trees)[/]",
        spinner=SPINNER,
    ) as status:
        project_name = project.name if project else None
        do_clean_filename = clean_filenames or (
            clean_filenames is None and AppConfig().get_attribute(project_name, "clean_filenames")
        )

        for f in files_to_process:
            if do_clean_filename:
                new_filename = f.clean_filename()
            else:
                new_filename = f.clean_filename(date_only=True)

            logger.trace(f"{f.path.name} -> {new_filename}")

            if organize_files and project:
                new_parent = f.get_new_parent(
                    project=project,
                    use_nltk=use_nltk_library,
                    user_terms=terms,
                    force=force,
                    status=status,
                    verbosity=verbosity,
                )
                logger.trace(
                    f"📁 {Path(*Path(f.path).parts[-3:])} -> {Path(*Path(new_parent).parts[-3:])}"
                )

            if f.has_new_parent or f.has_new_stem or f.has_new_suffixes:
                files_with_updates.append(f)
            else:
                files_with_no_updates.append(f)

    return files_with_no_updates, files_with_updates
