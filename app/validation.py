import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_recipient(name: str, email: str) -> str | None:
    if not name or not name.strip():
        return "Name must not be empty"
    if len(name) > 100:
        return "Name must be at most 100 characters"
    if not EMAIL_RE.match(email):
        return "Invalid email address"
    return None
