# type: ignore
"""Fixtures for tests."""

import shutil
from pathlib import Path
from textwrap import dedent

import pytest

from jdfile._config.config import Config
from jdfile.models.file import File

CONFIG_1 = """
[fixture]
    date_format         = "None"
    ignore_dotfiles     = true
    ignored_files       = ['ignore.txt']
    match_case          = ["BarBaz"]
    overwrite_existing  = false
    path                = "PATH"
    separator           = "ignore"
    split_words         = false
    stopwords           = ["qux"]
    strip_stopwords     = false
    transform_case      = "ignore"
"""

TEST_FILES = [
    "foobar.txt",
    ".dotfile",
    "ignore.txt",
    "1974-03-19 foo.JPEG.GZ",
    "$#@FOO(#BAR)*&^.txt",
    "FooBarBaz.txt",
    "___foo----BARBAZ March 19, 1974---.txt",
    "03191974 foo bar.txt",
    "foo_Mar19_1974_bar.txt",
    "foo 19Mar1974 bar.txt",
    "foobar_2.txt",
    "lorem_ipsum.txt",
    "foo_bar_baz_QUX.txt",
    "IpSum.txt",
    "qux.txt",
    "waldo.txt",
]

DIRS = [
    "10-19 foo/11 bar/11.01 foo",
    "10-19 foo/11 bar/11.02 bar",
    "10-19 foo/11 bar/11.03 baz",
    "10-19 foo/12 baz/12.01 foo",
    "10-19 foo/12 baz/12.02 bar",
    "10-19 foo/12 baz/12.03 QUX",
    "10-19 foo/12 baz/12.04 baz",
    "10-19 foo/12 baz/12.05 waldo",
    "20-29_bar/20_foo/20.01_foo_bar_baz",
    "20-29_bar/20_foo/20.02_bar",
    "20-29_bar/20_foo/20.03_waldo",
    "20-29_bar/21_bar",
    "30-39_baz",
    "foo/bar/foo",
    "foo/bar/bar",
    "foo/bar/baz",
    "foo/bar/qux",
]


@pytest.fixture()
def test_file_object(tmp_path):
    """Fixture for creating a test File object."""
    config = Config()
    test_file = Path(tmp_path / "test_file.txt")
    test_file.touch()
    yield File(path=test_file, config=config)
    test_file.unlink(missing_ok=True)


@pytest.fixture()
def config1_project(tmp_path):
    """Fixture to create a config object with values parsed from a config file.

    Returns:
        tuple: (config object, original_files_path, project_path)
    """
    project_path = Path(tmp_path / "project")
    project_path.mkdir(parents=True, exist_ok=True)

    original_files_path = Path(tmp_path / "originals")
    original_files_path.mkdir(parents=True, exist_ok=True)

    config_path = Path(tmp_path / "config.toml")
    config_path.write_text(CONFIG_1.replace("PATH", str(project_path)))
    config = Config(config_path=config_path, context={"project_name": "fixture"})

    for d in DIRS:
        Path(project_path / d).mkdir(parents=True, exist_ok=True)
    term_file1 = Path(project_path, "10-19 foo/11 bar/11.01 foo/.jdfile")
    term_file2 = Path(project_path, "foo/bar/baz/.jdfile")
    term_file1.write_text(
        dedent(
            """\
            # words to match
            lorem
            """
        )
    )
    term_file2.write_text(
        dedent(
            """\
            Ipsum
            """
        )
    )

    for f in TEST_FILES:
        Path(original_files_path / f).touch()
    yield config, original_files_path, project_path

    # # Cleanup
    # shutil.rmtree(project_path)
    # shutil.rmtree(original_files_path)
