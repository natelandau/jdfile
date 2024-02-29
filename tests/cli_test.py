# type: ignore
"""Test jdfile CLI."""


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
    ("args", "filename", "expected_file", "config_data", "exit_code"),
    [
        (["--sep", "DASH"], "foo bar baz.txt", f"{TODAY}-foo-bar-baz.txt", {}, 0),
        (["--sep", "SPACE"], "foo bar baz.txt", f"{TODAY} foo bar baz.txt", {}, 0),
        (["--sep", "UNDERSCORE"], "foo bar baz.txt", f"{TODAY}_foo_bar_baz.txt", {}, 0),
        (["--sep", "IGNORE"], "baz-bar_foo bar.txt", f"{TODAY}_baz-bar_foo bar.txt", {}, 0),
        ([], "foo bar baz.txt", f"{TODAY}-foo-bar-baz.txt", {"separator": "dash"}, 0),
        ([], "foo bar baz.txt", f"{TODAY} foo bar baz.txt", {"separator": "space"}, 0),
        ([], "foo bar baz.txt", f"{TODAY}_foo_bar_baz.txt", {"separator": "underscore"}, 0),
        ([], "baz-bar_foo bar.txt", f"{TODAY}_baz-bar_foo bar.txt", {"separator": "ignore"}, 0),
        (["--case", "CAMELCASE"], "Baz bar FOO.txt", f"{TODAY}_BazBarFoo.txt", {}, 0),
        (["--case", "IGNORE"], "Baz bar FOO.txt", f"{TODAY}_Baz bar FOO.txt", {}, 0),
        (["--case", "LOWER"], "Baz bar FOO.txt", f"{TODAY}_baz bar foo.txt", {}, 0),
        (["--case", "SENTENCE"], "Baz bar FOO.txt", f"{TODAY}_Baz bar foo.txt", {}, 0),
        (["--case", "UPPER"], "Baz bar FOO.txt", f"{TODAY}_BAZ BAR FOO.txt", {}, 0),
        ([], "Baz bar FOO jan 11 2004", "2004-01-11_BazBarFoo", {"transform_case": "CAMELCASE"}, 0),
        ([], "Baz bar FOO.txt", f"{TODAY}_baz bar foo.txt", {"transform_case": "lower"}, 0),
        ([], "Baz bar FOO.txt", f"{TODAY}_Baz bar foo.txt", {"transform_case": "sentence"}, 0),
        ([], "Baz bar FOO.txt", f"{TODAY}_BAZ BAR FOO.txt", {"transform_case": "upper"}, 0),
        ([], "$#@FOO(#BAR)*&^.txt", f"{TODAY}_FOOBAR.txt", {}, 0),
        (
            ["--split-words"],
            "FooBar.txt",
            f"{TODAY}_FooBar.txt",
            {"match_case_list": ["FooBar"]},
            0,
        ),
        ([], "Baz bar.txt", f"{TODAY}_Baz.txt", {"stopwords": ["bar"]}, 0),
        (["--keep-stopwords"], "Baz bar.txt", f"{TODAY}_Baz bar.txt", {"stopwords": ["bar"]}, 0),
        ([], ".dotfile_test.txt", "No files to process", {}, 1),
        ([], ".dotfile_test.txt", ".dotfile.txt", {"ignore_dotfiles": "false"}, 0),
        (
            ["--date-format", "%Y"],
            "foo bar baz.txt",
            f"{date.today().strftime('%Y')}-foo-bar-baz.txt",
            {"separator": "dash"},
            0,
        ),
        (
            [],
            "foo bar baz.txt",
            f"{date.today().strftime('%Y')}-foo-bar-baz.txt",
            {"separator": "dash", "date_format": "%Y"},
            0,
        ),
        (["--split-words"], "FooBar Baz.txt", "Foo Bar Baz.txt", {"date_format": ""}, 0),
        (["--case", "LOWER"], "Foo Bar Baz.txt", "foo bar baz_1.txt", {"date_format": ""}, 0),
        (
            ["--case", "LOWER", "--overwrite"],
            "Foo Bar Baz.txt",
            "foo bar baz.txt",
            {"date_format": ""},
            0,
        ),
        (["--sep", "DASH"], "foo bar baz.TAR.gz", f"{TODAY}-foo-bar-baz.tar.gz", {}, 0),
    ],
)
def test_filename_cleaning(
    mock_config,
    tmp_path,
    create_file,
    exit_code,
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
    assert result.exit_code == exit_code
    if exit_code != 0:
        assert expected_file in strip_ansi(result.output)
    else:
        assert f"{filename} -> {expected_file}" in strip_ansi(result.output)
        assert (tmp_path / expected_file).exists()
        if "--overwrite" not in args:
            assert not original_file.exists()


@pytest.mark.parametrize(
    ("args"),
    [
        (["--project=test", "--no-clean"]),
        (["--project=test", "--no-clean", "--dry-run"]),
    ],
)
def test_jdfile_project(mock_config, mock_project, debug, args):
    """Test processing a jdfile project with not duplicate folders."""
    original_files_path, project_path = mock_project

    num_original_files = len(list(original_files_path.rglob("*")))

    override_config = {
        "date_format": "",  # Do not add dates to filenames
    }

    with AppConfig.change_config_sources(mock_config(**override_config)):
        result = runner.invoke(app, [str(original_files_path), *args])

    debug("result", strip_ansi(result.output))

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


@pytest.mark.parametrize(
    ("args", "exit_code", "expected_result"),
    [
        (
            ["--project=not_a_project", "--no-clean", "--dry-run"],
            0,
            "Project not found: not_a_project",
        ),
        (["--project=not_a_project", "--tree"], 1, "Project not found: not_a_project"),
        (["--tree"], 1, "No project specified"),
    ],
)
def test_validate_project(mock_config, mock_project, debug, args, exit_code, expected_result):
    """Test processing a jdfile project with not duplicate folders."""
    original_files_path, _ = mock_project

    override_config = {
        "date_format": "",  # Do not add dates to filenames
    }

    with AppConfig.change_config_sources(mock_config(**override_config)):
        result = runner.invoke(app, [str(original_files_path), *args])

    debug("result", strip_ansi(result.output))

    assert result.exit_code == exit_code
    assert expected_result in strip_ansi(result.output)
