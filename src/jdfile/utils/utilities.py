"""Utilities for jdfile."""


import re
from pathlib import Path

from rich import box
from rich.table import Table

from jdfile._config.config import Config
from jdfile.models.file import File
from jdfile.models.project import Project
from jdfile.utils import alerts
from jdfile.utils.alerts import logger as log
from jdfile.utils.console import console


def build_file_list(
    files: list[Path], config: Config, project: Project = None
) -> tuple[list[File], list[File]]:
    """Build a list of files to process. If a directory is specified, all files in the directory will be processed.

    Args:
        config (Config): Configuration object.
        files (list[Path]): List of files or directories to process.
        project (Project, optional): Project object. Defaults to None.

    Returns:
            list[Path]: List of files to process.
    """
    config._ignored_files.extend([".DS_Store", ".jdfile", ".stignore"])
    if len(config.ignored_regex) > 0:
        combined_regex = "(" + ")|(".join(config.ignored_regex) + ")"
    else:
        combined_regex = "^$"  # match nothing

    directories = [f for f in files if f.is_dir() and f.exists()]
    for _dir in directories:
        files.remove(_dir)
        for f in _dir.rglob("*"):
            depth_of_file = len(f.relative_to(_dir).parts)
            if depth_of_file <= config.depth and f.is_file():
                files.append(f)

    initial_files_length = len(files)

    with console.status(
        "Processing Files...  [dim](Can take a while for large directory trees)[/]",
        spinner="bouncingBall",
    ):
        all_files = [
            File(path=f, config=config, project=project)
            for f in files
            if f.is_file()
            and f.name not in config.ignored_files
            and not re.search(combined_regex, f.name)
        ]

    for file in [x for x in all_files if len(x.organize_possible_folders) > 0]:
        file.select_new_parent()

    if config.ignore_dotfiles:
        all_files = [f for f in all_files if not f.is_dotfile]

    processed_files = [f for f in all_files if f.organize_skip is False]
    skip_organize_files = [f for f in all_files if f.organize_skip is True]

    log.info(f"Processed {len(processed_files)} of {initial_files_length} files")
    return sorted(processed_files, key=lambda x: x.name), sorted(
        skip_organize_files, key=lambda x: x.name
    )


def table_confirmation(files: list[File], project: Project, total_files: int) -> None:
    """Display a confirmation table to the user.

    Args:
        files (list[File]): List of files to process.
        project (Project): Project object.
        total_files (int): Total number of files to process.
    """
    alerts.notice("Confirm the changes below")
    if project and project.exists and len([x for x in files if x.parent != x.new_parent]) > 0:
        organized_files = True
    else:
        organized_files = False

    table = Table(
        "#",
        "Original Name",
        "New Name",
        "New Path" if organized_files else "",
        "Diff",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold",
        min_width=40,
        title=f"Pending changes for {len(files)} of {total_files} files",
    )
    for _n, file in enumerate(files, start=1):
        table.add_row(
            str(_n),
            file.stem + "".join(file.suffixes),
            file.new_stem + "".join(file.new_suffixes)
            if file.has_changes()
            else "[green]No Changes[/green]",
            str(file.new_parent.relative_to(project.path))
            if organized_files and file.parent != file.new_parent
            else "",
            file.print_diff() if file.has_changes() else "",
        )
    console.print(table)


def table_skipped_files(files: list[File]) -> None:
    """Display a table of files that could not be organized.

    Args:
        files (list[File]): List of files to process.
    """
    table = Table(
        "#",
        "Filename",
        box=None,
        show_header=False,
        title_style="yellow",
        title_justify="left",
        min_width=64,
    )
    alerts.warning("These files matched no folders and were skipped")
    for file in files:
        if len(file.path.parents) > 2:  # noqa: PLR2004
            parents = "         [dim]…/[/]" + str(
                file.path.parent.relative_to(file.path.parents[2])
            )
        else:
            parents = str(file.path.parent)

        table.add_row(f"{parents}/[bold]{file.name}[/]")

    console.print(table)
    console.print("\n")
