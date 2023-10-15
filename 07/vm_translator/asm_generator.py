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
}

segment_limit = {
    "local": LCL_LENGTH,
    "argument": ARG_LENGTH,
    "this": THIS_LENGTH,
    "that": THAT_LENGTH,
    "temp": TEMP_LENGTH,
    "static": STATIC_LENGTH,
    "pointer": 1,
}


class AsmGenerator:
    def __init__(self, filename: str):
        self.filename = filename
        self.output = ""
        self.operations = {
            "add": self._add,
            "sub": self._sub,
            "neg": self._neg,
            "eq": self._eq,
            "gt": self._gt,
            "lt": self._lt,
            "and": self._and,
            "or": self._or,
            "not": self._not,
        }

    def init_setup(self):
        self.writeln(self.generate_comment("Setup"))
        self.writeln("@256")
        self.writeln("D=A")
        self.writeln("@SP")
        self.writeln("M=D")
        # FIXME: This is for testing purposes
        self.writeln("@1000")
        self.writeln("D=A")
        self.writeln("@LCL")
        self.writeln("M=D")

        self.writeln("@2000")
        self.writeln("D=A")
        self.writeln("@THIS")
        self.writeln("M=D")

        self.writeln("@3000")
        self.writeln("D=A")
        self.writeln("@THAT")
        self.writeln("M=D")

    def end_setup(self):
        # self.d_is_true()
        pass

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

    def arithmetic_instruction(self, instruction: str):
        operation = instruction.lower().strip()
        if operation not in self.operations:
            raise Exception("Unexpected instruction: " + instruction)
        self.writeln(self.generate_comment(instruction))
        self.operations[operation]()

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
        IS_DIRECT_REFERENCE = memory_segment in ("static", "temp", "pointer")
        if relative_address == 0 or IS_DIRECT_REFERENCE:
            self.writeln(self.get_pointer(memory_segment, relative_address))
            if not IS_DIRECT_REFERENCE:
                self.writeln("A=M")
            return
        self.writeln(f"@{relative_address}")
        self.writeln("D=A")
        self.writeln(self.get_pointer(memory_segment, relative_address))
        self.writeln("A=M+D")

    def pop_instruction(self, memory_segment: str, relative_address: int):
        if memory_segment == "constant":
            raise Exception("Cannot pop to constant")

        if memory_segment in ("pointer", "static", "temp"):
            self._decrement_stack_pointer()
            self.writeln(self.get_pointer(memory_segment, relative_address))
            self.writeln("M=D")
            return
        if relative_address == 0:
            self._decrement_stack_pointer()
            self.writeln(self.get_pointer(memory_segment, relative_address))
            self.writeln("A=M")
            self.writeln("M=D")
            return
        self.writeln(f"@{relative_address}")
        self.writeln("D=A")
        self.writeln(self.get_pointer(memory_segment, relative_address))

        self.writeln("D=M+D")  # Address to save

        self.writeln("@R13")
        self.writeln("M=D")
        self._decrement_stack_pointer()

        self.writeln("@R13")
        self.writeln("A=M")
        self.writeln("M=D")

    def _increment_stack_pointer(self):
        self.writeln("@SP")
        self.writeln("M=M+1")

    def _decrement_stack_pointer(self, set_d_to_m: bool = True):
        self.writeln("@SP")
        self.writeln("AM=M-1")
        if set_d_to_m:
            self.writeln("D=M")

    def generate_comment(self, text: str):
        return f"{COMMENT_SYMBOL} {text}"

    def get_pointer(self, memory_segment: str, relative_address: int):
        if (limit := segment_limit.get(memory_segment)) and relative_address > limit:
            raise Exception(
                f"Address {relative_address} is out of bounds for '{memory_segment}'"
            )
        if memory_segment == "pointer":
            return "@THIS" if relative_address == 0 else "@THAT"
        if memory_segment == "static":
            return f"@{self.filename}.{relative_address}"
        if memory_segment == "temp":
            return f"@R{TEMP_START + relative_address}"
        return "@" + segments_pointer_names[memory_segment]

    def _add(self):
        self._decrement_stack_pointer(set_d_to_m=True)
        self._decrement_stack_pointer(set_d_to_m=False)
        self.writeln("M=D+M")
        self._increment_stack_pointer()

    def _sub(self):
        self._decrement_stack_pointer(set_d_to_m=True)
        self._decrement_stack_pointer(set_d_to_m=False)
        self.writeln("M=M-D")
        self._increment_stack_pointer()

    def _neg(self):
        self._decrement_stack_pointer(set_d_to_m=False)
        self.writeln("M=-M")
        self._increment_stack_pointer()

    def _set_d_to_true_if_not_0(self, jmp_instr: str = "JEQ"):
        label = f"END_IF_{len(self.output)}"
        self.writeln(f"@{label}")
        self.writeln(f"D;{jmp_instr}")
        self.writeln("D=-1")  # Skip this if is zero
        self.writeln(f"({label})")

    def _eq(self, jmp_instr: str = "JEQ"):
        self._decrement_stack_pointer(set_d_to_m=True)
        self._decrement_stack_pointer(set_d_to_m=False)
        self.writeln("D=D-M")
        self._set_d_to_true_if_not_0(jmp_instr)
        self.writeln("@SP")
        self.writeln("A=M")
        self.writeln("M=!D")
        self._increment_stack_pointer()

    def _gt(self):
        self._eq("JLT")

    def _lt(self):
        self._eq("JGT")

    def _and(self):
        pass

    def _or(self):
        pass

    def _not(self):
        self._decrement_stack_pointer(set_d_to_m=True)
        self._set_d_to_true_if_not_0()
        self.writeln("M=!D")
        self._increment_stack_pointer()

    # def d_is_true(self):
    #     self.writeln("(D_IS_TRUE)")
    #     self.writeln("@R14")
    #     self.writeln("A=M")
    #     self.writeln("D;JEQ")
    #     self.writeln("D=1")
    #     self.writeln("0;JMP")

    # def if_true_d_1(self):
    #     label = f"END_IF_{hash(len(self.output))}"
    #     self.writeln("@R13")
    #     self.writeln("M=D")
    #     self.writeln(f"@{label}")
    #     self.writeln("D=A")
    #     self.writeln("@R14")
    #     self.writeln("M=D")
    #     self.writeln("@R13")
    #     self.writeln("D=M")
    #     self.writeln(f"@D_IS_TRUE")
    #     self.writeln("D;JEQ")
    #     self.writeln("D=1")
    #     self.writeln(f"({label})")
