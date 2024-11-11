# type: ignore
"""Test the file model."""

from pathlib import Path
from unittest.mock import patch

from jdfile.models import File
from jdfile.utils import console

# Mock the stat call to return a consistent ctime


def test_with_hypothesis() -> None:
    """Test instantiating and cleaning files with various unicode characters."""
    # GIVEN a file with the provided name in a clean directory
    filename = "testfile.txt"
    # console.log("before: ", filename)  # for debugging

    mock_stat = type("MockStat", (), {"st_ctime": 1234567890.0})

    with patch("jdfile.models.file.Path.stat", return_value=mock_stat):
        file = File(path=Path(filename), project=None)
        # console.log(file.__dict__)
        # assert False
        # console.log("after: ", file.path)  # for debugging
        assert str(file.path) == filename
        file.clean_filename()
        # console.log("cleaned: ", file.path.name)  # for debugging
