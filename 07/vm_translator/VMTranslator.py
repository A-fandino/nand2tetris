#!/usr/bin/python3


import os
from asm_generator import AsmGenerator
from vm_parser import VmParser
from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.add_argument("filepath", help="VM file to translate")
argparser.add_argument("-o", "--output", help="Output file name")
args = argparser.parse_args()


def main():
    filename = os.path.basename(args.filepath).split(".")[0]
    with open(args.filepath, "r") as f:
        lines = f.read()
    parser = VmParser(lines)
    code = AsmGenerator(filename)
    # code.init_setup()
    while (line := parser.next_line()) is not None:
        if not parser.is_instruction():
            continue
        if parser.is_push_pop():
            code.stack_instruction(line)
            continue
        code.arithmetic_instruction(line)
    code.end_setup()
    output = args.output
    if output is None:
        output = filename + ".asm"
    with open(output, "w") as f:
        f.write(code.output)
    print(output)


if __name__ == "__main__":
    main()
