# type: ignore
"""Tests for dates.py."""

from datetime import date, datetime, timedelta

import pytest

from jdfile.models.dates import Date, DatePattern

TODAY = date.today()
YESTERDAY = date.today() - timedelta(days=1)
TOMORROW = date.today() + timedelta(days=1)
LAST_MONTH = date.today().replace(month=date.today().month - 1)
LAST_WEEK = date.today() - timedelta(days=7)


def test__month_to_number():
    """Test month_to_number."""
    date = DatePattern(string="")

    assert date._month_to_number("JAN") == "01"
    assert date._month_to_number("feb") == "02"
    assert date._month_to_number("mar") == "03"
    assert date._month_to_number("apr") == "04"
    assert date._month_to_number("may") == "05"
    assert date._month_to_number("jun") == "06"
    assert date._month_to_number("jul") == "07"
    assert date._month_to_number("aug") == "08"
    assert date._month_to_number("sep") == "09"
    assert date._month_to_number("oct") == "10"
    assert date._month_to_number("nov") == "11"
    assert date._month_to_number("dec") == "12"
    assert date._month_to_number("january") == "01"
    assert date._month_to_number("february") == "02"
    assert date._month_to_number("march") == "03"
    assert date._month_to_number("april") == "04"
    assert date._month_to_number("may") == "05"
    assert date._month_to_number("june") == "06"
    assert date._month_to_number("july") == "07"
    assert date._month_to_number("august") == "08"
    assert date._month_to_number("september") == "09"
    assert date._month_to_number("OcTobEr") == "10"
    assert date._month_to_number("november") == "11"
    assert date._month_to_number("december") == "12"
    assert not date._month_to_number("xxx")


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("this not a valid date 2019-99-01 and more text", False, ""),
        ("file 2022-12-32", False, ""),
        ("file_2022_01_01_somefile", True, (date(2022, 1, 1), "2022_01_01")),
        ("file 2022-12-31", True, (date(2022, 12, 31), "2022-12-31")),
        ("20221231", True, (date(2022, 12, 31), "20221231")),
        ("2022/12/31", True, (date(2022, 12, 31), "2022/12/31")),
    ],
)
def test_pattern_yyyy_mm_dd(filename, is_true, expected):
    """Test DatePattern.yyyy_mm_dd."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.yyyy_mm_dd() == expected
    else:
        assert d.yyyy_mm_dd() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("this not a valid date 2019-99-01 and more text", False, ""),
        ("file 2022-12-32", False, ""),
        ("file 2022-12-31", False, ""),
        ("file_2022_01_01_somefile", True, (date(2022, 1, 1), "2022_01_01")),
        ("file 2022-31-12", True, (date(2022, 12, 31), "2022-31-12")),
        ("20223112", True, (date(2022, 12, 31), "20223112")),
        ("2022/31/12", True, (date(2022, 12, 31), "2022/31/12")),
    ],
)
def test_pattern_yyyy_dd_mm(filename, is_true, expected):
    """Test DatePattern.yyyy_mm_dd."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.yyyy_dd_mm() == expected
    else:
        assert d.yyyy_dd_mm() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("this not a valid date 2019-99-01 and more text", False, ""),
        ("file 2022-12-32", False, ""),
        ("file 2022-12-31", False, ""),
        ("march 42nd, 2022", False, ""),
        ("hello 23 march, 2020 world", False, ""),
        ("march 3rd 2022", True, (date(2022, 3, 3), "march 3rd 2022")),
        ("foo march 1st, 2019", True, (date(2019, 3, 1), "march 1st, 2019")),
        ("jan 3rd, 2022", True, (date(2022, 1, 3), "jan 3rd, 2022")),
        ("foo Oct 22, 2019 bar", True, (date(2019, 10, 22), "Oct 22, 2019")),
        ("foo Oct222019 bar", True, (date(2019, 10, 22), "Oct222019")),
    ],
)
def test_pattern_month_dd_yyyy(filename, is_true, expected):
    """Test DatePattern.month_dd_yyyy."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.month_dd_yyyy() == expected
    else:
        assert d.month_dd_yyyy() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("this not a valid date 2019-99-01 and more text", False, ""),
        ("file 2022-12-32", False, ""),
        ("file 2022-12-31", False, ""),
        ("march 42nd, 2022", False, ""),
        ("march 3rd 2022", False, ""),
        ("hello 23 march, 2020 world", True, (date(2020, 3, 23), "23 march, 2020")),
        ("22nd June, 2019 and more text", True, (date(2019, 6, 22), "22nd June, 2019")),
    ],
)
def test_dd_month_yyyy(filename, is_true, expected):
    """Test DatePattern.dd_month_yyyy."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.dd_month_yyyy() == expected
    else:
        assert d.dd_month_yyyy() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("this not a valid date 2019-99-01 and more text", False, ""),
        ("file 2022-12-32", False, ""),
        ("file 2022-12-31", False, ""),
        ("march 42nd, 2022", False, ""),
        ("march 3rd 2022", True, (date(TODAY.year, 3, 3), "march 3rd")),
        ("sep 42nd", False, ""),
        ("sep 4", True, (date(TODAY.year, 9, 4), "sep 4")),
        ("sept 4th", True, (date(TODAY.year, 9, 4), "sept 4th")),
    ],
)
def test_month_dd(filename, is_true, expected):
    """Test DatePattern.month_dd."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.month_dd() == expected
    else:
        assert d.month_dd() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("this not a valid date 2019-99-01 and more text", False, ""),
        ("file 2022-12-32", False, ""),
        ("file 2022-12-31", False, ""),
        ("march 42nd, 2022", False, ""),
        ("march 3rd 2022", False, ""),
        ("sep 2025", True, (date(2025, 9, 1), "sep 2025")),
        ("xxx_December,-2019/aaa", True, (date(2019, 12, 1), "December,-2019")),
        ("mar2022", True, (date(2022, 3, 1), "mar2022")),
    ],
)
def test_month_yyyy(filename, is_true, expected):
    """Test DatePattern.month_dd."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.month_yyyy() == expected
    else:
        assert d.month_yyyy() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("this not a valid date 2019-99-01 and more text", False, ""),
        ("march 42nd, 2022", False, ""),
        ("march 3rd 2022", False, ""),
        ("2025 sep", True, (date(2025, 9, 1), "2025 sep")),
        ("xxx_2019, December,-2019/aaa", True, (date(2019, 12, 1), "2019, December")),
        ("2022mar", True, (date(2022, 3, 1), "2022mar")),
    ],
)
def test_yyyy_month(filename, is_true, expected):
    """Test DatePattern.yyyy_month."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.yyyy_month() == expected
    else:
        assert d.yyyy_month() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", True, (date(2022, 12, 23), "12232022")),
        ("foo 30122022 bar", False, ""),
        ("foo 01-22-2019 bar", True, (date(2019, 1, 22), "01-22-2019")),
        ("foo 12112022 bar", True, (date(2022, 12, 11), "12112022")),
    ],
)
def test_mmddyyyy(filename, is_true, expected):
    """Test DatePattern.mmddyyyy."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.mmddyyyy() == expected
    else:
        assert d.mmddyyyy() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", False, ""),
        ("foo 2122022 bar", False, ""),
        ("foo 30122022 bar", True, (date(2022, 12, 30), "30122022")),
        ("foo 01-22-2019 bar", False, ""),
        ("foo 22-01-2019 bar", True, (date(2019, 1, 22), "22-01-2019")),
        ("foo 12112022 bar", True, (date(2022, 11, 12), "12112022")),
    ],
)
def test_ddmmyyyy(filename, is_true, expected):
    """Test DatePattern.ddmmyyyy."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.ddmmyyyy() == expected
    else:
        assert d.ddmmyyyy() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 2022-12", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", False, ""),
        ("1201", True, (date(TODAY.year, 12, 1), "1201")),
        ("1301", False, ""),
    ],
)
def test_mm_dd(filename, is_true, expected):
    """Test DatePattern.mm_dd."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.mm_dd() == expected
    else:
        assert d.mm_dd() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 202212", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", False, ""),
        ("1201", True, (date(TODAY.year, 1, 12), "1201")),
        ("1301", True, (date(TODAY.year, 1, 13), "1301")),
        ("3301", False, ""),
    ],
)
def test_dd_mm(filename, is_true, expected):
    """Test DatePattern.dd_mm."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.dd_mm() == expected
    else:
        assert d.dd_mm() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 202212", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", False, ""),
        ("Todays agenda", True, (date(TODAY.year, TODAY.month, TODAY.day), "Todays")),
        ("fooTodayBar", True, (date(TODAY.year, TODAY.month, TODAY.day), "Today")),
    ],
)
def test_today(filename, is_true, expected):
    """Test DatePattern.today."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.today() == expected
    else:
        assert d.today() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 202212", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", False, ""),
        (
            "Yesterday's agenda",
            True,
            (date(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day), "Yesterday's"),
        ),
        (
            "fooyesterday.bar",
            True,
            (date(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day), "yesterday"),
        ),
    ],
)
def test_yesterday(filename, is_true, expected):
    """Test DatePattern.yesterday."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.yesterday() == expected
    else:
        assert d.yesterday() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 202212", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", False, ""),
        (
            "tomorrow's agenda",
            True,
            (date(TOMORROW.year, TOMORROW.month, TOMORROW.day), "tomorrow's"),
        ),
        (
            "footomorrow bar",
            True,
            (date(TOMORROW.year, TOMORROW.month, TOMORROW.day), "tomorrow"),
        ),
    ],
)
def test_tomorrow(filename, is_true, expected):
    """Test DatePattern.tomorrow."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.tomorrow() == expected
    else:
        assert d.tomorrow() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 202212", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", False, ""),
        (
            "last week's agenda",
            True,
            (date(LAST_WEEK.year, LAST_WEEK.month, LAST_WEEK.day), "last week's"),
        ),
        (
            "foo last.week bar",
            True,
            (date(LAST_WEEK.year, LAST_WEEK.month, LAST_WEEK.day), "last.week"),
        ),
    ],
)
def test_last_week(filename, is_true, expected):
    """Test DatePattern.last_week."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.last_week() == expected
    else:
        assert d.last_week() is None


@pytest.mark.parametrize(
    ("filename", "is_true", "expected"),
    [
        ("file 202212", False, ""),
        ("string with no date", False, ""),
        ("foo 12232022 bar", False, ""),
        (
            "last Month's agenda",
            True,
            (date(LAST_MONTH.year, LAST_MONTH.month, LAST_MONTH.day), "last Month's"),
        ),
        (
            "foo last_month bar",
            True,
            (date(LAST_MONTH.year, LAST_MONTH.month, LAST_MONTH.day), "last_month"),
        ),
    ],
)
def test_last_month(filename, is_true, expected):
    """Test DatePattern.last_month."""
    d = DatePattern(string=filename)
    if is_true:
        assert d.last_month() == expected
    else:
        assert d.last_month() is None


def test_date_class(tmp_path):
    """Test Date class."""
    file = tmp_path / "test_file.txt"
    file.touch()
    ctime = datetime.fromtimestamp(file.stat().st_ctime)
    d = Date(date_format="%Y-%m-%d", string="a file with a date 2020-11-01", ctime=ctime)
    assert d.date == date(2020, 11, 1)
    assert d.original_string == "a file with a date 2020-11-01"
    assert d.date_format == "%Y-%m-%d"
    assert d.found_string == "2020-11-01"
    assert d.ctime == ctime

    d = Date(date_format="%Y-%m-%d", string="a file without date", ctime=ctime)
    assert d.date == date(ctime.year, ctime.month, ctime.day)
    assert d.original_string == "a file without date"
    assert d.date_format == "%Y-%m-%d"
    assert d.found_string is None
    assert d.ctime == ctime

    d = Date(date_format="%Y-%m-%d", string="no date")
    assert d.date is None
    assert d.original_string == "no date"
    assert d.date_format == "%Y-%m-%d"
    assert d.found_string is None
    assert d.ctime is None


@pytest.mark.parametrize(
    ("filename", "date_format", "expected"),
    [
        ("January 13,2020", "%B %d,%Y", "January 13,2020"),
        ("13th, jan 2019", "%Y, %b %d", "2019, Jan 13"),
        ("2021-09-03", "%m-%Y-%d", "09-2021-03"),
    ],
)
def test_reformat_date(filename, date_format, expected):
    """Test reformat_date."""
    d = Date(date_format=date_format, string=filename)
    assert d.reformatted_date == expected
