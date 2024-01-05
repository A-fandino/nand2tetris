import os

from CodeGenerator import CodeGenerator
from Tokenizer import JackTokenizer
from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.add_argument("path", help="Jack file or directory to translate")
# argparser.add_argument("-o", "--output", help="Output file name")
argparser.add_argument(
    "--in-origin",
    action="store_true",
    dest="in_origin",
    help="Generates the file in the same directory as the input file if not output file is specified",
)
args = argparser.parse_args()


def get_input_files():
    if os.path.isfile(args.path):
        return [args.path]
    source_files = [
        os.path.join(args.path, f)
        for f in os.listdir(args.path)
        if os.path.isfile(os.path.join(args.path, f)) and f.endswith(".jack")
    ]
    if not source_files:
        raise Exception("No .jack files found in directory")
    return source_files


def get_output_file(file: str, tokenized: bool = False):
    filename, _ = os.path.splitext(os.path.basename(file))
    path = filename
    if args.in_origin:
        dirname = os.path.dirname(file)
        path = os.path.join(dirname, filename)

    ext = ".vm"
    if tokenized:
        ext = "T.xml"
    return path + ext


def main():
    input_files = get_input_files()
    for file in input_files:
        tokenizer = JackTokenizer(file)
        tokenizer.compute_tokens()
        tokenizer.generate_xml_file(get_output_file(file, True))

        engine = CodeGenerator(tokenizer, get_output_file(file))
        engine.compile()
        engine.generate_file()


if __name__ == "__main__":
    main()
