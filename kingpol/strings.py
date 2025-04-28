import re


def normalize_docstring(docstring: str) -> str:
    """Normalize a docstring by removing leading and trailing whitespace.

    Examples
    --------
    >>> normalize_docstring("  Hello World  ")
    'Hello World'
    >>> normalize_docstring("  Hello\\nWorld  ")
    'Hello\\nWorld'
    >>> normalize_docstring("  Hello\\n  World  ")
    'Hello\\nWorld'
    """
    return re.sub(r"^[ \t]+|[ \t]+$", "", docstring, flags=re.MULTILINE).strip()
