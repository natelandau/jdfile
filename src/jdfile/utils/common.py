"""Common utility functions for jdfile."""

import re


def match_pattern(string: str, pattern: str) -> bool:
    """Determine if a string matches a given pattern.

    Args:
        string: The string to match.
        pattern: The pattern to match against.

    Returns:
        `True` if the string matches the pattern, otherwise `False`.
    """
    return re.match(pattern, string) is not None
