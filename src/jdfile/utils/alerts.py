"""Logging and alerts."""
import sys
from enum import Enum
from pathlib import Path
from textwrap import wrap

import rich.repr
import typer
from loguru import logger

from jdfile.utils.console import console


class LogLevel(Enum):
    """Enum for log levels."""

    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    EXCEPTION = 60


class VerboseLevel(Enum):
    """Enum for verbose levels."""

    WARN = 0
    INFO = 1
    DEBUG = 2
    TRACE = 3


def dryrun(msg: str) -> None:
    """Print a message if the dry run flag is set.

    Args:
        msg: Message to print
    """
    console.print(f"[cyan]DRYRUN   | {msg}[/cyan]")


def success(msg: str) -> None:
    """Print a success message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[green]SUCCESS  | {msg}[/green]")


def warning(msg: str) -> None:
    """Print a warning message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[yellow]WARNING  | {msg}[/yellow]")


def error(msg: str) -> None:
    """Print an error message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[red]ERROR    | {msg}[/red]")


def notice(msg: str) -> None:
    """Print a notice message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[bold]NOTICE   | {msg}[/bold]")


def info(msg: str) -> None:
    """Print a notice message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"INFO     | {msg}")


def usage(msg: str, width: int = None) -> None:
    """Print a usage message without using logging.

    Args:
        msg: Message to print
        width (optional): Width of the message
    """
    if width is None:
        width = console.width - 15

    for _n, line in enumerate(wrap(msg, width=width)):
        if _n == 0:
            console.print(f"[dim]USAGE    | {line}")
        else:
            console.print(f"[dim]         | {line}")


def debug(msg: str) -> None:
    """Print a debug message without using logging.

    Args:
        msg: Message to print
    """
    console.print(f"[blue]DEBUG    | {msg}[/blue]")


def dim(msg: str) -> None:
    """Print a message in dimmed color.

    Args:
        msg: Message to print
    """
    console.print(f"[dim]{msg}[/dim]")


def _log_formatter(record: dict) -> str:
    """Create custom log formatter based on the log level.  This effects the logs sent to stdout/stderr but not the log file."""
    if (
        record["level"].name == "INFO"
        or record["level"].name == "SUCCESS"
        or record["level"].name == "WARNING"
    ):
        return "<level><normal>{level: <8} | {message}</normal></level>\n{exception}"

    if record["level"].name == "TRACE" or record["level"].name == "DEBUG":
        return "<level><normal>{level: <8} | {message}</normal></level> <fg #c5c5c5>({name}:{function}:{line})</fg #c5c5c5>\n{exception}"

    return "<level>{level: <8} | {message}</level> <fg #c5c5c5>({name}:{function}:{line})</fg #c5c5c5>\n{exception}"


@rich.repr.auto
class LoggerManager:
    """Instantiate the loguru logging system with the following levels.

        - TRACE: Usage: log.trace("")
        - DEBUG: Usage: log.debug("")
        - INFO: Usage: log.info("")
        - WARNING: Usage: log.warning("")
        - ERROR: Usage: log.error("")
        - CRITICAL: Usage: log.critical("")
        - EXCEPTION: Usage: log.exception("")

    Attributes:
        log_file (Path): Path to the log file.
        verbosity (int): Verbosity level.
        log_to_file (bool): Whether to log to a file.
        log_level (int): Default log level (verbosity overrides this)

    Examples:
        Instantiate the logger:

            logging = _utils.alerts.LoggerManager(
                verbosity,
                log_to_file,
                log_file,
                log_level)
    """

    def __init__(
        self,
        log_file: Path = Path("/logs"),
        verbosity: int = 0,
        log_to_file: bool = False,
        log_level: int = 30,
    ) -> None:
        self.verbosity = verbosity
        self.log_to_file = log_to_file
        self.log_file = log_file
        self.log_level = log_level

        if self.log_file == Path("/logs") and self.log_to_file:  # pragma: no cover
            print("No log file specified")
            raise typer.Exit(1)

        if self.verbosity >= VerboseLevel.TRACE.value:
            logger.remove()
            logger.add(
                sys.stderr,
                level="TRACE",
                format=_log_formatter,  # type: ignore[arg-type]
                backtrace=False,
                diagnose=True,
            )
            self.log_level = 5
        elif self.verbosity == VerboseLevel.DEBUG.value:
            logger.remove()
            logger.add(
                sys.stderr,
                level="DEBUG",
                format=_log_formatter,  # type: ignore[arg-type]
                backtrace=False,
                diagnose=True,
            )
            self.log_level = 10
        elif self.verbosity == VerboseLevel.INFO.value:
            logger.remove()
            logger.add(
                sys.stderr,
                level="INFO",
                format=_log_formatter,  # type: ignore[arg-type]
                backtrace=False,
                diagnose=True,
            )
            self.log_level = 20
        else:
            logger.remove()
            logger.add(
                sys.stderr,
                format=_log_formatter,  # type: ignore[arg-type]
                level="SUCCESS",
                backtrace=False,
                diagnose=True,
            )
            self.log_level = 25

        if self.log_to_file is True:
            logger.add(
                self.log_file,
                rotation="5 MB",
                level=self.log_level,
                backtrace=False,
                diagnose=True,
                delay=True,
            )
            logger.debug(f"Logging to file: {self.log_file}")

        logger.debug("Logging instantiated")

    def is_trace(self, msg: str | None = None) -> bool:
        """Check if the current log level is TRACE.

        Args:
            msg (optional): Message to print. Defaults to None.

        Returns:
            bool: True if the current log level is TRACE or lower, False otherwise.
        """
        if self.log_level <= LogLevel.TRACE.value:
            if msg:
                console.print(msg)
            return True
        return False

    def is_debug(self, msg: str | None = None) -> bool:
        """Check if the current log level is DEBUG.

        Args:
            msg (optional): Message to print. Defaults to None.

        Returns:
            bool: True if the current log level is DEBUG or lower, False otherwise.
        """
        if self.log_level <= LogLevel.DEBUG.value:
            if msg:
                console.print(msg)
            return True
        return False

    def is_info(self, msg: str | None = None) -> bool:
        """Check if the current log level is INFO.

        Args:
            msg (optional): Message to print. Defaults to None.

        Returns:
            bool: True if the current log level is INFO or lower, False otherwise.
        """
        if self.log_level <= LogLevel.INFO.value:
            if msg:
                console.print(msg)
            return True
        return False

    def is_default(self, msg: str | None = None) -> bool:
        """Check if the current log level is default level (SUCCESS or WARNING).

        Args:
            msg (optional): Message to print. Defaults to None.

        Returns:
            bool: True if the current log level is default or lower, False otherwise.
        """
        if self.log_level <= LogLevel.WARNING.value:
            if msg:
                console.print(msg)
            return True
        return False  # pragma: no cover
