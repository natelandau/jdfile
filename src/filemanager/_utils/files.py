"""Utilities for working with files."""
import re
from collections.abc import Generator
from enum import Enum
from pathlib import Path

import rich.repr
from rich import box, print
from rich.prompt import Prompt
from rich.table import Table
from typer import Abort

from filemanager._utils import Folder, alerts, create_date, dedupe_list, find_synonyms, parse_date


@rich.repr.auto
class File:
    """Class describing user-specified files to be managed.

    Args:
        path: (str) Path to the file.

    Attributes:
        path: (Path) Path to the file.
        parent: (Path) Parent directory of the file.
        stem: (str) Name of the file without the suffix.
        new_stem: (str) Original name of the file without the suffix.
        suffixes: (list[str]) List of suffixes of the file.
        new_suffixes: (list[str]) Original list of suffixes of the file.
        dotfile: (bool) Whether the file is a dotfile.
    """

    def __init__(
        self,
        path: Path,
        terms: list[str],
    ) -> None:
        """Initialize File object.

        Args:
            path: (str) Path to the file.
            terms: (list[str]) List of additional terms used for matching to folders.
        """
        self.terms = terms
        self.path: Path = path.expanduser().resolve()
        self.new_path = self.path
        self.parent: Path = self.path.parent
        self.new_parent: Path = self.parent
        self.stem: str = str(self.path)[
            : str(self.path).rfind("".join(self.path.suffixes))
        ].replace(f"{str(self.parent)}/", "")
        self.new_stem: str = self.stem
        self.suffixes: list[str] = self.path.suffixes
        self.new_suffixes: list[str] = self.suffixes

        if re.match(r"^\.", self.stem):
            self.dotfile: bool = True
        else:
            self.dotfile = False

    def __rich_repr__(self) -> Generator[tuple[str, str | Path | bool | list[str]], None, None]:
        """Rich representation of the File object."""
        yield "path", self.path
        yield "new_path", self.new_path
        yield "parent", self.parent
        yield "new_parent", self.new_parent
        yield "stem", self.stem
        yield "new_stem", self.new_stem
        yield "suffixes", self.suffixes
        yield "new_suffixes", self.new_suffixes
        yield "dotfile", self.dotfile

    def clean(self, separator: Enum, case: Enum, stopwords: list[str]) -> None:
        """Cleans the filename and updates instance variables for 'stem' and 'suffixes'.

        Args:
            separator: (Enum) Separator to use.
            case: (Enum) Case to use.
            stopwords: (list[str]) List of stopwords to remove (optional).
        """
        self.new_stem = re.sub(r"[^\w\d\-_ ]", " ", self.new_stem)

        for stopword in stopwords:
            self.new_stem = re.sub(rf"(^|[-_ ]){stopword}([-_ ]|$)", " ", self.new_stem, flags=re.I)

        if re.match(r"^.$", self.new_stem):
            self.new_stem = self.stem

        if case == "lower":
            self.new_stem = self.new_stem.lower()
        elif case == "upper":
            self.new_stem = self.new_stem.upper()
        elif case == "title":
            self.new_stem = self.new_stem.title()

        if separator == "underscore":
            self.new_stem = re.sub(r"[-_ \.]", "_", self.new_stem)
            self.new_stem = re.sub(r"_+", "_", self.new_stem)
        elif separator == "dash":
            self.new_stem = re.sub(r"[-_ \.]", "-", self.new_stem)
            self.new_stem = re.sub(r"-+", "-", self.new_stem)
        elif separator == "space":
            self.new_stem = re.sub(r"[-_ \.]", " ", self.new_stem)
            self.new_stem = re.sub(r" +", " ", self.new_stem)
        else:
            self.new_stem = re.sub(r"_+", "_", self.new_stem)
            self.new_stem = re.sub(r"-+", "-", self.new_stem)
            self.new_stem = re.sub(r" +", " ", self.new_stem)

        self.new_stem = self.new_stem.strip(" -_")

        if self.dotfile is True:
            self.new_stem = f".{self.new_stem}"
        else:
            self.new_stem = self.new_stem

        new_suffixes = [ext.lower() for ext in self.new_suffixes]
        self.new_suffixes = [".jpg" if ext == ".jpeg" else ext for ext in new_suffixes]

    def add_date(self, add_date: bool, date_format: str, separator: Enum) -> None:
        """Add and/or remove a date in a filename. Updates instance variables for 'stem'.

        Args:
            add_date: (bool) Whether to add date to the filename.
            date_format: (str) Format of the date.
            separator: (Enum) Separator to use.

        """
        date_string: str | None = None
        new_date: str | None = None
        date_string, new_date = parse_date(self.new_stem, date_format)
        if date_string is None:
            date_string = ""
            new_date = create_date(self.new_path, date_format)
        else:
            self.new_stem = self.new_stem.replace(date_string, "")
            self.new_stem = self.new_stem.strip(" -_")

        if add_date is True:
            if separator == "underscore":
                sep = "_"
                self.new_stem = re.sub(r"_+", "_", self.new_stem)
            elif separator == "dash":
                sep = "-"
                self.new_stem = re.sub(r"-+", "-", self.new_stem)
            else:
                sep = " "
                self.new_stem = re.sub(r" +", " ", self.new_stem)

            if self.dotfile is True:
                self.new_stem = self.stem.lstrip(".")
                self.new_stem = f".{new_date}{sep}{self.new_stem}"
            else:
                self.new_stem = f"{new_date}{sep}{self.new_stem}"

    def rename(
        self, dry_run: bool, overwrite: bool, separator: Enum, append_unique_integer: bool
    ) -> None:
        """Rename the file based on self.new_parent, self.new_stem, and self.new_suffixes.

        Args:
            dry_run: (bool) Whether to perform a dry run.
            overwrite: (bool) Whether to overwrite the file if it already exists.
            separator: (Enum) Separator to use.
            append_unique_integer: (bool) Whether to append a unique integer after the extensions or place it before the extension (default).

        Raises:
            Abort: If the writing the file with the new name fails.
        """
        target = Path(self.new_parent, f"{self.new_stem}{''.join(self.new_suffixes)}")
        if target == self.path:
            alerts.info(f"{self.stem}{''.join(self.suffixes)} -> No change")
        else:
            if not overwrite:
                target = create_unique_filename(target, separator, append_unique_integer)

            if dry_run:
                if self.parent == target.parent:
                    alerts.dryrun(f"{self.stem}{''.join(self.suffixes)} -> {target.name}")
                else:
                    alerts.dryrun(f"{self.stem}{''.join(self.suffixes)} -> {target}")

            else:
                try:
                    alerts.success(f"{self.stem}{''.join(self.suffixes)} -> {target.name}")
                    self.path.rename(target)
                except Exception as e:
                    alerts.error(f"{e}")
                    raise Abort() from e

    def organize(  # noqa: C901
        self, stopwords: list[str], folders: list, use_synonyms: bool, jd_number: str
    ) -> None:
        """Matches a file to a Johnny Decimal folder based on the JD number or matching words in the filename.

        Updates self.new_parent.

        Args:
            stopwords: (list[str]) List of stopwords to use.
            folders: (list[Folder]) List of Folder objects to match against.
            use_synonyms: (bool) Whether to use synonyms for matching.
            jd_number: (str) JD number to match against.

        Raises:
            Abort: If a specified number is not found

        """
        filename = self.new_stem
        for stopword in stopwords:
            filename = re.sub(rf"(^|[-_ ]){stopword}([-_ ]|$)", " ", filename, flags=re.I)

        file_words = [
            word.lower()
            for word in re.split(r"\-|,|_| |\.", filename)
            if re.match(r"^[^\d]+$", word)
        ]

        file_words.extend(self.terms)

        all_matched_terms = {}
        possible_folders = []
        jd_numbers = []
        for folder in folders:
            jd_numbers.append(folder.number)

            if use_synonyms:
                terms = [t for t in folder.terms if t not in stopwords]
                terms = sorted(dedupe_list([syn for term in terms for syn in find_synonyms(term)]))
            else:
                terms = [t for t in folder.terms if t not in stopwords]

            matched_terms = []
            for term in terms:
                if term.lower() in file_words:
                    matched_terms.append(term.lower())
                    if folder not in possible_folders:
                        possible_folders.append(folder)

            if len(matched_terms) > 0:
                all_matched_terms[folder.name] = matched_terms

        if jd_number:
            for number in jd_numbers:
                if jd_number == number:
                    self.new_parent = folders[jd_numbers.index(number)].path
                    return

            alerts.error(f"No folder found matching: [tan]{jd_number}[/tan]")
            raise Abort()
        else:
            if len(possible_folders) == 0:
                alerts.info("[tan]{self.new_stem}[/tan]: No folders found matching the filename")
            else:
                self.new_parent = print_organize_table(possible_folders, self, all_matched_terms)


