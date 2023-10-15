#!/usr/bin/python3


from asm_generator import AsmGenerator
from vm_parser import VmParser


def main():
    with open("./Test.vm", "r") as f:
        lines = f.read()

    parser = VmParser(lines)
    code = AsmGenerator("Test.asm")
    code.init_setup()
    while (line := parser.next_line()) is not None:
        if not parser.is_instruction():
            continue
        if parser.is_push_pop():
            code.stack_instruction(line)
            continue
        code.arithmetic_instruction(line)
    code.end_setup()
    print(code.output)
    with open("./Test.asm", "w") as f:
        f.write(code.output)


if __name__ == "__main__":
    main()
