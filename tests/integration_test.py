# type: ignore
"""Test jdfile CLI."""

import re
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from jdfile.constants import VERSION
from jdfile.jdfile import app
from jdfile.utils import AppConfig, console
from tests.helpers import strip_ansi

runner = CliRunner()
TODAY = date.today().strftime("%Y-%m-%d")


@pytest.mark.parametrize(
    ("args", "expected", "exit_code"),
    [
        ([], "No files to process", 1),
        (["--help"], "Usage: main [OPTIONS] [FILES]...", 0),
        (["--version"], f"jdfile version: {VERSION}", 0),
    ],
)
def test_basic_args(mock_config, args, expected, exit_code, debug):
    """Test basic CLI arguments."""
    with AppConfig.change_config_sources(mock_config()):
        result = runner.invoke(app, args)

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == exit_code
    assert expected in strip_ansi(result.output)


@pytest.mark.parametrize(
    ("args", "filename", "message", "config_data"),
    [
        ([], ".dotfile_test.txt", "No files to process", {}),
        ([], "", "No files to process", {}),
        (["--project", "nonexistent"], "test_file.txt", "Project not found: nonexistent", {}),
        (["--tree"], "", "No project specified", {}),
        (["--tree", "--project", "nonexistent"], "", "Project not found: nonexistent", {}),
    ],
)
def test_failure_states(create_file, mock_config, args, filename, message, config_data, debug):
    """Test failure states."""
    # GIVEN a file with the provided name in a clean directory
    original_file = create_file(filename)

    with AppConfig.change_config_sources(mock_config(**config_data)):
        result = runner.invoke(app, [str(original_file), *args])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code != 0
    assert message in strip_ansi(result.output)


@pytest.mark.parametrize(
    ("args", "filename", "expected_file", "config_data"),
    [
        (["--sep", "DASH"], "foo bar baz.txt", f"{TODAY}-foo-bar-baz.txt", {}),
        (["--sep", "SPACE"], "foo bar baz.txt", f"{TODAY} foo bar baz.txt", {}),
        (["--sep", "UNDERSCORE"], "foo bar baz.txt", f"{TODAY}_foo_bar_baz.txt", {}),
        (["--sep", "IGNORE"], "baz-bar_foo bar.txt", f"{TODAY}_baz-bar_foo bar.txt", {}),
        ([], "foo bar baz.txt", f"{TODAY}-foo-bar-baz.txt", {"separator": "dash"}),
        ([], "foo bar baz.txt", f"{TODAY} foo bar baz.txt", {"separator": "space"}),
        ([], "foo bar baz.txt", f"{TODAY}_foo_bar_baz.txt", {"separator": "underscore"}),
        ([], "baz-bar_foo bar.txt", f"{TODAY}_baz-bar_foo bar.txt", {"separator": "ignore"}),
        (["--case", "CAMELCASE"], "Baz bar FOO.txt", f"{TODAY}_BazBarFoo.txt", {}),
        (["--case", "IGNORE"], "Baz bar FOO.txt", f"{TODAY}_Baz bar FOO.txt", {}),
        (["--case", "LOWER"], "Baz bar FOO.txt", f"{TODAY}_baz bar foo.txt", {}),
        (["--case", "SENTENCE"], "Baz bar FOO.txt", f"{TODAY}_Baz bar foo.txt", {}),
        (["--case", "UPPER"], "Baz bar FOO.txt", f"{TODAY}_BAZ BAR FOO.txt", {}),
        ([], "Baz bar FOO jan 11 2004", "2004-01-11_BazBarFoo", {"transform_case": "CAMELCASE"}),
        ([], "Baz bar FOO.txt", f"{TODAY}_baz bar foo.txt", {"transform_case": "lower"}),
        ([], "Baz bar FOO.txt", f"{TODAY}_Baz bar foo.txt", {"transform_case": "sentence"}),
        ([], "Baz bar FOO.txt", f"{TODAY}_BAZ BAR FOO.txt", {"transform_case": "upper"}),
        ([], "$#@FOO(#BAR)*&^.txt", f"{TODAY}_FOOBAR.txt", {}),
        (["--split-words"], "FooBar.txt", f"{TODAY}_FooBar.txt", {"match_case_list": ["FooBar"]}),
        ([], "Baz bar.txt", f"{TODAY}_Baz.txt", {"stopwords": ["bar"]}),
        (["--keep-stopwords"], "Baz bar.txt", f"{TODAY}_Baz bar.txt", {"stopwords": ["bar"]}),
        ([], ".dotfile_test.txt", ".dotfile.txt", {"ignore_dotfiles": "false"}),
        (
            ["--date-format", "%Y"],
            "foo bar baz.txt",
            f"{date.today().strftime('%Y')}-foo-bar-baz.txt",
            {"separator": "dash"},
        ),
        (
            [],
            "foo bar baz.txt",
            f"{date.today().strftime('%Y')}-foo-bar-baz.txt",
            {"separator": "dash", "date_format": "%Y"},
        ),
        (["--split-words", "--no-format-dates"], "FooBar Baz.txt", "Foo Bar Baz.txt", {}),
        (
            ["--case", "LOWER", "--overwrite", "--no-format-dates"],
            "Foo Bar Baz.txt",
            "foo bar baz.txt",
            {},
        ),
        (["--sep", "DASH"], "foo bar baz.TAR.gz", f"{TODAY}-foo-bar-baz.tar.gz", {}),
    ],
)
def test_filename_cleaning(
    mock_config,
    tmp_path,
    create_file,
    debug,
    args,
    filename,
    config_data,
    expected_file,
):
    """Test cleaning filenames with various arguments."""
    # GIVEN a file with the provided name in a clean directory
    original_file = create_file(filename)

    # WHEN the file is processed with the provided arguments
    with AppConfig.change_config_sources(mock_config(**config_data)):
        result = runner.invoke(app, [str(original_file), *args])

    # debug("result", strip_ansi(result.output))

    # THEN the file is renamed as expected
    assert result.exit_code == 0
    assert f"{filename} -> {expected_file}" in strip_ansi(result.output)
    assert (tmp_path / expected_file).exists()
    if "--overwrite" not in args:
        assert not original_file.exists()


