from typing import Optional
import constants as c


class VmParser:
    text: str = None
    textLines: list = None
    lineNumber: int
    instructionNumber: int

    def __init__(self, text: str):
        self.text = text
        self.textLines = text.splitlines()
        self.reset()

    def next_line(self):
        self.lineNumber += 1
        if self.is_instruction():
            self.instructionNumber += 1
        return self.get_line()

    def get_line(
        self, strip: bool = True, remove_comments: bool = True
    ) -> Optional[str]:
        if self.lineNumber >= len(self.textLines):
            return None
        line = self.textLines[self.lineNumber]
        if remove_comments:
            line = line.split(c.COMMENT_SYMBOL)[0].strip()
        if strip:
            line = line.strip()
        return line

    def is_instruction(self) -> bool:
        line = self.get_line()
        return line and not line.startswith(c.COMMENT_SYMBOL)

    def is_whitespace(self) -> bool:
        line = self.get_line()
        return not line or line.startswith(c.COMMENT_SYMBOL)

    def is_push_pop(self) -> bool:
        line = self.get_line()
        return line.startswith((c.PUSH, c.POP))

    def is_control_flow(self, instruction: str) -> bool:
        command = instruction.split()[0]
        return command in c.FLOW_CONTROL_COMMANDS

    def reset(self):
        self.lineNumber = -1
        self.instructionNumber = 0
