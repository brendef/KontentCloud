import re


def validate_email(email) -> str:

    if not re.search(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email address"

    return ""


def validate_password(password):

    if len(password) < 6:
        return "Password must be at least 6 characters long"

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"

    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit"

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"

    return ""
