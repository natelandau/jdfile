# type: ignore
"""Test date utilities."""
from pathlib import Path

import pytest

from filemanager._utils.dates import create_date, month_to_number, parse_date
from tests.helpers import Regex


def test_create_date(mocker):
    """Test create_date."""
    mocker.patch("filemanager._utils.dates.Path.stat", st_ctime=1661526200.5003605)
    assert create_date(Path("test.txt"), date_format="%Y-%m-%d") == "1970-01-01"


@pytest.mark.parametrize(
    ("full_string", "expected_date", "expected_string", "date_format"),
    [
        # no matched dates
        ("this string has no date", None, None, "%Y-%m-%d"),
        ("this not a valid date 2019-99-01 and more text", None, None, "%Y-%m-%d"),
        ("this not a valid date 2019-06-99 and more text", None, None, "%Y-%m-%d"),
        # yyyymmdd
        ("a 2021-03-23 b", "2021-03-23", "2021-03-23", "%Y-%m-%d"),
        ("2022.12.23", "2022-12-23", "2022.12.23", "%Y-%m-%d"),
        ("2022/12/23", "2022-12-23", "2022/12/23", "%Y-%m-%d"),
        ("this is text 2019-06-01 and more text", "01/06/2019", "2019-06-01", "%d/%m/%Y"),
        ("asdf 2019:01:22:02:28asdf ", "2019-01-22", "2019:01:22", "%Y-%m-%d"),
        ("asdf 2019012212asdf ", "2019-01-22", "20190122", "%Y-%m-%d"),
        ("2022_03_31", "2022-03-31", "2022_03_31", "%Y-%m-%d"),
        # yyyy_dd_mm
        ("a 2021-31-03 b", "2021-03-31", "2021-31-03", "%Y-%m-%d"),
        ("a 2021-24-12 b", "2021-12-24", "2021-24-12", "%Y-%m-%d"),
        # month_dd_yyyy
        ("march 3rd, 2022", "2022-03-03", "march 3rd, 2022", "%Y-%m-%d"),
        ("something march 1st, 2019", "2019-03-01", "march 1st, 2019", "%Y-%m-%d"),
        ("jan 3rd, 2022", "2022-01-03", "jan 3rd, 2022", "%Y-%m-%d"),
        ("this is text Oct 22, 2019 and more text", "2019-10-22", "Oct 22, 2019", "%Y-%m-%d"),
        # dd_month_yyyy
        ("hello 23 march, 2020 world", "2020-03-23", "23 march, 2020", "%Y-%m-%d"),
        ("22nd June, 2019 and more text", "2019-06-22", "22nd June, 2019", "%Y-%m-%d"),
        # month_yyyy
        ("march 2022", "2022-03-01", "march 2022", "%Y-%m-%d"),
        ("mar2019 month no date", "2019-03-01", "mar2019", "%Y-%m-%d"),
        ("oct-2019 month no date", "2019-10-01", "oct-2019", "%Y-%m-%d"),
        ("a-test-January, 2019-is here", "2019-01-01", "January, 2019", "%Y-%m-%d"),
        ("a-test January, 19 2019 is here", "2019-01-19", "January, 19 2019", "%Y-%m-%d"),
        # yyyy_month
        ("something 2019, oct", "2019-10-01", "2019, oct", "%Y-%m-%d"),
        ("something 2019November", "2019-11-01", "2019November", "%Y-%m-%d"),
        # mmddyyyy
        ("asdf 11222019 asdf", "2019-11-22", "11222019", "%Y-%m-%d"),
        ("asdf 01222019 asdf", "2019-01-22", "01222019", "%Y-%m-%d"),
        ("asdf 01-22-2019 asdf", "2019-01-22", "01-22-2019", "%Y-%m-%d"),
        # ddmmyyyy
        ("asdf 16112019 asdf", "2019-11-16", "16112019", "%Y-%m-%d"),
        ("asdf 24-06-2021 asdf", "2021-06-24", "24-06-2021", "%Y-%m-%d"),
        ("a-test 22/12/2019-is here", "2019-12-22", "22/12/2019", "%Y-%m-%d"),
        ("a-test-22/12/2019-is here", "2019-12-22", "22/12/2019", "%Y-%m-%d"),
        # mmdd
        ("just a month and a day 03 19", "03-19", "03 19", "%m-%d"),
        ("just a month and a day 01-11", "01-11", "01-11", "%m-%d"),
        # ddmm
        ("just a day and a month 31 03", "03-31", "31 03", "%m-%d"),
        ("just a day and a month 24 11", "11-24", "24 11", "%m-%d"),
        # specified dates
        ("today", Regex(r"\d{4}-\d{2}-\d{2}"), None, "%Y-%m-%d"),
        ("yesterday", Regex(r"\d{4}-\d{2}-\d{2}"), None, "%Y-%m-%d"),
        ("last week", Regex(r"\d{4}-\d{2}-\d{2}"), None, "%Y-%m-%d"),
        ("last month", Regex(r"\d{4}-\d{2}-\d{2}"), None, "%Y-%m-%d"),
        ("tomorrow", Regex(r"\d{4}-\d{2}-\d{2}"), None, "%Y-%m-%d"),
    ],
)
def test_parse_date(full_string, expected_date, expected_string, date_format):
    """Test parse_date."""
    assert parse_date(full_string, date_format) == (expected_string, expected_date)


def test_month_to_number():
    """Test month_to_number."""
    assert month_to_number("jan") == "01"
    assert month_to_number("feb") == "02"
    assert month_to_number("mar") == "03"
    assert month_to_number("apr") == "04"
    assert month_to_number("may") == "05"
    assert month_to_number("jun") == "06"
    assert month_to_number("jul") == "07"
    assert month_to_number("aug") == "08"
    assert month_to_number("sep") == "09"
    assert month_to_number("oct") == "10"
    assert month_to_number("nov") == "11"
    assert month_to_number("dec") == "12"
    assert month_to_number("january") == "01"
    assert month_to_number("february") == "02"
    assert month_to_number("march") == "03"
    assert month_to_number("april") == "04"
    assert month_to_number("may") == "05"
    assert month_to_number("june") == "06"
    assert month_to_number("july") == "07"
    assert month_to_number("august") == "08"
    assert month_to_number("september") == "09"
    assert month_to_number("october") == "10"
    assert month_to_number("november") == "11"
    assert month_to_number("december") == "12"
    assert month_to_number("xxx") == ""