def create_unique_filename(original: Path, separator: Enum, append_integer: bool = False) -> Path:
    """Create a unique filename by creating a unique integer and adding it to the filename.

    Args:
        original (Path): The original filename.
        separator (Enum): The separator to use.
        append_integer (bool, optional): If True, append an integer to the filename. If false, places unique integer before file extensions. Defaults to False.

    Returns:
        Path: The unique filename.

    """
    if separator == "underscore":
        sep = "_"
    elif separator == "dash":
        sep = "-"
    elif separator == "space":
        sep = " "
    else:
        sep = "-"

    if original.exists():
        parent: Path = original.parent
        stem: str = str(original)[: str(original).rfind("".join(original.suffixes))].replace(
            f"{str(parent)}/", ""
        )
        suffixes: list[str] = original.suffixes

        unique_integer = 1
        if append_integer:
            new_path = Path(parent / f"{stem}{''.join(suffixes)}.{unique_integer}")
        else:
            new_path = Path(parent / f"{stem}{sep}{unique_integer}{''.join(suffixes)}")

        while new_path.exists():
            unique_integer += 1
            if append_integer:
                new_path = Path(parent / f"{stem}{''.join(suffixes)}.{unique_integer}")
            else:
                new_path = Path(parent / f"{stem}{sep}{unique_integer}{''.join(suffixes)}")

        return new_path

    else:
        return original


