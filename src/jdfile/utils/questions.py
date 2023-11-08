"""Gather user input from the command line."""

from pathlib import Path

import inflect
import questionary
import typer

from jdfile.utils import alerts

p = inflect.engine()

questionary.prompts.select.DEFAULT_STYLE = questionary.Style(  # type:ignore [attr-defined]
    [("qmark", "")]
)

STYLE = questionary.Style(
    [
        ("qmark", "bold"),
        ("question", "bold"),
        ("separator", "fg:#808080"),
        ("answer", "fg:#FF9D00 bold"),
        ("instruction", "fg:#808080"),
        ("highlighted", "bold underline"),
        ("text", ""),
        ("pointer", "bold"),
    ]
)


def select_folder(
    possible_folders: dict, project_path: Path, filename: str
) -> str:  # pragma: no cover
    """Select a folder from a list of choices.

    Args:
        filename (str): Name of the file.
        possible_folders (dict): Dictionary of possible folders.
        project_path (Path): Path to the root of the project.

    Returns:
        str: Path to the selected folder or "skip"
    """
    choices: list[dict[str, str] | questionary.Separator] = [questionary.Separator()]
    max_length = len(max(possible_folders, key=len))

    for _k, _v in possible_folders.items():
        matching_terms = ", ".join(set(_v[1]))
        folder_path = str(_v[0].path.relative_to(project_path))

        choices.append(
            {
                "name": f"{folder_path:{max_length}} [matching: {matching_terms}]",
                "value": _v[0].path,
            }
        )

    choices.extend(
        [
            questionary.Separator(),
            {"name": "Skip this file", "value": "skip"},
            {"name": "Abort", "value": "abort"},
        ]
    )

    alerts.notice(
        f"Found {len(possible_folders)} possible {p.plural_noun('folder', len(possible_folders))} for '[cyan bold]{filename}[/]'"
    )
    result = questionary.select(
        "Select a folder", choices=choices, style=STYLE, qmark="INPUT    |"
    ).ask()

    if result is None or result == "abort":
        raise typer.Abort()

    return result