@pytest.mark.parametrize(
    ("args"),
    [
        (["--project=test_jd", "--no-clean", "--no-format-dates"]),
        (["--project=test_jd", "--no-clean", "--dry-run", "--no-format-dates"]),
    ],
)
def test_jdfile_project(mock_config, mock_project, debug, args):
    """Test processing a jdfile project with not duplicate folders."""
    original_files_path, project_path = mock_project

    num_original_files = len(list(original_files_path.rglob("*")))

    override_config = {}

    with AppConfig.change_config_sources(mock_config(**override_config)):
        result = runner.invoke(app, [str(original_files_path), *args])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == 0
    assert "⚠️ Files with no changes" in strip_ansi(result.output)
    assert "/originals/big orange bear.txt" in strip_ansi(result.output)
    assert f"Committing 3 with changes of {num_original_files} total files" in strip_ansi(
        result.output
    )
    assert "lazy dog.txt -> …/project/40-49 dog/lazy dog.txt" in strip_ansi(result.output)
    assert (original_files_path / "big orange bear.txt").exists()
    if "--dry-run" in args:
        assert (original_files_path / "cute fluffy cat.txt").exists()
        assert (original_files_path / "lazy dog.txt").exists()
        assert (original_files_path / "quick brown fox.txt").exists()
        assert not (project_path / "20-29_bar/22 cat/cute fluffy cat.txt").exists()
        assert not (project_path / "40-49 dog/lazy dog.txt").exists()
        assert not (project_path / "20-29_bar/20_foo/20.04 fox/quick brown fox.txt").exists()
    else:
        assert not (original_files_path / "cute fluffy cat.txt").exists()
        assert not (original_files_path / "lazy dog.txt").exists()
        assert not (original_files_path / "quick brown fox.txt").exists()
        assert (project_path / "20-29_bar/22 cat/cute fluffy cat.txt").exists()
        assert (project_path / "40-49 dog/lazy dog.txt").exists()
        assert (project_path / "20-29_bar/20_foo/20.04 fox/quick brown fox.txt").exists()


