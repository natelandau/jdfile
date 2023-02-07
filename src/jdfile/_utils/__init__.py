"""Shared utilities."""
from jdfile._utils.utilities import (  # isort: skip
    dedupe_list,
    diff_strings,
    from_camel_case,
    select_option,
)

from jdfile._utils.words import (  # isort: skip
    find_synonyms,
    instantiate_nltk,
    populate_stopwords,
)
from jdfile._utils.projectFolders import (  # isort: skip
    populate_project_folders,
    show_tree,
    Folder,
)
from jdfile._utils import alerts
from jdfile._utils.alerts import LoggerManager
from jdfile._utils.dates import create_date, parse_date
from jdfile._utils.files import File, create_unique_filename
from jdfile._utils.tables import show_confirmation_table

__all__ = [
    "alerts",
    "create_date",
    "create_unique_filename",
    "dedupe_list",
    "diff_strings",
    "File",
    "find_synonyms",
    "Folder",
    "from_camel_case",
    "instantiate_nltk",
    "LoggerManager",
    "parse_date",
    "populate_project_folders",
    "populate_stopwords",
    "select_option",
    "show_confirmation_table",
    "show_tree",
]
