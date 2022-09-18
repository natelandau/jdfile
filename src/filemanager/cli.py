"""filemanager CLI."""

from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console

from filemanager.__version__ import __version__

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore [no-redef]

from filemanager._utils import (
    File,
    alerts,
    instantiate_nltk,
    populate_project_folders,
    populate_stopwords,
    select_option,
    show_confirmation_table,
    show_tree,
)
from filemanager._utils.alerts import logger as log

app = typer.Typer(add_completion=False, no_args_is_help=True, rich_markup_mode="rich")

typer.rich_utils.STYLE_HELPTEXT = ""


def load_configuration(paths: list[Path], required: bool = False) -> dict:
    """Load configuration data from toml file. If not found, return default config.

    Args:
        paths: List of possible config locations.
        required: If True, raise exception if config not found.

    Returns:
        dict: Configuration data.

    Raises:
        Exit: If config file is malformed or not found
    """
    config = {}
    for config_file in paths:
        if config_file.exists():
            log.debug(f"Loading configuration from {config_file}")
            with open(config_file, mode="rb") as fp:
                try:
                    config = tomllib.load(fp)
                except tomllib.TOMLDecodeError as e:
                    log.exception(f"Could not parse '{config_file}'")
                    raise typer.Exit(code=1) from e
            break

    if not config and required:
        log.error("No configuration found. Please create a config file.")
        raise typer.Exit(code=1)
    else:
        return config


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"filemanager version: {__version__}")
        raise typer.Exit()


class Case(str, Enum):
    """Define choices for case transformation."""

    lower = "lower"  # type: ignore[assignment]
    upper = "upper"  # type: ignore[assignment]
    title = "title"  # type: ignore[assignment]
    ignore = "ignore"


class Separator(str, Enum):
    """Define choices for separator transformation."""

    underscore = "underscore"
    dash = "dash"
    space = "space"
    ignore = "ignore"


