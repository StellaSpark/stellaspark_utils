from calendar import monthrange
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Tuple
from typing import Union

import hashlib
import pytz
import re
import unidecode


def q(ids: Union[str, List[str], Tuple[str]]) -> Union[str, List[str]]:
    """Return quoted and sanitized SQL column or table identifiers."""
    if isinstance(ids, (list, tuple)):
        return [f'"{_id}"' for _id in ids]
    else:
        return f'"{ids}"'


def sq(string: Union[str, List]) -> List[str]:
    """Return single-quoted strings that are safe for HTML."""
    return (
        [chr(39) + str(elem) + chr(39) for elem in string]
        if isinstance(string, (list, tuple))
        else chr(39) + str(string) + chr(39)
    )


def to_lwu(
    string: str,
    keep_colons: bool = True,
    keep_minus: bool = False,
    keep_double_underscores: bool = False,
) -> str:
    """Convert string to lowercase_with_underscores format.

    Also replace dots and hyphens with underscores for Postgres table name compatibility. Maintaining or removing
    colons is optional, since some Nexus identifiers may contain these (such as GeoServer layers) whereas other
    identifiers are not allowed to have this (e.g. Postgres colnames)
    """
    # Order to_replace matters!
    to_replace = {
        "<>": "_uneq_",
        ">=": "_gte_",
        "=>": "_gte_",
        "<=": "_lte_",
        "=<": "_lte_",
        ">": "_gt_",
        "<": "_lt_",
        "!=": "_uneq_",
        "==": "_eq_",
        "=": "_eq_",
        "%": "_pct_",
        "°": "_deg_",
        "&": "_and_",
    }

    # Make sure that the space is always replaced between the minuses
    to_underscore = [" "] if keep_minus else [" - ", " ", "-"]
    to_underscore.extend([".", "+", ",", "/"])

    if not keep_double_underscores:
        to_underscore.append("__")

    to_underscore.extend(["___", "____"])  # Order here matters, replace duplicate underscores last
    to_remove = [
        "[",
        "]",
        "(",
        ")",
        "{",
        "}",
        "#",
        ";",
        "'",
        '"',
        "?",
        "!",
        "*",
        "@",
        "$",
        "|",
    ]

    if not keep_colons:
        to_remove.append(":")

    for substr, replacement in to_replace.items():
        string = string.replace(substr, replacement)

    for substr in to_underscore:
        string = string.replace(substr, "_")

    for substr in to_remove:
        string = string.replace(substr, "")

    # Ensure that final string does not have _ at the end or start
    string = string.strip("_")
    string = unidecode.unidecode(string)  # Remove any accents, convert greek, cyrillic or chinese characters

    return string.lower()


def is_float(string: str) -> bool:
    """Quickly check if string is also a valid number."""
    try:
        float(string)
        return True
    except ValueError:
        return False


def extract_sql_columns(sql_string: str) -> List[str]:
    """Extract column names from an SQL 'where' statement."""
    split_by = " and | or | in | not between | between | order by | asc | desc | is null| is not null|!=|<=|>=|<>|>|<|="
    elems = re.split(split_by, sql_string.lower())
    elems = [elem.strip() for elem in elems]

    # Not a column if it is a number, a single-quoted item, or an expression with spaces (such as 'limit 1')
    cols = [elem for elem in elems if (not bool(re.search("[' ()]", elem)) and (not is_float(elem)) and elem)]
    return cols


def parse_time_placeholders(string: str) -> str:
    """Substitute time placeholders.

    Substitute the following placeholders with current year, month and days respectively (possibly with a subtraction):
     - {-30:%Y-%m-%d}
     - {%Y}
     - {%Y/%m/%d}

    https://www.programiz.com/python-programming/datetime/strftime
    """
    # Find fields that contain placeholders with percent signs (datetime-like)
    fields = re.findall(r"{([-|%|\d].+?)}", string)
    contains_any = ("%",)
    fields = [field for field in fields if any(substr in field for substr in contains_any)]
    if not fields:
        return string

    now = datetime.now()
    for field in fields:
        if ":" in field:
            days = 0
            seconds = 0
            if "day" in field:
                field_sanitized = re.sub(r"[a-zA-Z]", "", field.split("day")[0]).strip()
                days = int(eval(field_sanitized))
            elif "year" in field:
                field_sanitized = re.sub(r"[a-zA-Z]", "", field.split("year")[0]).strip()
                years = int(eval(field_sanitized))
                days = get_days_offset(now.year, now.month, years_offset=years)
            elif "second" in field:
                field_sanitized = re.sub(r"[a-zA-Z]", "", field.split("second")[0]).strip()
                seconds = int(eval(field_sanitized))
            else:
                raise ValueError("Unknown time offset")

            timestamp = now + timedelta(days=days, seconds=seconds)
            pos = field.find(":")
            if field[pos + 1 :] == "%unix":  # noqa
                string = string.replace("{" + field + "}", str(int(timestamp.timestamp())))
            else:
                string = string.replace("{" + field + "}", eval(f"{timestamp: f'{field[pos + 1:]}'}"))
        else:
            if field == "%unix":
                string = string.replace("{" + field + "}", str(int(now.timestamp())))
            else:
                string = string.replace("{" + field + "}", eval(f"{now: f'{field}'}"))

    return string


def get_days_offset(
    year: int,
    month: int,
    years_offset: int = 0,
    months_offset: int = 0,
    days_offset: int = 0,
) -> int:
    """Get offset in days, counting from the given year and current month.

    In case of a net-negative offset, the returned number of days will be negative. Vise versa.
    """
    # To account for leap years, also add the years offset to the months, we calculate the amount of days in one go
    months_offset = months_offset + (12 * years_offset)

    days = 0
    for _ in range(0, abs(months_offset)):
        if months_offset < 0:
            if month == 1:
                year = year - 1
                month = 12
            else:
                month = month - 1
            days = days - monthrange(year, month)[1]
        else:
            if month == 12:
                year = year + 1
                month = 1
            else:
                month = month + 1
            days = days + monthrange(year, month)[1]

    days = days + days_offset

    return days


def ensure_tz_aware(datetime_string: str) -> str:
    """Ensure that datetime string is iso-formatted and is timezone aware."""
    datetime_obj = datetime.fromisoformat(datetime_string)
    is_tz_aware = datetime_obj.tzinfo is not None and datetime_obj.tzinfo.utcoffset(datetime_obj) is not None
    if is_tz_aware:
        return datetime_string
    datetime_obj_tz = datetime_obj.replace(tzinfo=pytz.utc)  # Make timezone aware (UTC)
    return datetime_obj_tz.isoformat()


def make_identifier(string: str) -> str:
    """Make a PG-compatible identifier (table names, column names, constraint names, etc.).

    - Ensure that any double-quotes are removed from the candidate-name
    - Identifiers are limited to a maximum length of 63 bytes. In case we have an identifier that is longer than
      allowed length, limit the length in a smart way; e.g. by maintaining the last part while creating a hash for the
      first part.
    """
    PG_COLNAME_LIMIT = 63

    string = str(string)  # Convert ints etc.
    string = string.replace('"', "").replace("%", "pct")  # Make sure there are no quotes within column name

    if len(string) > PG_COLNAME_LIMIT:
        # Shorten column to reasonable length. Prefix hash with 't' character, since hash may begin with number, which
        # is invalid as PG column name
        string_split = string.split("_")
        string = f"t{hashlib.sha224('_'.join(string_split[0:-1]).encode('utf8')).hexdigest()[:7]}_{string_split[-1]}"

    return string
