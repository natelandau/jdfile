# type: ignore
"""Shared fixtures for tests."""

from pathlib import Path

import pytest
from dynaconf import settings

from jdfile.utils import console

TEST_FILES = [
    "quick brown fox.txt",
    "lazy dog.txt",
    "cute fluffy cat.txt",
    "big orange bear.txt",
    # "cuddly gray koala.txt",
]
# Mock project folder structure using animals as friendly keys
# `koala` matches 2 folders
# `fox` matches 1 folder
# `cat` matches 1 folder
# `dog` matches 1 folder
# `bear` matches no folders
DIRS = [
    "10-19 foo/11 bar/11.01 foo",
    "10-19 foo/11 bar/11.02 bar",
    "10-19 foo/11 bar/11.03 koala",
    "10-19 foo/12 baz/12.01 foo",
    "10-19 foo/12 baz/12.02 bar",
    "10-19 foo/12 baz/12.03 koala",
    "10-19 foo/12 baz/12.04 baz",
    "10-19 foo/12 baz/12.05 waldo",
    "20-29_bar/20_foo/20.01_foo_bar_baz",
    "20-29_bar/20_foo/20.02_bar",
    "20-29_bar/20_foo/20.03_waldo",
    "20-29_bar/20_foo/20.04 fox",
    "20-29_bar/21_bar",
    "20-29_bar/22 cat",
    "30-39_baz",
    "40-49 dog",
    "foo/bar/foo",
    "foo/bar/bar",
    "foo/bar/baz",
    "foo/bar/qux",
]
FIXTURE_CONFIG = Path(__file__).resolve().parent / "fixtures/fixture_config.toml"


@pytest.fixture
def create_file(tmp_path):
    """Create a file for testing."""

    def _inner(name: str, path: str | None = None, content: str | None = None):
        """Create a file with the provided name and content.

        Args:
            name (str): The name of the file to create.
            path (str, optional): The path to create the file in. Defaults to None.
            content (str, optional): The content to write to the file. Defaults to None.
        """
        file_path = Path(tmp_path / path / name) if path else Path(tmp_path / name)

        if path:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        if content:
            file_path.write_text(content)
        else:
            file_path.touch()

        return file_path

    return _inner


@pytest.fixture
def debug():
    """Print debug information to the console. This is used to debug tests while writing them."""

    def _debug_inner(label: str, value: str | Path, stop: bool = False):
        """Print debug information to the console. This is used to debug tests while writing them.

        Args:
            label (str): The label to print above the debug information.
            value (str | Path): The value to print. When this is a path, prints all files in the path.
            stop (bool, optional): Whether to break after printing. Defaults to False.

        Returns:
            bool: Whether to break after printing.
        """
        console.rule(label)
        if not isinstance(value, Path) or not value.is_dir():
            console.print(value)
        else:
            for p in value.rglob("*"):
                console.print(p)

        console.rule()

        if stop:
            return pytest.fail("Breakpoint")

        return True

    return _debug_inner


@pytest.fixture
def mock_project(tmp_path):
    """Fixture to create a config object with values parsed from a config file.

    Returns:
        tuple: (original_files_dir, project_root_dir, config_path)
    """
    project_path = Path(tmp_path / "project")
    project_path.mkdir(parents=True, exist_ok=True)

    original_files_path = Path(tmp_path / "originals")
    original_files_path.mkdir(parents=True, exist_ok=True)

    config_path = Path(tmp_path / "config.toml")
    config_text = FIXTURE_CONFIG.read_text()
    config_path.write_text(config_text.replace("PATH_GOES_HERE", str(project_path)))

    for d in DIRS:
        Path(project_path / d).mkdir(parents=True, exist_ok=True)

    for f in TEST_FILES:
        Path(original_files_path / f).touch()

    return original_files_path, project_path, config_path
