"""Work with dates."""
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from jdfile._utils.alerts import logger as log


def parse_date(  # noqa: C901
    string: str,
    date_format: str = "%Y-%m-%d",
) -> tuple[None, None] | tuple[str | None, str]:
    """Parse date from string.

    Args:
        string: String to parse for a date.
        date_format: Date format to use. Defaults to "%Y-%m-%d".

    Returns:
        Tuple of (date as found in text, reformatted date) if date is found, else None.
    """
    yyyy_mm_dd = re.search(
        r"""
        # (?:.*[^0-9]|^)        # Start of string
        (?P<complete>
            (?P<year>20[0-2][0-9])
            [-\./_, :]*?
            (?P<month>0[1-9]|1[0-2])
            [-\./_, :]*?
            (?P<day>
            0[1-9]
            |
            [12][0-9]
            |
            3[01])
        )
        # (?:[^0-9].*|$)        # End of string from end of date
        """,
        string,
        re.X,
    )

    yyyy_dd_mm = re.search(
        r"""
        # (?:.*[^0-9]|^)        # Start of string until beginning of date (1)
        (?P<complete>
            (?P<year>20[0-2][0-9])
            [-\.\/_, :]*?
            (?P<day>0[1-9]|[12][0-9]|3[01])
            [-\.\/_, :]*?
            (?P<month>0[1-9]|1[0-2])
        )
        # (?:[^0-9].*|$)        # End of string from end of date
        """,
        string,
        re.X,
    )

    month_dd_yyyy = re.search(
        r"""
        (?P<complete>
            (?P<month>january|jan|ja|february|feb|fe|march|mar|ma|april|apr|ap|may|june|jun|july|jul|ju|august|aug|september|sep|october|oct|november|nov|december|dec)
            [-\./_, ]*?
            (?P<day>0?[1-9]|[12][0-9]|3[01])(?:nd|rd|th|st)?
            [-\./_, ]*?
            (?P<year>20[0-2][0-9])
        )
        ([^0-9].*|$) # End of string from end of date)
    """,
        string,
        re.X | re.I,
    )

    dd_month_yyyy = re.search(
        r"""
        (?:.*[^0-9]|^) # text before date
        (?P<complete>
            (?P<day>0?[1-9]|[12][0-9]|3[01])(?:nd|rd|th|st)?
            [-\./_, ]*
            (?P<month>january|jan|ja|february|feb|fe|march|mar|ma|april|apr|ap|may|june|jun|july|jul|ju|august|aug|september|sep|october|oct|november|nov|december|dec)
            [-\./_, ]*
            (?P<year>20[0-2][0-9])
        )
        (?:[^0-9].*|$) # text after date (7)
    """,
        string,
        re.X | re.I,
    )

    month_dd = re.search(
        r"""
        (?P<complete>
            (?P<month>january|jan|ja|february|feb|fe|march|mar|ma|april|apr|ap|may|june|jun|july|jul|ju|august|aug|september|sep|october|oct|november|nov|december|dec)
            [-\./_, ]*?
            (?P<day>0?[1-9]|[12][0-9]|3[01])(?:nd|rd|th|st)
        )
        ([^0-9].*|$) # End of string from end of date)
        """,
        string,
        re.X | re.I,
    )

    month_yyyy = re.search(
        r"""
        (?P<complete>
            (?P<month>january|jan|ja|february|feb|fe|march|mar|ma|april|apr|ap|may|june|jun|july|jul|ju|august|aug|september|sep|october|oct|november|nov|december|dec)
            [-\./_, ]*
            (?P<year>20[0-2][0-9])
        )
        (?:[^0-9].*|$)
        """,
        string,
        re.X | re.I,
    )

    yyyy_month = re.search(
        r"""
        (?P<complete>
            (?P<year>20[0-2][0-9])
            [-\./_, ]*
            (?P<month>january|jan|ja|february|feb|fe|march|mar|ma|april|apr|ap|may|june|jun|july|jul|ju|august|aug|september|sep|october|oct|november|nov|december|dec)
        )
        (?:[^0-9].*|$)
        """,
        string,
        re.X | re.I,
    )

    mmddyyyy = re.search(
        r"""
        (?:.*[^0-9]|^)
        (?P<complete>
            (?P<month>0[1-9]|1[0-2])
            [-\./_ :]*
            (?P<day>0[1-9]|[12][0-9]|3[01])
            [-\./_ :]*
            (?P<year>20[0-2][0-9])
            )
            (?:[^0-9].*|$)
        """,
        string,
        re.X | re.I,
    )

    ddmmyyyy = re.search(
        r"""
        (?:.*[^0-9]|^) # Text before date
        (?P<complete>
            (?P<day>0[1-9]|[12][0-9]|3[01])
            [-\.\/_ :]*?
            (?P<month>0[1-9]|1[0-2])
            [-\.\/_ :]*?
            (?P<year>20[0-2][0-9])
        )
        (?:[^0-9].*|$) # Text after date
        """,
        string,
        re.X | re.I,
    )

    mm_dd = re.search(
        r"""
        (?:.*[^0-9]|^) # Text before date
        (?P<complete>
            (?P<month>0[1-9]|1[0-2])
            [-\.\/_ ]*
            (?P<day>0[1-9]|[12][0-9]|3[01])
        )
        (?:[^0-9].*|$) # Text after date
        """,
        string,
        re.X | re.I,
    )

    dd_mm = re.search(
        r"""
        (?:.*[^0-9]|^) # Text before date
        (?P<complete>
            (?P<day>0[1-9]|[12][0-9]|3[01])
            [-\.\/_ ]*
            (?P<month>0[1-9]|1[0-2])
        )
        (?:[^0-9].*|$) # Text after date
        """,
        string,
        re.X | re.I,
    )

    if yyyy_mm_dd:
        log.trace("Found yyyy_mm_dd")
        year = yyyy_mm_dd.group("year")
        month = yyyy_mm_dd.group("month")
        day = yyyy_mm_dd.group("day")
        date_string = yyyy_mm_dd.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif yyyy_dd_mm:
        log.trace("Found yyyy_dd_mm")
        year = yyyy_dd_mm.group("year")
        month = yyyy_dd_mm.group("month")
        day = yyyy_dd_mm.group("day")
        date_string = yyyy_dd_mm.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif month_dd_yyyy:
        log.trace("Found month_dd_yyyy")
        year = month_dd_yyyy.group("year")
        month = month_to_number(month_dd_yyyy.group("month"))
        day = month_dd_yyyy.group("day")
        date_string = month_dd_yyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif dd_month_yyyy:
        log.trace("Found dd_month_yyyy")
        year = dd_month_yyyy.group("year")
        month = month_to_number(dd_month_yyyy.group("month"))
        day = dd_month_yyyy.group("day")
        date_string = dd_month_yyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif month_dd:
        log.trace("Found month_dd")
        year = date.today().year
        month = month_to_number(month_dd.group("month"))
        day = month_dd.group("day")
        date_string = month_dd.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif month_yyyy:
        log.trace("Found month_yyyy")
        year = month_yyyy.group("year")
        month = month_to_number(month_yyyy.group("month"))
        day = "01"
        date_string = month_yyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif yyyy_month:
        log.trace("Found yyyy_month")
        year = yyyy_month.group("year")
        month = month_to_number(yyyy_month.group("month"))
        day = "01"
        date_string = yyyy_month.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif mmddyyyy:
        log.trace("Found mmddyyyy")
        year = mmddyyyy.group("year")
        month = mmddyyyy.group("month")
        day = mmddyyyy.group("day")
        date_string = mmddyyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif ddmmyyyy:
        log.trace("Found ddmmyyyy")
        year = ddmmyyyy.group("year")
        month = ddmmyyyy.group("month")
        day = ddmmyyyy.group("day")
        date_string = ddmmyyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif mm_dd:
        log.trace("Found mm_dd")
        year = date.today().year
        month = mm_dd.group("month")
        day = mm_dd.group("day")
        date_string = mm_dd.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif dd_mm:
        log.trace("Found dd_mm")
        year = date.today().year
        month = dd_mm.group("month")
        day = dd_mm.group("day")
        date_string = dd_mm.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif string.lower() == "today" or string.lower() == "now":
        date_string = None
        constructed_date = date.today().strftime("%m/%d/%Y")
    elif string.lower() == "yesterday":
        date_string = None
        yesterday = date.today() - timedelta(days=1)
        constructed_date = yesterday.strftime("%m/%d/%Y")
    elif string.lower() == "tomorrow":
        date_string = None
        tomorrow = date.today() + timedelta(days=1)
        constructed_date = tomorrow.strftime("%m/%d/%Y")
    elif string.lower() == "last week":
        date_string = None
        last_week = date.today() - timedelta(days=7)
        constructed_date = last_week.strftime("%m/%d/%Y")
    elif string.lower() == "last month":
        date_string = None
        last_month = date.today() - timedelta(days=30)
        constructed_date = last_month.strftime("%m/%d/%Y")

    else:
        return None, None

    try:
        return date_string, datetime.strptime(constructed_date, "%m/%d/%Y").strftime(date_format)
    except ValueError:  # pragma: no cover
        log.error(f"{constructed_date} is not a valid date")
        return None, None


