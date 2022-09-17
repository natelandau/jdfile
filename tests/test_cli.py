# type: ignore
"""Test filemanager CLI."""
import re
from pathlib import Path

from typer.testing import CliRunner

from filemanager.cli import app
from tests.helpers import Regex

runner = CliRunner()


def test_version():
    """Test printing version and then exiting."""
    result = runner.invoke(app, ["-n", "--version"])
    assert result.exit_code == 0
    assert result.output == Regex(r"filemanager version: \d+\.\d+\.\d+$")


def test_no_files_specified():
    """Test no files specified."""
    result = runner.invoke(app, ["-n"])
    assert result.exit_code == 1
    assert result.output == "ERROR    | No files were specified\n"


def test_no_changes_recommended(test_files):
    """Test no changes recommended does not ask for input."""
    result = runner.invoke(app, ["-n", str(test_files[24])])
    assert result.exit_code == 0
    assert result.output == Regex(r"INFO     \| TESTFILE\.txt -> No changes")


def test_filenames_in_dryrun(test_files, tmp_path):
    """Test clean command."""
    result = runner.invoke(
        app,
        ["-n", "--force", str(test_files[3])],
    )
    assert result.exit_code == 0
    assert (
        result.output
        == "DRYRUN   | 2022-08-28 a_FIne &(filename).txt -> 2022-08-28 FIne filename.txt\n"
    )

    # Test abort on selecting Quit
    result = runner.invoke(
        app,
        ["-n", "--sep", "space", str(test_files[7])],
        input="q\n",
    )
    assert result.exit_code == 1
    assert result.output == Regex(r"Aborted\.")

    # test commit a single file
    result = runner.invoke(
        app,
        ["-n", "--sep", "space", str(test_files[7])],
        input="C\n",
    )
    assert result.exit_code == 0
    assert result.output == Regex(
        r"DRYRUN   \| __stripped.*separators--\.txt.*->.*stripped.*separators\.txt"
    )

    # test entire directory
    originals = Path(tmp_path / "originals")
    result = runner.invoke(app, ["-n", "--sep", "space", str(originals)], input="C\n")
    assert result.output == Regex(r"╭───────────────┬───────────────────────────────────────────╮")
    assert result.output == Regex(r"Iterate over all 26 changes")
    assert result.output == Regex(r"DRYRUN   \| two-extensions\.TAR\.gz.*->.*extensions\.tar\.gz")
    assert result.exit_code == 0


def test_file_iteration(test_files):
    """Test iterating over files."""
    # Abort on an iterated item
    result = runner.invoke(
        app,
        ["-nr", "--sep", "dash", "--case", "upper", str(test_files[14]), str(test_files[24])],
        input="I\nQ\n",
    )
    assert result.exit_code == 1
    assert result.output == Regex(r"Aborted.")

    # Commit all changes
    result = runner.invoke(
        app,
        ["-nr", "--sep", "dash", "--case", "upper", str(test_files[14]), str(test_files[24])],
        input="I\nC\nC\n",
    )
    assert result.exit_code == 0
    assert result.output == Regex(
        r"DRYRUN   \| month-DD-YYYY file january 01 2016\.txt.*->.*MONTH-DD-YYYY-FILE\.txt",
        re.DOTALL,
    )
    assert result.output == Regex(
        r"INFO     \| TESTFILE\.txt.*->.*No changes",
        re.DOTALL,
    )

    # Skip an item
    result = runner.invoke(
        app,
        ["-nr", "--sep", "dash", "--case", "upper", str(test_files[14]), str(test_files[24])],
        input="i\nS\nC\n",
    )
    assert result.exit_code == 0
    assert result.output != Regex(r"->.*MONTH-DD-YYYY-FILE\.txt", re.DOTALL | re.MULTILINE)
    assert result.output == Regex(
        r"INFO     \| TESTFILE\.txt.*->.*No changes",
        re.DOTALL,
    )

    # Skip all items
    result = runner.invoke(
        app,
        ["-nr", "--sep", "dash", "--case", "upper", str(test_files[14]), str(test_files[24])],
        input="I\ns\ns\n",
    )
    assert result.exit_code == 0
    assert result.output != Regex(r"->.*MONTH-DD-YYYY-FILE\.txt", re.DOTALL | re.MULTILINE)
    assert result.output != Regex(
        r"INFO     \| TESTFILE\.txt.*->.*No changes",
        re.DOTALL,
    )
    assert result.output == Regex(r"INFO     \| No files to commit")


def test_clean_permutations(test_files):
    """Test clean command."""
    result = runner.invoke(
        app,
        ["-nd", "--diff", "--sep", "underscore", "--case", "title", str(test_files[14])],
        input="C\n",
    )
    assert result.exit_code == 0
    assert result.output == Regex(
        r".*month-DD-YYYY file january 01 2016\.txt.*->.*2016-01-01_Month_Dd_Yyyy_File\.txt",
        re.I | re.DOTALL,
    )

    result = runner.invoke(
        app, ["-nr", "--sep", "dash", "--case", "upper", str(test_files[14])], input="C\n"
    )
    assert result.exit_code == 0
    assert result.output == Regex(
        r".*month-DD-YYYY file january 01 2016.txt.*->.*MONTH-DD-YYYY-FILE.txt", re.I | re.DOTALL
    )

    result = runner.invoke(app, ["-n", "--no-clean", str(test_files[19])], input="C\n")
    assert result.exit_code == 0
    assert result.output == Regex(r"INFO     \| specialChars\(@#\$\)-&\*\.txt.*->.*No.*changes")

    result = runner.invoke(app, ["-nd", "--sep", "dash", str(test_files[8])], input="C\n")
    assert result.exit_code == 0
    assert result.output == Regex(r"ALLCAPS\.txt -> \d{4}-\d{2}-\d{2}-ALLCAPS\.txt")


def test_writing_files(test_files, tmp_path):
    """Test writing files."""
    result = runner.invoke(app, ["--overwrite", str(test_files[21])], input="C\n")
    assert result.exit_code == 0
    assert result.output == Regex(r"testfile\.txt -> No change")
    assert Path(tmp_path / "originals" / "testfile.txt").exists()

    result = runner.invoke(
        app, ["--case", "lower", "--sep", "space", str(test_files[24])], input="C\n"
    )
    assert result.exit_code == 0
    assert result.output == Regex(r"TESTFILE\.txt -> testfile 2\.txt")
    assert Path(tmp_path / "originals" / "testfile 2.txt").exists()
