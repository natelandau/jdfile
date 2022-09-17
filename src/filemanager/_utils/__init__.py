"""Shared utilities."""
from filemanager._utils.utilities import dedupe_list, diff_strings, select_option  # isort:skip
from filemanager._utils.synonyms import find_synonyms, instantiate_nltk  # isort: skip
from filemanager._utils.johnnyDecimal import show_tree, Folder  # isort: skip
from filemanager._utils import alerts
from filemanager._utils.alerts import LoggerManager
from filemanager._utils.dates import create_date, parse_date
from filemanager._utils.files import File, create_unique_filename
from filemanager._utils.organize import populate_project_folders, populate_stopwords
from filemanager._utils.output import show_confirmation_table

__all__ = [
    "alerts",
    "create_date",
    "create_unique_filename",
    "dedupe_list",
    "diff_strings",
    "File",
    "find_synonyms",
    "Folder",
    "instantiate_nltk",
    "LoggerManager",
    "parse_date",
    "populate_project_folders",
    "populate_stopwords",
    "select_option",
    "show_confirmation_table",
    "show_tree",
]
