#!/usr/bin/python3


import os
from asm_generator import AsmGenerator
from vm_parser import VmParser
from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.add_argument("path", help="VM file or directory to translate")
argparser.add_argument("-o", "--output", help="Output file name")
argparser.add_argument(
    "--origin-directory",
    action="store_true",
    dest="origin_directory",
    help="Generates the file in the same directory as the input file if not output file is specified",
)
args = argparser.parse_args()


def main():
    code = AsmGenerator()
    source_files = [args.path]
    if os.path.isdir(args.path):
        code.init_setup()  # We only setup when compiling from a directory
        source_files = [
            os.path.join(args.path, f)
            for f in os.listdir(args.path)
            if os.path.isfile(os.path.join(args.path, f)) and f.endswith(".vm")
        ]
        if not source_files:
            print("No .vm files found in directory")
            return
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
            if parser.is_control_flow(line):
                code.control_flow_instruction(line)
                continue
            code.arithmetic_instruction(line)
    output = args.output
    if output is None:
        output = os.path.basename(os.path.normpath(args.path)).split(".")[0] + ".asm"
        if args.origin_directory:
            output = os.path.join(os.path.dirname(args.path), output)
    with open(output, "w") as f:
        f.write(code.output)
    print(output)


if __name__ == "__main__":
    main()
