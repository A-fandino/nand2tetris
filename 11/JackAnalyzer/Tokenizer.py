from __future__ import annotations

from utils import sanitize_text
from constants import (
    KEYWORDS,
    MAX_INT,
    STRING_DELIMITER,
    SYMBOL,
    WHITE_SPACE,
)
import re


class JackTokenizer:
    file_content: str
    file_name: str
    # tokens: str = "<tokens>\n"
    tokens: list = []
    pointer: int = -1
    current_token: str = ""
    token_pointer: int = -1
    # Could be calculated (may be expensive)
    line = 1
    lineChar = 1

    def __init__(self, input_file: str):
        self.file_name = input_file
        with open(input_file, "r") as f:
            self.file_content = f.read()

    def _generate_metadata(self):
        return {"line": self.line, "char": self.lineChar, "file": self.file_name}

    def advance(self) -> dict:
        if self.token_pointer < len(self.tokens):
            self.token_pointer += 1
        return self.get_token()

    def get_token(self):
        return (
            self.tokens[self.token_pointer]
            if len(self.tokens) > self.token_pointer
            else {"token": "EOF", "metadata": self._generate_metadata(), "type": "EOF"}
        )

    def has_more_tokens(self):
        return self.token_pointer < len(self.tokens) - 1

    def next_char(self, advance=True):
        if self.pointer < (len(self.file_content)):
            next_ptr = self.pointer + 1
            if advance:
                self.lineChar += 1
                self.pointer = next_ptr
                if self.current_char == "\n":
                    self.new_line()
            return (
                self.file_content[next_ptr]
                if next_ptr < len(self.file_content)
                else None
            )
        return None

    def prev_char(self):
        # Decrease line char if we are going back to the previous line
        if self.current_char == "\n":
            self.line -= 1
        self.pointer -= 1
        return self.current_char

    @property
    def current_char(self):
        return (
            self.file_content[self.pointer]
            if self.pointer >= 0 and self.pointer < len(self.file_content)
            else None
        )

    def compute_tokens(self):
        self.reset()
        while (char := self.next_char()) is not None:
            if self.is_whitespace(char):
                continue
            if char == STRING_DELIMITER:
                self.tokenize_string()
                self.add_current_token("stringConstant")
                continue
            if char.isdigit():
                self.tokenize_int()
                self.add_current_token("integerConstant")
                continue
            if re.match("[a-zA-Z_]", char):
                self.tokenize_identifier()
                self.add_current_token(
                    "keyword" if self.current_token in KEYWORDS else "identifier"
                )
                continue
            if char == "/":
                next_char = self.next_char(advance=False)
                if next_char in ("/", "*"):
                    self.skip_comment()
                    continue
            if char in SYMBOL:
                self.add_token("symbol", char)
                continue
        self.end()

    def tokenize_string(self):
        while (char := self.next_char()) not in (STRING_DELIMITER, None):
            self.add_to_token(char)
        if char is None:
            self.panic("String not closed")

    def tokenize_int(self):
        self.prev_char()
        while (char := self.next_char()) is not None and char.isdigit():
            self.add_to_token(char)
        if char is not None and re.match("[a-zA-Z]", char):
            self.panic(f"Invalid character {char} after int constant")
        if int(self.current_token) > MAX_INT:
            self.panic("Int constant too large")
        self.prev_char()

    def tokenize_identifier(self):
        self.add_to_token(self.current_char)
        while (char := self.next_char()) is not None and re.match("[a-zA-Z0-9_]", char):
            self.add_to_token(char)
        self.prev_char()

    def skip_comment(self):
        char = self.next_char()
        if char == "/":
            while (char := self.next_char()) != "\n" and char is not None:
                pass
            return
        if char == "*":
            self.prev_char()
            while (
                (char := self.next_char()) != "*"
                or self.next_char(advance=False) != "/"
            ) and char is not None:
                pass
            self.next_char()
            return
        # Revert back to the previous char in case it is not a comment
        self.prev_char()

    def is_whitespace(self, char: str):
        return char in WHITE_SPACE

    def add_token(self, type: str, token: str):
        self.tokens.append(
            {"type": type, "token": token, "metadata": self._generate_metadata()}
        )

    def add_to_token(self, char: str):
        self.current_token += char

    def add_current_token(self, type: str):
        self.add_token(type, self.current_token)
        self.current_token = ""

    def end(self):
        pass

    def reset(self):
        self.pointer = -1
        self.tokens = []
        self.current_token = ""
        self.line = 1
        self.lineChar = 1

    def new_line(self):
        self.line += 1
        self.lineChar = 1

    def panic(self, message: str):
        raise Exception(f"{message} at line {self.line} (char: {self.lineChar})")

    def generate_xml_file(self, filename):
        xml_output = "<tokens>\n"
        for token in self.tokens:
            type = token["type"]
            sane_token = sanitize_text(token["token"])
            xml_output += f"<{type}> {sane_token} </{type}>\n"
        xml_output += "</tokens>\n"
        with open(filename, "w") as f:
            f.write(xml_output)
