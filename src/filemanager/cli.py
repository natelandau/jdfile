"""filemanager CLI."""

from enum import Enum
from pathlib import Path

import typer

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore [no-redef]

from filemanager._utils import alerts
from filemanager._utils.alerts import logger as log
from filemanager._utils.dates import date_in_filename
from filemanager._utils.strings import change_case, clean_special_chars, use_specified_separator

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
# @pysnooper.snoop(depth=2)
def main(
    verbosity: int = typer.Option(
        0,
        "-v",
        "--verbose",
        show_default=False,
        help="""Set verbosity level (0=WARN, 1=INFO, 2=DEBUG, 3=TRACE)""",
        count=True,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Dry run",
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
        ...,
        help="Files or directories to process",
        dir_okay=True,
        file_okay=True,
        exists=True,
        resolve_path=True,
    ),
    clean: bool = typer.Option(
        False,
        "--clean",
        "-c",
        help="Clean filename",
        rich_help_panel="Clean Options",
    ),
    add_date: bool = typer.Option(
        None,
        "--add-date/--remove-date",
        "-d/-r",
        help="Add a formatted date to beginning of filename.",
        rich_help_panel="Clean Options",
    ),
    case: Case = typer.Option(
        Case.ignore,
        case_sensitive=False,
        help="Case transformation. [dim](default: ignore)[/dim]",
        rich_help_panel="Clean Options",
        show_default=False,
    ),
    separator: Separator = typer.Option(
        Separator.ignore,
        "--separator",
        "-s",
        case_sensitive=False,
        help="Word separator. [dim](default: ignore)[/dim]",
        rich_help_panel="Clean Options",
        show_default=False,
    ),
    date_format: str = typer.Option(
        "%Y-%m-%d",
        "--date-format",
        "-f",
        help="Specify a date format.",
        rich_help_panel="Clean Options",
        show_default=True,
    ),
) -> None:
    """Clean and act on specified files and directories."""
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
            Path.cwd() / f"{__package__}.toml",
            Path.cwd() / f".{__package__}.toml",
        ]

    config = load_configuration(possible_config_locations, required=False)  # noqa: F841

    list_of_files: list[Path] = []
    for file in files:
        if file.is_file():
            list_of_files.append(file)
        if file.is_dir():
            for f in file.iterdir():
                if f.is_file():
                    list_of_files.append(f)

    for file in list_of_files:
        log.info(f"Processing: {file}")
        parent: Path = file.parent
        stem: str = str(file)[: str(file).rfind("".join(file.suffixes))].replace(
            f"{str(parent)}/", ""
        )
        orig_stem: str = stem

        suffixes: list[str] = file.suffixes

        stem, date = date_in_filename(stem, file, add_date, date_format, separator)

        if clean:
            stem = clean_special_chars(stem)

        stem = use_specified_separator(stem, separator)
        stem = change_case(stem, case)

        if dry_run:
            alerts.dryrun(f"{orig_stem}{''.join(suffixes)} -> {date}{stem}{''.join(suffixes)}")
