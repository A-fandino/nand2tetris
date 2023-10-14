#!/usr/bin/python3


from asm_generator import AsmGenerator
from vm_parser import VmParser


def main():
    with open("./test", "r") as f:
        lines = f.read()

    parser = VmParser(lines)
    code = AsmGenerator("test.asm")
    while (line := parser.next_line()) is not None:
        if not parser.is_instruction():
            continue
        code.stack_instruction(line)
    print(code.output)


if __name__ == "__main__":
    main()
