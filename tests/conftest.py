# type: ignore
"""Shared fixtures for tests."""
import re
from pathlib import Path
from textwrap import dedent

import py
import pytest
from confz import DataSource, FileSource

from jdfile.utils import AppConfig, console

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


@pytest.fixture()
def create_file(tmp_path):
    """Create a file for testing."""

    def _inner(name: str, path: str | None = None, content: str | None = None):
        """Create a file with the provided name and content.

        Args:
            name (str): The name of the file to create.
            path (str, optional): The path to create the file in. Defaults to None.
            content (str, optional): The content to write to the file. Defaults to None.
        """
        file_path = Path(path / name) if path else Path(tmp_path / name)

        if content:
            file_path.write_text(content)
        else:
            file_path.touch()

        return file_path

    return _inner


@pytest.fixture()
def debug():
    """Print debug information to the console. This is used to debug tests while writing them."""

    def _debug_inner(label: str, value: str | Path, breakpoint: bool = False, width: int = 80):
        """Print debug information to the console. This is used to debug tests while writing them.

        Args:
            label (str): The label to print above the debug information.
            value (str | Path): The value to print. When this is a path, prints all files in the path.
            breakpoint (bool, optional): Whether to break after printing. Defaults to False.
            width (int, optional): The width of the console output. Defaults to 80, pytest's default when running without `-s`.

        Returns:
            bool: Whether to break after printing.
        """
        regexes_to_strip = [
            r"\( *● *\) Processing Files...  \(Can take a while for large directory trees\)",
            r"\]8;id=.*8;;",
        ]

        console.rule(label)
        # If a directory is passed, print the contents
        if isinstance(value, Path) and value.is_dir():
            for p in value.rglob("*"):
                console.print(p, width=width)
        else:
            for line in value.split("\n"):
                stripped_line = line
                for regex in regexes_to_strip:
                    stripped_line = re.sub(regex, "", stripped_line)
                console.print(stripped_line, width=width)

        console.rule()

        if breakpoint:
            return pytest.fail("Breakpoint")

        return True

    return _debug_inner


@pytest.fixture()
def mock_config(tmp_path):
    """Mock specific configuration data for use in tests by accepting arbitrary keyword arguments.

    The function dynamically collects provided keyword arguments, filters out any that are None,
    and prepares data sources with the overridden configuration for file processing.

    Usage:
        def test_something(mock_config):
            # Override the configuration with specific values
            with AppConfig.change_config_sources(config_data(some_key="some_value")):
                    # Test the functionality
                    result = do_something()
                    assert result
    """

    def _inner(**kwargs):
        """Collects provided keyword arguments, omitting any that are None, and prepares data sources with the overridden configuration.

        Args:
            **kwargs: Arbitrary keyword arguments representing configuration settings.

        Returns:
            list: A list containing a FileSource initialized with the fixture configuration and a DataSource with the overridden data.
        """
        # Filter out None values from kwargs
        override_data = {key: value for key, value in kwargs.items() if value is not None}

        # If a 'config.toml' file exists in the test directory, use it as the configuration source
        if Path(tmp_path / "config.toml").exists():
            config_file_source = str(tmp_path / "config.toml")
        else:
            # Check for 'config_file' in kwargs and use it if present, else default to FIXTURE_CONFIG
            config_file_source = kwargs.get("config_file", FIXTURE_CONFIG)

        # Return a list of data sources with the overridden configuration
        return [FileSource(config_file_source), DataSource(data=override_data)]

    return _inner


@pytest.fixture()
def mock_project(tmp_path):
    """Fixture to create a config object with values parsed from a config file.

    Returns:
        tuple: (original_files_dir, project_root_dir)
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
    # term_file1 = Path(project_path, "10-19 foo/11 bar/11.01 foo/.jdfile")
    # term_file2 = Path(project_path, "foo/bar/baz/.jdfile")
    # term_file1.write_text(
    #     dedent(
    #         """\
    #         # words to match
    #         lorem
    #         """
    #     )
    # )
    # term_file2.write_text(
    #     dedent(
    #         """\
    #         Ipsum
    #         """
    #     )
    # )

    for f in TEST_FILES:
        Path(original_files_path / f).touch()

    return original_files_path, project_path
