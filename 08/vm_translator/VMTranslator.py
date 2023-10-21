#!/usr/bin/python3


import os
from asm_generator import AsmGenerator
from vm_parser import VmParser
from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.add_argument("path", help="VM file or directory to translate")
argparser.add_argument("-o", "--output", help="Output file name")
args = argparser.parse_args()


def main():
    code = AsmGenerator()
    source_files = [args.path]
    if os.path.isdir(args.path):
        source_files = [
            os.path.join(args.path, f)
            for f in os.listdir(args.path)
            if os.path.isfile(os.path.join(args.path, f)) and f.endswith(".vm")
        ]
    for file in source_files:
        filename = os.path.basename(file)
        code.set_filename(filename.split(".")[0])
        code.writeln(code.generate_comment(f"Source File: {filename}"))
        with open(file, "r") as f:
            lines = f.read()
        parser = VmParser(lines)
        # code.init_setup()
        while (line := parser.next_line()) is not None:
            if not parser.is_instruction():
                continue
            if parser.is_push_pop():
                code.stack_instruction(line)
                continue
            code.arithmetic_instruction(line)
    output = args.output
    if output is None:
        output = os.path.basename(os.path.normpath(args.path)).split(".")[0] + ".asm"
    with open(output, "w") as f:
        f.write(code.output)
    print(output)


if __name__ == "__main__":
    main()
