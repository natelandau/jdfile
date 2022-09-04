# type: ignore
"""Test string utility functions."""
from enum import Enum

from filemanager._utils.strings import change_case, clean_special_chars, use_specified_separator


def test_clean_special_chars():
    """Test cleaning special characters."""
    assert clean_special_chars(".dotfile.file") == ".dotfile file"
    assert clean_special_chars("I have nothing to string") == "I have nothing to string"
    assert (
        clean_special_chars("I have many special: !@#$%^&*()_+-=[]{}|;':,./<>? characters")
        == "I have many special _ - characters"
    )


def test_use_specified_separator():
    """Test use_specified_separator."""

    class Separator(str, Enum):
        """Define choices for separator transformation."""

        underscore = "underscore"
        dash = "dash"
        space = "space"
        ignore = "ignore"

    assert (
        use_specified_separator("-string to-underscore", Separator.underscore)
        == "string_to_underscore"
    )
    assert use_specified_separator("-string-to__dashes---", Separator.dash) == "string-to-dashes"
    assert use_specified_separator("-string-to__spaces---", Separator.space) == "string to spaces"
    assert (
        use_specified_separator("-string-to__ ignore---", Separator.ignore) == "string-to_ ignore"
    )


def test_change_case():
    """Test changing case of a string."""

    class Case(str, Enum):
        """Define choices for case transformation."""

        lower = "lower"
        upper = "upper"
        title = "title"
        ignore = "ignore"

    assert change_case("string TO LOWERCASE", Case.lower) == "string to lowercase"
    assert change_case("string_to_uppercase", Case.upper) == "STRING_TO_UPPERCASE"
    assert change_case("string-tO-TITLEcase", Case.title) == "String-To-Titlecase"
    assert change_case("string WITH an IgNorEd CaSe", Case.ignore) == "string WITH an IgNorEd CaSe"
