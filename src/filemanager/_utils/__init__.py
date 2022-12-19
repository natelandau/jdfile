"""Shared utilities."""
from filemanager._utils.utilities import (  # isort:skip
    dedupe_list,
    diff_strings,
    from_camel_case,
    select_option,
)

from filemanager._utils.words import (  # isort: skip
    find_synonyms,
    instantiate_nltk,
    populate_stopwords,
)
from filemanager._utils.projectFolders import (  # isort: skip
    populate_project_folders,
    show_tree,
    Folder,
)
from filemanager._utils import alerts
from filemanager._utils.alerts import LoggerManager
from filemanager._utils.dates import create_date, parse_date
from filemanager._utils.files import File, create_unique_filename
from filemanager._utils.tables import show_confirmation_table

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
