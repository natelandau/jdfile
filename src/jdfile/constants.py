"""Constants for the jdfile package."""

from enum import Enum
from pathlib import Path

import typer

APP_DIR = Path(typer.get_app_dir("jdfile"))
CONFIG_PATH = APP_DIR / "config.toml"
VERSION = "1.1.5"
ALWAYS_IGNORE_FILES = (".DS_Store", ".jdfile", ".stignore")
SPINNER = "bouncingBall"


class FolderType(str, Enum):
    """Enum for folder types."""

    AREA = "area"  # Used by Johnny Decimal Folders
    CATEGORY = "category"  # Used by Johnny Decimal Folders
    SUBCATEGORY = "subcategory"  # Used by Johnny Decimal Folders
    OTHER = "other"  # Any non-JD folder


class ProjectType(str, Enum):
    """Enum for project types."""

    JD = "jd"
    FOLDER = "folder"


class Separator(str, Enum):
    """Define choices for separator transformation."""

    DASH = "-"
    IGNORE = "ignore"
    NONE = ""
    SPACE = " "
    UNDERSCORE = "_"


class TransformCase(str, Enum):
    """Define choices for case transformation."""

    CAMELCASE = "camelcase"
    IGNORE = "ignore"
    LOWER = "lower"
    SENTENCE = "sentence"
    TITLE = "title"
    UPPER = "upper"


class InsertLocation(str, Enum):
    """Define choices for inserting text."""

    AFTER = "after"
    BEFORE = "before"
