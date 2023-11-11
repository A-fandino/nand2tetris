OPERATORS = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
UNARY_OPERATORS = {"-", "~"}
OTHER_SYMBOLS = {
    "{",
    "}",
    "(",
    ")",
    "[",
    "]",
    ".",
    ",",
    ";",
}

SYMBOL = {*OPERATORS, *UNARY_OPERATORS, *OTHER_SYMBOLS}

KEYWORD_CONST = {"true", "false", "null", "this"}
KEYWORDS = {
    "class",
    "constructor",
    "function",
    "method",
    "field",
    "static",
    "var",
    "int",
    "char",
    "boolean",
    "void",
    "let",
    "do",
    "if",
    "else",
    "while",
    "return",
}

WHITE_SPACE = {" ", "\t", "\n"}

MAX_INT = 32767

STRING_DELIMITER = '"'
