"""Utilities and functions for CLI output."""
import time

from rich import box, print
from rich.console import Console
from rich.live import Live
from rich.table import Table

from filemanager._utils import File, diff_strings


def show_confirmation_table(
    list_of_files: list[File],
    show_diff: bool,
    project_name: str,
    total_num: int = 0,
    index: int = 0,
) -> None:
    """Print a table with process files.  Use this table to review changes and confirm.

    Args:
        list_of_files (list[File]): List of files to be processed.
        show_diff (bool): Show diff of files.
        project_name (str): Name of project.
        total_num (int, optional): Total number of files to be processed. Defaults to 0.
        index (int, optional): Index of file in list. Defaults to 0.

    """
    console = Console()
    console.clear()

    confirmation_table = Table(
        caption="Review the changes above and confirm",
        title_style="bold",
        box=box.ROUNDED,
    )
    confirmation_table.add_column("", justify="right", style="bold")
    confirmation_table.add_column(
        f"{len(list_of_files)} files processed"
        if total_num == 0
        else f"Processing {index} of {total_num} files",
        justify="left",
    )

    with Live(confirmation_table, refresh_per_second=6):
        for file in list_of_files:
            time.sleep(0.1)

            confirmation_table.add_row("File:", f"{file.path.name}", style="bold")
            confirmation_table.add_row(
                "New Filename:",
                file.target().name if file.has_change() else "[green]NO CHANGES[/green]",
                end_section=bool(not project_name and (not show_diff or not file.has_change())),
            )
            if show_diff and file.has_change():
                confirmation_table.add_row(
                    "Diff:",
                    diff_strings(file.path.name, file.target().name),
                    end_section=bool(not project_name and show_diff),
                )

            if project_name:
                confirmation_table.add_row(
                    "Path:",
                    "[dim]No new folder found[/]"
                    if file.target().parent == file.parent
                    else str(file.relative_parent),
                    end_section=True,
                )
    print("\n")
    print(f"relative parent: {file.relative_parent}")
