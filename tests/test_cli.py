# type: ignore
"""Test filemanager CLI."""
import re

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


def test_help():
    """Test printing helo and then exiting."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert result.output == Regex(r"Usage: \w+ \[OPTIONS\] \[FILES\]\.\.")


def test_project_not_found(
    test_project,
):
    """Test not finding a specified project."""
    config, project_root = test_project

    result = runner.invoke(
        app,
        [f"--config-file={config}", "--organize=no_project", "--tree"],
    )
    assert result.exit_code == 1
    assert result.stdout == Regex(
        r"ERROR +\| 'no_project' is not defined in the config file.*Aborted", re.DOTALL
    )


def test_config_not_found(
    test_project,
):
    """Test not finding specified config file."""
    config, project_root = test_project

    result = runner.invoke(
        app,
        ["--config-file=no-config", "--organize=no_project", "--tree"],
    )
    assert result.exit_code == 2
    assert result.stdout == Regex(r"File 'no-config' does not exist", re.DOTALL)
