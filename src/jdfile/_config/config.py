"""Instantiate Configuration class and set default values."""

import functools
import re
import shutil
from pathlib import Path
from typing import Any

import rich.repr
import typer

from jdfile.utils import alerts
from jdfile.utils.alerts import logger as log
from jdfile.utils.enums import InsertLocation, Separator, TransformCase

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore [no-redef]

PATH_CONFIG_DEFAULT = Path(__file__).parent / "default_config.toml"


@rich.repr.auto
class Config:
    """Representation of a configuration file."""

    def __init__(
        self,
        config_path: Path | None = None,
        context: dict[str, Any] = {},
    ) -> None:
        """Initialize configuration file."""
        self.config_path = config_path.expanduser().resolve() if config_path else None
        self.context = context

        if (
            "project_name" in self.context
            and self.context["project_name"] is not None
            and config_path is not None
        ):
            if not self.config_path.exists():
                self._create_config()
            self.config_file_dict = self._load_config_file()
            self.project_config = self._find_project_config()
            self.project_path = Path(self.project_config["path"]).expanduser().resolve()
        else:
            self.project_name: str | None = None
            self.project_path = None
            self.config_file_dict = {}
            self.project_config = {}

        self._clean = (
            self.context["clean"]
            if "clean" in self.context and self.context["clean"] is not None
            else False
        )
        self._depth = (
            self.context["depth"]
            if "depth" in self.context and self.context["depth"] is not None
            else 1
        )
        self._ignored_files = self.project_config.get("ignored_files", [])
        self._ignored_regex = self.project_config.get("ignored_regex", [])
        self._organize = (
            self.context["organize"]
            if "organize" in self.context and self.context["organize"] is not None
            else True
        )

        self._cli_terms = self._get_cli_terms()
        self._date_format = self._get_date_format()
        self._strip_stopwords = self._get_strip_stopwords()
        self._ignore_dotfiles = self._get_ignore_dotfiles()
        self._overwrite_existing = self._get_overwrite_existing()
        # TODO: Add insert location to cli/config options
        self.insert_location = InsertLocation.BEFORE

    def __rich_repr__(self) -> rich.repr.Result:  # pragma: no cover  # noqa: PLW3201
        """Return the representation of the configuration file."""
        yield "config_path", self.config_path
        yield "clean", self.clean
        yield "cli_terms", self.cli_terms
        yield "date_format", self.date_format
        yield "dry_run", self.dry_run
        yield "force", self.force
        yield "ignore_dotfiles", self.ignore_dotfiles
        yield "ignored_files", self.ignored_files
        yield "ignored_regex", self.ignored_regex
        yield "insert_location", self.insert_location
        yield "match_case", self.match_case
        yield "organize", self.organize
        yield "project_name", self.project_name
        yield "project_path", self.project_path
        yield "separator", self.separator
        yield "split_words", self.split_words
        yield "strip_stopwords", self.strip_stopwords
        yield "stopwords", self.stopwords
        yield "transform_case", self.transform_case
        yield "use_nltk", self.use_nltk

    def _create_config(self) -> None:
        """Create a configuration file from the default when it does not exist.

        Returns:
            None: Exit the program after creating the configuration file.

        Raises:
            typer.Exit: Exit the program after creating the configuration file.
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(PATH_CONFIG_DEFAULT, self.config_path)
        alerts.success(f"Created default configuration file at {self.config_path}")
        alerts.notice(f"Please edit {self.config_path} before continuing")
        raise typer.Exit(code=1)

    def _get_cli_terms(self) -> list[str]:
        """Get the terms from the command line.

        Returns:
            list[str]: Terms from the command line.
        """
        if "cli_terms" in self.context and self.context["cli_terms"] is not None:
            return self.context["cli_terms"]

        return []

    def _get_date_format(self) -> str:
        """Get the date format for the project.

        Returns:
            str: Date format for the project.

        Raises:
            typer.Abort: If the date format is invalid.
        """
        if "date_format" in self.context and self.context["date_format"] is not None:
            date_format = self.context["date_format"]
        elif "date_format" in self.project_config:
            if self.project_config["date_format"].lower() == "none":
                return None
            date_format = self.project_config["date_format"]
        else:
            return None

        valid_format_codes = [
            "%a",
            "%A",
            "%w",
            "%d",
            "%b",
            "%B",
            "%m",
            "%y",
            "%Y",
            "%H",
            "%I",
            "%p",
            "%M",
            "%S",
            "%f",
            "%z",
            "%Z",
            "%j",
            "%U",
            "%W",
            "%c",
            "%x",
            "%X",
            "%%",
            "%G",
            "%u",
            "%V",
        ]
        values = re.findall(r"%\w", date_format)
        for value in values:
            if value not in valid_format_codes:
                alerts.error(f"Invalid date format: {date_format}")
                raise typer.Abort()

        return date_format

    def _get_overwrite_existing(self) -> bool:
        """Get the overwrite_existing option for the project."""
        if "overwrite_existing" in self.context and self.context["overwrite_existing"] is not None:
            return self.context["overwrite_existing"]

        if "overwrite_existing" in self.project_config:
            return self.project_config["overwrite_existing"]

        return False

    def _get_strip_stopwords(self) -> bool:
        """Strip stop words from a string.

        Returns:
            bool: Strip stopwords option for the project.
        """
        if "strip_stopwords" in self.context and isinstance(self.context["strip_stopwords"], bool):
            return self.context["strip_stopwords"]

        if "strip_stopwords" in self.project_config:
            return self.project_config["strip_stopwords"]

        return False

    def _get_ignore_dotfiles(self) -> bool:
        """Get the ignore_dotfiles option for the project.

        Returns:
            bool: ignore_dotfiles option for the project.
        """
        if "ignore_dotfiles" in self.context and self.context["ignore_dotfiles"] is not None:
            return self.context["ignore_dotfiles"]

        if "ignore_dotfiles" in self.project_config:
            return self.project_config["ignore_dotfiles"]

        return True

    def _find_project_config(self) -> dict[str, Any]:
        """Find a project configuration in the config file matching the project name.

        Returns:
            dict[str, Any]: Configuration for this run.

        Raises:
            typer.Abort: If the project does not exist in the config file.
        """
        for _project in self.config_file_dict:
            if self.context["project_name"] == _project:
                self.project_name = _project
                return self.config_file_dict[_project]

        log.error(f"Project does not exist in config file: {self.context['project_name']}")
        raise typer.Abort()

    def _load_config_file(self) -> dict[str, Any]:
        """Load the configuration file.

        Returns:
            dict[str, Any]: Configuration file as a dictionary.

        Raises:
            typer.Exit: If the configuration file is empty or malformed.
        """
        log.debug(f"Loading configuration from {self.config_path}")
        with self.config_path.open("rb") as f:
            try:
                config_file_dict = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                log.exception(f"Could not parse '{self.config_path}'")
                raise typer.Exit(code=1) from e

        if config_file_dict == {}:
            log.error(f"Configuration file '{self.config_path}' is empty or malformed")
            raise typer.Exit(code=1)

        for key, value in config_file_dict.items():
            if not isinstance(value, dict) or "path" not in config_file_dict[key]:  # noqa: PLR1733
                log.error(f"Configuration file '{self.config_path}' is malformed")
                raise typer.Exit(code=1)

        return config_file_dict

    @functools.cached_property
    def transform_case(self) -> TransformCase:
        """Get the case transformation for the project.

        Returns:
            TransformCase: Case transformation for the project.

        Raises:
            typer.Abort: If the case transformation is invalid.
        """
        if "transform_case" in self.context and self.context["transform_case"] is not None:
            transform_case = self.context["transform_case"]
        elif "transform_case" in self.project_config:
            transform_case = self.project_config["transform_case"]
        else:
            return TransformCase.IGNORE

        if isinstance(transform_case, str):
            try:
                transform_case = TransformCase[transform_case.upper()]
            except KeyError as e:
                alerts.error(f"Invalid case: {transform_case}")
                raise typer.Abort() from e

        return transform_case

    @functools.cached_property
    def separator(self) -> Separator:
        """Get the separator transformation for the project.

        Returns:
            Separator: Separator transformation for the project.

        Raises:
            typer.Abort: If the separator transformation is invalid.
        """
        if "separator" in self.context and self.context["separator"] is not None:
            separator = self.context["separator"]
        elif "separator" in self.project_config:
            separator = self.project_config["separator"]
        else:
            return Separator.IGNORE

        if isinstance(separator, str):
            try:
                separator = Separator[separator.upper()]
            except KeyError as e:
                alerts.error(f"Invalid separator: {separator}")
                raise typer.Abort() from e

        return separator

    @property
    def clean(self) -> bool:
        """Get the clean option for the project.

        Returns:
            bool: Clean option for the project.
        """
        return self._clean

    @clean.setter
    def clean(self, value: bool) -> None:
        self._clean = value

    @property
    def date_format(self) -> str:
        """Get the date format for the project.

        Returns:
            str: Date format for the project.
        """
        return self._date_format

    @date_format.setter
    def date_format(self, value: str) -> None:
        self._date_format = value

    @property
    def dry_run(self) -> bool:
        """Get the dry run option for the project.

        Returns:
            bool: Dry run option for the project.
        """
        if "dry_run" in self.context and self.context["dry_run"] is not None:
            return self.context["dry_run"]

        return False

    @property
    def force(self) -> bool:
        """Get the force option for the project.

        Returns:
            bool: Force option for the project.
        """
        if "force" in self.context and self.context["force"] is not None:
            return self.context["force"]

        return False

    @property
    def ignore_dotfiles(self) -> bool:
        """Get the ignore_dotfiles option for the project.

        Returns:
            bool: ignore_dotfiles option for the project.
        """
        return self._ignore_dotfiles

    @ignore_dotfiles.setter
    def ignore_dotfiles(self, value: bool) -> None:
        self._ignore_dotfiles = value

    @property
    def ignored_files(self) -> list[str]:
        """Get the ignored files for the project."""
        return self._ignored_files

    @ignored_files.setter
    def ignored_files(self, value: list[str]) -> None:
        self._ignored_files = value

    @property
    def ignored_regex(self) -> list[str]:
        """Get the ignored regex patterns for the project."""
        return self._ignored_regex

    @ignored_regex.setter
    def ignored_regex(self, value: list[str]) -> None:
        self._ignored_regex = value

    @property
    def split_words(self) -> bool:
        """Split words in a string.

        Returns:
            bool: Split words option for the project.
        """
        if "split_words" in self.context and isinstance(self.context["split_words"], bool):
            return self.context["split_words"]

        if "split_words" in self.project_config:
            return self.project_config["split_words"]

        return False

    @property
    def cli_terms(self) -> list[str]:
        """Get the terms from the CLI.

        Returns:
            List[str]: Terms from the CLI.
        """
        return self._cli_terms

    @cli_terms.setter
    def cli_terms(self, value: list[str]) -> None:
        self._cli_terms = value

    @property
    def depth(self) -> int:
        """Set the depth to search for files.

        Returns:
            int: Depth to search for files.
        """
        return self._depth

    @depth.setter
    def depth(self, value: int) -> None:
        self._depth = value

    @property
    def strip_stopwords(self) -> bool:
        return self._strip_stopwords

    @strip_stopwords.setter
    def strip_stopwords(self, value: bool) -> None:
        self._strip_stopwords = value

    @property
    def match_case(self) -> list[str]:
        """Get the match case for the project.

        Returns:
            List[str]: Match case for the project.
        """
        if "match_case" in self.project_config:
            return self.project_config["match_case"]

        return []

    @property
    def organize(self) -> bool:
        """Get the organize option for the project.

        Returns:
            bool: Organize option for the project.
        """
        return self._organize

    @organize.setter
    def organize(self, value: bool) -> None:
        self._organize = value

    @property
    def overwrite_existing(self) -> bool:
        """Get the overwrite existing option for the project.

        Returns:
            bool: Overwrite existing option for the project.
        """
        return self._overwrite_existing

    @overwrite_existing.setter
    def overwrite_existing(self, value: bool) -> None:
        self._overwrite_existing = value

    @property
    def stopwords(self) -> list[str]:
        """Get the stopwords for the project.

        Returns:
            List[str]: Stopwords for the project.
        """
        if "stopwords" in self.project_config:
            return self.project_config["stopwords"]

        return []

    @property
    def use_nltk(self) -> bool:
        """Get the use nltk option for the project.

        Returns:
            bool: Use nltk option for the project.
        """
        if "use_nltk" in self.context and self.context["use_nltk"] is not None:
            return self.context["use_nltk"]

        if "use_synonyms" in self.project_config:
            return self.project_config["use_synonyms"]

        return False
