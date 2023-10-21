import constants as c
from constants import COMMENT_SYMBOL


segments_pointer_names = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
}

segment_limit = {
    "local": c.LCL_LENGTH,
    "argument": c.ARG_LENGTH,
    "this": c.THIS_LENGTH,
    "that": c.THAT_LENGTH,
    "temp": c.TEMP_LENGTH,
    "static": c.STATIC_LENGTH,
    "pointer": 1,
}


class AsmGenerator:
    filename = None

    def __init__(self):
        self.output = ""
        self.operations = {
            c.ADD: self._add,
            c.SUB: self._sub,
            c.NEG: self._neg,
            c.EQ: self._eq,
            c.GT: self._gt,
            c.LT: self._lt,
            c.AND: self._and,
            c.OR: self._or,
            c.NOT: self._not,
        }

    def set_filename(self, filename: str):
        self.filename = filename

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

    def write(self, text: str):
        self.output += text

    def writeln(self, text: str):
        self.write(text + "\n")

    def stack_instruction(self, instruction: str):
        operation, memory_segment, address = instruction.lower().strip().split()
        address = int(address)
        if address < 0:
            raise Exception("Address cannot be negative")
        self.writeln(self.generate_comment(instruction))
        if operation == c.PUSH:
            self.push_instruction(memory_segment, address)
            return
        if operation == c.POP:
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
            return f"@R{c.TEMP_START + relative_address}"
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

    def _eq(self):
        self._decrement_stack_pointer(set_d_to_m=True)
        self._decrement_stack_pointer(set_d_to_m=False)
        self.writeln("D=D-M")
        self._set_d_to_true_if_not_0()
        self.writeln("@SP")
        self.writeln("A=M")
        self.writeln("M=!D")
        self._increment_stack_pointer()

    def _gt(self):
        self.default_compare("JGT")

    def _lt(self):
        self.default_compare("JLT")

    def _and(self):
        self._decrement_stack_pointer(set_d_to_m=True)
        self._decrement_stack_pointer(set_d_to_m=False)
        self.writeln("M=D&M")
        self._increment_stack_pointer()

    def _or(self):
        self._decrement_stack_pointer(set_d_to_m=True)
        self._decrement_stack_pointer(set_d_to_m=False)
        self.writeln("M=D|M")
        self._increment_stack_pointer()

    def _not(self):
        self._decrement_stack_pointer(set_d_to_m=True)
        # self._set_d_to_true_if_not_0()  #! This may be unnecessary
        self.writeln("M=!D")
        self._increment_stack_pointer()

    def default_compare(self, jmp_instr: str):
        id = str(len(self.output))
        IF_TRUE = "IF_TRUE_" + id
        END_IF = "END_IF_" + id
        self._decrement_stack_pointer(set_d_to_m=True)
        self._decrement_stack_pointer(set_d_to_m=False)
        self.writeln("D=M-D")

        # IF
        self.writeln(f"@{IF_TRUE}")
        self.writeln(f"D;{jmp_instr}")
        self.writeln("D=0")
        self.writeln(f"@{END_IF}")
        self.writeln("0;JMP")
        self.writeln(f"({IF_TRUE})")
        self.writeln(f"D=-1")
        self.writeln(f"({END_IF})")
        # ENDIF

        # SET BOOLEAN TO STACK
        self.writeln("@SP")
        self.writeln("A=M")
        self.writeln("M=D")
        self._increment_stack_pointer()

    def control_flow_instruction(self, line: str):
        self.writeln(self.generate_comment(line))
        if line.startswith(c.LABEL):
            self.label_instruction(line)
            return
        if line.startswith(c.GOTO) or line.startswith(c.IF_GOTO):
            self.goto_instruction(line)
            return
        if line.startswith(c.FUNCTION):
            self.function_instruction(line)
            return
        if line.startswith(c.CALL):
            self.call_instruction(line)
            return
        if line.startswith(c.RETURN):
            self.return_instruction(line)
            return
        raise Exception("Unexpected instruction: " + line)

    def label_instruction(self, line: str):
        assert line.startswith(c.LABEL)
        _, label = line.split()
        self.writeln(f"({label})")

    def goto_instruction(self, line: str):
        assert line.startswith(c.GOTO) or line.startswith(c.IF_GOTO)
        _, label = line.split()
        if line.startswith(c.GOTO):
            self.writeln(f"@{label}")
            self.writeln("0;JMP")
            return
        self._decrement_stack_pointer()
        self.writeln(f"@{label}")
        self.writeln("D;JNE")

    def function_instruction(self, line: str):
        assert line.startswith(c.FUNCTION)

    def call_instruction(self, line: str):
        assert line.startswith(c.CALL)

    def return_instruction(self, line: str):
        assert line.startswith(c.RETURN)