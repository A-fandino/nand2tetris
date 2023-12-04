from __future__ import annotations
from enum import Enum
from Tokenizer import JackTokenizer
from constants import SUBROUTINE_KEYWORDS, TYPE_KEYWORDS, Symbol, Keyword


def wrap(tag: str):
    def decorator(func: function):
        def wrapper(self: CompilationEngine, *args, **kwargs):
            self.open_tag(tag)
            rtrn_value = func(self, *args, **kwargs)
            self.close_tag(tag)
            return rtrn_value

        return wrapper

    return decorator


class CompilationEngine:
    content: str = ""
    tokenizer: JackTokenizer = None
    output_file: str = None
    indent = 0

    def __init__(self, tokenizer: JackTokenizer, output_file: str):
        self.tokenizer = tokenizer
        self.output_file = output_file
        self.content = ""
        self.indent = 0

    def panic(self, message: str):
        line = self.tokenizer.get_token()["line"]
        raise Exception(f"{message} at line {line}")

    def expect(
        self,
        token_values: str | list[str] | None = None,
        token_types: str | list[str] | None = None,
        advance=True,
        add_tag=True,
    ):
        token = self.tokenizer.get_token()
        if token.get("type") == "EOF":
            self.panic(f"Unexpected end of file")
        if token_values is not None:
            if not isinstance(token_values, list):
                token_values = [token_values]
        if token_types is not None:
            if not isinstance(token_types, list):
                token_types = [token_types]
        type_matches = token_types is None or token.get("type") in token_types
        value_match = token_values is None or token.get("token") in token_values
        if not (type_matches and value_match):
            self.panic(f"Expected any of '{token_values}' found '{token.get('token')}'")
        if add_tag:
            self.add_current_tag()
        if advance:
            self.tokenizer.advance()

    def write(self, text: str, indent=True):
        tabs = "\t" * self.indent if indent else ""
        self.content += tabs + text

    def writeln(self, text: str, indent=True):
        self.write(f"{text}\n", indent=indent)

    def add_current_tag(self):
        token = self.tokenizer.get_token()
        self.add_one_line_tag(token["type"], token["token"])

    def add_one_line_tag(self, type: str, content: str):
        self.writeln(f"<{type}> {content} </{type}>")

    def open_tag(self, tag_name: str):
        self.writeln(f"<{tag_name}>")
        self.indent += 1

    def close_tag(self, tag_name: str):
        self.indent -= 1
        self.writeln(f"</{tag_name}>")

    def compile(self):
        self.tokenizer.advance()
        self._compileClass()
        assert self.tokenizer.get_token()["type"] == "EOF"

    @wrap("class")
    def _compileClass(self):
        self.expect(Keyword.CLASS.value)
        self.expectIdentifier()
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        while self.tokenizer.get_token()["token"] in (
            Keyword.STATIC.value,
            Keyword.FIELD.value,
        ):
            self._compileClassVarDec()
        while self.tokenizer.get_token()["token"] in (
            Keyword.METHOD.value,
            Keyword.FUNCTION.value,
        ):
            self._compileSubroutine()

        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    def _compileClassVarDec(self):
        pass

    @wrap("subroutineDec")
    def _compileSubroutine(self):
        self.expect(SUBROUTINE_KEYWORDS)
        self.expect(TYPE_KEYWORDS)
        self.expectIdentifier()
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileParameterList()
        self.expect(Symbol.RIGHT_BRACKET.value)
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        self._compileSubroutineBody()
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    def _compileParameterList(self):
        pass

    @wrap("subroutineBody")
    def _compileSubroutineBody(self):
        depth = 0
        while (token := self.tokenizer.advance())[
            "token"
        ] != Symbol.RIGHT_CURLY_BRACKET.value or depth > 0:
            val = token["token"]
            if val == Symbol.LEFT_CURLY_BRACKET.value:
                depth += 1
                continue
            if val == Symbol.RIGHT_CURLY_BRACKET.value:
                depth -= 1

    def _compileVarDec(self):
        pass

    def _compileStatements(self):
        pass

    def _compileDo(self):
        pass

    def _compileLet(self):
        pass

    def _compileWhile(self):
        pass

    def _compileReturn(self):
        pass

    def _compileIf(self):
        pass

    def _compileExpression(self):
        pass

    def _compileTerm(self):
        pass

    def _compileExpressionList(self):
        pass

    def _compileIdentifier(self):
        token = self.tokenizer.get_token()
        if token["type"] != "identifier":
            raise self.panic(f"Expected an identifier but found a {token['type']}")
        self.tokenizer.advance()

    def generate_file(self):
        with open(self.output_file, "w") as f:
            f.write(self.content)
