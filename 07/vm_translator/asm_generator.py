COMMENT_SYMBOL = "//"

SP = 0
LCL = 1
ARG = 2
THIS = 3
THAT = 4

TEMP_START = 5
TEMP_LENGTH = 7

STATIC_START = 16
STATIC_LENGTH = 255 - STATIC_START

LCL_LENGTH, ARG_LENGTH, THIS_LENGTH, THAT_LENGTH = 1000, 1000, 1000, 1000


segments_pointers = {
    "local": LCL,
    "argument": ARG,
    "this": THIS,
    "that": THAT,
    "temp": TEMP_START,
    "static": STATIC_START,
}
segments_pointer_names = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    "temp": f"R{TEMP_START}",
}

segment_limit = {
    "local": LCL_LENGTH,
    "argument": ARG_LENGTH,
    "this": THIS_LENGTH,
    "that": THAT_LENGTH,
    "temp": TEMP_LENGTH,
    "static": STATIC_LENGTH,
}


class AsmGenerator:
    def __init__(self, filename: str):
        self.filename = filename
        self.output = ""

    def init_setup(self):
        self.writeln(self.generate_comment("Setup"))
        self.writeln("@256")
        self.writeln("D=A")
        self.writeln("@SP")
        self.writeln("M=D")
        self.writeln("@1015")  # FIXME: This is for testing purposes
        self.writeln("D=A")
        self.writeln("@LCL")
        self.writeln("M=D")

    def write(self, text: str):
        self.output += text

    def writeln(self, text: str):
        self.write(text + "\n")

    def stack_instruction(self, instruction: str):
        operation, memory_segment, address = instruction.lower().strip().split()
        address = int(address)
        self.writeln(self.generate_comment(instruction))
        if operation == "push":
            self.push_instruction(memory_segment, address)
            return
        if operation == "pop":
            self.pop_instruction(memory_segment, address)
            return
        raise Exception("Unexpected instruction: " + instruction)

    # def arithmetic_instruction(instruction: str):
    def push_instruction(self, memory_segment: str, relative_address: int):
        if memory_segment == "constant":
            self.writeln(f"@{relative_address}")
            self.writeln("D=A")
        else:
            self.point_to_address(memory_segment, relative_address)
            self.writeln("D=M")
        self.writeln("@SP")
        self.writeln("M=M+1")
        self.writeln("A=M-1")
        self.writeln("M=D")

    def point_to_address(self, memory_segment: str, relative_address: int):
        if memory_segment == "static":
            self.writeln(self.get_pointer(memory_segment, relative_address))
            return
        self.writeln(f"@{relative_address}")
        self.writeln("D=A")
        self.writeln(self.get_pointer(memory_segment))
        self.writeln("A=M+D")

    def pop_instruction(self, memory_segment: str, relative_address: int):
        if memory_segment == "constant":
            raise Exception("Cannot pop to constant")

        if relative_address == 0 or memory_segment in ("pointer", "static"):
            self.writeln("@SP")
            self.writeln("AM=M-1")
            self.writeln("D=M")
            self.writeln(self.get_pointer(memory_segment, relative_address))
            self.writeln("M=D")
            return
        self.writeln(f"@{relative_address}")
        self.writeln("D=A")
        self.writeln(self.get_pointer(memory_segment))

        self.writeln("D=M+D")  # Address to save

        self.writeln("@R13")
        self.writeln("M=D")
        self.writeln("@SP")
        self.writeln("AM=M-1")
        self.writeln("D=M")

        self.writeln("@R13")
        self.writeln("A=M")
        self.writeln("M=D")

    def generate_comment(self, text: str):
        return f"{COMMENT_SYMBOL} {text}"

    def get_pointer(self, memory_segment: str, relative_address: int = None):
        if (limit := segment_limit.get(memory_segment)) and relative_address > limit:
            raise Exception(
                f"Address {relative_address} is out of bounds for '{memory_segment}'"
            )
        if memory_segment == "pointer":
            if relative_address is None:
                raise Exception("Didn't get pointer address")
            return "@THIS" if relative_address == 0 else "@THAT"
        if memory_segment == "static":
            if relative_address is None:
                raise Exception("Static address must be provided")
            return f"@{self.filename}.{relative_address}"
        return "@" + segments_pointer_names[memory_segment]
