"""Helpers for the jdfile cli."""

import re
from pathlib import Path

import typer
from dynaconf import ValidationError
from loguru import logger
from rich.prompt import Confirm

from jdfile import settings
from jdfile.constants import ALWAYS_IGNORE_FILES, SPINNER
from jdfile.models import File, Project
from jdfile.utils import console
from jdfile.views import confirmation_table, skipped_file_table


def confirm_changes_to_files(
    file_list: list[File],
    confirm_changes_flag: bool,
    force: bool,
    project: Project,
) -> bool:
    """Prompt for confirmation of file changes if required, and display a summary of the changes.

    This function generates and displays a table summarizing the pending changes to a list of files. It then prompts the user for confirmation before proceeding with the changes. The confirmation step can be bypassed with the force flag.

    Args:
        file_list (list[File]): The list of File objects to confirm changes for.
        confirm_changes_flag (bool): Flag indicating whether user confirmation is required.
        force (bool): If True, bypasses the confirmation prompt and proceeds with changes.
        project (Project): The current project context, used for displaying relevant paths.

    Returns:
        bool: True if the changes are confirmed by the user or if confirmation is bypassed; False otherwise.
    """
    if not force and confirm_changes_flag:
        logger.info("Confirm the changes below")
        table = confirmation_table(
            files=file_list,
            project_path=project.path if project else None,
            total_files=len(file_list),
        )
        console.print(table)
        return Confirm.ask("Commit changes?")

    return True


def get_file_list(files: list[Path]) -> list[Path]:
    """Build and return a sorted list of processable files from the given paths.

    This function considers both individual files and directories in the input list. For directories, it recursively searches for files up to the specified depth. It filters out files based on ignore patterns, dotfiles, and specific ignore rules defined either in the Project object or the application's default configuration.

    Args:
        files: A list of files or directories to process.

    Returns:
        A sorted list of Path objects representing files to be processed.
    """
    if not files:
        return []
    # Determine files to ignore and regex patterns based on project or default configuration
    files_to_ignore = ALWAYS_IGNORE_FILES + settings.ignored_files
    ignore_file_regex = settings.ignore_file_regex or "^$"

    def is_ignored_file(file: Path) -> bool:
        """Determine if a file should be ignored based on its name or path.

        Args:
            file (Path): The file to check for ignore status.

        Returns:
            bool: True if the file should be ignored, False otherwise.
        """
        return (
            (settings.ignore_dotfiles and file.name.startswith("."))
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
                    depth_of_file <= settings.depth
                    and f.is_file()
                    and not is_ignored_file(f)
                    and f not in processable_files
                ):
                    processable_files.append(f)

    logger.debug(f"{len(processable_files)} files to process")
    return sorted(processable_files)


def load_configuration(
    cli_overrides: dict = {}, settings_file: Path | None = None, project_name: str | None = None
) -> None:
    """Load and validate the configuration file. Optionally override with new configuration data from CLI args.

    Args:
        cli_overrides (dict): New configuration data to be validated.
        settings_file (Path | None): Path to settings file if not using the default.
        project_name (str | None): Name of the project to use if not using the default.

    Raises:
        typer.Exit: If the configuration file is invalid.
    """
    if settings_file:
        settings.load_file(path=settings_file)

    if project_name:
        use_project_settings(project_name)

    # Update settings for any non-None CLI options
    for option, value in cli_overrides.items():
        if value is not None:
            setattr(settings, option, value)

    # Validate settings
    try:
        settings.validators.validate_all()
    except ValidationError as e:
        accumulative_errors = e.details
        logger.error(accumulative_errors)
        raise typer.Exit(1) from e
    except KeyError as e:
        logger.error(f"{e}")
        raise typer.Exit(1) from e

    if settings.verbosity >= 2:  # pragma: no cover  # noqa: PLR2004
        logger.debug(settings.as_dict())


def show_files_without_updates(file_list: list[File], project: Project) -> None:
    """Display a table of files that do not have a new parent directory after processing.

    This function identifies files within the provided list that do not have updates to their parent directory and, if the organize files flag is enabled, displays a table of these files. It's useful for visualizing which files will remain unchanged in their current location after an organization operation.

    Args:
        file_list (list[File]): The list of File objects to check for updates.
        project (Project): The current project context.
        organize_files_flag (bool): Flag indicating whether file organization is enabled.
    """
    files_without_new_parent = [x for x in file_list if not x.has_new_parent]
    if project and settings.organize_files and files_without_new_parent:
        table = skipped_file_table(files_without_new_parent)
        console.print(table)


def update_files(
    files_to_process: list[File],
    project: Project | None,
    terms: list[str],
    force: bool,
) -> tuple[list[File], list[File]]:
    """Process files for cleaning and organizing based on the specified parameters.

    This function iterates over a list of files, applying filename cleaning and, if specified, organizing them into new directories based on their content and additional user-specified terms. Files are processed for potential renaming and reorganization, and separated into lists of those with and without updates.

    Args:
        files_to_process (list[File]): The list of File objects to be processed.
        project (Project | None): The current project context, if applicable.
        terms (list[str]): List of additional terms to consider in file organization.
        force (bool): Force file movement without confirmation for matching directories.

    Returns:
        tuple[list[File], list[File]]: A tuple containing two lists: the first with files that did not require updates, and the second with files that were updated.
    """
    files_with_no_updates = []
    files_with_updates = []
    with console.status(
        "Processing Files...  [dim](Can take a while for large directory trees)[/]",
        spinner=SPINNER,
    ) as status:
        for f in files_to_process:
            if settings.clean_filenames:
                new_filename = f.clean_filename()
            else:
                new_filename = f.clean_filename(date_only=True)

            logger.trace(f"{f.path.name} -> {new_filename}")

            if settings.organize_files and project:
                new_parent = f.get_new_parent(
                    project=project,
                    user_terms=terms,
                    force=force,
                    status=status,
                )

                logger.trace(
                    f"📁 {Path(*Path(f.path).parts[-3:])} -> {Path(*Path(new_parent).parts[-3:])}"
                )

            if f.has_new_parent or f.has_new_stem or f.has_new_suffixes:
                files_with_updates.append(f)
            else:
                files_with_no_updates.append(f)

    return files_with_no_updates, files_with_updates


def use_project_settings(project_name: str) -> None:
    """Update global settings with project-specific configuration.

    Args:
        project_name: The name of the project to use.
    """
    if project := settings.projects.get(project_name):
        logger.debug(f"Using project settings for {project_name}")
        settings.project_name = project_name
        # Update settings only for attributes that exist in the project config
        for key, value in project.items():
            setattr(settings, key, value)
