# type: ignore
"""Test filemanager CLI."""
import re

from typer.testing import CliRunner

from filemanager.cli import app
from tests.helpers import Regex

runner = CliRunner()


def test_filenames_in_dryrun(test_files):
    """Test clean command."""
    result = runner.invoke(app, ["-cn", str(test_files[3])])
    assert result.exit_code == 0
    assert (
        result.output
        == "DRYRUN   | 2022-08-28 a_fine &(filename).txt -> 2022-08-28 a_fine filename.txt\n"
    )

    result = runner.invoke(app, ["-cn", "-s", "space", str(test_files[7])])
    assert result.exit_code == 0
    assert result.output == "DRYRUN   | __stripped separators--.txt -> stripped separators.txt\n"

    result = runner.invoke(
        app, ["-cnd", "-s", "underscore", "--case", "title", str(test_files[14])]
    )
    assert result.exit_code == 0
    assert result.output == Regex(
        r".*month-DD-YYYY file january 01 2016\.txt.*->.*2016-01-01_Month_Dd_Yyyy_File\.txt",
        re.I | re.DOTALL,
    )

    result = runner.invoke(app, ["-cnr", "-s", "dash", "--case", "upper", str(test_files[14])])
    assert result.exit_code == 0
    assert result.output == Regex(
        r".*month-DD-YYYY file january 01 2016.txt.*->.*MONTH-DD-YYYY-FILE.txt", re.I | re.DOTALL
    )

    result = runner.invoke(app, ["-n", "-s", "dash", "--case", "lower", str(test_files[19])])
    assert result.exit_code == 0
    assert result.output == "DRYRUN   | specialChars(@#$)-&*.txt -> specialchars(@#$)-&*.txt\n"

    result = runner.invoke(app, ["-nd", "-s", "dash", str(test_files[8])])
    assert result.exit_code == 0
    assert result.output == Regex(r"ALLCAPS\.txt -> \d{4}-\d{2}-\d{2}-ALLCAPS\.txt")
