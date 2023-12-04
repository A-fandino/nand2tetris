from __future__ import annotations
from enum import Enum
from Tokenizer import JackTokenizer
from constants import (
    STATEMENT_KEYWORDS,
    SUBROUTINE_KEYWORDS,
    TYPE_KEYWORDS,
    DECLARATION_TYPE_TYPES,
    Symbol,
    Keyword,
)


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
        if not value_match:
            self.panic(f"Expected any of '{token_values}' found '{token.get('token')}'")
        if not type_matches:
            self.panic(
                f"Unsupported {token['type']} '{token['token']}'. Expected {token_types}"
            )
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
        self._compileSubroutineBody()

    @wrap("parameterList")
    def _compileParameterList(self):
        is_first = True
        while (token := self.tokenizer.get_token())[
            "type"
        ] in DECLARATION_TYPE_TYPES or token["token"] == Symbol.COMMA.value:
            if not is_first:
                self.expect(Symbol.COMMA.value)
            tval = token["token"]
            ttype = token["type"]
            if ttype == "keyword" and tval not in TYPE_KEYWORDS:
                self.panic(f"Unsupported keyword '{token.get('token')}'")
            self.add_current_tag()
            self.tokenizer.advance()
            self.expectIdentifier()
            is_first = False

    @wrap("subroutineBody")
    def _compileSubroutineBody(self):
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        while self.tokenizer.get_token()["token"] == Keyword.VAR.value:
            self._compileVarDec()
        token = self.tokenizer.get_token()
        self._compileStatements()

        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    @wrap("varDec")
    def _compileVarDec(self):
        self.expect(Keyword.VAR.value)
        self.expect(None, DECLARATION_TYPE_TYPES)
        is_first = True
        while self.tokenizer.get_token()["token"] != Symbol.SEMICOLON.value:
            if is_first is False:
                self.expect(Symbol.COMMA.value)
            self.expectIdentifier()
            is_first = False
        self.expect(Symbol.SEMICOLON.value)

    @wrap("statements")
    def _compileStatements(self):
        while token := self.tokenizer.get_token():
            value = token["token"]
            if value == Keyword.DO.value:
                self._compileDo()
            elif value == Keyword.IF.value:
                self._compileIf()
            elif value == Keyword.WHILE.value:
                self._compileWhile()
            elif value == Keyword.LET.value:
                self._compileLet()
            elif value == Keyword.RETURN.value:
                self._compileReturn()
            else:
                break

    @wrap("doStatement")
    def _compileDo(self):
        self.expect(Keyword.DO.value)

    @wrap("letStatement")
    def _compileLet(self):
        self.expect(Keyword.LET.value)
        self.expectIdentifier()
        self.expect(Symbol.EQUAL_SIGN.value)
        self._compileExpression()
        self.expect(Symbol.SEMICOLON.value)

    @wrap("whileStatement")
    def _compileWhile(self):
        self.expect(Keyword.WHILE.value)
        self.expect(Symbol.LEFT_BRACKET)
        self._compileExpression()
        self.expect(Symbol.RIGHT_BRACKET)
        self.expect(Symbol.LEFT_CURLY_BRACKET)
        self._compileStatements()
        self.expect(Symbol.RIGHT_CURLY_BRACKET)

    @wrap("returnStatement")
    def _compileReturn(self):
        self.expect(Keyword.RETURN.value)
        if self.tokenizer.get_token()["value"] != Symbol.SEMICOLON.value:
            self._compileExpression()
        self.expect(Symbol.SEMICOLON.value)

    @wrap("ifStatement")
    def _compileIf(self):
        self.expect(Keyword.IF.value)
        self.expect(Symbol.LEFT_BRACKET)
        self._compileExpression()
        self.expect(Symbol.RIGHT_BRACKET)
        self.expect(Symbol.LEFT_CURLY_BRACKET)
        self._compileStatements()
        self.expect(Symbol.RIGHT_CURLY_BRACKET)
        token = self.tokenizer.get_token()
        if token["token"] == Keyword.ELSE.value:
            self.expect(Keyword.ELSE.value)
            self.expect(Symbol.LEFT_CURLY_BRACKET)
            self._compileStatements()
            self.expect(Symbol.RIGHT_CURLY_BRACKET)

    @wrap("expression")
    def _compileExpression(self):
        pass

    @wrap("term")
    def _compileTerm(self):
        pass

    @wrap("expressionList")
    def _compileExpressionList(self):
        pass

    def expectIdentifier(self):
        self.expect(None, "identifier")

    def generate_file(self):
        with open(self.output_file, "w") as f:
            f.write(self.content)