@app.command()
def main(  # noqa: C901
    verbosity: int = typer.Option(
        0,
        "-v",
        "--verbose",
        show_default=False,
        help="""Set verbosity level (0=WARN, 1=INFO, 2=DEBUG, 3=TRACE)""",
        count=True,
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Dry run – don't actually change anything",
    ),
    log_to_file: bool = typer.Option(
        False,
        "--log-to-file",
        help="Log to file",
        show_default=True,
    ),
    log_file: Path = typer.Option(
        Path(Path.home() / "logs" / "halp.log"),
        help="Path to log file",
        show_default=True,
        dir_okay=False,
        file_okay=True,
        exists=False,
    ),
    config_file: Path = typer.Option(
        None,
        help="Specify a custom path to configuration file.",
        show_default=False,
        dir_okay=False,
        file_okay=True,
        exists=True,
    ),
    files: list[Path] = typer.Argument(
        None,
        help="Files or directories to process",
        dir_okay=True,
        file_okay=True,
        exists=True,
        resolve_path=True,
    ),
    clean: bool = typer.Option(
        True,
        "--clean/--no-clean",
        help="Clean the filename – remove special characters, optionally change case and word separators",
        rich_help_panel="Clean Filename Options",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force changes to files without prompting for confirmation. Use with caution!",
    ),
    overwrite: bool = typer.Option(
        False,
        help="Overwrite existing files when renaming.  If false, will create a numbered version of the file.",
        show_default=True,
        rich_help_panel="Filesystem Options",
    ),
    append_unique_integer: bool = typer.Option(
        False,
        "--append",
        help="When renaming, if the file already exists, append a unique integer after the file extension. [dim]Default places the unique integer before the file extension.[/dim]",
        rich_help_panel="Filesystem Options",
        show_default=True,
    ),
    add_date: bool = typer.Option(
        None,
        "--add-date/--remove-date",
        "-d/-r",
        help="Add or remove a formatted date to beginning of filename. [dim]Default does nothing with dates.[/dim]",
        rich_help_panel="Clean Filename Options",
        show_default=False,
    ),
    case: Case = typer.Option(
        Case.ignore,
        case_sensitive=False,
        help="Case transformation. [dim](default: ignore)[/dim]",
        rich_help_panel="Clean Filename Options",
        show_default=False,
    ),
    separator: Separator = typer.Option(
        Separator.ignore,
        "--separator",
        "--sep",
        case_sensitive=False,
        help="Word separator. [dim](default: ignore)[/dim]",
        rich_help_panel="Clean Filename Options",
        show_default=False,
    ),
    date_format: str = typer.Option(
        "%Y-%m-%d",
        "--date-format",
        help="Specify a date format.",
        rich_help_panel="Clean Filename Options",
        show_default=True,
    ),
    project_name: str = typer.Option(
        None,
        "--organize",
        "-o",
        help="JohnnyDecimal project to organize files into.",
        rich_help_panel="Filesystem Options",
    ),
    print_tree: bool = typer.Option(
        False,
        "--tree",
        help="Print a tree of the files and directories.",
        show_default=True,
        rich_help_panel="Filesystem Options",
    ),
    use_synonyms: bool = typer.Option(
        True,
        "--syns/--no-syns",
        help="Use synonyms to match words.",
        show_default=True,
        rich_help_panel="Filesystem Options",
    ),
    terms: list[str] = typer.Option(
        None,
        "--term",
        "-t",
        help="Term or JohnnyDecimal numbers used to match files. Add multiple terms with multiple --term flags.",
        rich_help_panel="Filesystem Options",
    ),
    jd_number: str = typer.Option(
        None,
        "--number",
        help="JohnnyDecimal number to override term matching when using --organize.",
        show_default=False,
        rich_help_panel="Filesystem Options",
    ),
    show_diff: bool = typer.Option(
        False,
        "--diff",
        help="Show a diff of the changes that would be made.",
        show_default=True,
        rich_help_panel="Filesystem Options",
    ),
) -> None:
    """A script which cleans and reformats filenames.

    Run in [blue]--dry-run[/blue] mode to see what changes would be made.

    Default behavior is to rename a file with the following options:

    • Remove special characters
    • Trim multiple separators ([blue]_[/blue], [blue]-[/blue], [reverse blue] [/reverse blue])
    • Replace all [blue].jpeg[/blue] extensions to [blue].jpg[/blue]
    • Lowercase extensions
    • Avoid overwriting files by adding a unique integer

    Additional options:

    • Parse the filename for a date which can be reformated as [blue]YYYY-MM-DD[/blue] and added to the beginning of the filename, or removed
    • Normalize to a common word separator ([blue]_[/blue], [blue]-[/blue], [reverse blue] [/reverse blue])
    • Normalize the filename to lowercase, uppercase, or titlecase


    """
    console = Console()
    alerts.LoggerManager(  # pragma: no cover
        log_file,
        verbosity,
        log_to_file,
    )

    if config_file:  # pragma: no cover
        possible_config_locations = [config_file]
    else:
        possible_config_locations = [
            Path.home() / ".config" / f"{__package__}.toml",
            Path.home() / f".{__package__}" / f"{__package__}.toml",
            Path.home() / f".{__package__}.toml",
        ]

    config = load_configuration(possible_config_locations, required=False)
    try:
        config["ignored_files"].append(".filemanager")
    except KeyError:
        config["ignored_files"] = [".filemanager"]

    if project_name:
        folders: list = populate_project_folders(config, project_name)
        if use_synonyms:
            instantiate_nltk()

    if print_tree and project_name:
        show_tree(folders[0].root)
        raise typer.Exit()
    elif print_tree:
        alerts.error("You must specify a project name to show the tree.")
        raise typer.Exit(1)

    if len(files) == 0:
        alerts.error("No files were specified")
        raise typer.Exit(1)

    list_of_files: list[File] = []
    for possible_file in files:
        if possible_file.is_file() and possible_file.stem not in config["ignored_files"]:
            list_of_files.append(File(possible_file, terms))
        if possible_file.is_dir():
            for f in possible_file.iterdir():
                if f.is_file() and f.stem not in config["ignored_files"]:
                    list_of_files.append(File(f, terms))

    stopwords = populate_stopwords(config, project_name)

    num_recommended_changes = 0
    for file in list_of_files:
        if clean:
            file.clean(separator, case, stopwords)
            file.match_case(config)
        if add_date is not None:
            file.add_date(add_date, date_format, separator)
        if project_name:
            file.organize(stopwords, folders, use_synonyms, jd_number, force)
        if file.has_change():
            num_recommended_changes += 1

    if force or num_recommended_changes == 0:
        for file in list_of_files:
            file.commit(dry_run, overwrite, separator, append_unique_integer)
    else:
        show_confirmation_table(list_of_files, show_diff, project_name)

        if len(list_of_files) == 1:
            choices: dict[str, str] = {
                "C": "Commit all changes",
                "Q": "Quit without making any changes",
            }
        else:
            choices = {
                "C": f"Commit all [tan]{len(list_of_files)}[/tan] changes",
                "I": f"Iterate over all [tan]{num_recommended_changes}[/tan] files with changes",
                "Q": "Quit without making any changes",
            }

        choice = select_option(choices, show_choices=True)
        if choice.upper() == "Q":
            raise typer.Abort()
        elif choice.upper() == "C":
            console.clear()
            print(f"[bold underline]{len(list_of_files)} files processed[/]\n")
            for file in list_of_files:
                file.commit(dry_run, overwrite, separator, append_unique_integer)
        elif choice.upper() == "I":

            console.clear()
            choices = {
                "C": "Commit all changes",
                "S": "Skip this file and continue",
                "Q": "Quit without making any changes",
            }

            for idx, file in enumerate(list_of_files, start=1):
                if file.has_change():
                    show_confirmation_table(
                        [file], show_diff, project_name, total_num=len(list_of_files), index=idx
                    )
                    choice = select_option(choices, show_choices=True)
                    if choice.upper() == "Q":
                        raise typer.Abort()
                    elif choice.upper() == "S":
                        file.new_parent = file.parent
                        file.new_stem = file.stem
                        file.new_path = file.path
                        file.new_stem = file.stem
                        file.new_suffixes = file.suffixes

            console.clear()
            print(f"[bold underline]{len(list_of_files)} files processed[/]\n")
            for file in list_of_files:
                file.commit(dry_run, overwrite, separator, append_unique_integer)
