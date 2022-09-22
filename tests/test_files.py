# type: ignore
"""Test file utilities."""

from pathlib import Path

from filemanager._utils import File, create_unique_filename, populate_stopwords
from tests.helpers import Regex


def test_create_unique_filename(test_files, tmp_path):
    """Test create_unique_filename."""
    assert str(create_unique_filename(test_files[21], "underscore", True)) == Regex(
        r".*originals/testfile\.txt\.2"
    )

    assert str(create_unique_filename(test_files[21], "underscore", False)) == Regex(
        r".*originals/testfile_1\.txt"
    )

    assert str(create_unique_filename(test_files[21], "space", False)) == Regex(
        r".*originals/testfile 2\.txt"
    )

    assert str(create_unique_filename(test_files[21], "dash", False)) == Regex(
        r".*originals/testfile-1\.txt"
    )

    assert str(
        create_unique_filename(Path(tmp_path / "originals" / "somefile.txt"), "dash", False)
    ) == Regex(r".*originals/somefile.txt")


def test_file_creation(test_files):
    """Test creating a file object."""
    stopwords = populate_stopwords()
    terms = ["term1", "term2", "term3"]
    file = File(test_files[3], terms)

    assert file.path == test_files[3]
    assert file.new_path == test_files[3]
    assert file.parent == test_files[3].parent
    assert file.new_parent == test_files[3].parent
    assert file.stem == test_files[3].stem
    assert file.new_stem == test_files[3].stem
    assert file.suffixes == test_files[3].suffixes
    assert file.new_suffixes == test_files[3].suffixes
    assert file.dotfile is False
    assert file.terms == terms

    file.clean(separator="dash", case="upper", stopwords=stopwords)
    assert file.stem == test_files[3].stem
    assert file.new_stem == "2022-08-28-FINE-FILENAME"

    file.clean(separator="space", case="lower", stopwords=stopwords)
    assert file.new_stem == "2022 08 28 fine filename"

    file.add_date(
        add_date=True,
        date_format="%Y-%m-%d",
        separator="space",
    )
    assert file.new_stem == "2022-08-28 fine filename"

    file.add_date(
        add_date=True,
        date_format="%Y/%m/%d",
        separator="underscore",
    )
    assert file.new_stem == "2022/08/28_fine filename"

    file.add_date(
        add_date=False,
        date_format="%Y-%m-%d",
        separator="space",
    )
    assert file.new_stem == "fine filename"

    file = File(test_files[26], terms)
    assert file.dotfile is True
    file.clean(separator="underscore", case="upper", stopwords=stopwords)
    assert file.new_stem == ".DOTFILE"
    assert file.new_suffixes == [".jpg", ".zip", ".gzip"]
    file.add_date(
        add_date=True,
        date_format="%Y-%m-%d",
        separator="underscore",
    )
    assert file.new_stem == Regex(r"^\.\d{4}-\d{2}-\d{2}_dotfile")

    file = File(test_files[15], [])
    file.clean("underscore", "title", stopwords)
    assert file.new_stem == "Multiple_Separators_Stripped"
