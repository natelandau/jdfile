"""Gather user input from the command line."""

from pathlib import Path

import inflect
import questionary
import typer
from loguru import logger

from jdfile.models import Folder

p = inflect.engine()


STYLE = questionary.Style(
    [
        ("qmark", ""),
        ("question", "bold"),
        ("separator", "fg:#808080"),
        ("answer", "fg:#FF9D00"),
        ("instruction", "fg:#808080"),
        ("highlighted", "bold underline"),
        ("text", ""),
        ("pointer", "bold"),
    ]
)


def select_folder(
    possible_folders: dict[Folder, list[str]], project_path: Path, filename: str
) -> str:  # pragma: no cover
    """Select a folder from a list of choices.

    Args:
        filename (str): Name of the file.
        possible_folders (dict[Folder, list[str]]): List of possible folders.
        project_path (Path): Path to the root of the project.

    Returns:
        str: Path to the selected folder or "skip"

    Raises:
        typer.Abort: If the user chooses to abort.
    """
    choices: list[dict[str, str] | questionary.Separator] = [questionary.Separator()]
    max_length = max(len(str(obj.path.relative_to(project_path))) for obj in possible_folders)

    for folder, terms in possible_folders.items():
        matching_terms = ", ".join(set(terms))
        folder_path = str(folder.path.relative_to(project_path))

        choices.append(
            {
                "name": f"{folder_path:{max_length}} [matching: {matching_terms}]",
                "value": str(folder.path),
            }
        )

    choices.extend(
        [
            questionary.Separator(),
            {"name": "Skip this file", "value": "skip"},
            {"name": "Abort", "value": "abort"},
        ]
    )

    logger.info(
        f"Found {len(possible_folders)} possible {p.plural_noun('folder', len(possible_folders))} for '[cyan bold]{filename}[/]'"
    )
    result = questionary.select("Select a folder", choices=choices, style=STYLE).ask()

    if result is None or result == "abort":
        raise typer.Abort()

    return result
