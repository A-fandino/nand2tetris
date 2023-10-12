#!/usr/bin/python3


from vm_parser import VmParser


def main():
    with open("../MemoryAccess/BasicTest/BasicTest.vm", "r") as f:
        lines = f.read()

    parser = VmParser(lines)
    while (line := parser.next_line()) is not None:
        if not parser.is_instruction():
            continue
        print(parser.lineNumber, "-", line)


if __name__ == "__main__":
    main()
