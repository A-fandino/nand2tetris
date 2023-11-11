from constants import MAX_INT, STRING_DELIMITER, SYMBOL, WHITE_SPACE
import re


class JackTokenizer:
    input_file: str = ""
    file_content: str
    tokens: str = "<tokens>\n"
    pointer: int = -1
    current_token: str = ""

    # Could be calculated (maybe expensive)
    line = 1
    lineChar = 1

    def __init__(self, input_file: str):
        self.input_file = input_file
        with open(input_file, "r") as f:
            self.file_content = f.read()

    def next_char(self, advance=True):
        if self.pointer < (len(self.file_content) - 1):
            curr_pointer = self.pointer + 1
            if advance:
                self.lineChar += 1
                self.pointer = curr_pointer
            return self.file_content[curr_pointer]
        return None

    def prev_char(self):
        self.pointer -= 1
        return self.current_char

    @property
    def current_char(self):
        return self.file_content[self.pointer]

    def compute_tokens(self):
        self.reset()
        while (char := self.next_char()) is not None:
            if self.is_whitespace(char):
                if char == "\n":
                    self.new_line()
                continue
            if char == STRING_DELIMITER:
                self.tokenize_string()
                self.add_current_token("stringConstant")
                continue
            if char.isdigit():
                self.tokenize_int()
                self.add_current_token("integerConstant")
                continue
        self.end()

    def tokenize_string(self):
        while (char := self.next_char()) not in (STRING_DELIMITER, None):
            self.current_token += char
        if char is None:
            self.panic("String not closed")

    def tokenize_int(self):
        self.prev_char()
        while (char := self.next_char()) is not None and char.isdigit():
            self.current_token += char
        if char is not None and re.match("[a-zA-Z]", char):
            self.panic(f"Invalid character {char} after int constant")
        if int(self.current_token) > MAX_INT:
            self.panic("Int constant too large")

    def tokenize_identifier(self):
        self.prev_char()
        while (char := self.next_char()) is not None and not self.is_whitespace(char):
            if not re.match("[a-zA-Z][0-9]_"):
                self.panic(f"Invalid character {char} found in identifier")
            self.current_token += char
        # TODO:

    def is_whitespace(self, char: str):
        return char in WHITE_SPACE

    def add_token(self, type: str, token: str):
        self.tokens += f"\t<{type}>{token}</{type}>\n"

    def add_current_token(self, type: str):
        self.add_token(type, self.current_token)
        self.current_token = ""

    def end(self):
        self.tokens += "</tokens>\n"
        filename = self.input_file.split(".")[0] + "T.xml"
        with open(filename, "w") as f:
            f.write(self.tokens)

    def reset(self):
        self.pointer = -1
        self.tokens = "<tokens>\n"
        self.current_token = ""
        self.line = 1
        self.lineChar = 1

    def new_line(self):
        self.line += 1
        self.lineChar = 1

    def panic(self, message: str):
        raise Exception(f"{message} at line {self.line} (char: {self.lineChar})")
