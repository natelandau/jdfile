# type: ignore
"""Tests for string utilities."""

from jdfile.constants import InsertLocation, Separator, TransformCase
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


def test_insert_1():
    """Test insert() function.

    GIVEN a string, a value, a location, and a separator
    WHEN separator is IGNORE and location is BEFORE
    THEN the value is inserted before the string
    """
    assert insert("foo bar", "qux", InsertLocation.BEFORE, Separator.IGNORE) == "qux_foo bar"


def test_insert_2():
    """Test insert() function.

    GIVEN a string, a value, a location, and a separator
    WHEN separator is SPACE and location is AFTER
    THEN the value is inserted after the string
    """
    assert insert("foo bar", "qux", InsertLocation.AFTER, Separator.SPACE) == "foo bar qux"


def test_insert_3():
    """Test insert() function.

    GIVEN a string, a value, a location, and a separator
    WHEN separator is NONE and location is AFTER
    THEN the value is inserted after the string
    """
    assert insert("foo bar", "qux", InsertLocation.AFTER, Separator.NONE) == "foo barqux"


def test_insert_4():
    """Test insert() function.

    GIVEN a string, a value, a location, and a separator
    WHEN separator is UNDERSCORE and location is AFTER
    THEN the value is inserted before the string
    """
    assert insert("foo bar", "qux", InsertLocation.AFTER, Separator.UNDERSCORE) == "foo bar_qux"


def test_insert_5():
    """Test insert() function.

    GIVEN a string, a value, a location, and a separator
    WHEN separator is DASH and location is AFTER
    THEN the value is inserted before the string
    """
    assert insert("foo bar", "qux", InsertLocation.AFTER, Separator.DASH) == "foo bar-qux"


def test_match_case_1():
    """Test match_case() function.

    GIVEN a string and a list of strings
    WHEN the list is empty
    THEN the string is returned unchanged
    """
    assert match_case("FooBar BAZ", []) == "FooBar BAZ"


def test_match_case_2():
    """Test match_case() function.

    GIVEN a string and a list of strings
    WHEN no list is provided
    THEN the string is returned unchanged
    """
    assert match_case("FooBar BAZ") == "FooBar BAZ"


def test_match_case_3():
    """Test match_case() function.

    GIVEN a string and a list of strings
    WHEN values in the list match the string
    THEN return the changed string
    """
    assert match_case("foobar baz", ["FOOBAR", "BAZ"]) == "FOOBAR BAZ"
    assert match_case("foobar baz", ["FooBar"]) == "FooBar baz"


def test_normalize_separators_1():
    """Test normalize_separators() function.

    GIVEN a string and a target separator
    WHEN the targe separator is not specified
    THEN the string is returned unchanged
    """
    assert normalize_separators("foo-bar_baz foo") == "foo-bar_baz foo"
    assert normalize_separators("text.without.any.separators") == "text.without.any.separators"


def test_normalize_separators_2():
    """Test normalize_separators() function.

    GIVEN a string and a target separator
    WHEN the targe separator is IGNORE
    THEN the string is returned unchanged
    """
    assert normalize_separators("foo-bar_baz foo") == "foo-bar_baz foo"


def test_normalize_separators_3():
    """Test normalize_separators() function.

    GIVEN a string and a target separator
    WHEN the targe separator is NONE
    THEN the string is returned with all separators removed
    """
    assert normalize_separators("- _foo-bar___baz foo", Separator.NONE) == "foobarbazfoo"


def test_normalize_separators_4():
    """Test normalize_separators() function.

    GIVEN a string and a target separator
    WHEN the targe separator is SPACE
    THEN the string is returned with all separators changed to spaces
    """
    assert normalize_separators("foo--bar_baz foo", Separator.SPACE) == "foo bar baz foo"


def test_normalize_separators_5():
    """Test normalize_separators() function.

    GIVEN a string and a target separator
    WHEN the targe separator is DASH
    THEN the string is returned with all separators changed to dashes
    """
    assert normalize_separators(" foo-bar___baz foo", Separator.DASH) == "foo-bar-baz-foo"


def test_normalize_separators_6():
    """Test normalize_separators() function.

    GIVEN a string and a target separator
    WHEN the targe separator is UNDERSCORE
    THEN the string is returned with all separators changed to underscores
    """
    """Test normalizing separators in a string."""
    assert normalize_separators("--foo--bar_baz foo--", Separator.UNDERSCORE) == "foo_bar_baz_foo"


def test_camelcase_words():
    """Test splitting camelcase words in a string."""
    assert split_camelcase_words("foo bar baz") == "foo bar baz"
    assert split_camelcase_words("fooBarBaz") == "foo Bar Baz"
    assert split_camelcase_words("fooBarBaz", match_case_list=["fooBarBaz"]) == "fooBarBaz"
    assert split_camelcase_words("fooBarBaz", match_case_list=["BarBaz"]) == "foo BarBaz"


def test_split_words():
    """Test splitting words in a string into a list."""
    assert split_words("foo bar baz") == ["foo", "bar", "baz"]
    assert split_words("---99_ _9foo-b9ar_baz9 9f9oo9") == ["9foo", "b9ar", "baz9", "9f9oo9"]
    assert split_words("123 a 456 B 789 c") == []


def test_strip_special_chars():
    """Test stripping special characters from a string."""
    assert strip_special_chars("foo bar-baz_123") == "foo bar-baz_123"
    assert strip_special_chars("%foo~!@#$%^bar_baz:123") == "foobar_baz123"


def test_strip_stopwords():
    """Test stripping stopwords from a string."""
    assert strip_stopwords("foo bar baz") == "foo bar baz"
    assert strip_stopwords("foo bar baz", stopwords=["bar"]) == "foo  baz"
    assert strip_stopwords("foo bar bar1 baz", stopwords=["bar", "baz"]) == "foo  bar1"
    assert strip_stopwords("foo bar baz", stopwords=["foo", "bar", "baz"]) == "foo bar baz"


def test_transform_case():
    """Test transforming the case of a string."""
    assert transform_case("foo bar baz", TransformCase.CAMELCASE) == "FooBarBaz"
    assert transform_case("foo_bar_baz", TransformCase.CAMELCASE) == "FooBarBaz"
    assert transform_case("foo-bar-baz", TransformCase.CAMELCASE) == "FooBarBaz"
    assert transform_case("foo+bar+baz", TransformCase.CAMELCASE) == "Foo+Bar+Baz"
    assert transform_case("FOO BAR BAZ", TransformCase.LOWER) == "foo bar baz"
    assert transform_case("foo bar baz", TransformCase.UPPER) == "FOO BAR BAZ"
    assert transform_case("foo BAR BAZ", TransformCase.SENTENCE) == "Foo bar baz"
    assert transform_case("foo bar baz", TransformCase.TITLE) == "Foo Bar Baz"
    assert transform_case("foo BAR Baz", TransformCase.IGNORE) == "foo BAR Baz"
