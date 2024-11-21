"""Model for the File object."""

import difflib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar

from loguru import logger
from rich.status import Status

from jdfile import settings
from jdfile.constants import ProjectType, Separator
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

T = TypeVar("T")


class File:
    """Represents a file object with methods to clean and organize its filename according to user and application configurations."""

    def __init__(self, path: Path) -> None:
        """Initialize the File object with path, project, and user preferences.

        Sets up the file object with initial states and configurations based on the provided arguments or application defaults.

        Args:
            path (Path): The file's path.
        """
        self.path = path
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

    def __repr__(self) -> str:
        """Return a string representation of the File object."""
        return f"{self.path.name}"

    def _clean_stem(self, date_only: bool = False) -> str:
        """Generate a cleaned version of the file stem, applying various cleanup operations.

        Optionally focuses on date removal or applies a full cleanup process including splitting camelcase words, stripping stopwords, normalizing separators, and more, depending on configuration. It optionally reinserts the date and ensures dotfile names are preserved.

        Args:
            date_only (bool, optional): If True, focuses only on removing the date from the stem. Defaults to False.

        Returns:
            str: The cleaned stem of the file.
        """
        new_stem = self.stem

        # Create a date object
        if settings.format_dates and not self.is_dotfile and settings.date_format:
            date_object = (
                Date(
                    date_format=settings.date_format,
                    string=self.stem,
                    ctime=datetime.fromtimestamp(self.path.stat().st_ctime, tz=timezone.utc),
                )
                if settings.date_format
                else None
            )

            # Remove date from string
            if settings.format_dates and date_object and date_object.found_string:
                new_stem = re.sub(re.escape(date_object.found_string), "", new_stem)

        # Apply transformations if not restricted to date_only
        if not date_only:
            if settings.split_words:
                new_stem = split_camelcase_words(new_stem, settings.match_case_list)

            if settings.strip_stopwords:
                new_stem = strip_stopwords(new_stem, settings.stopwords)

            new_stem = strip_special_chars(new_stem)
            new_stem = transform_case(new_stem, settings.transform_case)
            new_stem = match_case(new_stem, settings.match_case_list)
            new_stem = normalize_separators(new_stem, settings.separator)
            new_stem = new_stem.strip(" -_.")

        # Insert date back into the string:
        if (
            settings.format_dates
            and not self.is_dotfile
            and settings.date_format
            and date_object
            and date_object.reformatted_date
        ):
            new_stem = insert(
                new_stem,
                date_object.reformatted_date,
                settings.insert_location,
                settings.separator,
            )

        # Keep dotfiles as dotfiles
        if self.is_dotfile and not new_stem.startswith("."):
            new_stem = f".{new_stem}"

        if new_stem != self.stem:
            self.has_new_stem = True

        return new_stem

    def _clean_suffixes(self) -> list[str]:
        """Clean the suffixes from the file's name, applying necessary conversions.

        Converts ".jpeg" to ".jpg" and ensures all suffixes are lowercase. Sets a flag if changes are made.

        Returns:
            list[str]: The cleaned list of suffixes for the file.
        """
        new_suffixes = [
            ".jpg" if ext.lower() == ".jpeg" else ext.lower() for ext in self.path.suffixes
        ]
        if new_suffixes != self.path.suffixes:
            self.has_new_suffixes = True

        return new_suffixes

    def clean_filename(self, date_only: bool = False) -> str:
        """Clean the filename, combining the cleaned stem and suffixes into a new filename.

        Optionally focuses on date removal from the stem or applies full filename cleaning.

        Args:
            date_only (bool, optional): If True, focuses only on removing the date from the stem. Defaults to False.

        Returns:
            str: The new name of the file after cleaning.
        """
        self.new_stem = self._clean_stem(date_only=date_only)
        self.new_suffixes = self.path.suffixes if date_only else self._clean_suffixes()

        self.new_name = f"{self.new_stem}{''.join(self.new_suffixes)}"
        return self.new_name

    @staticmethod
    def _tokenize_stem_with_synonyms(stem: str, user_terms: list[str] = []) -> list[str]:
        """Tokenize the stem of the file, optionally using NLTK for synonym expansion, and include user-defined terms.

        Splits the camelcase and other words in the stem, enriches the tokens with synonyms if NLTK is used, and includes any user-defined terms. Results in a list of unique, sorted tokens.

        Args:
            stem (str): The stem of the file.
            use_nltk (bool): Flag to indicate the use of NLTK for finding synonyms.
            user_terms (list[str]): Additional user-defined terms to include in the token list.

        Returns:
            list[str]: A sorted list of unique tokens derived from the stem.
        """
        if not user_terms:
            user_terms = []

        # Split the camelcase words and other words in the stem
        words_in_stem = split_words(split_camelcase_words(stem)) + user_terms

        # Extend with synonyms if NLTK is used
        if settings.use_synonyms:  # pragma: no cover
            synonyms = [synonym for word in words_in_stem for synonym in find_synonyms(word)]
            words_in_stem.extend(synonyms)

        # Return a sorted list of unique, lowercase tokens
        return sorted({word.lower() for word in words_in_stem})

    @property
    def target(self) -> Path:
        """Return the target path for the file after changes.

        Constructs the full target path combining new parent, stem, and suffixes.

        Returns:
            Path: The target path for the file.
        """
        return Path(self.new_parent / f"{self.new_stem}{''.join(self.new_suffixes)}")

    def commit(self, project: Project | None) -> bool:
        """Commit changes to the file by renaming or moving it to the new location.

        Logs the action taken based on verbosity level, project context, and whether it's a dry run.

        Args:
            project (Optional[Project]): The project context, if applicable.

        Returns:
            bool: True if changes were applied or simulated successfully, False if no changes were made.
        """
        if not self.has_changes():
            if settings.verbosity > 0:  # pragma: no cover
                logger.info(f"{self.path.name} -> No changes")
            return False

        if self.target.exists() and (not settings.overwrite_existing or self.target.is_dir()):
            self.unique_name()

        if project:
            try:
                display = "…/" + str(self.target.relative_to(project.path.parents[0]))
            except ValueError:  # pragma: no cover
                display = str(self.target)
        else:
            display = self.target.name

        if settings.dry_run:
            logger.log("DRYRUN", f"{self.path.name} -> {display}")
            return True

        self.path.rename(self.target)
        logger.success(f"{self.path.name} -> {display}")
        return True

    def get_new_parent(
        self,
        project: Project,
        user_terms: list[str] = [],
        force: bool = False,
        status: Status = None,
    ) -> Path:
        """Determine the new parent directory based on the file's stem and additional criteria.

        Processes the stem to identify matching folders within the project using either NLTK
        or custom logic. Optionally incorporates user-specified terms. Can force the file into
        the first matching folder or use interactive selection for multiple matches.

        Args:
            project (Project): The project object containing usable folders.
            user_terms (List[str], optional): Additional user-specified terms to consider. Defaults to None.
            force (bool): If True, forces the file into the first matching folder. Defaults to False.
            status (Status, optional): A rich status object for interactive feedback. Defaults to None.

        Returns:
            Path: The path to the new parent directory.
        """
        words_in_stem = self._tokenize_stem_with_synonyms(self.new_stem, user_terms)

        # Direct matching by number in JD project folders
        if settings.project_type == ProjectType.JD:
            for folder in project.usable_folders:
                if folder.number in words_in_stem:
                    logger.trace(
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

                logger.trace(f"ORGANIZE: '{self.path.name}' matched to '{folder_to_move_to}'")

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

                logger.trace(
                    f"ORGANIZE: '{self.path.name}' matched to {folder_to_move_to} by user selection"
                )
                status.start() if status else None

            if folder_to_move_to != self.path.parent:
                self.has_new_parent = True
                self.new_parent = folder_to_move_to

        return folder_to_move_to

    def get_diff_string(self) -> str:
        """Generate a diff string highlighting changes between the original and the new file name.

        Utilizes difflib to compare the original file name against the new name, providing a visual representation of changes with color-coded insertions (green) and deletions (red). This can be useful for reviewing changes before applying them.

        Returns:
            str: A string representing the differences between the original and new names, with insertions and deletions highlighted.
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
        """Determine if there are pending changes to the file's name or location.

        Checks flags indicating changes to the file's parent directory, stem, or suffixes to assess if any renaming or relocations are pending. This is useful for deciding whether file processing actions need to be executed.

        Returns:
            bool: True if there are changes pending; False otherwise.
        """
        return any(
            [
                self.has_new_parent,
                self.has_new_stem,
                self.has_new_suffixes,
            ]
        )

    def unique_name(self) -> None:
        """Ensure the new filename is unique within the target directory by appending a number.

        If the constructed new file name already exists in the target directory, this method appends an incrementing integer until a unique name is found. This prevents overwriting existing files and maintains file uniqueness.
        """
        sep = "_" if settings.separator == Separator.IGNORE else settings.separator.value

        i = 1
        original_new_stem = self.new_stem
        while self.target.exists():
            logger.trace(f"Unique name: '{self.target}' already exists")
            self.new_stem = f"{original_new_stem}{sep}{i}"
            i += 1
