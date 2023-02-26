"""Utilities for jdfile."""


from pathlib import Path

from rich.progress import Progress, SpinnerColumn, TextColumn

from jdfile._config.config import Config
from jdfile.models.file import File
from jdfile.models.project import Project
from jdfile.utils.alerts import logger as log


def build_file_list(files: list[Path], config: Config, project: Project = None) -> list[File]:
    """Build a list of files to process. If a directory is specified, all files in the directory will be processed.

        Args:
            config (Config): Configuration object.
            files (list[Path]): List of files or directories to process.
            project (Project, optional): Project object. Defaults to None.

    Returns:
            list[Path]: List of files to process.

    # for possible_file in files:
    #     if possible_file.is_file() and possible_file.stem not in config["ignored_files"]:
    #         list_of_files.append(File(possible_file, terms))
    #     if possible_file.is_dir():
    #         for f in possible_file.rglob("*"):
    #             depth_of_file = len(f.relative_to(possible_file).parts)
    #             if depth_of_file <= depth and f.is_file() and f.stem not in config["ignored_files"]:
    #                 list_of_files.append(File(f, terms))
    """
    directories = [f for f in files if f.is_dir() and f.exists()]
    for _dir in directories:
        files.remove(_dir)
        for f in _dir.rglob("*"):
            depth_of_file = len(f.relative_to(_dir).parts)
            if depth_of_file <= config.depth and f.is_file():
                files.append(f)

    with Progress(
        SpinnerColumn("simpleDotsScrolling"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Processing files...", total=None)
    all_files = sorted(
        [
            File(path=f, config=config, project=project)
            for f in files
            if f.is_file() and f.name not in config.ignored_files
        ],
        key=lambda x: x.name,
    )

    if config.ignore_dotfiles:
        return [f for f in all_files if not f.is_dotfile]

    log.trace(f"Found {len(all_files)} files.")
    return all_files
