"""Table views for the CLI."""

from pathlib import Path

from loguru import logger
from rich import box
from rich.table import Table

from jdfile import settings
from jdfile.models import File
from jdfile.utils import LogLevel


def confirmation_table(files: list[File], project_path: Path | None, total_files: int) -> Table:
    """Display a confirmation table to the user.

    Args:
        files (list[File]): List of files to process.
        project_path (Path): Path to project root.
        total_files (int): Total number of files to process.

    Returns:
        Table: Confirmation table.
    """
    organized_files = bool(project_path and [x for x in files if x.has_new_parent])

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold",
        min_width=40,
        title=f"Pending changes for {len(files)} of {total_files} files",
    )

    table.add_column("#")
    table.add_column("Original Name", overflow="fold")
    table.add_column("New Name", overflow="fold")
    if organized_files:
        table.add_column("New Path", overflow="fold")
    if settings.verbosity > LogLevel.INFO.value:
        table.add_column("Diff", overflow="fold")

    for _n, file in enumerate(files, start=1):
        table.add_row(
            str(_n),
            file.stem + "".join(file.path.suffixes),
            file.new_stem + "".join(file.new_suffixes)
            if file.has_changes()
            else "[green]No Changes[/green]",
            str("…/" + str(file.target.parent.relative_to(project_path)) + "/")
            if organized_files and file.has_new_parent
            else "",
            file.get_diff_string()
            if settings.verbosity > LogLevel.INFO.value and file.has_changes()
            else "",
        )

    return table


def skipped_file_table(files: list[File]) -> Table:
    """Display a table of files that could not be organized.

    Args:
        files (list[File]): List of files to process.

    Returns:
        Table: Table of skipped files.
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

    logger.warning("Files with no changes")

    for file in files:
        if len(file.path.parents) > 2:  # noqa: PLR2004
            parents = "         [dim]…/[/]" + str(
                file.path.parent.relative_to(file.path.parents[2])
            )
        else:
            parents = str(file.path.parent)

        table.add_row(f"{parents}/[bold]{file.path.name}[/]")

    return table
