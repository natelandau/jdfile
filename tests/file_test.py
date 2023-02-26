# type: ignore
"""Tests for the file module."""

from datetime import date
from pathlib import Path

import pytest
from rich import print

from jdfile._config.config import Config
from jdfile.models.file import File
from jdfile.models.project import Project


@pytest.mark.parametrize(
    (
        "filename",
        "config_clean",
        "expected_stem",
        "expected_suffixes",
        "is_dotfile",
        "date_format",
        "expected_diff",
    ),
    [
        ("foo bar.txt", True, "foo bar", [".txt"], False, None, "foo bar.txt"),
        ("I am foo bar", True, "foo bar", [], False, None, "[red reverse]I am [/]foo bar"),
        (".gitignore", True, ".gitignore", [], True, None, ".gitignore"),
        (
            "foo.JPEG.gz.tar",
            True,
            "foo",
            [".jpg", ".gz", ".tar"],
            False,
            None,
            "foo.[green reverse]jpg[/][red reverse]JPEG[/].gz.tar",
        ),
        (
            "10-13-2022 foo bar.txt",
            True,
            "10 13, 2022_foo bar",
            [".txt"],
            False,
            "%m %d, %Y",
            "10[green reverse] [/][red reverse]-[/]13[green reverse], [/][red reverse]-[/]2022[green reverse]_[/][red reverse] [/]foo bar.txt",
        ),
        (
            "bazJan12022_foo_bar.txt",
            True,
            "01 01, 2022_baz_foo_bar",
            [".txt"],
            False,
            "%m %d, %Y",
            "[green reverse]0[/][red reverse]bazJan[/]1[green reverse] 01, [/]2022[green reverse]_baz[/]_foo_bar.txt",
        ),
        (
            "Jan12022_foo_bar.txt",
            False,
            "2022-01-01__foo_bar",
            [".txt"],
            False,
            "%Y-%m-%d",
            "[red reverse]Jan1[/]2022[green reverse]-01-01_[/]_foo_bar.txt",
        ),
        (
            "I am foo bar",
            False,
            f"{date.today().strftime('%Y-%m-%d')}_I am foo bar",
            [],
            False,
            "%Y-%m-%d",
            f"[green reverse]{date.today().strftime('%Y-%m-%d')}_[/]I am foo bar",
        ),
    ],
)
def test_files(
    tmp_path,
    filename,
    config_clean,
    expected_stem,
    expected_suffixes,
    is_dotfile,
    date_format,
    expected_diff,
    capsys,
):
    """Test creating a File object."""
    config = Config()
    new_file = Path(tmp_path / filename)
    new_file.touch()
    config.clean = config_clean
    config.date_format = date_format
    config.strip_stopwords = True
    file = File(path=new_file, config=config)
    assert file.name == filename
    assert file.new_stem == expected_stem
    assert file.new_suffixes == expected_suffixes
    assert file.is_dotfile is is_dotfile
    assert file.print_diff() == f"{expected_diff}"


def test_tokenize_stem(tmp_path):
    """Test tokenizing a stem."""
    config = Config()
    file_path = Path(tmp_path / "---I_am_a_ tokenizedString!(12345)#$.txt")
    file_path.touch()
    config.clean = False
    config.cli_terms = ["additional", "72", "27-01", "27"]
    file = File(path=file_path, config=config)
    assert file.tokenize_stem() == [
        "27",
        "27-01",
        "72",
        "additional",
        "am",
        "string12345",
        "tokenized",
    ]


def test_unique_filename(tmp_path):
    """Test creating a unique filename."""
    config = Config()
    Path(tmp_path / "bar.txt").touch()
    Path(tmp_path / "foo.txt").touch()
    Path(tmp_path / "foo_1.txt").touch()
    Path(tmp_path / "foo_2.txt").touch()
    Path(tmp_path / "foo_3.txt").touch()
    Path(tmp_path / "I_am_foo.txt").touch()
    config.clean = True
    config.strip_stopwords = True
    file = File(path=Path(tmp_path / "I_am_foo.txt"), config=config)
    assert file.new_stem == "foo"
    file.unique_name()
    assert file.new_stem == "foo_4"

    file2 = File(path=Path(tmp_path / "bar.txt"), config=config)
    Path(tmp_path / "bar.txt").unlink()
    assert file2.new_stem == "bar"
    file2.unique_name()
    assert file2.new_stem == "bar"


def commit_respects_dryrun(tmp_path, capsys):
    """Test committing a unique filename with dryrun."""
    config = Config()
    config.dry_run = True
    Path(tmp_path / "bar.txt").touch()
    Path(tmp_path / "foo.txt").touch()
    Path(tmp_path / "foo_1.txt").touch()
    Path(tmp_path / "foo_2.txt").touch()
    Path(tmp_path / "foo_3.txt").touch()
    Path(tmp_path / "I_am_foo.txt").touch()
    config.clean = True
    config.strip_stopwords = True
    file = File(path=Path(tmp_path / "I_am_foo.txt"), config=config)
    assert file.new_stem == "foo"
    file.unique_name()
    assert file.new_stem == "foo_4"
    assert file.commit() is True
    assert Path(tmp_path / "I_am_foo.txt").exists() is True
    assert Path(tmp_path / "foo_4.txt").exists() is False
    captured = capsys.readouterr()
    assert "DRYRUN" in captured.out


