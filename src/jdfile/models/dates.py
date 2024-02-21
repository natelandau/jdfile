"""Date class for jdfile."""

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum

from jdfile.utils.alerts import logger as log


class MonthShort(Enum):
    """Enum for short month names."""

    JA = 1
    FE = 2
    MAR = 3
    AP = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AU = 8
    SE = 9
    OC = 10
    NO = 11
    DE = 12

    @classmethod
    def num_from_name(cls, month: str) -> str:
        """Convert a month name to a number."""
        for member in cls:
            if re.search(member.name, month, re.IGNORECASE):
                return str(member.value).zfill(2)

        return ""


@dataclass
class DatePattern:
    """Regex patterns to find dates in filename strings."""

    string: str
    pattern_day_flexible = r"0?[1-9]|[12][0-9]|3[01]"
    pattern_day_inflexible = r"0[1-9]|[12][0-9]|3[01]"
    pattern_month = r"0[1-9]|1[012]"
    pattern_months = r"january|jan?|february|feb?|march|mar?|april|apr?|may|june?|july?|august|aug?|september|sep?t?|october|oct?|november|nov?|december|dec?"
    pattern_separator = r"[-\./_, :]*?"
    pattern_year = r"20[0-2][0-9]"

    def yyyy_mm_dd(self) -> tuple[date, str] | None:
        """Search for a date in the format yyyy-mm-dd.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            # (?:.*[^0-9]|^)        # Start of string
            (?P<found>
                (?P<year>{self.pattern_year})
                {self.pattern_separator}
                (?P<month>{self.pattern_month})
                {self.pattern_separator}
                (?P<day>{self.pattern_day_inflexible})
            )
            # (?:[^0-9].*|$)        # End of string from end of date
            """,
            re.VERBOSE,
        )
        match = pattern.search(self.string)
        if match:
            try:
                return (
                    date(
                        int(match.group("year")), int(match.group("month")), int(match.group("day"))
                    ),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None

        return None

    def yyyy_dd_mm(self) -> tuple[date, str] | None:
        """Search for a date in the format yyyy-dd-mm.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            # (?:.*[^0-9]|^)
            (?P<found>
                (?P<year>{self.pattern_year})
                {self.pattern_separator}
                (?P<day>{self.pattern_day_inflexible})
                {self.pattern_separator}
                (?P<month>{self.pattern_month})
            )
            # (?:[^0-9].*|$)
            """,
            re.VERBOSE,
        )
        match = pattern.search(self.string)
        if match:
            try:
                return (
                    date(
                        int(match.group("year")), int(match.group("month")), int(match.group("day"))
                    ),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def month_dd_yyyy(self) -> tuple[date, str] | None:
        """Search for a date in the format month dd, yyyy.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?P<found>
                (?P<month>{self.pattern_months})
                {self.pattern_separator}
                (?P<day>{self.pattern_day_flexible})(?:nd|rd|th|st)?
                {self.pattern_separator}
                (?P<year>{self.pattern_year})
            )
            ([^0-9].*|$) # End of string from end of date)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            month = int(MonthShort.num_from_name(match.group("month")))

            try:
                return (
                    date(int(match.group("year")), month, int(match.group("day"))),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def dd_month_yyyy(self) -> tuple[date, str] | None:
        """Search for a date in the format dd month yyyy.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?:.*[^0-9]|^) # text before date
            (?P<found>
                (?P<day>{self.pattern_day_flexible})(?:nd|rd|th|st)?
                {self.pattern_separator}
                (?P<month>{self.pattern_months})
                {self.pattern_separator}
                (?P<year>{self.pattern_year})
            )
            (?:[^0-9].*|$) # text after date (7)
        """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            month = int(MonthShort.num_from_name(match.group("month")))
            try:
                return (
                    date(int(match.group("year")), month, int(match.group("day"))),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def month_dd(self) -> tuple[date, str] | None:
        """Search for a date in the format month dd.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?P<found>
                (?P<month>{self.pattern_months})
                {self.pattern_separator}
                (?P<day>{self.pattern_day_flexible})(?:nd|rd|th|st)?
            )
            ([^0-9].*|$) # End of string from end of date)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            month = int(MonthShort.num_from_name(match.group("month")))
            year = date.today().year
            try:
                return (
                    date(year, month, int(match.group("day"))),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def month_yyyy(self) -> tuple[date, str] | None:
        """Search for a date in the format month yyyy.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?P<found>
                (?P<month>{self.pattern_months})
                {self.pattern_separator}
                (?P<year>{self.pattern_year})
            )
            ([^0-9].*|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            month = int(MonthShort.num_from_name(match.group("month")))
            try:
                return (
                    date(int(match.group("year")), month, 1),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def yyyy_month(self) -> tuple[date, str] | None:
        """Search for a date in the format yyyy month.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?P<found>
                (?P<year>{self.pattern_year})
                {self.pattern_separator}
                (?P<month>{self.pattern_months})
            )
            ([^0-9].*|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            month = int(MonthShort.num_from_name(match.group("month")))
            try:
                return (
                    date(int(match.group("year")), month, 1),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def mmddyyyy(self) -> tuple[date, str] | None:
        """Search for a date in the format mmddyyyy.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?P<found>
                (?P<month>{self.pattern_month})
                {self.pattern_separator}
                (?P<day>{self.pattern_day_inflexible})
                {self.pattern_separator}
                (?P<year>{self.pattern_year})
            )
            ([^0-9].*|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            try:
                return (
                    date(
                        int(match.group("year")), int(match.group("month")), int(match.group("day"))
                    ),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def ddmmyyyy(self) -> tuple[date, str] | None:
        """Search for a date in the format ddmmyyyy.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?P<found>
                (?P<day>{self.pattern_day_inflexible})
                {self.pattern_separator}
                (?P<month>{self.pattern_month})
                {self.pattern_separator}
                (?P<year>{self.pattern_year})
            )
            ([^0-9].*|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            try:
                return (
                    date(
                        int(match.group("year")), int(match.group("month")), int(match.group("day"))
                    ),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def mm_dd(self) -> tuple[date, str] | None:
        """Search for a date in the format mm-dd.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?:^|[^0-9])
            (?P<found>
                (?P<month>{self.pattern_month})
                {self.pattern_separator}
                (?P<day>{self.pattern_day_inflexible})
            )
            (?:[^0-9]|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            year = date.today().year
            try:
                return (
                    date(year, int(match.group("month")), int(match.group("day"))),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def dd_mm(self) -> tuple[date, str] | None:
        """Search for a date in the format dd-mm.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            rf"""
            (?:^|[^0-9])
            (?P<found>
                (?P<day>{self.pattern_day_inflexible})
                {self.pattern_separator}
                (?P<month>{self.pattern_month})
            )
            (?:[^0-9]|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            year = date.today().year
            try:
                return (
                    date(year, int(match.group("month")), int(match.group("day"))),
                    str(match.group("found")),
                )
            except ValueError as e:
                log.trace(f"Error while reformatting date {match}: {e}")
                return None
        return None

    def today(self) -> tuple[date, str] | None:
        """Search for a date in the format today.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            r"""
            (?:^|[^0-9])
            (?P<found>
                (?P<today>today'?s?)
            )
            (?:[^0-9]|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            return (
                date.today(),
                str(match.group("found")),
            )
        return None

    def yesterday(self) -> tuple[date, str] | None:
        """Search for a date in the format yesterday.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            r"""
            (?:^|[^0-9])
            (?P<found>
                (?P<yesterday>yesterday'?s?)
            )
            (?:[^0-9]|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            yesterday = date.today() - timedelta(days=1)
            return (
                date(yesterday.year, yesterday.month, yesterday.day),
                str(match.group("found")),
            )
        return None

    def tomorrow(self) -> tuple[date, str] | None:
        """Search for a date in the format tomorrow.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            r"""
            (?:^|[^0-9])
            (?P<found>
                (?P<tomorrow>tomorrow'?s?)
            )
            (?:[^0-9]|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            tomorrow = date.today() + timedelta(days=1)
            return (
                date(tomorrow.year, tomorrow.month, tomorrow.day),
                str(match.group("found")),
            )
        return None

    def last_week(self) -> tuple[date, str] | None:
        """Search for a date in the format last week.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            r"""
            (?:^|[^0-9])
            (?P<found>
                (?P<last_week>last[- _\.]?week'?s?)
            )
            (?:[^0-9]|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            return (
                date.today() - timedelta(days=7),
                str(match.group("found")),
            )
        return None

    def last_month(self) -> tuple[date, str] | None:
        """Search for a date in the format last month.

        Args:
            string (str): String to search for a date.

        Returns:
            tuple[date, str]: A tuple containing the date and the date string found.
        """
        pattern = re.compile(
            r"""
            (?:^|[^0-9])
            (?P<found>
                (?P<last_month>last[- _\.]?month'?s?)
            )
            (?:[^0-9]|$)
            """,
            re.VERBOSE | re.IGNORECASE,
        )
        match = pattern.search(self.string)
        if match:
            return (
                date.today().replace(month=date.today().month - 1, day=1),
                str(match.group("found")),
            )
        return None


class Date:
    """Date class for jdfile."""

    def __init__(self, date_format: str, string: str, ctime: datetime | None = None) -> None:
        """Initialize the Date class.

        Args:
            date_format (str): Date format to use.
            string (str): String to search for a date.
            ctime (datetime, optional): Creation time of the file. Defaults to None.
        """
        self.original_string = string
        self.date_format = date_format
        self.ctime = ctime
        if self.date_format is None:
            self.date, self.found_string, self.reformatted_date = None, None, None
        else:
            self.date, self.found_string = self._find_date()
            self.reformatted_date = self._reformat_date()

    def _find_date(self) -> tuple:  # noqa: C901,PLR0911,PLR0912
        """Find date in a string and reformat it to self.date_format. If no date is found, return None.

        Args:
            text (str): The text to search for dates

        Returns:
            (tuple) A tuple containing the reformatted date and the date string found in the input.
        """
        date_search = DatePattern(self.original_string)
        if date_search.yyyy_mm_dd():
            return date_search.yyyy_mm_dd()

        if date_search.yyyy_dd_mm():  # pragma: no cover
            return date_search.yyyy_dd_mm()

        if date_search.month_dd_yyyy():  # pragma: no cover
            return date_search.month_dd_yyyy()

        if date_search.dd_month_yyyy():  # pragma: no cover
            return date_search.dd_month_yyyy()

        if date_search.month_dd():  # pragma: no cover
            return date_search.month_dd()

        if date_search.month_yyyy():  # pragma: no cover
            return date_search.month_yyyy()

        if date_search.yyyy_month():  # pragma: no cover
            return date_search.yyyy_month()

        if date_search.mmddyyyy():  # pragma: no cover
            return date_search.mmddyyyy()

        if date_search.ddmmyyyy():  # pragma: no cover
            return date_search.ddmmyyyy()

        if date_search.mm_dd():  # pragma: no cover
            return date_search.mm_dd()

        if date_search.dd_mm():  # pragma: no cover
            return date_search.dd_mm()

        if date_search.today():  # pragma: no cover
            return date_search.today()

        if date_search.yesterday():  # pragma: no cover
            return date_search.yesterday()

        if date_search.tomorrow():  # pragma: no cover
            return date_search.tomorrow()

        if date_search.last_week():  # pragma: no cover
            return date_search.last_week()

        if date_search.last_month():  # pragma: no cover
            return date_search.last_month()

        if self.ctime:
            return date(self.ctime.year, self.ctime.month, self.ctime.day), None

        return None, None

    def _reformat_date(self) -> str:
        """Reformat the date to self.date_format.

        Returns:
            str: Reformatted date.
        """
        if self.date:
            try:
                return self.date.strftime(self.date_format)
            except ValueError as e:
                log.trace(f"Error while reformatting date {self.date}: {e}")
                self.date, self.found_string, self.reformatted_date = None, None, None
        return None
