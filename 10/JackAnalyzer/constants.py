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


OPERATORS = {
    Symbol.PLUS_SIGN.value,
    Symbol.MINUS_SIGN.value,
    Symbol.ASTERISK.value,
    Symbol.SLASH.value,
    Symbol.AMPERSAND.value,
    Symbol.VERTICAL_BAR.value,
    Symbol.LESS_THAN_SIGN.value,
    Symbol.GREATER_THAN_SIGN.value,
    Symbol.EQUAL_SIGN.value,
}
UNARY_OPERATORS = {
    Symbol.MINUS_SIGN.value,
    Symbol.TILDE.value,
}

OTHER_SYMBOLS = {
    Symbol.LEFT_CURLY_BRACKET.value,
    Symbol.RIGHT_CURLY_BRACKET.value,
    Symbol.LEFT_BRACKET.value,
    Symbol.RIGHT_BRACKET.value,
    Symbol.LEFT_SQUARE_BRACKET.value,
    Symbol.RIGHT_SQUARE_BRACKET.value,
    Symbol.DOT.value,
    Symbol.COMMA.value,
    Symbol.SEMICOLON.value,
}
SYMBOL = {*OPERATORS, *UNARY_OPERATORS, *OTHER_SYMBOLS}

KEYWORD_CONST = {
    Keyword.TRUE.value,
    Keyword.FALSE.value,
    Keyword.NULL.value,
    Keyword.THIS.value,
}

GRAMMATIC_KEYWORDS = {
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
}

KEYWORDS = {*KEYWORD_CONST, *GRAMMATIC_KEYWORDS}

SUBROUTINE_KEYWORDS = [Keyword.FUNCTION.value, Keyword.METHOD.value]
TYPE_KEYWORDS = [
    Keyword.INT.value,
    Keyword.CHAR.value,
    Keyword.BOOLEAN.value,
    Keyword.VOID.value,
]

SYMBOL_TO_XML = {
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "&": "&amp;",
}

WHITE_SPACE = {" ", "\t", "\n"}

MAX_INT = 32767

STRING_DELIMITER = '"'

SPECIAL_CHARACTERS = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
}
