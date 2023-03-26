# type: ignore
"""Tests for the file module."""

from datetime import date
from pathlib import Path

import pytest

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
):
    """Test creating a File object.

    GIVEN a filename, a config object, and expected values
    WHEN a File object is created
    THEN assert that the File object is created correctly.
    """
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
    assert file.organize_possible_folders == {}
    assert file.organize_skip is False


def test_tokenize_stem(tmp_path):
    """Test tokenizing a stem.

    GIVEN a filename with a stem
    WHEN the tokenize_stem method is called
    THEN assert that the stem is tokenized correctly into a list of strings.
    """
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
    """Test creating a unique filename.

    GIVEN a file in a directory with other files
    WHEN the unique_name method is called and a file exists with the same name
    THEN assert that the file is renamed to a unique name
    """
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
    """Test committing a unique filename with dryrun.

    GIVEN a file with changes
    WHEN the commit method is called with dryrun
    THEN assert that the file is not renamed or moved
    """
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
    """Test committing a unique filename.

    GIVEN a file in a directory with other files
    WHEN the unique_name method is called and a file exists with the same name
    THEN assert that the file is renamed to a unique name and the original file is deleted
    """
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
    """Test overwriting a file.

    GIVEN a file in a directory with other files
    WHEN the unique_name method is called and a file exists with the same name
    THEN assert that the new file overwrites the existing file
    """
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
    """Ensure no organizing happens when organize is False.

    GIVEN a file, a project, and a config with organize set to False
    WHEN the commit method is called
    THEN assert that the file is cleaned but not moved
    """
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
    """Test creating a File object from a project.

    GIVEN a file, a project, and a JD number matching a project folder
    WHEN the File object is created
    THEN assert that the new parent is the project folder with a matching JD number
    """
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = True
    config.cli_terms = ["11.01"]
    file = File(path=Path(original_files_path / "foobar.txt"), config=config, project=project)
    assert file.commit() is True
    assert Path(original_files_path / "foobar.txt").exists() is False
    assert Path(project_path / "10-19 foo/11 bar/11.01 foo/foobar.txt").exists() is True


def test_new_path_no_match(config1_project):
    """Test creating a File object from a project without term matching a directory.

    GIVEN a project, and a file
    WHEN the File object is created and not folders match terms in the file
    THEN assert that the file is flagged as "skipped" and new_parent is the same as parent
    """
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = True
    config.cli_terms = []
    file = File(path=Path(original_files_path / ".dotfile"), config=config, project=project)
    assert file.commit() is False
    assert file.organize_skip is True
    assert Path(original_files_path / ".dotfile").exists() is True
    assert file.parent == file.new_parent


def test_new_path_by_terms_single_match(config1_project):
    """Test creating a File object from a project with a single matching term.

    GIVEN a project, and a file
    WHEN the File object is created and a single folder matches a term in the file
    THEN assert that the file is moved to the single matching folder
    """
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = True
    config.cli_terms = []
    file = File(path=Path(original_files_path / "qux.txt"), config=config, project=project)
    assert file.commit() is True
    assert file.organize_skip is False
    assert Path(original_files_path / "qux.txt").exists() is False
    assert Path(project_path / "10-19 foo/12 baz/12.03 QUX/qux.txt").exists() is True


def test_new_path_by_terms_multiple_matches(config1_project):
    """Test creating a File object from a project with multiple matching terms.

    GIVEN a project, and a file
    WHEN the File object is created and multiple folders match terms in the file
    THEN assert that the possible folders are added to `organize_possible_folders` and `new_parent` is set to None

    """
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = False
    config.cli_terms = []
    file = File(path=Path(original_files_path / "waldo.txt"), config=config, project=project)
    assert file.new_parent is None
    assert len(file.organize_possible_folders) == 2
    assert "10-19 foo/12 baz/12.05 waldo" in file.organize_possible_folders
    assert "20-29_bar/20_foo/20.03_waldo" in file.organize_possible_folders


def test_select_new_parent_skip(config1_project, mocker):
    """Test creating a File object from a project with multiple matching terms.

    GIVEN a project, and a file is created and multiple folders match terms in the file
    WHEN the select_new_parent method is called and a user selects "skip"
    THEN assert that the file is flagged as "skipped" and new_parent is the same as parent
    """
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = False
    config.cli_terms = []
    file = File(path=Path(original_files_path / "waldo.txt"), config=config, project=project)
    assert file.new_parent is None

    mocker.patch("jdfile.models.file.select_folder", return_value="skip")
    file.select_new_parent()
    assert file.organize_skip is True
    assert file.new_parent == file.parent


def test_select_new_parent_select(config1_project, mocker):
    """Test creating a File object from a project with multiple matching terms.

    GIVEN a project, and a file is created and multiple folders match terms in the file
    WHEN the select_new_parent method is called and a user selects a folder
    THEN assert that `new_parent` is set to the selected folder
    """
    config, original_files_path, project_path = config1_project
    project = Project(config)
    config.clean = False
    config.cli_terms = []
    file = File(path=Path(original_files_path / "waldo.txt"), config=config, project=project)
    assert file.new_parent is None

    mocker.patch(
        "jdfile.models.file.select_folder",
        return_value=Path(project_path / "20-29_bar/20_foo/20.03_waldo"),
    )
    file.select_new_parent()
    assert file.new_parent != file.parent
    assert file.new_parent == Path(project_path / "20-29_bar/20_foo/20.03_waldo")
    assert file.organize_skip is False
