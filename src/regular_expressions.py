import re


def input_language_definitions(message: str) -> str:
    reg = "[a-zA-Z]+"
    result = re.search(reg, message)
    if result is None:
        return "ru"
    return "en"
