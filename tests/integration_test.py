# type: ignore
"""Test the jdfile CLI."""

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

from jdfile.constants import VERSION
from jdfile.jdfile import app
from tests.helpers import strip_ansi

runner = CliRunner()
TODAY = datetime.now(tz=timezone.utc).date().strftime("%Y-%m-%d")
FIXTURE_CONFIG = Path(__file__).resolve().parent / "fixtures/fixture_config.toml"
FIXTURE_CONFIG_DOTFILES = Path(__file__).resolve().parent / "fixtures/fixture_config_dotfiles.toml"


@pytest.mark.parametrize(
    ("args", "expected", "exit_code"),
    [
        ([], "No files to process", 1),
        (["--help"], "Usage: main [OPTIONS] [FILES]...", 0),
        (["--version"], f"jdfile version: {VERSION}", 0),
    ],
)
def test_args_without_processing(args, expected, exit_code, debug):
    """Test basic CLI arguments."""
    result = runner.invoke(app, ["--settings-file", FIXTURE_CONFIG, *args])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == exit_code
    assert expected in strip_ansi(result.output)


@pytest.mark.parametrize(
    ("args", "filename", "message", "config_data"),
    [
        ([], ".dotfile_test.txt", "No files to process", {}),
        ([], "", "No files to process", {}),
        (["--project", "nonexistent"], "test_file.txt", "No project specified", {}),
        (["--tree"], "", "No project specified", {}),
        (["--tree", "--project", "nonexistent"], "", "No project specified", {}),
    ],
)
def test_failure_states(create_file, args, filename, message, config_data, debug):
    """Test failure states."""
    # GIVEN a file with the provided name in a clean directory

    original_file = create_file(filename)

    result = runner.invoke(app, ["--settings-file", FIXTURE_CONFIG, str(original_file), *args])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code != 0
    assert message in strip_ansi(result.output)


@pytest.mark.parametrize(
    ("args", "filename", "expected_file", "dotfiles_config"),
    [
        (["--sep", "DASH"], "foo bar baz.txt", f"{TODAY}-foo-bar-baz.txt", False),
        (["--sep", "SPACE"], "foo bar baz.txt", f"{TODAY} foo bar baz.txt", False),
        (["--sep", "UNDERSCORE"], "foo bar baz.txt", f"{TODAY}_foo_bar_baz.txt", False),
        (["--sep", "IGNORE"], "baz-bar_foo bar.txt", f"{TODAY}_baz-bar_foo bar.txt", False),
        ([], "foo bar baz.txt", f"{TODAY}_foo bar baz.txt", False),
        (["--case", "CAMELCASE"], "Baz bar FOO.txt", f"{TODAY}_BazBarFoo.txt", False),
        (["--case", "IGNORE"], "Baz bar FOO.txt", f"{TODAY}_Baz bar FOO.txt", False),
        (["--case", "LOWER"], "Baz bar FOO.txt", f"{TODAY}_baz bar foo.txt", False),
        (["--case", "SENTENCE"], "Baz bar FOO.txt", f"{TODAY}_Baz bar foo.txt", False),
        (["--case", "UPPER"], "Baz bar FOO.txt", f"{TODAY}_BAZ BAR FOO.txt", False),
        ([], "Baz bar FOO.txt", f"{TODAY}_Baz bar FOO.txt", False),
        ([], "$#@BAR(#FOO)*&^.txt", f"{TODAY}_BARFOO.txt", False),
        (["--split-words"], "FooBar.txt", f"{TODAY}_FooBar.txt", False),
        (["--split-words"], "BarFoo.txt", f"{TODAY}_Bar Foo.txt", False),
        ([], "Baz qux.txt", f"{TODAY}_Baz.txt", False),
        (["--keep-stopwords"], "Baz qux.txt", f"{TODAY}_Baz qux.txt", False),
        ([], ".dotfile_test.txt", ".dotfile.txt", True),
        (
            ["--date-format", "%Y"],
            "foo-bar-baz.txt",
            f"{datetime.now(tz=timezone.utc).date().strftime('%Y')}_foo-bar-baz.txt",
            False,
        ),
        (
            [],
            "foo bar baz.txt",
            f"{datetime.now(tz=timezone.utc).date().strftime('%Y-%m-%d')}_foo bar baz.txt",
            False,
        ),
        (["--split-words", "--no-format-dates"], "BarFoo Baz.txt", "Bar Foo Baz.txt", False),
        (
            ["--case", "LOWER", "--overwrite", "--no-format-dates"],
            "Foo Bar Baz.txt",
            "foo bar baz.txt",
            False,
        ),
        (["--sep", "DASH"], "foo bar baz.TAR.gz", f"{TODAY}-foo-bar-baz.tar.gz", False),
    ],
)
def test_filename_cleaning(
    tmp_path,
    create_file,
    debug,
    args,
    filename,
    dotfiles_config,
    expected_file,
):
    """Test cleaning filenames with various arguments."""
    # GIVEN a file with the provided name in a clean directory
    original_file = create_file(filename)
    # GIVEN a mocked config file location

    fixture_config = FIXTURE_CONFIG if not dotfiles_config else FIXTURE_CONFIG_DOTFILES

    # WHEN the file is processed with the provided arguments
    result = runner.invoke(app, ["--settings-file", fixture_config, str(original_file), *args])

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
def test_jdfile_project(mock_project, debug, args):
    """Test processing a jdfile project with not duplicate folders."""
    original_files_path, project_path, config_path = mock_project

    num_original_files = len(list(original_files_path.rglob("*")))

    result = runner.invoke(app, ["--settings-file", config_path, str(original_files_path), *args])

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