def test_commit_unique_name(tmp_path):
    """Test committing a unique filename."""
    config = Config()
    Path(tmp_path / "bar.txt").touch()
    Path(tmp_path / "foo.txt").touch()
    Path(tmp_path / "foo_1.txt").touch()
    Path(tmp_path / "foo_2.txt").touch()
    Path(tmp_path / "foo_3.txt").touch()
    Path(tmp_path / "I_am_foo.txt").touch()
    config.clean = True
    config.strip_stopwords = True
    file = File(path=Path(tmp_path / "I_am_foo.txt"), config=config)
    assert file.new_stem == "foo"
    file.unique_name()
    assert file.new_stem == "foo_4"
    assert file.commit() is True
    assert Path(tmp_path / "I_am_foo.txt").exists() is False
    assert Path(tmp_path / "foo_4.txt").exists() is True


def test_commit_overwrite_original(tmp_path):
    """Test overwriting a file."""
    config = Config()
    config.overwrite_existing = True
    Path(tmp_path / "bar.txt").touch()
    Path(tmp_path / "foo.txt").touch()
    Path(tmp_path / "foo_1.txt").touch()
    Path(tmp_path / "foo_2.txt").touch()
    Path(tmp_path / "foo_3.txt").touch()
    Path(tmp_path / "I_am_foo.txt").touch()
    config.clean = True
    config.strip_stopwords = True
    file = File(path=Path(tmp_path / "I_am_foo.txt"), config=config)
    assert file.new_stem == "foo"
    assert file.commit() is True
    assert file.new_stem == "foo"
    assert Path(tmp_path / "I_am_foo.txt").exists() is False
    assert Path(tmp_path / "foo_4.txt").exists() is False
    assert Path(tmp_path / "foo.txt").exists() is True


def test_no_organize(config1_project):
    """Ensure no organizing happens when organize is False."""
    config, original_files_path, project_path = config1_project
    project = Project(config)
    fixture = Path(original_files_path / "foobar(one).txt")
    fixture.touch()
    config.clean = True
    config.organize = False
    config.cli_terms = ["11.01"]
    file = File(path=fixture, config=config, project=project)
    assert file.commit() is True
    assert Path(original_files_path / "foobarone.txt").exists() is True
    assert file.parent == file.new_parent
    assert Path(project_path / "10-19 foo/11 bar/11.01 foo/foobarone.txt").exists() is False


def test_new_path_by_number(config1_project):
    """Test creating a File object from a project."""
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = True
    config.cli_terms = ["11.01"]
    file = File(path=Path(original_files_path / "foobar.txt"), config=config, project=project)
    assert file.commit() is True
    assert Path(original_files_path / "foobar.txt").exists() is False
    assert Path(project_path / "10-19 foo/11 bar/11.01 foo/foobar.txt").exists() is True


def test_new_path_no_match(config1_project):
    """Test creating a File object from a project without term matching a directory."""
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = True
    config.cli_terms = []
    file = File(path=Path(original_files_path / ".dotfile"), config=config, project=project)
    assert file.commit() is False
    assert file.skip_file is True
    assert Path(original_files_path / ".dotfile").exists() is True
    assert file.parent == file.new_parent


def test_new_path_by_terms_single_match(config1_project):
    """Test creating a File object from a project with a single matching term."""
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = True
    config.cli_terms = []
    file = File(path=Path(original_files_path / "qux.txt"), config=config, project=project)
    assert file.commit() is True
    assert file.skip_file is False
    assert Path(original_files_path / "qux.txt").exists() is False
    assert Path(project_path / "10-19 foo/12 baz/12.03 QUX/qux.txt").exists() is True


def test_new_path_by_terms_multiple_matches_skip(config1_project, mocker):
    """Test creating a File object from a project with multiple matching terms."""
    mocker.patch(
        "jdfile.models.file.select_folder",
        return_value="skip",
    )

    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = False
    config.cli_terms = []
    file = File(
        path=Path(original_files_path / "foo_Mar19_1974_bar.txt"), config=config, project=project
    )
    assert file.skip_file is True
    assert file.parent == file.new_parent
    assert file.commit() is False
    assert Path(original_files_path / "foo_Mar19_1974_bar.txt").exists() is True


def test_new_path_by_terms_multiple_selection(config1_project, mocker):
    """Test creating a File object from a project with multiple matching terms."""
    config, original_files_path, project_path = config1_project

    mocker.patch(
        "jdfile.models.file.select_folder",
        return_value=Path(project_path / "20-29_bar/21_bar"),
    )

    project = Project(config)
    config.clean = True
    config.cli_terms = []
    print("\n---------------------------------------")
    file = File(
        path=Path(original_files_path / "foo_Mar19_1974_bar.txt"), config=config, project=project
    )
    assert file.commit() is True
    assert Path(original_files_path / "foo_Mar19_1974_bar.txt").exists() is False
    assert Path(project_path / "20-29_bar/21_bar/foo_Mar19_1974_bar.txt").exists() is True
