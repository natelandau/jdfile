"""Model for the File object."""
import difflib
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import rich.repr

from jdfile._config import Config
from jdfile.models.dates import Date
from jdfile.models.project import Project
from jdfile.utils import alerts
from jdfile.utils.alerts import logger as log
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


@rich.repr.auto
class File:
    """Representation for a File object."""

    def __init__(
        self, path: Path | None = None, config: Config = Config(), project: Project = None
    ) -> None:
        """Initialize the File object.

        Args:
            path (Path, optional): Path to the file. Defaults to None.
            config (Config, optional): Configuration object. Defaults to Config().
            project (Project, optional): Project object. Defaults to None.
        """
        log.trace(f"Initializing File: {path}")
        self.config = config
        self.accessed = datetime.fromtimestamp(path.stat().st_atime)
        self.created = datetime.fromtimestamp(path.stat().st_ctime)
        self.modified = datetime.fromtimestamp(path.stat().st_mtime)
        self.name = path.name
        self.parent = path.parent
        self.path = path.expanduser().resolve()
        self.suffixes = self.path.suffixes
        self.stem = str(self.path)[: str(self.path).rfind("".join(self.path.suffixes))].replace(
            f"{self.parent!s}/", ""
        )
        if re.match(r"^\.", self.stem):
            self.is_dotfile: bool = True
        else:
            self.is_dotfile = False
        self.project = project
        self.organize_possible_folders: dict[str, Any] = {}
        self.organize_skip = False

        #### Create new attributes for the file ####
        if self.config.date_format:
            self.date = Date(date_format=config.date_format, string=self.stem, ctime=self.created)
        else:
            self.date = None

        if self.config.clean:
            self.new_stem = self._clean_stem()
            self.new_suffixes = self._clean_suffixes()
        else:
            self.new_stem = self.stem
            if self.date and self.date.found_string:
                self.new_stem = re.sub(re.escape(self.date.found_string), "", self.new_stem)
            if self.date and self.date.reformatted_date:
                self.new_stem = insert(
                    self.new_stem,
                    self.date.reformatted_date,
                    self.config.insert_location,
                    self.config.separator,
                )
            self.new_suffixes = self.suffixes.copy()

        self.new_parent = (
            self._get_new_parent()
            if self.project and self.project.exists and config.organize
            else self.parent
        )

    def __rich_repr__(self) -> rich.repr.RichReprResult:  # pragma: no cover
        """Rich representation of the File object.

        Returns:
            rich.repr.RichReprResult: Rich representation of the File object.
        """
        yield "accessed", self.accessed
        yield "created", self.created
        yield "is_dotfile", self.is_dotfile
        yield "modified", self.modified
        yield "name", self.name
        yield "parent", self.parent
        yield "path", self.path
        yield "skip_file", self.organize_skip
        yield "stem", self.stem
        yield "suffixes", self.suffixes
        yield "target", self.target

    def _clean_stem(self) -> str:
        """Create a cleaned stem for the file.

        Returns:
            str: Cleaned stem for the file.
        """
        new_stem = self.stem

        if self.date and self.date.found_string:
            new_stem = re.sub(re.escape(self.date.found_string), "", new_stem)

        if self.config.split_words:
            new_stem = split_camelcase_words(new_stem, self.config.match_case)

        if self.config.strip_stopwords:
            new_stem = strip_stopwords(new_stem, self.config.stopwords)

        new_stem = strip_special_chars(new_stem)
        new_stem = transform_case(new_stem, self.config.transform_case)
        new_stem = match_case(new_stem, self.config.match_case)
        new_stem = normalize_separators(new_stem, self.config.separator)
        new_stem = new_stem.strip(" -_.")

        if self.date and self.date.reformatted_date:
            new_stem = insert(
                new_stem,
                self.date.reformatted_date,
                self.config.insert_location,
                self.config.separator,
            )

        if self.is_dotfile and not re.match(r"^\.", new_stem):
            return f".{new_stem}"

        return new_stem

    def _clean_suffixes(self) -> list[str]:
        """Clean suffixes from the new filename.

        Returns:
            list[str]: Cleaned suffixes.
        """
        return [".jpg" if ext.lower() == ".jpeg" else ext.lower() for ext in self.suffixes]

    def _get_new_parent(self) -> Path:
        """Identify the new parent directory for the file.

        Returns:
            Path: New directory for the file.
        """
        words_in_stem = self.tokenize_stem()

        # If a JD number is specified, stop matching other terms
        if match_from_number := [
            i.path for i in self.project.usable_folders if i.number in words_in_stem
        ]:
            log.trace(f"'{self.name}' matched folder from number")
            return match_from_number[0]

        # Match terms to folders
        possible_folders: dict[str, Any] = {}
        for f in self.project.usable_folders:
            key = str(f.path.relative_to(self.project.path))
            for term in [_t.lower() for _t in f.terms]:
                if term.lower() in words_in_stem and key not in possible_folders:
                    possible_folders[key] = [f, [term]]
                if term.lower() in words_in_stem and key in possible_folders:
                    possible_folders[key][1].append(term)

        if len(possible_folders) == 0:
            self.organize_skip = True
            return self.parent

        if len(possible_folders) == 1 or self.config.force:
            log.trace(f"'{self.name}': 1 matching folder")
            return next(iter(possible_folders.values()))[0].path

        if len(possible_folders) > 1:
            self.organize_possible_folders = possible_folders
            return None

        # If no matches are found, skip the file
        self.organize_skip = True
        return self.parent

    @property
    def target(self) -> Path:
        """Return the target path for the file.

        Returns:
            Path: Target path for the file.
        """
        return Path(self.new_parent / f"{self.new_stem}{''.join(self.new_suffixes)}")

    def commit(self, verbosity: int = 1) -> bool:
        """Commit the changes to the file by writing the new filename to disk.

        Returns:
            bool: True if the file was successfully moved, False otherwise.
            verbosity (int, optional): Verbosity level. Defaults to 1.
        """
        if not self.has_changes() or self.organize_skip:
            if verbosity > 0:
                alerts.info(f"{self.name} -> No changes")
            return False

        if self.target.exists() and (not self.config.overwrite_existing or self.target.is_dir()):
            self.unique_name()

        if self.project and self.project.exists:
            try:
                display = ".../" + str(self.target.relative_to(self.project.path.parents[0]))
            except ValueError:  # pragma: no cover
                display = str(self.target)
        else:
            display = self.target.name

        if self.config.dry_run:
            alerts.dryrun(f"{self.name} -> {display}")
            return True

        self.path.rename(self.target)
        log.success(f"{self.name} -> {display}")
        return True

    def has_changes(self) -> bool:
        """Return whether the file has a change.

        Returns:
            True if the file has a change, False otherwise.
        """
        return self.target != self.path

    def print_diff(self) -> str:
        """Print the diff between the original and new stems.

        Returns:
            str: Diff between the original and new stems.
        """
        output = []
        a = f"{self.stem}{''.join(self.suffixes)}"
        b = f"{self.new_stem}{''.join(self.new_suffixes)}"

        matcher = difflib.SequenceMatcher(None, a, b)

        green = "[green reverse]"
        red = "[red reverse]"
        endgreen = "[/]"
        endred = "[/]"

        for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
            if opcode == "equal":
                output.append(a[a0:a1])
            elif opcode == "insert":
                output.append(f"{green}{b[b0:b1]}{endgreen}")
            elif opcode == "delete":
                output.append(f"{red}{a[a0:a1]}{endred}")
            elif opcode == "replace":
                output.append(f"{green}{b[b0:b1]}{endgreen}")
                output.append(f"{red}{a[a0:a1]}{endred}")

        return "".join(output)

    def select_new_parent(self) -> None:
        """Select the new parent directory for the file."""
        result = select_folder(
            possible_folders=self.organize_possible_folders,
            project_path=self.project.path,
            filename=self.name,
        )
        if result == "skip":
            self.organize_skip = True
            self.new_parent = self.parent
        else:
            self.organize_skip = False
            self.new_parent = Path(result)

    def tokenize_stem(self) -> list[str]:
        """Tokenize the stem of the file.

        Returns:
            list[str]: List of tokens from the stem, all lowercase.
        """
        string = self.new_stem
        string = split_camelcase_words(string)
        words_in_stem = split_words(string)
        words_in_stem.extend(self.config.cli_terms)
        synonyms = []
        if self.config.use_nltk:  # pragma: no cover
            for _w in words_in_stem:
                synonyms.extend(find_synonyms(_w))
        words_in_stem.extend(synonyms)

        return sorted({x.lower() for x in words_in_stem})

    def unique_name(self) -> None:
        """Append an integer to the end of the new filename if the target path already exists."""
        sep = self.config.separator.value if self.config.separator.name != "IGNORE" else "_"

        i = 1
        original_new_stem = f"{self.new_stem}"
        while self.target.exists():
            self.new_stem = f"{original_new_stem}{sep}{i}"
            i += 1
