"""jdfile CLI."""

from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger

from jdfile.cli import (
    confirm_changes_to_files,
    get_file_list,
    get_project,
    load_configuration,
    show_files_without_updates,
    update_files,
)
from jdfile.constants import APP_DIR, VERSION, Separator, TransformCase
from jdfile.utils import (
    AppConfig,
    LogLevel,
    console,
    instantiate_logger,
)
from jdfile.utils.nltk import instantiate_nltk

from jdfile.models import File  # isort: skip

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)
typer.rich_utils.STYLE_HELPTEXT = ""


SeparatorOption = Enum("SeparatorOption", {x.name: x.name for x in Separator}, type=str)  # type: ignore [misc]
TransformCaseOption = Enum("TransformCaseOption", {x.name: x.name for x in TransformCase}, type=str)  # type: ignore [misc]


def separator_callback(value: SeparatorOption) -> Separator:
    """Convert a SeparatorOption to a Separator.

    Args:
        value (SeparatorOption): The SeparatorOption.

    Returns:
        Separator: The Separator.
    """
    return Separator[value.name] if value else None


def transform_case_callback(value: TransformCaseOption) -> TransformCase:
    """Convert a TransformCaseOption to a TransformCase.

    Args:
        value (TransformCaseOption): The TransformCaseOption.

    Returns:
        TransformCase: The TransformCase.
    """
    return TransformCase[value.name] if value else None


def version_callback(value: bool) -> None:
    """Print version and exit.

    Args:
        value (bool): The value.

    Raises:
        typer.Exit: If the user chooses to exit.
    """
    if value:
        console.print(f"{__package__} version: {VERSION}")
        raise typer.Exit()


