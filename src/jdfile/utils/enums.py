"""Enums for the jdfile app."""

from enum import Enum


class FolderType(Enum):
    """Enum for folder types."""

    AREA = "area"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"


class TransformCase(Enum):
    """Define choices for case transformation."""

    CAMELCASE = "camelcase"
    IGNORE = "ignore"
    LOWER = "lower"
    SENTENCE = "sentence"
    TITLE = "title"
    UPPER = "upper"


class Separator(Enum):
    """Define choices for separator transformation."""

    DASH = "-"
    IGNORE = "ignore"
    NONE = ""
    SPACE = " "
    UNDERSCORE = "_"


class InsertLocation(Enum):
    """Define choices for inserting text."""

    AFTER = "after"
    BEFORE = "before"
