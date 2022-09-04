"""Work with dates."""
import re
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path

from filemanager._utils.alerts import logger as log


def date_in_filename(
    stem: str, full_file: Path, add_date: bool | None, date_format: str, separator: Enum
) -> tuple[str, str]:
    """Add or remove a date from the beginning of a filename.

    Args:
        stem (str): The filename to add or remove a date from.
        full_file (Path): The full path to the file.
        add_date (bool): Whether to add a date to the beginning of the filename.
        date_format (str): The date format to use.
        separator (Enum): The separator to use.

    Returns:
        stem: The filename with the date optionally removed.
        new_date: The date and separator to prepend to the filename.
    """
    if add_date is None:
        return stem, ""
    else:
        date_string, new_date = parse_date(stem, date_format)
        if date_string is None:
            date_string = ""
            new_date = create_date(full_file, date_format)

    stem = stem.replace(date_string, "")

    if add_date is True:

        if separator == "underscore":
            sep = "_"
        elif separator == "dash":
            sep = "-"
        else:
            sep = " "
        date = f"{new_date}{sep}"
    else:
        date = ""

    return stem, date


def parse_date(  # noqa: C901
    string: str, date_format: str = "%Y-%m-%d"
) -> tuple[None, None] | tuple[str, str]:
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
        log.info("Found yyyy_mm_dd")
        year = yyyy_mm_dd.group("year")
        month = yyyy_mm_dd.group("month")
        day = yyyy_mm_dd.group("day")
        date_string = yyyy_mm_dd.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif yyyy_dd_mm:
        log.info("Found yyyy_dd_mm")
        year = yyyy_dd_mm.group("year")
        month = yyyy_dd_mm.group("month")
        day = yyyy_dd_mm.group("day")
        date_string = yyyy_dd_mm.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif month_dd_yyyy:
        log.info("Found month_dd_yyyy")
        year = month_dd_yyyy.group("year")
        month = month_to_number(month_dd_yyyy.group("month"))
        day = month_dd_yyyy.group("day")
        date_string = month_dd_yyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif dd_month_yyyy:
        log.info("Found dd_month_yyyy")
        year = dd_month_yyyy.group("year")
        month = month_to_number(dd_month_yyyy.group("month"))
        day = dd_month_yyyy.group("day")
        date_string = dd_month_yyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif month_yyyy:
        log.info("Found month_yyyy")
        year = month_yyyy.group("year")
        month = month_to_number(month_yyyy.group("month"))
        day = "01"
        date_string = month_yyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif yyyy_month:
        log.info("Found yyyy_month")
        year = yyyy_month.group("year")
        month = month_to_number(yyyy_month.group("month"))
        day = "01"
        date_string = yyyy_month.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif mmddyyyy:
        log.info("Found mmddyyyy")
        year = mmddyyyy.group("year")
        month = mmddyyyy.group("month")
        day = mmddyyyy.group("day")
        date_string = mmddyyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif ddmmyyyy:
        log.info("Found ddmmyyyy")
        year = ddmmyyyy.group("year")
        month = ddmmyyyy.group("month")
        day = ddmmyyyy.group("day")
        date_string = ddmmyyyy.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif mm_dd:
        log.info("Found mm_dd")
        year = date.today().year
        month = mm_dd.group("month")
        day = mm_dd.group("day")
        date_string = mm_dd.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    elif dd_mm:
        log.info("Found dd_mm")
        year = date.today().year
        month = dd_mm.group("month")
        day = dd_mm.group("day")
        date_string = dd_mm.group("complete")
        constructed_date = f"{month}/{day}/{year}"

    else:
        return None, None

    try:
        return date_string, datetime.strptime(constructed_date, "%m/%d/%Y").strftime(date_format)
    except ValueError:
        log.error(f"{constructed_date} is not a valid date")  # noqa: TC400
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
        return datetime.fromtimestamp(created_date, tz=timezone.utc).strftime(  # noqa: TC300
            date_format
        )
    except Exception:
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
    elif re.match(r"^fe.*", month, re.I):
        return "02"
    elif re.match(r"^mar.*", month, re.I):
        return "03"
    elif re.match(r"^ap.*", month, re.I):
        return "04"
    elif re.match(r"^may.*", month, re.I):
        return "05"
    elif re.match(r"^jun.*", month, re.I):
        return "06"
    elif re.match(r"^jul.*", month, re.I):
        return "07"
    elif re.match(r"^au.*", month, re.I):
        return "08"
    elif re.match(r"^se.*", month, re.I):
        return "09"
    elif re.match(r"^oc.*", month, re.I):
        return "10"
    elif re.match(r"^no.*", month, re.I):
        return "11"
    elif re.match(r"^de.*", month, re.I):
        return "12"

    return ""
