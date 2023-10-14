COMMENT_SYMBOL = "//"

SP = 0
LCL = 1
ARG = 2
THIS = 3
THAT = 4

TEMP_START = 5
TEMP_END = 12

STATIC_START = 16
STATIC_END = 255

STACK_START = 256
STACK_END = 2047

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
    "static": "256",
}


class AsmGenerator:
    def __init__(self, filename: str):
        self.filename = filename
        self.output = ""

    def write(self, text: str):
        self.output += text

    def writeln(self, text: str):
        self.write(text + "\n")

    def stack_instruction(self, instruction: str):
        [operation, memory_space, address] = instruction.lower().strip()
        self.writeln(self.generate_comment(instruction))
        if operation == "push":
            self.push_instruction(memory_space, address)
            return
        if operation == "pop":
            # code += self.pop_instruction(memory_space, address)
            return
        raise Exception("Unexpected instruction: " + instruction)

    # def arithmetic_instruction(instruction: str):
    def push_instruction(self, memory_space: str, relative_address: int):
        if memory_space == "constant":
            self.writeln(f"@{relative_address}")
            self.writeln("D=A")
        else:
            self.point_to_address(memory_space, relative_address)
            self.writeln("D=M")
        self.writeln(f"@{SP}")
        self.writeln("M=M+1")

    def point_to_address(self, memory_space: str, relative_address: int):
        if memory_space == "static":
            self.writeln(f"@{self.filename}.{relative_address}")
            return
        self.writeln(f"@{relative_address}")
        self.writeln("D=A")
        self.writeln(self.get_pointer(memory_space))
        self.writeln("A=M+D")

    def pop_instruction(self, memory_space: str, relative_address: int):
        if memory_space == "constant":
            raise Exception("Cannot pop to constant")

        self.writeln(f"@{relative_address}")
        self.writeln("D=A")
        self.writeln(self.get_pointer(memory_space))

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
        return f"{COMMENT_SYMBOL} {text}\n"

    def get_pointer(memory_space: str):
        return "@" + segments_pointers[memory_space]
