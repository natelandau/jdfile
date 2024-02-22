"""Constants for the jdfile package."""

from enum import Enum


class FolderType(str, Enum):
    """Enum for folder types."""

    AREA = "area"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"


class TransformCase(str, Enum):
    """Define choices for case transformation."""

    CAMELCASE = "camelcase"
    IGNORE = "ignore"
    LOWER = "lower"
    SENTENCE = "sentence"
    TITLE = "title"
    UPPER = "upper"


class Separator(str, Enum):
    """Define choices for separator transformation."""

    DASH = "-"
    IGNORE = "ignore"
    NONE = ""
    SPACE = " "
    UNDERSCORE = "_"


class InsertLocation(str, Enum):
    """Define choices for inserting text."""

    AFTER = "after"
    BEFORE = "before"


VERSION = "1.1.5"
