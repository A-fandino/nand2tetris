from constants import SPECIAL_CHARACTERS


def sanitize_text(text: str):
    return "".join([SPECIAL_CHARACTERS.get(char, char) for char in text])