def test_jd_project_tree(mock_config, mock_project, debug):
    """Test viewing a project folder tree."""
    _, _ = mock_project

    with AppConfig.change_config_sources(mock_config()):
        result = runner.invoke(app, ["--tree", "--project=test_jd"])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == 0
    assert "├── 10-19 foo" in strip_ansi(result.output)
    assert "│   ├── 11 bar" in strip_ansi(result.output)
    assert "│   │   ├── 11.01 foo" in strip_ansi(result.output)
    assert "└── foo" not in strip_ansi(result.output)
    assert "└── bar" not in strip_ansi(result.output)


def test_folder_project_tree(mock_config, mock_project, debug):
    """Test viewing a project folder tree."""
    _, _ = mock_project

    with AppConfig.change_config_sources(mock_config()):
        result = runner.invoke(app, ["--tree", "--project=test_folder"])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == 0
    assert "├── 10-19 foo" in strip_ansi(result.output)
    assert "│   ├── 11 bar" in strip_ansi(result.output)
    assert "│   │   ├── 11.01 foo" in strip_ansi(result.output)
    assert "└── foo" in strip_ansi(result.output)
    assert "└── bar" in strip_ansi(result.output)


@pytest.mark.parametrize(
    ("args", "expected_filename"),
    [
        (["--no-format-dates"], "original_2.txt"),
        (["--no-overwrite", "--no-format-dates"], "original_2.txt"),
        (["--overwrite", "--no-format-dates"], "original.txt"),
        (["--sep", "DASH", "--no-format-dates"], "original-1.txt"),
    ],
)
def test_overwriting_files(tmp_path, mock_config, create_file, debug, args, expected_filename):
    """Test overwriting files."""
    # GIVEN a file with the provided name in a clean directory
    existing_file_1 = create_file("original.txt")
    existing_file_2 = create_file("original_1.txt")
    file_to_clean = create_file("origi&$nal.txt")

    assert existing_file_1.exists()
    assert existing_file_2.exists()
    assert file_to_clean.exists()

    with AppConfig.change_config_sources(mock_config()):
        result = runner.invoke(app, [str(file_to_clean), *args])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == 0
    assert existing_file_1.exists()
    assert existing_file_2.exists()
    assert not file_to_clean.exists()
    assert Path(tmp_path / expected_filename).exists()
    assert f"origi&$nal.txt -> {expected_filename}" in strip_ansi(result.output)


@pytest.mark.parametrize(
    ("args", "user_input", "lines_expected"),
    [
        (
            ["--confirm", "--no-format-dates"],
            "n\r",
            [
                "# Original Name New Name",
                "1 big brown bear.txt brown bear.txt",
                "2 origi&$nal.txt original.txt",
            ],
        ),
        (
            ["--confirm", "-v", "--no-format-dates"],
            "y\r",
            [
                "# Original Name New Name Diff",
                "1 big brown bear.txt brown bear.txt big",
                "brown bear.txt",
                "2 origi&$nal.txt original.txt origi&$nal.txt",
                "Committing 2",
                "big brown bear.txt -> brown bear.txt",
                "origi&$nal.txt -> original.txt",
            ],
        ),
    ],
)
def test_user_input(tmp_path, mock_config, create_file, debug, args, user_input, lines_expected):
    """Test overwriting files."""
    create_file("big brown bear.txt", path="originals")
    create_file("origi&$nal.txt", path="originals")

    with AppConfig.change_config_sources(mock_config()):
        result = runner.invoke(
            app,
            [str(tmp_path / "originals"), *args],
            input=user_input,
            terminal_width=80,
        )

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == 0
    assert "Pending changes for 2 of 2 files" in strip_ansi(result.output)

    for line in lines_expected:
        assert line in re.sub(r" +", " ", strip_ansi(result.output))
