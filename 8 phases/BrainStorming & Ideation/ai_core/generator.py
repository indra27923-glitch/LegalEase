import re
from typing import Iterable


def sanitize_text(value: str) -> str:
    """
    Clean unnecessary whitespace from user input.
    """
    if not value:
        return ""

    value = str(value).replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive spaces while keeping line breaks.
    value = re.sub(r"[ \t]+", " ", value)

    # Remove excessive blank lines.
    value = re.sub(r"\n{3,}", "\n\n", value)

    return value.strip()


def split_terms(terms: str) -> list[str]:
    """
    Convert semicolon-separated terms into a clean list.

    Example:
        "Salary: 50000; Notice period: 30 days"
    
    becomes:
        ["Salary: 50000", "Notice period: 30 days"]
    """
    if not terms:
        return []

    cleaned = sanitize_text(terms)

    return [
        item.strip()
        for item in cleaned.split(";")
        if item.strip()
    ]


def iter_clean_lines(text: str) -> Iterable[str]:
    """
    Return non-empty cleaned lines from generated document text.
    """
    if not text:
        return []

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return lines