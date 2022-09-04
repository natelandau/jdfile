"""Utilities for working with strings."""
import re
from enum import Enum


def clean_extensions(extensions: list[str]) -> list:
    """Cleans file extensions."""
    new_extensions = [ext.lower() for ext in extensions]
    return [".jpg" if ext == ".jpeg" else ext for ext in new_extensions]


def change_case(string: str, case: Enum) -> str:
    """Changes the case of a string.

    Args:
        string (str): The string to change.
        case (str): The case to change to.

    Returns:
        str: The string with the specified case.

    """
    if case == "lower":
        return string.lower()
    elif case == "upper":
        return string.upper()
    elif case == "title":
        return string.title()
    else:
        return string


def clean_special_chars(string: str) -> str:
    """Cleans special characters from a string.  Periods as first characters are retained to ensure dotfiles remain dotfiles. Common word separators like hyphens, underscores, and spaces are not removed.

    Args:
        string (str): The string to clean.

    Returns:
        str: The cleaned string.

    """
    if re.match(r"^\.", string):
        dotfile = True
    else:
        dotfile = False

    clean = re.compile(r"[^\w\d\-_ ]")
    string = clean.sub(" ", string)
    string = string.strip()
    string = re.sub(" +", " ", string)

    if dotfile is True:
        return f".{string}"
    else:
        return string


def use_specified_separator(string: str, separator: Enum) -> str:
    """Replaces all separators with the specified separator.

    Args:
        string (str): The string to clean.
        separator (str): The separator to use.

    Returns:
        str: The string with the specified word separator

    """
    if separator == "underscore":
        string = re.sub(r"[-_ \.]", "_", string)
        string = re.sub(r"_+", "_", string)
        return string.strip("_")
    elif separator == "dash":
        string = re.sub(r"[-_ \.]", "-", string)
        string = re.sub(r"-+", "-", string)
        return string.strip("-")
    elif separator == "space":
        string = re.sub(r"[-_ \.]", " ", string)
        string = re.sub(r" +", " ", string)
        return string.strip(" ")
    else:
        string = re.sub(r"_+", "_", string)
        string = re.sub(r"-+", "-", string)
        string = re.sub(r" +", " ", string)
        return string.strip(" -_")
