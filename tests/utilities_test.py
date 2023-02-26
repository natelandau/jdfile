# type: ignore
"""Test jdfile utilities."""
from pathlib import Path

from jdfile._config.config import Config
from jdfile.utils.utilities import build_file_list


def test_build_file_list(tmp_path):
    """Test building a list of files to process."""
    config = Config()
    new_dir = tmp_path / "new_dir"
    new_dir.mkdir()
    second_dir = new_dir / "second_dir"
    second_dir.mkdir()
    Path(second_dir / "test4.txt").touch()

    files = [
        tmp_path / "test1.txt",  # 0
        tmp_path / ".dotfile",  # 1
        tmp_path / "test2.txt",  # 2
        new_dir / ".dotfile2",  # 3
        new_dir / "test3.txt",  # 4
        tmp_path / ".gitignore",  # 5
    ]
    for f in files:
        f.touch()

    file_paths = [f.path for f in build_file_list(files, config)]
    assert file_paths == [files[0], files[2], files[4]]

    config.ignore_dotfiles = False
    config.ignored_files = [".gitignore"]
    file_paths = [f.path for f in build_file_list(files, config)]
    assert file_paths == [files[1], files[3], files[0], files[2], files[4]]

    # Test directories and depth 1
    config.depth = 1
    file_paths = [f.path for f in build_file_list([tmp_path], config)]
    assert file_paths == [
        files[1],
        files[0],
        files[2],
    ]

    # Test directories and depth 2
    config.depth = 2
    file_paths = [f.path for f in build_file_list([tmp_path], config)]
    assert file_paths == [
        files[1],
        files[3],
        files[0],
        files[2],
        files[4],
    ]

    # Test directories and depth 3
    config.depth = 3
    file_paths = [f.path for f in build_file_list([tmp_path], config)]
    assert file_paths == [
        files[1],
        files[3],
        files[0],
        files[2],
        files[4],
        Path(second_dir / "test4.txt"),
    ]
