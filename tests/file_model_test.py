# type: ignore
"""Test the file model."""

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from jdfile.constants import Separator, TransformCase
from jdfile.models import File
from jdfile.utils import console


@given(
    stem=st.text(
        min_size=2,
        max_size=20,
        alphabet=st.characters(exclude_characters="0"),  # Fails on `0`
    ),
    extension=st.from_regex(r"(\.[a-zA-Z]{2,4}){1,2}", fullmatch=True),
)
def test_with_hypothesis(stem, extension):
    """Test instantiating and cleaning files with various unicode characters."""
    # GIVEN a file with the provided name in a clean directory
    filename = f"{stem}{extension}"

    file = File(
        path=Path(filename),
        project=None,
        user_date_format=False,
        user_separator=Separator.IGNORE,
        user_split_words=False,
        user_strip_stopwords=False,
        user_case_transformation=TransformCase.IGNORE,
        user_overwrite_existing=False,
        user_match_case_list=["test"],
    )
    # console.log(filename) # for debugging
    assert str(file.path) == filename
    file.clean_filename()
