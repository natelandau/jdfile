"""Helpers for the jdfile cli."""

import shutil
from pathlib import Path

import typer
from confz import validate_all_configs
from loguru import logger
from pydantic import ValidationError
from rich.prompt import Confirm

from jdfile.utils import AppConfig, console  # isort: skip
from jdfile.constants import CONFIG_PATH, SPINNER
from jdfile.models import File, Project
from jdfile.views import confirmation_table, skipped_file_table


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


def load_configuration() -> None:
    """Load the configuration."""
    if not CONFIG_PATH.exists():  # pragma: no cover
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        default_config_file = Path(__file__).parent.resolve() / "default_config.toml"
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