@app.command()
def main(
    clean_filenames: Annotated[
        Optional[bool],
        typer.Option(
            "--clean/--no-clean",
            help="Clean filenames",
            rich_help_panel="Filename Cleaning Options",
        ),
    ] = None,
    transform_case: Annotated[
        Optional[TransformCaseOption],
        typer.Option(
            "--case",
            help="Case transformation. [dim](default: ignore)[/dim]",
            rich_help_panel="Filename Cleaning Options",
            show_default=False,
        ),
    ] = None,
    confirm_changes: Annotated[
        bool,
        typer.Option(
            "--confirm/--no-confirm",
            help="Confirm changes before committing",
            show_default=True,
            rich_help_panel="Output Options",
        ),
    ] = False,
    date_format: Annotated[
        Optional[str],
        typer.Option(
            "--date-format",
            help="Specify a date format. If specified, the date will be appended to the filename.",
            rich_help_panel="Filename Cleaning Options",
            show_default=True,
        ),
    ] = None,
    depth: Annotated[
        int,
        typer.Option(
            "--depth",
            help="When processing directories, specify the depth to process",
            show_default=True,
            rich_help_panel="Filename Cleaning Options",
        ),
    ] = 1,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Dry run - don't actually change anything",
            show_default=True,
            rich_help_panel="Output Options",
        ),
    ] = False,
    files: Annotated[
        Optional[list[Path]],
        typer.Argument(
            ...,
            help="Files or directories to process",
            dir_okay=True,
            file_okay=True,
            exists=True,
            resolve_path=True,
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Force changes without prompting for confirmation. Use with caution!",
            show_default=True,
        ),
    ] = False,
    format_dates: Annotated[
        Optional[bool],
        typer.Option(
            "--format-dates/--no-format-dates",
            help="Format dates in filenames",
            rich_help_panel="Filename Cleaning Options",
            show_default=True,
        ),
    ] = None,
    log_file: Annotated[
        Path,
        typer.Option(
            help="Path to log file",
            show_default=True,
            dir_okay=False,
            file_okay=True,
            exists=False,
        ),
    ] = Path(f"{APP_DIR}/jdfile.log"),
    log_to_file: Annotated[
        bool,
        typer.Option(
            "--log-to-file",
            help="Log to file",
            show_default=True,
        ),
    ] = False,
    organize_files: Annotated[
        bool,
        typer.Option(
            "--organize/--no-organize",
            help="Move files into matched folders within a specified project",
            rich_help_panel="File Organization Options",
            show_default=True,
        ),
    ] = True,
    overwrite_existing: Annotated[
        Optional[bool],
        typer.Option(
            "--overwrite/--no-overwrite",
            help="Overwrite existing files",
            rich_help_panel="Filename Cleaning Options",
            show_default=True,
        ),
    ] = None,
    project_name: Annotated[
        Optional[str],
        typer.Option(
            "--project",
            "-p",
            help="Specify a project from the configuration file.",
            show_default=False,
            rich_help_panel="File Organization Options",
        ),
    ] = None,
    separator: Annotated[
        Optional[SeparatorOption],
        typer.Option(
            "--separator",
            "--sep",
            case_sensitive=False,
            help="Word separator",
            rich_help_panel="Filename Cleaning Options",
            show_default=False,
        ),
    ] = None,
    use_synonyms: Annotated[
        Optional[bool],
        typer.Option(
            "--syns/--no-syns",
            help="Use synonyms from NLTK to help match folders. Note, this will download the NLTK corpus if it is not already installed.",
            show_default=False,
            rich_help_panel="File Organization Options",
        ),
    ] = None,
    split_words: Annotated[
        Optional[bool],
        typer.Option(
            "--split-words/--no-split",
            help="Split words on capital letters",
            rich_help_panel="Filename Cleaning Options",
            show_default=False,
        ),
    ] = None,
    strip_stopwords: Annotated[
        Optional[bool],
        typer.Option(
            "--strip-stopwords/--keep-stopwords",
            help="Strip stopwords when cleaning filenames.",
            rich_help_panel="Filename Cleaning Options",
            show_default=False,
        ),
    ] = None,
    terms: Annotated[
        Optional[list[str]],
        typer.Option(
            "--term",
            "-t",
            help="Term used to match files to folders. Add multiple terms with additional --term flags",
            rich_help_panel="File Organization Options",
        ),
    ] = None,
    tree_view: Annotated[
        bool,
        typer.Option(
            "--tree",
            help="Print a tree representation of the directories within a project and exit",
            show_default=True,
            rich_help_panel="Output Options",
        ),
    ] = False,
    verbosity: Annotated[
        int,
        typer.Option(
            "-v",
            "--verbose",
            show_default=True,
            help="""Set verbosity level(0=INFO, 1=DEBUG, 2=TRACE)""",
            count=True,
        ),
    ] = 0,
    version: Annotated[  # noqa: ARG001
        Optional[bool],
        typer.Option(
            "--version",
            is_eager=True,
            callback=version_callback,
            help="Print version and exit",
        ),
    ] = None,
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
    -   Optionally, show previews of changes to be made before committing
    -   Ignore files listed in a config file by filename or by regex
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
    instantiate_logger(verbosity, log_file, log_to_file)

    new_config_data: dict = {}
    new_config_data.update(
        {
            k: v
            for k, v in {
                "clean_filenames": clean_filenames,
                "date_format": date_format,
                "format_dates": format_dates,
                "overwrite_existing": overwrite_existing,
                "separator": separator,
                "split_words": split_words,
                "strip_stopwords": strip_stopwords,
                "transform_case": transform_case,
                "use_synonyms": use_synonyms,
            }.items()
            if v is not None
        }
    )

    load_configuration(new_config_data=new_config_data)

    if verbosity > 1:  # pragma: no cover
        console.log(AppConfig(), highlight=True)

    if tree_view:
        project = get_project(project_name, exit_on_fail=True, verbosity=verbosity)
        project.tree()
        raise typer.Exit()  # noqa: DOC501

    if not files:
        logger.error("No files to process")
        raise typer.Exit(1)

    if not project_name:
        project = None
    else:
        project = get_project(project_name, exit_on_fail=True, verbosity=verbosity)

    files_to_process = [
        File(path=f, project=project)
        for f in get_file_list(files=files, depth=depth, project=project)
    ]

    if not files_to_process:
        logger.error("No files to process")
        raise typer.Exit(1)

    use_nltk_library = (
        use_synonyms or AppConfig().get_attribute(project_name, "use_synonyms", bool) or False
    )
    if project and use_nltk_library:  # pragma: no cover
        instantiate_nltk()

    files_with_no_updates, files_with_updates = update_files(
        files_to_process=files_to_process,
        clean_filenames=clean_filenames,
        organize_files=organize_files,
        project=project,
        use_nltk_library=use_nltk_library,
        terms=terms,
        force=force,
        verbosity=verbosity,
    )

    show_files_without_updates(
        files_with_no_updates,
        project,
        organize_files,
    )

    if not files_with_updates:
        logger.info(f"No changes out of {len(files_to_process)} files")
        raise typer.Exit()

    files_to_confirm = (
        files_with_updates
        if verbosity < LogLevel.DEBUG.value
        else files_with_updates + files_with_no_updates
    )
    if not confirm_changes_to_files(files_to_confirm, confirm_changes, force, project, verbosity):
        raise typer.Exit()

    logger.info(
        f"Committing {len(files_with_updates)} with changes of {len(files_to_process)} total files"
    )
    for file in files_with_updates:
        file.commit(verbosity=verbosity, project=project, dry_run=dry_run)

    raise typer.Exit()


if __name__ == "__main__":  # pragma: no cover
    app()
