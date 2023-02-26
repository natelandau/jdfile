# type: ignore
"""Test the project models - Folder, Project."""

from pathlib import Path

from jdfile._config.config import Config
from jdfile.models.project import Project
from jdfile.utils.enums import FolderType
from tests.helpers import strip_ansi


def test_project_indexing(config1_project):
    """Test indexing project folders and creating File objects."""
    config, originals_path, project_path = config1_project

    project = Project(config=config)
    assert project.exists is True
    assert project.name == "fixture"
    assert project.path == project_path
    assert len(project.usable_folders) == 11
    assert project.usable_folders[0].name == "foo"
    assert project.usable_folders[0].number == "11.01"
    assert project.usable_folders[0].path == Path(project_path / "10-19 foo/11 bar/11.01 foo")
    assert project.usable_folders[0].terms == ["foo", "lorem"]
    assert project.usable_folders[0].area == Path(project_path / "10-19 foo")
    assert project.usable_folders[0].category == Path(project_path / "10-19 foo/11 bar")
    assert project.usable_folders[0].type == FolderType.SUBCATEGORY

    assert project.usable_folders[1].name == "bar"
    assert project.usable_folders[1].number == "11.02"
    assert project.usable_folders[1].path == Path(project_path / "10-19 foo/11 bar/11.02 bar")
    assert project.usable_folders[1].terms == ["bar"]
    assert project.usable_folders[1].area == Path(project_path / "10-19 foo")
    assert project.usable_folders[1].category == Path(project_path / "10-19 foo/11 bar")
    assert project.usable_folders[1].type == FolderType.SUBCATEGORY

    assert project.usable_folders[7].name == "foo_bar_baz"
    assert project.usable_folders[7].number == "20.01"
    assert project.usable_folders[7].path == Path(
        project_path / "20-29_bar/20_foo/20.01_foo_bar_baz"
    )
    assert project.usable_folders[7].terms == ["foo", "bar", "baz"]
    assert project.usable_folders[7].area == Path(project_path / "20-29_bar")
    assert project.usable_folders[7].category == Path(project_path / "20-29_bar/20_foo")
    assert project.usable_folders[7].type == FolderType.SUBCATEGORY

    assert project.usable_folders[9].name == "bar"
    assert project.usable_folders[9].number == "21"
    assert project.usable_folders[9].path == Path(project_path / "20-29_bar/21_bar")
    assert project.usable_folders[9].terms == ["bar"]
    assert project.usable_folders[9].area == Path(project_path / "20-29_bar")
    assert project.usable_folders[9].category == Path(project_path / "20-29_bar/21_bar")
    assert project.usable_folders[9].type == FolderType.CATEGORY

    assert project.usable_folders[10].name == "baz"
    assert project.usable_folders[10].number == "30-39"
    assert project.usable_folders[10].path == Path(project_path / "30-39_baz")
    assert project.usable_folders[10].terms == ["baz"]
    assert project.usable_folders[10].area == Path(project_path / "30-39_baz")
    assert project.usable_folders[10].category is None
    assert project.usable_folders[10].type == FolderType.AREA


def test_name_not_in_config():
    """Test creating a project without a name in the config."""
    config = Config()
    project = Project(config=config)
    assert project.exists is False


def test_tree(tmp_path, config1_project, capsys):
    """Test the tree method."""
    expected = f"""\
{tmp_path}/project
│
├── 10-19 foo
│     ├── 11 bar
│     │     ├── 11.01 foo
│     │     ├── 11.02 bar
│     │     └── 11.03 baz
│     └── 12 baz
│             ├── 12.01 foo
│             ├── 12.02 bar
│             ├── 12.03 QUX
│             └── 12.04 baz
├── 20-29_bar
│     ├── 20_foo
│     │     ├── 20.01_foo_bar_baz
│     │     └── 20.02_bar
│     └── 21_bar
└── 30-39_baz
"""

    config, originals_path, project_path = config1_project
    project = Project(config=config)
    project.tree()
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == expected

    project2 = Project()
    project2.tree()
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "WARNING  | No Johnny Decimal project found.\n"
