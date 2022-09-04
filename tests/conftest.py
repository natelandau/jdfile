# type: ignore
"""Fixtures for tests."""

from pathlib import Path

import pytest


@pytest.fixture()
def test_files(tmp_path):
    """Create testfiles for test.

    Args:
        tmp_path (Path): Path to tmpdir created by tmp_path builtin fixture.

    Returns:
        list of test filenames.
    """
    filenames = [
        "2019-01-02_underscore_with_date.txt",  # 0
        "2021-06-08_some_TEST_file.txt",  # 1
        "2022-08-28_a-fine_&(filename).txt",  # 2
        "2022-08-28 a_fine &(filename).txt",  # 3
        "2022-08-28 A FINE &(FILENAME)" ".dotfile.txt",  # 4
        "2022-08-28 date and &(chars).txt",  # 5
        "[b]rackets.txt",  # 6
        "__stripped separators--.txt",  # 7
        "ALLCAPS.txt",  # 8
        "lowercase.txt",  # 9
        "disk_image.dmg",  # 10
        "i_have_underscores.txt",  # 11
        "month-DD-YY March 19, 74 test.txt",  # 12
        "month-DD-YY March 21, 2002 test.txt",  # 13
        "month-DD-YYYY file january 01 2016.txt",  # 14
        "Multiple---separators  are___stripped.txt",  # 15
        "one.txt",  # 16
        "some (TEST) file 2022-08-28.txt",  # 17
        "some_file_12-22-2021.txt",  # 18
        "specialChars(@#$)-&*.txt",  # 19
        "two-extensions.tar.gz",  # 20
        "testfile.txt",  # 21
        "testfile.txt.1",  # 22
        "testfile 1.txt",  # 23
        "TESTFILE.txt",  # 24
    ]

    originals = tmp_path / "originals"
    originals.mkdir(parents=True, exist_ok=True)
    new = tmp_path / "new"
    new.mkdir(parents=True, exist_ok=True)

    test_files = []
    for file in filenames:
        Path(originals / file).touch()
        test_files.append(Path(originals / file))

    return test_files
