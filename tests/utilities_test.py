# type: ignore
"""Test jdfile utilities."""
from pathlib import Path

from jdfile._config.config import Config
from jdfile.models.project import Project
from jdfile.utils.utilities import build_file_list


def test_build_file_list_single(tmp_path):
    """Test building a list of files to process.

    GIVEN a single file
    WHEN the file is processed
    THEN the file is returned
    """
    config = Config()
    config.clean = False
    files = [Path(tmp_path / "test1.txt")]
    files[0].touch()
    files_to_process, skipped_files = build_file_list(files, config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 1
    assert files_to_process[0].path == files[0]


def test_build_file_list_multiple(tmp_path):
    """Test building a list of files to process.

    GIVEN multiple files
    WHEN the files are processed
    THEN the files are returned
    """
    config = Config()
    config.clean = False
    files = [
        Path(tmp_path / "test1.txt"),
        Path(tmp_path / "test2.txt"),
        Path(tmp_path / "test3.txt"),
    ]
    for f in files:
        f.touch()
    files_to_process, skipped_files = build_file_list(files, config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 3
    for file in files_to_process:
        assert file.path in files


def test_build_file_list_single_directory(tmp_path):
    """Test building a list of files to process.

    GIVEN a single directory
    WHEN the directory is processed
    THEN the files in the directory are returned
    """
    config = Config()
    config.clean = False
    new_dir = tmp_path / "new_dir"
    new_dir.mkdir()
    files = [Path(new_dir / "test1.txt")]
    files[0].touch()
    files_to_process, skipped_files = build_file_list([new_dir], config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 1
    assert files_to_process[0].path == files[0]


def test_build_file_list_multiple_directories(tmp_path):
    """Test building a list of files to process.

    GIVEN multiple directories and a specified file
    WHEN the directories and file are processed
    THEN the files in the directories are returned
    """
    config = Config()
    config.clean = False
    new_dir = tmp_path / "new_dir"
    new_dir.mkdir()
    second_dir = new_dir / "second_dir"
    second_dir.mkdir()
    files = [
        Path(tmp_path / "test0.txt"),
        Path(new_dir / "test1.txt"),
        Path(second_dir / "test2.txt"),
        Path(second_dir / "test3.txt"),
    ]
    for f in files:
        f.touch()
    files_to_process, skipped_files = build_file_list([new_dir, second_dir, files[0]], config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 4
    for file in files_to_process:
        assert file.path in files


def test_build_file_list_depth_1(tmp_path):
    """Test building a list of files to process.

    GIVEN multiple directories and depth set to 1
    WHEN the directories are processed
    THEN only the files in the first directory are returned
    """
    config = Config()
    config.clean = False
    new_dir = tmp_path / "new_dir"
    new_dir.mkdir()
    second_dir = new_dir / "second_dir"
    second_dir.mkdir()
    files = [
        Path(new_dir / "test1.txt"),
        Path(second_dir / "test2.txt"),
        Path(second_dir / "test3.txt"),
    ]
    for f in files:
        f.touch()
    files_to_process, skipped_files = build_file_list([new_dir], config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 1
    assert files_to_process[0].path == files[0]


def test_build_file_list_depth_2(tmp_path):
    """Test building a list of files to process.

    GIVEN multiple directories and depth set to 2
    WHEN the directories are processed
    THEN only the files in the first and second directories are returned
    """
    config = Config()
    config.clean = False
    config.depth = 2
    new_dir = tmp_path / "new_dir"
    new_dir.mkdir()
    second_dir = new_dir / "second_dir"
    second_dir.mkdir()
    files = [
        Path(new_dir / "test1.txt"),
        Path(second_dir / "test2.txt"),
        Path(second_dir / "test3.txt"),
    ]
    for f in files:
        f.touch()
    files_to_process, skipped_files = build_file_list([new_dir], config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 3
    for file in files_to_process:
        assert file.path in files


def test_build_file_list_ignore_dotfiles(tmp_path):
    """Test building a list of files to process.

    GIVEN a two files, one of which is a dotfile
    WHEN the files are processed and dotfiles are ignored
    THEN the dotfile is skipped
    """
    config = Config()
    config.clean = False
    config.ignore_dotfiles = True
    files = [Path(tmp_path / "test1.txt"), Path(tmp_path / ".dotfile.txt")]
    files[0].touch()
    files_to_process, skipped_files = build_file_list(files, config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 1
    assert files_to_process[0].path == files[0]


def test_build_file_list_ignored_files(tmp_path):
    """Test building a list of files to process.

    GIVEN a list of files and specified ignored files
    WHEN the files are processed
    THEN only the non-ignored files are returned
    """
    config = Config()
    config.clean = False
    config.ignored_files = ["test1.txt", "test2.txt"]
    files = [
        Path(tmp_path / "test1.txt"),
        Path(tmp_path / "test2.txt"),
        Path(tmp_path / "test3.txt"),
    ]
    for f in files:
        f.touch()
    files_to_process, skipped_files = build_file_list(files, config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 1
    assert files_to_process[0].path == files[2]


def test_build_file_list_ignore_regex(tmp_path):
    """Test building a list of files to process.

    GIVEN a list of files and specified ignored regex patterns
    WHEN the files are processed
    THEN only the non-ignored files are returned
    """
    config = Config()
    config.clean = False
    config.ignored_regex = ["\\.jpg$", "^\\w+2"]
    files = [
        Path(tmp_path / "test1.txt"),
        Path(tmp_path / "test1.jpg"),
        Path(tmp_path / "test2.txt"),
    ]
    for f in files:
        f.touch()

    files_to_process, skipped_files = build_file_list(files, config)
    assert len(skipped_files) == 0
    assert len(files_to_process) == 1
    assert files_to_process[0].path == files[0]


def test_build_file_list_skipped_only(config1_project):
    """Test building a list of files to process.

    GIVEN a list of files and a project
    WHEN the files are processed and no files match a folder
    THEN all files are added to `skipped_files`
    """
    config, original_files_path, project_path = config1_project
    project = Project(config)
    files = [Path(original_files_path / "testfile.txt")]
    files[0].touch()
    files_to_process, skipped_files = build_file_list(files, config, project)
    assert len(skipped_files) == 1
    assert len(files_to_process) == 0
    assert skipped_files[0].path == files[0]


def test_build_file_list_skipped_and_processed(config1_project):
    """Test building a list of files to process.

    GIVEN a list of files and a project
    WHEN the files are processed and some files match a folder
    THEN skipped files are added to `skipped_files` and processed files are added to `files_to_process`
    """
    config, original_files_path, project_path = config1_project
    project = Project(config)
    files = [Path(original_files_path / "testfile.txt"), Path(original_files_path / "QUX.txt")]
    files[0].touch()
    files[1].touch()
    files_to_process, skipped_files = build_file_list(files, config, project)
    assert len(skipped_files) == 1
    assert len(files_to_process) == 1
    assert skipped_files[0].path == files[0]
    assert files_to_process[0].path == files[1]
