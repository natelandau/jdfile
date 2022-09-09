"""Shared utilities."""
from filemanager._utils.utilities import dedupe_list  # isort:skip
from filemanager._utils.synonyms import find_synonyms, instantiate_nltk  # isort: skip
from filemanager._utils import alerts
from filemanager._utils.alerts import LoggerManager
from filemanager._utils.dates import create_date, parse_date
from filemanager._utils.files import File, create_unique_filename
from filemanager._utils.organize import (
    build_project_folder_list,
    populate_projects,
    populate_stopwords,
)

__all__ = [
    "alerts",
    "build_project_folder_list",
    "create_date",
    "create_unique_filename",
    "dedupe_list",
    "File",
    "find_synonyms",
    "instantiate_nltk",
    "LoggerManager",
    "parse_date",
    "populate_projects",
    "populate_stopwords",
]
