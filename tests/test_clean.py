# type: ignore
"""Test cleaning filenames."""
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from jdfile.cli import app
from tests.helpers import Regex

runner = CliRunner()


@pytest.fixture()
def create_file(tmp_path, filename):
    """Fixture for creating a file.

    Args:
        tmp_path: (Path) Temporary path to create the test file.
        filename: (str) Filename to create.

    Returns:
        file: (Path) Path to the created file.

    """
    originals = tmp_path / "originals"
    originals.mkdir(parents=True, exist_ok=True)
    Path(originals / filename).touch()
    return Path(originals / filename)


@pytest.mark.parametrize(
    ("file_num", "command", "expected"),
    [
        (  # lowercase
            1,
            ["-n", "--force", "--case=lower"],
            r"DRYRUN   \| 2021-06-08_some_TEST_file\.txt -> 2021-06-08 file\.txt",
        ),
        (  # uppercase
            1,
            ["-n", "--force", "--case=upper"],
            r"DRYRUN   \| 2021-06-08_some_TEST_file\.txt -> 2021-06-08 FILE\.txt",
        ),
        (  # separator space
            15,
            ["-n", "--force", "--sep=space"],
            r"DRYRUN +\| Multiple---separators  are___stripped\.txt.*->.*Multiple.*separators.*stripped\.txt",
        ),
        (  # separator underscore
            15,
            ["-n", "--force", "--sep=underscore"],
            r"DRYRUN +\| Multiple---separators  are___stripped\.txt.*->.*Multiple_separators_stripped\.txt",
        ),
        (  # separator dash
            15,
            ["-n", "--force", "--sep=dash"],
            r"DRYRUN +\| Multiple---separators  are___stripped\.txt.*->.*Multiple-separators-stripped\.txt",
        ),
        (  # remove date
            1,
            ["-n", "-r", "--force", "--case=lower"],
            r"DRYRUN +\| 2021-06-08_some_TEST_file\.txt -> file\.txt",
        ),
        (  # separator add-date
            15,
            ["-n", "--force", "--sep=dash", "--add-date"],
            r"DRYRUN +\| Multiple---separators  are___stripped\.txt.*->.*\d{4}-\d{2}-\d{2}-Multiple-separators-stripped\.txt",
        ),
        (  # separator add-date with custom format
            15,
            ["-n", "--force", "--sep=space", "--add-date", "--date-format=%d.%m.%Y"],
            r"DRYRUN +\| Multiple---separators  are___stripped\.txt.*->.*\d{2}\.\d{2}\.\d{4}.*Multiple.*separators.*stripped\.txt",
        ),
        (  # clean special characters
            19,
            ["-n", "--force"],
            r"DRYRUN +\| specialChars\(@#\$\)-&\*\.txt -> specialChars\.txt",
        ),
        (  # do not clean special characters
            19,
            ["-n", "--force", "--no-clean"],
            r"INFO +\| specialChars\(@#\$\)-&\*\.txt -> No changes",
        ),
        (  # splitting words
            27,
            ["-n", "--force", "--case=title", "--split-words"],
            r"->.*Quick.*Brown.*Fox.*Camel.*Case.*Words\.txt",
        ),
        (  # dotfiles stay dotfiles, suffixes are cleaned
            26,
            ["-n", "--force"],
            r"DRYRUN +\| \.dotfile\.JPEG\.ZIP\.gzip.*->.*\.dotfile\.jpg\.zip\.gzip",
        ),
        (  # correctly find and move dates to start of filename
            13,
            ["-n", "--force", "--add-date"],
            r"DRYRUN +\| month-DD-YY March 21,.*2002.*test\.txt.*->.*2002-03-21.*month-DD-YY\.txt",
        ),
    ],
)
def test_cleaning_filenames(test_files, file_num, command, expected):
    """Test permutations."""
    whole_command = [*command, str(test_files[file_num])]
    result = runner.invoke(
        app,
        whole_command,
    )
    assert result.exit_code == 0
    assert result.output == Regex(expected, re.DOTALL)


@pytest.mark.parametrize(
    ("file1", "file2", "command", "expected1", "expected2"),
    [
        (  # separator space
            15,
            19,
            ["-n", "--force", "--sep=space"],
            r"DRYRUN +\| Multiple---separators  are___stripped\.txt.*->.*Multiple.*separators.*stripped\.txt",
            r"DRYRUN +\| specialChars\(@#\$\)-&\*\.txt.*->.*specialChars\.txt",
        ),
        (  # all files correct
            9,
            25,
            ["-n", "--force", "--case=lower"],
            r"INFO +\| lowercase\.txt -> No changes",
            r"INFO +\| \.dotfile\.txt -> No changes",
        ),
        (  # all files correct
            9,
            25,
            ["-n", "--filter-correct", "--case=lower"],
            r"NOTICE +\| All files are already correct",
            r"NOTICE +\| All files are already correct",
        ),
    ],
)
def test_cleaning_multiple_files(test_files, file1, file2, command, expected1, expected2):
    """Test cleaning multiple files."""
    whole_command = [*command, str(test_files[file1])] + [str(test_files[file2])]
    result = runner.invoke(
        app,
        whole_command,
    )
    assert result.exit_code == 0
    assert result.output == Regex(expected1, re.DOTALL)
    assert result.output == Regex(expected2, re.DOTALL)


