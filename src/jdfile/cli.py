"""jdfile CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from jdfile.__version__ import __version__
from jdfile._config import Config
from jdfile.models.project import Project
from jdfile.utils import alerts
from jdfile.utils.alerts import logger as log
from jdfile.utils.enums import Separator, TransformCase
from jdfile.utils.nltk import instantiate_nltk
from jdfile.utils.utilities import build_file_list

app = typer.Typer(add_completion=False, no_args_is_help=True, rich_markup_mode="rich")

typer.rich_utils.STYLE_HELPTEXT = ""


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"{__package__} version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Dry run - don't actually change anything",
    ),
    clean: bool = typer.Option(
        True,
        "--clean/--no-clean",
        help="Clean filenames",
        rich_help_panel="Filename Cleaning Options",
    ),
    case: TransformCase = typer.Option(
        None,
        case_sensitive=False,
        help="Case transformation. [dim](default: ignore)[/dim]",
        rich_help_panel="Filename Cleaning Options",
        show_default=False,
    ),
    config_file: Path = typer.Option(
        Path(Path.home() / f".{__package__}/{__package__}.toml"),
        help="Specify a custom path to configuration file.",
        show_default=False,
        dir_okay=False,
        file_okay=True,
    ),
    confirm_changes: bool = typer.Option(
        False,
        "--confirm/--no-confirm",
        help="Confirm changes before committing",
        show_default=True,
    ),
    date_format: str = typer.Option(
        None,
        "--date-format",
        help="Specify a date format. If specified, the date will be appended to the filename.",
        rich_help_panel="Filename Cleaning Options",
        show_default=True,
    ),
    depth: int = typer.Option(
        1,
        "--depth",
        help="How many levels deep to search for files to process",
        rich_help_panel="Filename Cleaning Options",
        show_default=True,
    ),
    files: list[Path] = typer.Argument(
        ...,
        help="Files or directories to process",
        dir_okay=True,
        file_okay=True,
        exists=True,
        resolve_path=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force changes without prompting for confirmation. Use with caution!",
        show_default=True,
    ),
    log_file: Path = typer.Option(
        Path(Path.home() / "logs" / f"{__package__}.log"),
        help="Path to log file",
        show_default=True,
        dir_okay=False,
        file_okay=True,
        exists=False,
    ),
    log_to_file: bool = typer.Option(
        False,
        "--log-to-file",
        help="Log to file",
        show_default=True,
    ),
    organize: bool = typer.Option(
        True,
        "--organize/--no-organize",
        help="Move files into matched folders within a specified project",
        rich_help_panel="File Organization Options",
        show_default=True,
    ),
    overwrite_existing: bool = typer.Option(
        None,
        "--overwrite/--no-overwrite",
        help="Overwrite existing files",
        rich_help_panel="Filename Cleaning Options",
        show_default=True,
    ),
    print_tree: bool = typer.Option(
        False,
        "--tree",
        help="Print a tree representation of the directories within a project and exit",
        show_default=True,
        rich_help_panel="File Organization Options",
    ),
    project_name: str = typer.Option(
        None,
        "--project",
        "-p",
        help="Specify a project from the configuration file.",
        rich_help_panel="File Organization Options",
    ),
    separator: Separator = typer.Option(
        None,
        "--separator",
        case_sensitive=False,
        help="Word separator",
        rich_help_panel="Filename Cleaning Options",
        show_default=False,
    ),
    split_words: bool = typer.Option(
        None,
        "--split-words/--no-split",
        help="Split words on capital letters",
        rich_help_panel="Filename Cleaning Options",
        show_default=True,
    ),
    strip_stopwords: bool = typer.Option(
        None,
        "--stopwords/--keep-stopwords",
        help="Strip stopwords when cleaning filenames.",
        rich_help_panel="Filename Cleaning Options",
        show_default=True,
    ),
    terms: list[str] = typer.Option(
        None,
        "--term",
        "-t",
        help="Term used to match files. Add multiple terms with multiple --term flags",
        rich_help_panel="File Organization Options",
    ),
    verbosity: int = typer.Option(
        1,
        "-v",
        "--verbose",
        show_default=False,
        help="""Set verbosity level (0=WARN, 1=INFO, 2=DEBUG, 3=TRACE)""",
        count=True,
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", help="Print version and exit", callback=version_callback, is_eager=True
    ),
    use_nltk: bool = typer.Option(
        False,
        "--syns/--no-syns",
        help="Use synonyms from NLTK to help match folders. Note, this will download the NLTK corpus if it is not already installed.",
        show_default=True,
        rich_help_panel="File Organization Options",
    ),
) -> None:
    """[bold]jdfile[/] cleans and normalizes filenames. In addition, if you have directories which follow the [Johnny Decimal](https://johnnydecimal.com), jdfile can move your files into the appropriate directory.

        [bold]jdfile[/] cleans filenames based on your preferences.

    -   Remove special characters
    -   Trim multiple separators ([reverse #999999]word____word[/] becomes [reverse #999999]word_word[/])
    -   Normalize to [reverse #999999]lower case[/], [reverse #999999]upper case[/], [reverse #999999]sentence case[/], or [reverse #999999]title case[/]
    -   Normalize all files to a common word separator ([reverse #999999]_[/], [reverse #999999]-[/], [reverse #999999] [/])
    -   Enforce lowercase file extensions
    -   Remove common English stopwords
    -   Split [reverse #999999]camelCase[/] words into separate words ([reverse #999999]camel Case[/])
    -   Parse the filename for a date in many different formats
    -   Remove or reformat the date and add it to the the beginning of the filename
    -   Avoid overwriting files by adding a unique integer when renaming/moving
    -   Clean entire directory trees
    -   Optionally, show previews of changes to be made before commiting
    -   Ignore files listed in a config file
    -   Specify casing for words which should never be changed (ie. [reverse #999999]iMac[/] will never be re-cased)

    When a project is specified, [bold]jdfile[/] will organize your files into folders.

    -   Move files into directory trees following the [link=https://johnnydecimal.com]Johnny Decimal[/] system
    -   Parse files and folder names looking for matching terms
    -   Uses [link=https://www.nltk.org]nltk[/] to lookup synonyms to improve matching
    -   Add [reverse #999999].jdfile[/] files to directories containing a list of words that will match files

    [bold underline]Example Usage:[/]

    [dim]Normalize all files in a directory to lowercase, with underscore separators[/]
    $ jdfile --case=lower --separator=underscore /path/to/directory

    # Clean all files in a directory and confirm all changes before committing them
    $ jdfile --clean /path/to/directory

    [dim]Strip common English stopwords from all files in a directory[/]
    $ jdfile --stopwords /path/to/directory

    [dim]Transform a date and add it to the filename[/]
    $ jdfile --date-format="%Y-%m-%d" ./somefile_march 3rd, 2022.txt

    [dim]Print a tree representation of a Johnny Decimal project[/]
    $ jdfile --project={project_name} --tree

    [dim]Use the settings of a project in the config file to clean filenames without[/]
    [dim]organizing them into folders[/]
    $ jdfile --project={project_name} --no-organize path/to/some_file.jpg

    [dim]Organize files into a Johnny Decimal project with specified terms with title casing[/]
    $ jdfile ---project={project_name} --term=term1 --term=term2 path/to/some_file.jpg
    """
    console = Console()
    alerts.LoggerManager(  # pragma: no cover
        log_file,
        verbosity,
        log_to_file,
    )
    context = {
        "clean": clean,
        "cli_terms": terms,
        "confirm_changes": confirm_changes,
        "date_format": date_format,
        "depth": depth,
        "dry_run": dry_run,
        "force": force,
        "organize": organize,
        "overwrite_existing": overwrite_existing,
        "print_tree": print_tree,
        "project_name": project_name,
        "separator": separator,
        "split_words": split_words,
        "strip_stopwords": strip_stopwords,
        "transform_case": case,
        "use_nltk": use_nltk,
    }
    log.trace(f"Context: {context}")

    config: Config = Config(
        config_path=config_file,
        context=context,
    )
    log.debug(f"Loaded config: {config_file}")
    log.trace(f"Config: {config}")

    project = Project(config=config)

    log.trace(f"Loaded project: {project}")
    if print_tree:
        project.tree()
        raise typer.Exit()

    if project.exists and use_nltk:
        instantiate_nltk()
    if project.exists:
        all_files = build_file_list(files, config, project)
    else:
        all_files = build_file_list(files, config)

    if files is None or len(files) == 0 or len(all_files) == 0:
        alerts.error("No files found to process")
        raise typer.Exit(1)

    log.debug(f"Working on {len(all_files)} files")

    if confirm_changes:
        table = Table(
            "#",
            "Original Name",
            "New Name",
            "New Path" if project and project.exists else "",
            "Diff",
            box=box.SIMPLE,
            show_header=True,
        )
        for _n, file in enumerate(all_files, start=1):
            table.add_row(
                str(_n),
                file.stem + "".join(file.suffixes),
                file.new_stem + "".join(file.new_suffixes)
                if file.has_changes()
                else "[green]No Changes[/green]",
                str(file.new_parent.relative_to(project.path))
                if project.exists and file.parent != file.new_parent
                else "",
                file.print_diff() if file.has_changes() else "",
            )
        console.print(table)
        if not force:
            make_chages = Confirm.ask("Commit changes?")
            if not make_chages:
                raise typer.Exit()

    for file in all_files:
        file.commit()
