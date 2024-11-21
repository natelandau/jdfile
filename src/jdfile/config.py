"""Instantiate neatpathConfig class and set default values."""

from pathlib import Path

from dynaconf import Dynaconf, Validator

from jdfile.constants import (
    CONFIG_PATH,
    InsertLocation,
    Separator,
    TransformCase,
)

settings = Dynaconf(
    envvar_prefix="JDFILE",
    settings_files=[
        Path(__file__).parents[0].absolute() / "defaults.toml",
        CONFIG_PATH,
    ],
    environments=False,
)


settings.validators.register(
    Validator("clean_filenames", cast=bool, default=True),
    Validator("date_format", default="%Y-%m-%d", cast=str),
    Validator("format_dates", cast=bool, default=True),
    Validator("ignore_dotfiles", cast=bool, default=True),
    Validator("ignore_file_regex", default="", cast=str),
    Validator("ignored_files", default=[], cast=list),
    Validator("insert_location", default="before", cast=lambda v: InsertLocation[v.upper()]),
    Validator("match_case_list", default=[], cast=list),
    Validator("overwrite_existing", cast=bool, default=False),
    Validator("separator", default="ignore", cast=lambda v: Separator[v.upper()]),
    Validator("split_words", cast=bool, default=False),
    Validator("stopwords", default=[], cast=list),
    Validator("strip_stopwords", cast=bool, default=True),
    Validator("transform_case", default="ignore", cast=lambda v: TransformCase[v.upper()]),
    Validator("use_synonyms", cast=bool),
)
