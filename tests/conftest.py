# type: ignore
"""Fixtures for tests."""

from pathlib import Path
from textwrap import dedent

import pytest


@pytest.fixture()
def test_project(tmp_path):
    """Fixture for creating a test config file.

    Args:
        tmp_path: (Path) Temporary path to create the test config file.

    Returns:
        root: (Path) Root directory of the test config file.
    """
    project = Path(tmp_path) / "project"
    project.mkdir(parents=True, exist_ok=True)

    folders = [
        Path(project, "10-19 area1"),
        Path(project, "10-19 area1/11 category1"),
        Path(project, "10-19 area1/11 category1/11.01 subcategory1"),
        Path(project, "10-19 area1/11 category1/11.02 subcategory2"),
        Path(project, "10-19 area1/11 category1/11.03 subcategory3"),
        Path(project, "10-19 area1/12 category2"),
        Path(project, "10-19 area1/12 category2/12.01 subcategory1"),
        Path(project, "10-19 area1/12 category2/12.02 subcategory2"),
        Path(project, "10-19 area1/12 category2/12.03 subcategory3"),
        Path(project, "20-29 area2"),
        Path(project, "20-29 area2/20 category1"),
        Path(project, "20-29 area2/20 category1/20.01 subcategory1"),
        Path(project, "20-29 area2/20 category1/20.02 subcategory2"),
        Path(project, "20-29 area2/21 category2"),
        Path(project, "30-39 project plans"),
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    term_file1 = Path(project, "10-19 area1/11 category1/11.01 subcategory1/.filemanager")
    term_file2 = Path(project, "10-19 area1/11 category1/11.02 subcategory2/.filemanager")

    term_file1.write_text(
        dedent(
            """\
            # words to match
            fruit
            apple
            orange
            """
        )
    )
    term_file2.write_text(
        dedent(
            """\
            fruit
            apple
            banana
            """
        )
    )

    config = Path(tmp_path) / "filemanager.toml"
    config_text = f"""\
        match_case = [
            "PEAR",
            "KiWi"
        ]

        [projects]

        [projects.jd]
        name = "test"
        path = "{project}"
        stopwords = ["apricot"]
        """

    config.write_text(dedent(config_text))

    return str(config), str(project)


@pytest.fixture()
def test_files(tmp_path) -> Path:
    """Create testfiles for testing filename.

    Args:
        tmp_path (Path): Path to tmpdir created by tmp_path builtin fixture.

    Returns:
        list of test filenames.
    """
    filenames = [
        "2019-01-02_underscore_with_date.txt",  # 0
        "2021-06-08_some_TEST_file.txt",  # 1
        "2022-08-28_a-fine_&(filename).txt",  # 2
        "2022-08-28 a_FIne &(filename).txt",  # 3
        "2022-08-28 A FINE &(FILENAME)",  # 4
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
        "two-extensions.TAR.gz",  # 20
        "testfile.txt",  # 21
        "testfile.txt.1",  # 22
        "testfile 1.txt",  # 23
        "TESTFILE.txt",  # 24
        ".dotfile.txt",  # 25
        ".dotfile.JPEG.ZIP.gzip",  # 26
        "QuickBrownFox has camelCase words.txt",  # 27
        "quick brown apples and fruit.txt",  # 28
        "quick_project_and_foxes.txt",  # 29
        "quick brown apricot and fruit.txt",  # 30
        "quick brown banana.txt",  # 31
        "category1 and subcategory1.txt",  # 32
        "quick brown area3 and fruit.txt",  # 33
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