def print_organize_table(
    possible_folders: list[Folder], file: File, all_matched_terms: dict
) -> Path:
    """Print table to select a folder from a list of possible folders.

    Args:
        possible_folders (list[Folder]): List of possible folders to match against.
        file (File): File object to match against.
        all_matched_terms (dict): Dictionary of matched terms.

    Returns:
        Path: The new parent directory.

    Raises:
        Abort: If the user chooses to abort after being presented a list of potential directories.
    """
    choices: list[str] = []
    choice_table = Table(
        title=f"Select folder for '[tan]{file.new_stem}[/tan]'",
        title_style="bold",
        show_lines=False,
        box=box.SQUARE,
    )
    choice_table.add_column("Choice", justify="center", style="bold", min_width=4)
    choice_table.add_column("Number")
    choice_table.add_column("Folder Name")
    choice_table.add_column("Project Path", justify="left", style="dim")
    choice_table.add_column("Matched Terms", justify="left", style="dim")

    length = len(possible_folders)
    for idx, folder in enumerate(possible_folders, start=1):
        choices.append(str(idx))

        if idx != length:
            choice_table.add_row(
                str(idx),
                folder.number,
                folder.name,
                folder.tree,
                ", ".join(set(all_matched_terms[folder.name])),
                style="bold",
            )
        else:
            choice_table.add_row(
                str(idx),
                folder.number,
                folder.name,
                folder.tree,
                ", ".join(set(all_matched_terms[folder.name])),
                end_section=True,
                style="bold",
            )

    choices.append("s")
    choice_table.add_row("s", "skip", style="cyan")
    choices.append("a")
    choice_table.add_row("a", "abort", style="cyan")
    print("\n")
    print(choice_table)
    choice = Prompt.ask("Folder to use:", choices=sorted(choices))
    if choice == "a":
        raise Abort
    elif choice == "s":
        return file.parent
    else:
        return possible_folders[int(choice) - 1].path
