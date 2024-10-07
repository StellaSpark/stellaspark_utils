import hashlib


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
