from enum import Enum


class Keyword(Enum):
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    INT = "int"
    BOOLEAN = "boolean"
    CHAR = "char"
    VOID = "void"
    VAR = "var"
    STATIC = "static"
    FIELD = "field"
    LET = "let"
    DO = "do"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    THIS = "this"


class Symbol(Enum):
    LEFT_CURLY_BRACKET = "{"
    RIGHT_CURLY_BRACKET = "}"
    LEFT_BRACKET = "("
    RIGHT_BRACKET = ")"
    LEFT_SQUARE_BRACKET = "["
    RIGHT_SQUARE_BRACKET = "]"
    DOT = "."
    COMMA = ","
    SEMICOLON = ";"
    PLUS_SIGN = "+"
    MINUS_SIGN = "-"
    ASTERISK = "*"
    SLASH = "/"
    AMPERSAND = "&"
    VERTICAL_BAR = "|"
    LESS_THAN_SIGN = "<"
    GREATER_THAN_SIGN = ">"
    EQUAL_SIGN = "="
    TILDE = "~"


OPERATORS_CODE = {
    Symbol.PLUS_SIGN.value: "add",
    Symbol.MINUS_SIGN.value: "sub",
    Symbol.AMPERSAND.value: "and",
    Symbol.VERTICAL_BAR.value: "or",
    Symbol.LESS_THAN_SIGN.value: "lt",
    Symbol.GREATER_THAN_SIGN.value: "gt",
    Symbol.EQUAL_SIGN.value: "eq",
    Symbol.ASTERISK.value: "call Math.multiply 2",
    Symbol.SLASH.value: "call Math.divide 2",
}

OPERATORS = list(OPERATORS_CODE.keys())

UNARY_CODE = {
    Symbol.MINUS_SIGN.value: "neg",
    Symbol.TILDE.value: "not",
}

UNARY_OPERATORS = list(UNARY_CODE.keys())

OTHER_SYMBOLS = [
    Symbol.LEFT_CURLY_BRACKET.value,
    Symbol.RIGHT_CURLY_BRACKET.value,
    Symbol.LEFT_BRACKET.value,
    Symbol.RIGHT_BRACKET.value,
    Symbol.LEFT_SQUARE_BRACKET.value,
    Symbol.RIGHT_SQUARE_BRACKET.value,
    Symbol.DOT.value,
    Symbol.COMMA.value,
    Symbol.SEMICOLON.value,
]

SYMBOL = [*OPERATORS, *UNARY_OPERATORS, *OTHER_SYMBOLS]

KEYWORD_CODE = {
    Keyword.TRUE.value: "push constant 1\nneg",  # could also be !0
    Keyword.FALSE.value: "push constant 0",
    Keyword.NULL.value: "push constant 0",
    Keyword.THIS.value: "push pointer 0",
}

KEYWORD_CONST = list(KEYWORD_CODE.keys())

GRAMMATIC_KEYWORDS = [
    Keyword.CLASS.value,
    Keyword.CONSTRUCTOR.value,
    Keyword.FUNCTION.value,
    Keyword.METHOD.value,
    Keyword.FIELD.value,
    Keyword.STATIC.value,
    Keyword.VAR.value,
    Keyword.INT.value,
    Keyword.CHAR.value,
    Keyword.BOOLEAN.value,
    Keyword.VOID.value,
    Keyword.LET.value,
    Keyword.DO.value,
    Keyword.IF.value,
    Keyword.ELSE.value,
    Keyword.WHILE.value,
    Keyword.RETURN.value,
]

KEYWORDS = [*KEYWORD_CONST, *GRAMMATIC_KEYWORDS]

CLASS_VAR_DEC_KEYWORDS = [
    Keyword.FIELD.value,
    Keyword.STATIC.value,
]

SUBROUTINE_KEYWORDS = [
    Keyword.FUNCTION.value,
    Keyword.METHOD.value,
    Keyword.CONSTRUCTOR.value,
]
TYPE_KEYWORDS = [
    Keyword.INT.value,
    Keyword.CHAR.value,
    Keyword.BOOLEAN.value,
    Keyword.VOID.value,
]

WHITE_SPACE = [" ", "\t", "\n"]

MAX_INT = 32767

STRING_DELIMITER = '"'

SPECIAL_CHARACTERS = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
}

DECLARATION_TYPE_TYPES = [
    "identifier",
    "keyword",
]
