"""Configuration file for the jdfile package."""


from typing import Annotated, Any, ClassVar, Optional

from confz import BaseConfig, ConfigSources, FileSource
from pydantic import BaseModel, BeforeValidator

from jdfile.constants import CONFIG_PATH, InsertLocation, Separator, TransformCase


def string_to_separator(value: str) -> Separator:
    """Convert a string to a Separator enum value.

    Raises:
        ValueError: If the provided value does not match any Separator enum.
    """
    try:
        return Separator[value.upper()]
    except KeyError as e:
        msg = f"Invalid separator: {value}"
        raise ValueError(msg) from e


def string_to_transform_case(value: str) -> TransformCase:
    """Convert a string to a TransformCase enum value.

    Raises:
        ValueError: If the provided value does not match any TransformCase enum.
    """
    try:
        return TransformCase[value.upper()]
    except KeyError as e:
        msg = f"Invalid transformation: {value}"
        raise ValueError(msg) from e


def string_to_insert_location(value: str) -> InsertLocation:
    """Convert a string to an InsertLocation enum value.

    Raises:
        ValueError: If the provided value does not match any InsertLocation enum.
    """
    try:
        return InsertLocation[value.upper()]
    except KeyError as e:
        msg = f"Invalid insert location: {value}"
        raise ValueError(msg) from e


ValidSeparator = Annotated[Separator, BeforeValidator(string_to_separator)]
ValidTransformCase = Annotated[TransformCase, BeforeValidator(string_to_transform_case)]
ValidInsertLocation = Annotated[InsertLocation, BeforeValidator(string_to_insert_location)]


class ConfigProject(BaseModel):
    """Define a jdfile configuration project with customizable settings."""

    date_format: Optional[str] = None
    clean_filenames: Optional[bool] = None
    ignore_dotfiles: Optional[bool] = None
    ignored_files: tuple[str, ...] = ()
    ignore_file_regex: Optional[str] = None
    insert_location: Optional[InsertLocation] = None
    match_case_list: tuple[str, ...] = ()
    overwrite_existing: Optional[bool] = None
    path: str
    separator: Optional[ValidSeparator] = None
    split_words: Optional[bool] = None
    stopwords: Optional[tuple[str, ...]] = None
    strip_stopwords: Optional[bool] = None
    transform_case: Optional[ValidTransformCase] = None
    use_synonyms: Optional[bool] = None


class AppConfig(BaseConfig):  # type: ignore [misc]
    """Configure jdfile settings including default values and per-project configurations."""

    projects: dict[str, ConfigProject] | None = None
    # Default values
    clean_filenames: Optional[bool] = True
    date_format: Optional[str] = None
    ignore_dotfiles: bool = True
    ignore_file_regex: Optional[str] = "^$"  # Default to match nothing
    ignored_files: tuple[str, ...] = ()
    insert_location: ValidInsertLocation = (
        InsertLocation.BEFORE
    )  # TODO: Make this a configurable option
    match_case_list: tuple[str, ...] = ()
    overwrite_existing: bool = False
    separator: ValidSeparator = Separator.IGNORE
    split_words: bool = False
    stopwords: tuple[str, ...] = ()
    strip_stopwords: bool = True
    transform_case: ValidTransformCase = TransformCase.IGNORE
    use_synonyms: bool = False

    CONFIG_SOURCES: ClassVar[ConfigSources | None] = [FileSource(file=CONFIG_PATH)]

    def get_attribute(cls, project_name: str, attribute: str) -> Any:
        """Retrieve a project-specific attribute or a default attribute value.

        Searches for an attribute within a specified project's configuration. If the attribute
        is not set or the project does not exist, it falls back to the default attribute value
        defined at the class level.

        Args:
            project_name: The name of the project to search for the attribute.
            attribute: The name of the attribute to retrieve.

        Returns:
            The value of the attribute from the project's configuration if present; otherwise,
            the default value of the attribute.
        """
        # Return the default attribute value if project_name is not provided
        if not project_name:
            return getattr(cls, attribute, None)

        # Attempt to retrieve the project's configuration and then the attribute
        project = cls.projects.get(project_name, None)
        if project:
            # If the project exists, try getting the attribute from the project
            value = getattr(project, attribute, None)
            if value is not None:
                return value

        # Fallback to the class-level default if the project-specific attribute is not set
        return getattr(cls, attribute, None)
