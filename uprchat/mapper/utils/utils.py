import re


def sanitize_str_value(value):
    if isinstance(value, str):
        return re.sub(r"[\"\'`]", " ", value)
    return value
