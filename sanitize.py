"""Input sanitization helpers.

One small, well-tested place for cleaning anything a user types.
HTML-escaping happens automatically at render time (Jinja2 autoescape),
so this module focuses on normalizing and bounding the raw input.
"""
import re

# Default cap on how much text we accept from a single field.
MAX_LEN = 10_000

# Control characters except tab (\x09), newline (\x0a), carriage return (\x0d).
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(raw, max_len: int = MAX_LEN) -> str:
    """Return a safe, bounded version of user-supplied text.

    - Coerces to str (never crashes on None / non-strings).
    - Removes control characters that have no business in a text field.
    - Trims surrounding whitespace.
    - Truncates to ``max_len`` characters.

    Note: this does NOT HTML-escape. Escaping is done at output time by the
    template engine (Jinja2 autoescape), which is the correct, context-aware
    place to do it. Never disable autoescape or use ``| safe`` on this text.
    """
    if raw is None:
        return ""
    text = str(raw)
    text = _CONTROL_CHARS.sub("", text)
    text = text.strip()
    if len(text) > max_len:
        text = text[:max_len]
    return text
