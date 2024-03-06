"""Model for the File object."""

import difflib
import re
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from loguru import logger
from rich.status import Status

from jdfile.constants import InsertLocation, ProjectType, Separator, TransformCase
from jdfile.utils import AppConfig, console
from jdfile.utils.nltk import find_synonyms
from jdfile.utils.questions import select_folder
from jdfile.utils.strings import (
    insert,
    match_case,
    normalize_separators,
    split_camelcase_words,
    split_words,
    strip_special_chars,
    strip_stopwords,
    transform_case,
)

from .dates import Date
from .project import Project


class File:
    """Representation for a File object."""

    def __init__(  # noqa: PLR0917
        self,
        path: Path,
        project: Project | None,
        user_date_format: str | None,
        user_format_dates: bool | None,
        user_separator: Separator | None,
        user_split_words: bool | None,
        user_strip_stopwords: bool | None,
        user_case_transformation: TransformCase | None,
        user_overwrite_existing: bool | None,
        user_match_case_list: list[str] | None = None,
    ) -> None:
        """Initializes the File object with path, project, and user preferences, setting up initial states and configuration based on application defaults or user inputs.

        Args:
            path (Path): The file's path.
            project (Optional[Project]): The associated project, if any.
            user_date_format (Optional[str]): User-specified date format.
            user_format_dates (Optional[bool]): Flag to enable date formatting.
            user_separator (Optional[Separator]): User-specified separator.
            user_split_words (Optional[bool]): Flag to enable word splitting.
            user_strip_stopwords (Optional[bool]): Flag to enable stopword stripping.
            user_case_transformation (Optional[TransformCase]): User-specified case transformation.
            user_overwrite_existing (Optional[bool]): Flag to enable overwriting existing files.
            user_match_case_list (Optional[list[str]]): User-specified list of words to match case.
        """
        self.path = path
        self.project_name = project.name if project else None
        self.stem = str(self.path)[: str(self.path).rfind("".join(self.path.suffixes))].replace(
            f"{self.path.parent}/", ""
        )
        self.is_dotfile = self.stem.startswith(".")

        # Initialize processing flags
        self.has_new_parent = False
        self.has_new_stem = False
        self.has_new_suffixes = False

        # Initialize new file attributes
        self.new_name = self.path.name
        self.new_parent = self.path.parent
        self.new_stem = self.stem
        self.new_suffixes = self.path.suffixes

        # Configuration attributes, favoring CLI options over configuration file defaults

        def get_config_or_default(
            user_value: bool | str | list[str] | None, config_key: str
        ) -> Any:
            """Helper function to simplify value assignment."""
            return (
                user_value
                if user_value is not None
                else AppConfig().get_attribute(self.project_name, config_key)
            )

        self.date_format: str = get_config_or_default(user_date_format, "date_format")
        self.format_dates: bool = get_config_or_default(user_format_dates, "format_dates")
        self.overwrite_existing: bool = get_config_or_default(
            user_overwrite_existing, "overwrite_existing"
        )
        self.separator: Separator = get_config_or_default(user_separator, "separator")
        self.do_split_words: bool = get_config_or_default(user_split_words, "split_words")
        self.strip_stopwords: bool = get_config_or_default(user_strip_stopwords, "strip_stopwords")
        self.case_transformation: TransformCase = get_config_or_default(
            user_case_transformation, "transform_case"
        )
        self.match_case_list: tuple[str, ...] = get_config_or_default(
            user_match_case_list, "match_case_list"
        )

    def __repr__(self) -> str:
        """Return a string representation of the File object."""
        return f"{self.path.name}"

    def _clean_stem(self, date_only: bool = False) -> str:
        """Generate a cleaned version of the file stem, optionally focusing on date removal or applying a full cleanup process.

        Conditionally remove the date from the stem, apply various cleanup operations like splitting camel case words, stripping stopwords, normalizing separators, and more, depending on the configuration. It optionally reinserts the date and ensures dotfile names are preserved.

        Args:
            date_only (bool, optional): If True, only remove the date from the stem. Defaults to False.

        Returns:
            str: The cleaned stem of the file.
        """
        new_stem = self.stem

        # Create a date object
        if self.format_dates and not self.is_dotfile and self.date_format:
            date_object = (
                Date(
                    date_format=self.date_format,
                    string=self.stem,
                    ctime=datetime.fromtimestamp(self.path.stat().st_ctime),
                )
                if self.date_format
                else None
            )

            # Remove date from string
            if self.format_dates and date_object and date_object.found_string:
                new_stem = re.sub(re.escape(date_object.found_string), "", new_stem)

        # Apply transformations if not restricted to date_only
        if not date_only:
            if self.do_split_words:
                new_stem = split_camelcase_words(new_stem, self.match_case_list)

            if self.strip_stopwords:
                new_stem = strip_stopwords(
                    new_stem,
                    cast(
                        tuple[str, ...], AppConfig().get_attribute(self.project_name, "stopwords")
                    ),
                )

            new_stem = strip_special_chars(new_stem)
            new_stem = transform_case(new_stem, self.case_transformation)
            new_stem = match_case(new_stem, self.match_case_list)
            new_stem = normalize_separators(new_stem, self.separator)
            new_stem = new_stem.strip(" -_.")

        # Insert date back into the string:
        if (
            self.format_dates
            and not self.is_dotfile
            and self.date_format
            and date_object
            and date_object.reformatted_date
        ):
            new_stem = insert(
                new_stem,
                date_object.reformatted_date,
                cast(
                    InsertLocation, AppConfig().get_attribute(self.project_name, "insert_location")
                ),
                self.separator,
            )

        # Keep dotfiles as dotfiles
        if self.is_dotfile and not new_stem.startswith("."):
            new_stem = f".{new_stem}"

        if new_stem != self.stem:
            self.has_new_stem = True

        return new_stem

    def _clean_suffixes(self) -> list[str]:
        """Clean suffixes from the new filename.

        Returns:
            list[str]: Cleaned suffixes.
        """
        new_suffixes = [
            ".jpg" if ext.lower() == ".jpeg" else ext.lower() for ext in self.path.suffixes
        ]
        if new_suffixes != self.path.suffixes:
            self.has_new_suffixes = True

        return new_suffixes

    def clean_filename(self, date_only: bool = False) -> str:
        """Clean the filename and suffixes."""
        self.new_stem = self._clean_stem(date_only=date_only)
        self.new_suffixes = self.path.suffixes if date_only else self._clean_suffixes()

        self.new_name = f"{self.new_stem}{''.join(self.new_suffixes)}"
        return self.new_name

    @staticmethod
    def _tokenize_stem_with_synonyms(
        stem: str, use_nltk: bool, user_terms: list[str] = []
    ) -> list[str]:
        """Tokenize and stem the given file stem, optionally using NLTK for synonym expansion, and include user-defined terms.

        This method splits the camelcase and other words in the stem, optionally enriches the token list with synonyms using NLTK,
        and incorporates any user-defined terms. The resulting list of tokens is made unique, converted to lowercase, and sorted.

        Args:
            stem (str): The stem of the file to process.
            use_nltk (bool): Flag to indicate the use of NLTK for finding synonyms.
            user_terms (list[str]): Additional user-defined terms to include in the token list.

        Returns:
            list[str]: A sorted list of unique tokens derived from the stem, all in lowercase.
        """
        # Split the camelcase words and other words in the stem
        words_in_stem = split_words(split_camelcase_words(stem)) + user_terms

        # Extend with synonyms if NLTK is used
        if use_nltk:  # pragma: no cover
            synonyms = [synonym for word in words_in_stem for synonym in find_synonyms(word)]
            words_in_stem.extend(synonyms)

        # Return a sorted list of unique, lowercase tokens
        return sorted({word.lower() for word in words_in_stem})

    @property
    def target(self) -> Path:
        """Return the target path for the file.

        Returns:
            Path: Target path for the file.
        """
        return Path(self.new_parent / f"{self.new_stem}{''.join(self.new_suffixes)}")

    def commit(self, verbosity: int, project: Project | None, dry_run: bool) -> bool:
        """Commit changes to the file by writing the new filename to disk.

        Args:
            verbosity (int): Verbosity level, with a higher number indicating more detailed output.
            project (Optional[Project]): Project object, if applicable. Defaults to None.
            dry_run (bool): If True, perform a dry run without making actual changes. Defaults to False.

        Returns:
            bool: True if the file was successfully moved or if a dry run is performed, False otherwise.
        """
        if not self.has_changes():
            if verbosity > 0:  # pragma: no cover
                logger.info(f"{self.path.name} -> No changes")
            return False

        if self.target.exists() and (not self.overwrite_existing or self.target.is_dir()):
            self.unique_name()

        if project:
            try:
                display = "…/" + str(self.target.relative_to(project.path.parents[0]))
            except ValueError:  # pragma: no cover
                display = str(self.target)
        else:
            display = self.target.name

        if dry_run:
            logger.log("DRYRUN", f"{self.path.name} -> {display}")
            return True

        self.path.rename(self.target)
        logger.success(f"{self.path.name} -> {display}")
        return True

    def get_new_parent(  # noqa: C901
        self,
        project: Project,
        use_nltk: bool,
        user_terms: list[str] = [],
        force: bool = False,
        status: Status = None,
        verbosity: int = 0,
    ) -> Path:
        """Determine the new parent directory based on the file's stem and additional criteria.

        Processes the stem to identify matching folders within the project using either NLTK
        or custom logic. Optionally incorporates user-specified terms. Can force the file into
        the first matching folder or use interactive selection for multiple matches.

        Args:
            project (Project): The project object containing usable folders.
            use_nltk (bool): Flag to use NLTK for tokenizing the stem.
            user_terms (List[str], optional): Additional user-specified terms to consider. Defaults to None.
            force (bool): If True, forces the file into the first matching folder. Defaults to False.
            status (Status, optional): A rich status object for interactive feedback. Defaults to None.
            verbosity (int, optional): Verbosity level for logging. Defaults to 0.

        Returns:
            Path: The path to the new parent directory.
        """
        words_in_stem = self._tokenize_stem_with_synonyms(self.new_stem, use_nltk, user_terms)

        # Direct matching by number in JD project folders
        if project.project_type == ProjectType.JD:
            for folder in project.usable_folders:
                if folder.number in words_in_stem:
                    if verbosity > 1:  # pragma: no cover
                        console.log(
                            f"ORGANIZE: '{self.path.name}' matched by jd number: {folder.path}"
                        )
                    self.has_new_parent = True
                    self.new_parent = folder.path
                    return folder.path

        # Collect folders matching any user terms or stem tokens
        matching_folders = {
            folder: [
                term
                for term in folder.terms
                if term.lower() in [word.lower() for word in words_in_stem]
            ]
            for folder in project.usable_folders
            if any(
                term.lower() in [word.lower() for word in words_in_stem] for term in folder.terms
            )
        }

        # Determine the folder to move file to based on matching criteria
        folder_to_move_to = self.path.parent  # Default to current parent if no matches found

        if matching_folders:
            if len(matching_folders) == 1 or force:
                folder_to_move_to = next(iter(matching_folders.keys())).path
                if verbosity > 1:  # pragma: no cover
                    console.log(f"ORGANIZE: '{self.path.name}' matched to '{folder_to_move_to}'")

            elif len(matching_folders) > 1:
                status.stop() if status else None
                selected_folder = select_folder(
                    possible_folders=matching_folders,
                    project_path=project.path,
                    filename=self.path.name,
                )
                folder_to_move_to = (
                    self.path.parent if selected_folder == "skip" else Path(selected_folder)
                )
                if verbosity > 1:  # pragma: no cover
                    console.log(
                        f"ORGANIZE:'{self.path.name}' matched to {folder_to_move_to} by user selection"
                    )
                status.start() if status else None

            if folder_to_move_to != self.path.parent:
                self.has_new_parent = True
                self.new_parent = folder_to_move_to

        return folder_to_move_to

    def get_diff_string(self) -> str:
        """Generate a diff string highlighting the changes from the original to the new stem.

        The method utilizes color codes to indicate insertions and deletions between
        the original and new strings. Equal segments are not color-coded. Insertions
        are highlighted in green, and deletions in red.

        Returns:
            A single string with color-coded differences.
        """
        original = f"{self.stem}{''.join(self.path.suffixes)}"
        new = f"{self.new_stem}{''.join(self.new_suffixes)}"
        matcher = difflib.SequenceMatcher(None, original, new)

        # Color codes for highlighting differences in the output
        green, red, end_color = "[green reverse]", "[red reverse]", "[/]"
        diff_output = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                diff_output.append(original[i1:i2])
            elif tag == "insert":
                diff_output.append(f"{green}{new[j1:j2]}{end_color}")
            elif tag == "delete":
                diff_output.append(f"{red}{original[i1:i2]}{end_color}")
            elif tag == "replace":
                diff_output.extend(
                    [f"{red}{original[i1:i2]}{end_color}", f"{green}{new[j1:j2]}{end_color}"]
                )

        return "".join(diff_output)

    def has_changes(self) -> bool:
        """Determine if the file's target state differs from its current state.

        Evaluates whether any aspect of the file's target location (parent directory, stem, or suffixes)
        differs from its current location, indicating pending changes.

        Returns:
            bool: True if there are pending changes to the file's location or name; False otherwise.
        """
        return any(
            [
                self.has_new_parent,
                self.has_new_stem,
                self.has_new_suffixes,
            ]
        )

    def unique_name(self) -> None:
        """Append an integer to the filename to ensure uniqueness if the target path exists.

        This method modifies `self.new_stem` by appending an incrementing integer, separated
        by the defined separator (or an underscore if the separator is set to IGNORE), until
        the constructed filename does not match an existing file path.
        """
        sep = "_" if self.separator == Separator.IGNORE else self.separator.value

        i = 1
        original_new_stem = self.new_stem
        while self.target.exists():
            logger.trace(f"Unique name: '{self.target}' already exists")
            self.new_stem = f"{original_new_stem}{sep}{i}"
            i += 1
