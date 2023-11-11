class JackTokenizer:
    input_file: str = ""
    file_content: str
    tokens: str = "<tokens>\n"
    pointer: int = 0
    current_token: str = ""

    def __init__(self, input_file: str):
        self.input_file = input_file
        with open(input_file, "r") as f:
            self.file_content = f.read()

    def next_char(self, advance=True):
        if self.pointer < len(self.tokens):
            curr_pointer = self.pointer
            if advance:
                self.pointer += 1
            return self.tokens[curr_pointer]
        return None

    def current_char(self):
        return self.file_content[self.pointer]

    def compute_tokens(self):
        self.reset()
        while (char := self.next_char()) is not None:
            pass
        self.end()

    def add_token(self, type: str, token: str):
        self.tokens += f"<{type}>{token}</{type}>"

    def end(self):
        self.tokens += "</tokens>\n"
        filename = self.input_file.split(".")[0] + "T.xml"
        with open(filename, "w") as f:
            f.write(self.tokens)

    def reset(self):
        self.pointer = 0
        self.tokens = "<tokens>\n"
        self.current_token = ""