@pytest.mark.parametrize(
    ("file1", "file2", "command", "expected1", "expected2", "user_input", "exit_code"),
    [
        (  # Two files with commit
            15,
            19,
            ["-n", "--sep=space"],
            r"DRYRUN +\| Multiple---separators  are___stripped\.txt.*->.*Multiple.*separators.*stripped\.txt",
            r"╭─+┬─+─╮.*│ +File: │ Multiple---separators  are___stripped.txt +\│.*│ New Filename: │ Multiple separators stripped.txt +\│.*Commit all \d changes",
            "C\n",
            0,
        ),
        (  # two files with quit
            15,
            19,
            ["-n", "--sep=space"],
            r"╭─+┬─+─╮.*│ +File: │ Multiple---separators  are___stripped.txt +\│.*│ New Filename: │ Multiple separators stripped.txt +\│.*Commit all \d changes",
            r"Aborted\.",
            "q\n",
            1,
        ),
        (  # iterate and skip all
            15,
            19,
            ["-n", "--sep=space"],
            r"╭─+┬─+─╮.*│ +File: │ Multiple---separators  are___stripped.txt +\│.*│ New Filename: │ Multiple separators stripped.txt +\│.*Commit all \d changes.*Processing 1 of 2 files.*Processing 2 of 2 files",
            r"INFO +\| Multiple---separators  are___stripped\.txt.*->.*No changes.*INFO +\| specialChars\(@#\$\)-&\*\.txt.*->.*No changes",
            "I\nS\nS\n",
            0,
        ),
        (  # iterate and skip one with show-diff
            15,
            19,
            ["-n", "--sep=space", "--case=upper", "--diff"],
            r"│ +File: │ Multiple---separators  are___stripped.txt +│.*│ *New Filename: │ MULTIPLE SEPARATORS.*STRIPPED\.txt +│.*│ +Diff: │ MULTIPLEultiple---separators.*SEPARATORS.*Diff: │ SPEspecialCIALCHARShars\(@#\$\)-&\*\.txt",
            r"INFO +\| Multiple---separators  are___stripped\.txt.*->.*No changes.*DRYRUN +\| specialChars\(@#\$\)-&\*\.txt.*->.*SPECIALCHARS\.txt",
            "I\nS\nC\n",
            0,
        ),
        (  # iterate and quit
            15,
            19,
            ["-n", "--sep=space", "--case=upper", "--diff"],
            r"│ +File: │ Multiple---separators  are___stripped.txt +│.*│ *New Filename: │ MULTIPLE SEPARATORS.*STRIPPED\.txt +│.*│ +Diff: │ MULTIPLEultiple---separators.*SEPARATORS.*Diff: │ SPEspecialCIALCHARShars\(@#\$\)-&\*\.txt",
            r"Aborted",
            "I\nS\nq\n",
            1,
        ),
        (  # one file with quit
            15,
            None,
            ["-n", "--sep=space", "--case=upper", "--diff"],
            r"╭─+┬─+─╮",
            r"Aborted",
            "Q\n",
            1,
        ),
        (  # one file with commit
            15,
            None,
            ["-n", "--sep=space", "--case=upper", "--diff"],
            r"╭─+┬─+─╮",
            r"DRYRUN +\| Multiple---separators.*are___stripped\.txt.*->.*MULTIPLE.*SEPARATORS.*STRIPPED\.txt",
            "C\n",
            0,
        ),
    ],
)
def test_table_display(
    test_files, file1, file2, command, expected1, expected2, user_input, exit_code
):
    """Test cleaning multiple files."""
    if file2 is None:
        whole_command = [*command, str(test_files[file1])]
    else:
        whole_command = [*command, str(test_files[file1])] + [str(test_files[file2])]

    result = runner.invoke(
        app,
        whole_command,
        input=user_input,
    )
    assert result.exit_code == exit_code
    assert result.output == Regex(expected1, re.DOTALL)
    assert result.output == Regex(expected2, re.DOTALL)


def test_entire_directory(tmp_path, test_files):
    """Test cleaning an entire directory."""
    originals = tmp_path / "originals"

    # Test depth 1
    result = runner.invoke(
        app,
        ["-n", "--force", str(originals)],
    )
    assert result.exit_code == 0
    assert result.output == Regex(
        r"INFO +\| disk_image\.dmg -> No change",
        re.DOTALL,
    )
    assert result.output == Regex(
        r"DRYRUN +\| specialChars\(@#\$\)-&\*\.txt.*->.*specialChars\.txt",
        re.DOTALL,
    )
    assert result.output == Regex(
        r"DRYRUN +\| __stripped separators--\.txt.*->.*stripped separators\.txt",
        re.DOTALL,
    )

    # test no files
    result = runner.invoke(
        app,
        ["-n", "--force", str(Path(tmp_path))],
    )
    assert result.exit_code == 1
    assert result.output == Regex(r"ERROR +\| No files were found")

    # Test depth 2
    result = runner.invoke(
        app,
        ["-n", "--force", "--depth=2", str(Path(tmp_path))],
    )
    assert result.exit_code == 0
    assert result.output == Regex(
        r"INFO +\| disk_image\.dmg -> No change",
        re.DOTALL,
    )
    assert result.output == Regex(
        r"DRYRUN +\| specialChars\(@#\$\)-&\*\.txt.*->.*specialChars\.txt",
        re.DOTALL,
    )
    assert result.output == Regex(
        r"DRYRUN +\| __stripped separators--\.txt.*->.*stripped separators\.txt",
        re.DOTALL,
    )
