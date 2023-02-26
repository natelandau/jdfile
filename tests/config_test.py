# type: ignore
"""Test configuration class."""

from pathlib import Path

import pytest
import typer

from jdfile._config.config import Config
from jdfile.utils.enums import Separator, TransformCase


def test_create_config(tmp_path):
    """Test creating a configuration file when none exists."""
    config_path = Path(tmp_path / "config.toml")

    assert config_path.exists() is False

    with pytest.raises(typer.Exit):
        Config(config_path=config_path, context={"project_name": "project_name"})
    assert config_path.exists()

    config = Config(config_path=config_path, context={"project_name": "project_name"})
    assert config.config_path == config_path
    assert config.config_path.exists()
    assert config.project_name == "project_name"
    assert config.config_file_dict == {
        "project_name": {
            "date_format": "None",
            "ignore_dotfiles": True,
            "ignored_files": ["file1.txt", "file2.txt"],
            "match_case": ["CEO", "CEOs", "iMac", "iPhone"],
            "overwrite_existing": False,
            "path": "~/johnnydecimal",
            "separator": "ignore",
            "split_words": False,
            "stopwords": ["stopword1", "stopword2"],
            "strip_stopwords": True,
            "transform_case": "ignore",
            "use_synonyms": False,
        },
    }
    assert config.project_config == {
        "date_format": "None",
        "ignore_dotfiles": True,
        "ignored_files": ["file1.txt", "file2.txt"],
        "match_case": ["CEO", "CEOs", "iMac", "iPhone"],
        "overwrite_existing": False,
        "path": "~/johnnydecimal",
        "separator": "ignore",
        "split_words": False,
        "stopwords": ["stopword1", "stopword2"],
        "strip_stopwords": True,
        "transform_case": "ignore",
        "use_synonyms": False,
    }
    assert config.date_format is None
    assert config.project_path == Path("~/johnnydecimal").expanduser()
    assert config.transform_case == TransformCase.IGNORE
    assert config.separator == Separator.IGNORE
    assert config.split_words is False
    assert config.ignored_files == ["file1.txt", "file2.txt"]
    assert config.match_case == ["CEO", "CEOs", "iMac", "iPhone"]
    assert config.stopwords == ["stopword1", "stopword2"]
    assert config.strip_stopwords is True
    assert config.depth == 1
    assert config.use_nltk is False


def test_raise_for_invalid_config(tmp_path):
    """Test error handling when creating a configuration file."""
    config_no_path = """\
[project_name]
    stopwords = ["stopword", "stopword"]
    ignored_files = ['.DS_Store', '.bashrc']
    match_case = ["CEO", "CEOs", "KPI", "KPIs", "OKR", "OKRs"]
    """
    config_no_dict_values = """\
some_not_dict_value = "some_value"
[project_name]
    path = "~/johnnydecimal"
    stopwords = ["stopword", "stopword"]
    ignored_files = ['.DS_Store', '.bashrc']
    match_case = ["CEO", "CEOs", "KPI", "KPIs", "OKR", "OKRs"]
    """
    missing_path = Path(tmp_path / "missing.toml")
    missing_path.touch()
    missing_path.write_text(config_no_path)

    config_no_dict_values_path = Path(tmp_path / "config_no_dict_values.toml")
    config_no_dict_values_path.touch()
    config_no_dict_values_path.write_text(config_no_dict_values)

    # Empty configuration file
    config_path = Path(tmp_path / "config.toml")
    config_path.touch()
    with pytest.raises(typer.Exit):
        Config(config_path, context={"project_name": "project_name"})

    # Missing path
    with pytest.raises(typer.Exit):
        Config(missing_path, context={"project_name": "project_name"})

    # Missing dict values
    config_path.write_text(config_no_dict_values)
    with pytest.raises(typer.Exit):
        Config(config_no_dict_values_path, context={"project_name": "project_name"})


def test_config_no_project_name_and_defaults():
    """Test configuration without a project name. This should return default configuration values."""
    config = Config()
    assert config.clean is False
    assert config.config_file_dict == {}
    assert config.date_format is None
    assert config.dry_run is False
    assert config.force is False
    assert config.project_config == {}
    assert config.project_name is None
    assert config.project_path is None
    assert config.separator == Separator.IGNORE
    assert config.transform_case == TransformCase.IGNORE
    assert config.use_nltk is False
    assert config.split_words is False


def test_wrong_project_name(tmp_path):
    """Test configuration with a wrong project name."""
    config_path = Path(tmp_path / "config.toml")
    config_path.touch()
    config_path.write_text(
        """\
[project_name]
    path = "~/johnnydecimal"
    stopwords = ["stopword", "stopword"]
    ignored_files = ['.DS_Store', '.bashrc']
    match_case = ["CEO", "CEOs", "KPI", "KPIs", "OKR", "OKRs"]
    """
    )
    with pytest.raises(typer.Abort):
        Config(config_path=config_path, context={"project_name": "wrong_name"})


def test_config_with_context():
    """Test configuration with a context."""
    context = {
        "clean": True,
        "date_format": "%Y-%m-%d",
        "dry_run": True,
        "force": True,
        "project_name": "name",
        "separator": "underscore",
        "split_words": True,
        "transform_case": "lower",
        "use_nltk": True,
    }
    config = Config(context=context)
    assert config.clean is True
    assert config.config_file_dict == {}
    assert config.date_format == "%Y-%m-%d"
    assert config.dry_run is True
    assert config.force is True
    assert config.project_config == {}
    assert config.project_name is None
    assert config.separator == Separator.UNDERSCORE
    assert config.split_words is True
    assert config.transform_case == TransformCase.LOWER
    assert config.use_nltk is True


def test_invalid_date_format():
    """Test invalid date format."""
    context = {
        "date_format": "%K-%m-%d",
    }

    with pytest.raises(typer.Abort):
        Config(context=context)


def test_invalid_separator():
    """Test invalid separator."""
    context = {
        "separator": "invalid",
    }

    config = Config(context=context)
    with pytest.raises(typer.Abort):
        config.separator


def test_invalid_case():
    """Test invalid case."""
    context = {
        "transform_case": "invalid",
    }

    config = Config(context=context)
    with pytest.raises(typer.Abort):
        config.transform_case


def test_context_overrides_config_file(tmp_path):
    """Test that context overrides configuration file."""
    config_path = Path(tmp_path / "config.toml")
    config_path.touch()
    config_path.write_text(
        """\
[test]
    date_format = "None"
    ignored_files = ['.DS_Store', '.bashrc']
    match_case = [
        "BWS",
        "CEO",
        "CEOs",
        "ISO",
        "KPI",
        "KPIs",
        "NDA",
        "NYC",
        "NYPR",
        "OKR",
        "OKRs",
        "PDDE",
        "SVP",
        "VP",
        "theSkimm",
    ]
    path = "~/tmp/test_project"
    separator = "ignore"
    split_words = true
    stopwords = ["stopword", "stopword"]
    transform_case = "ignore"
"""
    )
    config = Config(
        config_path=config_path,
        context={
            "project_name": "test",
            "date_format": "%Y-%m-%d",
            "transform_case": TransformCase.LOWER,
            "separator": "dash",
            "split_words": False,
        },
    )
    assert config.date_format == "%Y-%m-%d"
    assert config.project_name == "test"
    assert config.separator == Separator.DASH
    assert config.split_words is False
    assert config.transform_case == TransformCase.LOWER
    assert config.project_path == Path("~/tmp/test_project").expanduser()
