# type: ignore
"""Test organizing files into Johnny Decimal Folders."""
import re
from pathlib import Path

from typer.testing import CliRunner

from filemanager.cli import app
from tests.helpers import Regex

runner = CliRunner()


def test_find_no_folder(
    test_project,
    test_files,
    tmp_path,
):
    """Test not matching a folder."""
    config, project_root = test_project

    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "-n",
            "--force",
            "--organize=test",
            "--no-syns",
            str(test_files[8]),
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == Regex(
        r"WARNING +\| Skipping ALLCAPS\.txt.*\(No folders matched\).*INFO +\| ALLCAPS\.txt.*->.*No.*changes",
        re.DOTALL,
    )


def test_find_single_folder(test_project, test_files):
    """Test finding a single matching folder."""
    config, project_root = test_project

    # Match on term in .filemanager
    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "-n",
            "--force",
            "--organize=test",
            "--no-syns",
            str(test_files[31]),
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == Regex(
        r".*quick brown banana\.txt.*->.*/.*/project/10-19.*area1/11.*category1/11.02.*subcategory2/quick.*brown.*banana.txt",
        re.DOTALL,
    )

    # Match on foldername
    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "-n",
            "--force",
            "--organize=test",
            "--no-syns",
            "--sep=underscore",
            str(test_files[29]),
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == Regex(
        r"DRYRUN +\| quick_project_and_foxes\.txt.-*>.*/.*/project/30-39.*project.*plans/quick_project_foxes\.txt",
        re.DOTALL,
    )


def test_find_multiple_folders(test_project, test_files):
    """Test matching multiple folders."""
    config, project_root = test_project

    # Match multiple folders and select first with --force
    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "-n",
            "--force",
            "--organize=test",
            "--no-syns",
            str(test_files[30]),
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == Regex(
        r".*/.*/project/10-19.*area1/11.*category1/11.01.*subcategory1/quick.*brown.*fruit\.txt",
        re.DOTALL,
    )

    # Match multiple folders, show table and quit
    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "-n",
            "--organize=test",
            "--no-syns",
            str(test_files[30]),
        ],
        input="q\n",
    )
    assert result.exit_code == 1
    assert result.stdout == Regex(
        r"1.*subcategory1.*11.01.*/area1/category1/subcategory1.*fruit",
        re.DOTALL,
    )
    assert result.stdout == Regex(
        r"2.*subcategory2.*11.02.*/area1/category1/subcategory2.*fruit",
        re.DOTALL,
    )
    assert result.stdout == Regex(
        r"Aborted",
        re.DOTALL,
    )

    # Match multiple folders, show table and select none of the above
    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "-n",
            "--organize=test",
            "--no-syns",
            str(test_files[30]),
        ],
        input="N\nC\n",
    )
    assert result.exit_code == 0
    assert result.stdout == Regex(
        r"WARNING +\|.*\.txt.*\(No.*folder.*selected\)",
        re.DOTALL,
    )
    assert result.stdout == Regex(
        r"INFO +\| quick brown apricot and.*fruit\.txt.*->.*No.*changes",
        re.DOTALL,
    )

    # Match multiple folders, show table and select second option
    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "-n",
            "--organize=test",
            "--no-syns",
            str(test_files[30]),
        ],
        input="2\nC\n",
    )
    assert result.exit_code == 0
    assert result.stdout == Regex(
        r"DRYRUN +\| quick.*brown.*apricot.*and.*fruit\.txt.*->.*/.*/project/10-19.*area1/11.*category1/11.02.*subcategory2/quick.*brown.*fruit\.txt",
        re.DOTALL,
    )


def test_specify_a_folder(test_project, test_files):
    """Test specifying a folder."""
    config, project_root = test_project

    # Folder does not exist
    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "--force",
            "--organize=test",
            "--no-syns",
            "--number=48.03",
            str(test_files[8]),
        ],
    )
    assert result.exit_code == 1
    assert result.stdout == Regex(r"ERROR +\| No folder found matching: 48\.03")

    # Folder Exists
    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "--force",
            "--organize=test",
            "--no-syns",
            "--number=12.03",
            str(test_files[8]),
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == Regex(
        r"SUCCESS +\| ALLCAPS\.txt.*->.*/.*/project/10-19.*area1/12.*category2/12.03.*subcategory3/ALLCAPS\.txt",
        re.DOTALL,
    )


def test_commit_organize(
    test_project,
    test_files,
    tmp_path,
):
    """Test committing changes."""
    config, project_root = test_project

    result = runner.invoke(
        app,
        [
            f"--config-file={config}",
            "--force",
            "--organize=test",
            "--no-syns",
            str(test_files[31]),
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == Regex(
        r"SUCCESS +\| quick brown banana\.txt.*->.*/.*/project/10-19.*area1/11.*category1/11.02.*subcategory2/quick.*brown.*banana.txt",
        re.DOTALL,
    )

    # Check that file was moved
    assert Path(
        project_root, "10-19 area1/11 category1/11.02 subcategory2/quick brown banana.txt"
    ).exists()