def test_jd_project_tree(mock_project, debug):
    """Test viewing a project folder tree."""
    _, _, config_path = mock_project

    result = runner.invoke(app, ["--settings-file", config_path, "--tree", "--project=test_jd"])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == 0
    assert "├── 10-19 foo" in strip_ansi(result.output)
    assert "│   ├── 11 bar" in strip_ansi(result.output)
    assert "│   │   ├── 11.01 foo" in strip_ansi(result.output)
    assert "└── foo" in strip_ansi(result.output)
    assert "└── bar" in strip_ansi(result.output)


def test_folder_project_tree(mock_project, debug):
    """Test viewing a project folder tree."""
    _, _, config_path = mock_project

    result = runner.invoke(app, ["--settings-file", config_path, "--tree", "--project=test_folder"])

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
def test_overwriting_files(tmp_path, create_file, debug, args, expected_filename):
    """Test overwriting files."""
    # GIVEN a file with the provided name in a clean directory
    existing_file_1 = create_file("original.txt")
    existing_file_2 = create_file("original_1.txt")
    file_to_clean = create_file("origi&$nal.txt")

    assert existing_file_1.exists()
    assert existing_file_2.exists()
    assert file_to_clean.exists()

    result = runner.invoke(app, ["--settings-file", FIXTURE_CONFIG, str(file_to_clean), *args])

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == 0
    assert existing_file_1.exists()
    assert existing_file_2.exists()
    assert not file_to_clean.exists()

    # debug("tmpPath", tmp_path)

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
def test_user_input(tmp_path, create_file, debug, args, user_input, lines_expected):
    """Test overwriting files."""
    create_file("big brown bear.txt", path="originals")
    create_file("origi&$nal.txt", path="originals")

    result = runner.invoke(
        app,
        ["--settings-file", FIXTURE_CONFIG, str(tmp_path / "originals"), *args],
        input=user_input,
        terminal_width=80,
    )

    # debug("result", strip_ansi(result.output))

    assert result.exit_code == 0
    assert "Pending changes for 2 of 2 files" in strip_ansi(result.output)

    for line in lines_expected:
        assert line in re.sub(r" +", " ", strip_ansi(result.output))
