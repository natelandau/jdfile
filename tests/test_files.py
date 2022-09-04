# type: ignore
"""Test file utilities."""

from pathlib import Path

from filemanager._utils.files import create_unique_filename
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
