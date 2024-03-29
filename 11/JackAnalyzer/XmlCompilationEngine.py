from __future__ import annotations
from utils import sanitize_text
from Tokenizer import JackTokenizer
from constants import (
    CLASS_VAR_DEC_KEYWORDS,
    KEYWORD_CONST,
    OPERATORS,
    SUBROUTINE_KEYWORDS,
    TYPE_KEYWORDS,
    DECLARATION_TYPE_TYPES,
    UNARY_OPERATORS,
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
        with open("errout.xml", "w") as f:
            f.write(self.content)

        meta = self.tokenizer.get_token()["metadata"]
        raise Exception(
            f"{message} at line {meta['line']}:{meta['char']} in file {meta['file']}"
        )

    def expect(
        self,
        token_values: str | list[str] | None = None,
        token_types: str | list[str] | None = None,
        advance=True,
        add_tag=True,
        mandatory=True,
    ) -> bool:
        token = self.tokenizer.get_token()
        if token.get("type") == "EOF":
            self.panic(f"Unexpected end of file")
        if token_values is not None:
            if not isinstance(token_values, list):
                token_values = [token_values]
        if token_types is not None:
            if not isinstance(token_types, list):
                token_types = [token_types]

        type_match = token_types is None or token.get("type") in token_types
        value_match = token_values is None or token.get("token") in token_values
        if not value_match:
            if not mandatory:
                return False
            self.panic(f"Expected any of '{token_values}' found '{token.get('token')}'")
        if not type_match:
            if not mandatory:
                return False
            self.panic(
                f"Unsupported {token['type']} '{token['token']}'. Expected {token_types}"
            )
        if add_tag:
            self.add_current_tag()
        if advance:
            self.tokenizer.advance()
        return True

    def write(self, text: str, indent=True):
        tabs = "\t" * self.indent if indent else ""
        self.content += tabs + text

    def writeln(self, text: str, indent=True):
        self.write(f"{text}\n", indent=indent)

    def add_current_tag(self):
        token = self.tokenizer.get_token()
        self.add_one_line_tag(token["type"], token["token"])

    def add_one_line_tag(self, type: str, content: str):
        sane_content = sanitize_text(content)
        self.writeln(f"<{type}> {sane_content} </{type}>")

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

        while self.tokenizer.get_token()["token"] in CLASS_VAR_DEC_KEYWORDS:
            self._compileClassVarDec()
        while self.tokenizer.get_token()["token"] in SUBROUTINE_KEYWORDS:
            self._compileSubroutine()

        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    @wrap("classVarDec")
    def _compileClassVarDec(self):
        self.expect(CLASS_VAR_DEC_KEYWORDS)
        self.expect(None, DECLARATION_TYPE_TYPES)
        self._compileIdentifierList()
        self.expect(Symbol.SEMICOLON.value)

    @wrap("subroutineDec")
    def _compileSubroutine(self):
        self.expect(SUBROUTINE_KEYWORDS)
        self.expectType()
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
            self.expectType()
            self.expectIdentifier()
            is_first = False

    def expectType(self):
        token = self.tokenizer.get_token()
        tval = token["token"]
        ttype = token["type"]
        if ttype == "keyword" and tval not in TYPE_KEYWORDS:
            self.panic(f"Unsupported keyword '{token.get('token')}'")
        self.add_current_tag()
        self.tokenizer.advance()

    @wrap("subroutineBody")
    def _compileSubroutineBody(self):
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        while self.tokenizer.get_token()["token"] == Keyword.VAR.value:
            self._compileVarDec()
        self._compileStatements()
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    @wrap("varDec")
    def _compileVarDec(self):
        self.expect(Keyword.VAR.value)
        self.expect(None, DECLARATION_TYPE_TYPES)
        self._compileIdentifierList()
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
        self.expectIdentifier()
        token = self.tokenizer.get_token()
        if token["token"] == Symbol.DOT.value:
            self.expect(Symbol.DOT.value)
            self.expectIdentifier()
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileExpressionList()
        self.expect(Symbol.RIGHT_BRACKET.value)
        self.expect(Symbol.SEMICOLON.value)

    @wrap("letStatement")
    def _compileLet(self):
        self.expect(Keyword.LET.value)
        self.expectIdentifier(indexable=True)
        self.expect(Symbol.EQUAL_SIGN.value)
        self._compileExpression()
        self.expect(Symbol.SEMICOLON.value)

    @wrap("whileStatement")
    def _compileWhile(self):
        self.expect(Keyword.WHILE.value)
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileExpression()
        self.expect(Symbol.RIGHT_BRACKET.value)
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        self._compileStatements()
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    @wrap("returnStatement")
    def _compileReturn(self):
        self.expect(Keyword.RETURN.value)
        if self.tokenizer.get_token()["token"] != Symbol.SEMICOLON.value:
            self._compileExpression()
        self.expect(Symbol.SEMICOLON.value)

    @wrap("ifStatement")
    def _compileIf(self):
        self.expect(Keyword.IF.value)
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileExpression()
        self.expect(Symbol.RIGHT_BRACKET.value)
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        self._compileStatements()
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)
        token = self.tokenizer.get_token()
        if token["token"] == Keyword.ELSE.value:
            self.expect(Keyword.ELSE.value)
            self.expect(Symbol.LEFT_CURLY_BRACKET.value)
            self._compileStatements()
            self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    @wrap("expression")
    def _compileExpression(self):
        self._compileTerm()
        while self.tokenizer.get_token()["token"] in OPERATORS:
            self.expect(OPERATORS)
            self._compileTerm()

    @wrap("term")
    def _compileTerm(self):
        is_parenthesis = self.expect(Symbol.LEFT_BRACKET.value, mandatory=False)
        if is_parenthesis:
            self._compileExpression()
            self.expect(Symbol.RIGHT_BRACKET.value)
            return
        is_unary = self.expect(UNARY_OPERATORS, mandatory=False)
        if is_unary:
            self._compileTerm()
            return

        # This could be unified with the doStatement logic
        if self.expectIdentifier(mandatory=False, indexable=True):
            has_dot = self.expect(Symbol.DOT.value, mandatory=False)
            if has_dot:
                self.expectIdentifier()
            # Has dot dictates if parentheses are mandatory because you
            # cannot access attributes
            if self.expect(Symbol.LEFT_BRACKET.value, mandatory=has_dot):
                self._compileExpressionList()
                self.expect(Symbol.RIGHT_BRACKET.value)
            self.optionalIndex()
            return

        is_value = self.expect(KEYWORD_CONST, mandatory=False) or self.expect(
            None, ["stringConstant", "integerConstant"], mandatory=False
        )
        if is_value is False:
            self.panic("Expected value in term")

    @wrap("expressionList")
    def _compileExpressionList(self):
        is_first = True
        while (
            self.tokenizer.get_token()["token"] != Symbol.RIGHT_BRACKET.value
        ):  #! this is not correct
            if is_first is False:
                self.expect(Symbol.COMMA.value)
            self._compileExpression()
            is_first = False

    def _compileIdentifierList(self):
        is_first = True
        while self.tokenizer.get_token()["token"] != Symbol.SEMICOLON.value:
            if is_first is False:
                self.expect(Symbol.COMMA.value)
            self.expectIdentifier()
            is_first = False

    def expectIdentifier(self, mandatory=True, indexable=False):
        result = self.expect(None, "identifier", mandatory=mandatory)
        if result is False:
            return False
        if indexable:
            self.optionalIndex()
        return True

    def optionalIndex(self):
        if self.expect(Symbol.LEFT_SQUARE_BRACKET.value, mandatory=False):
            self._compileExpression()
            self.expect(Symbol.RIGHT_SQUARE_BRACKET.value)
            return True
        return False

    def generate_file(self):
        with open(self.output_file, "w") as f:
            f.write(self.content)
