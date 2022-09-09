"""Small utility functions."""


def dedupe_list(original: list) -> list:
    """Dedupe a list.

    Args:
        original (list): The list to dedupe.

    Returns:
        list: The de-duped list.

    """
    return list(set(original))