def create_date(file: Path, date_format: str = "%Y-%m-%d") -> str:
    """Create a date for a file.

    Args:
        file: (Path) The file to create a date for.
        date_format: (str) The format to use for the date.

    Returns:
        (str) The date for the file
    """
    try:
        created_date = Path(file).stat().st_ctime
        return datetime.fromtimestamp(created_date, tz=timezone.utc).strftime(date_format)
    except Exception:  # noqa: BLE001
        return date.today().strftime(date_format)


def month_to_number(month: str) -> str:  # noqa: C901
    """Convert a month name to a number.

    Args:
        month: (str) The month to convert.

    Returns:
        (str) The month number.
    """
    if re.match(r"^ja.*", month, re.I):
        return "01"
    if re.match(r"^fe.*", month, re.I):
        return "02"
    if re.match(r"^mar.*", month, re.I):
        return "03"
    if re.match(r"^ap.*", month, re.I):
        return "04"
    if re.match(r"^may.*", month, re.I):
        return "05"
    if re.match(r"^jun.*", month, re.I):
        return "06"
    if re.match(r"^jul.*", month, re.I):
        return "07"
    if re.match(r"^au.*", month, re.I):
        return "08"
    if re.match(r"^se.*", month, re.I):
        return "09"
    if re.match(r"^oc.*", month, re.I):
        return "10"
    if re.match(r"^no.*", month, re.I):
        return "11"
    if re.match(r"^de.*", month, re.I):
        return "12"

    return ""
