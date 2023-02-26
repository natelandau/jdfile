# type: ignore
"""Tests for string utilities."""

from jdfile.utils.enums import InsertLocation, Separator, TransformCase
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


def test_insert():
    """Test inserting a string into another string."""
    assert insert("foo bar", "qux", InsertLocation.BEFORE, Separator.IGNORE) == "qux_foo bar"
    assert insert("foo bar", "qux", InsertLocation.AFTER, Separator.SPACE) == "foo bar qux"
    assert insert("foo bar", "qux", InsertLocation.AFTER, Separator.NONE) == "foo barqux"
    assert insert("foo bar", "qux", InsertLocation.AFTER, Separator.UNDERSCORE) == "foo bar_qux"
    assert insert("foo bar", "qux", InsertLocation.AFTER, Separator.DASH) == "foo bar-qux"


def test_match_case():
    """Test matching the case of a string."""
    assert match_case("foobar baz") == "foobar baz"
    assert match_case("foobar baz", ["FOOBAR", "BAZ"]) == "FOOBAR BAZ"
    assert match_case("foobar baz", ["FooBar"]) == "FooBar baz"


def test_normalize_separators():
    """Test normalizing separators in a string."""
    assert normalize_separators("foo-bar_baz foo") == "foo-bar_baz foo"
    assert normalize_separators("foo-bar_baz foo", Separator.IGNORE) == "foo-bar_baz foo"
    assert normalize_separators("- _foo-bar___baz foo", Separator.NONE) == "foobarbazfoo"
    assert normalize_separators("foo--bar_baz foo", Separator.SPACE) == "foo bar baz foo"
    assert normalize_separators(" foo-bar___baz foo", Separator.DASH) == "foo-bar-baz-foo"
    assert normalize_separators("--foo--bar_baz foo--", Separator.UNDERSCORE) == "foo_bar_baz_foo"


def test_camelcase_words():
    """Test splitting words in a string."""
    assert split_camelcase_words("foo bar baz") == "foo bar baz"
    assert split_camelcase_words("fooBarBaz") == "foo Bar Baz"
    assert split_camelcase_words("fooBarBaz", match_case=["fooBarBaz"]) == "fooBarBaz"
    assert split_camelcase_words("fooBarBaz", match_case=["BarBaz"]) == "foo BarBaz"


def test_split_words():
    """Test splitting words in a string."""
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
    assert strip_stopwords("foo bar baz", stopwords=["bar", "baz"]) == "foo"
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
