from __future__ import annotations
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
from SymbolTable import SymbolCategory, SymbolTable


class CodeGenerator:
    content: str = ""
    tokenizer: JackTokenizer = None
    output_file: str = None
    indent = 0
    class_symbols = None
    subroutine_symbols = None

    def __init__(self, tokenizer: JackTokenizer, output_file: str):
        self.tokenizer = tokenizer
        self.output_file = output_file
        self.content = ""
        self.indent = 0
        self.class_symbols = SymbolTable()

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
        # if add_tag:
        #     self.add_current_tag()
        if advance:
            self.tokenizer.advance()
        return True

    def write(self, text: str, indent=True):
        tabs = "\t" * self.indent if indent else ""
        self.content += tabs + text

    def writeln(self, text: str, indent=True):
        self.write(f"{text}\n", indent=indent)

    def compile(self):
        self.tokenizer.advance()
        self._compileClass()
        assert self.tokenizer.get_token()["type"] == "EOF"

    def _compileClass(self):
        self.expect(Keyword.CLASS.value)
        self.expectIdentifier()
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)

        while self.tokenizer.get_token()["token"] in CLASS_VAR_DEC_KEYWORDS:
            self._compileClassVarDec()
        while self.tokenizer.get_token()["token"] in SUBROUTINE_KEYWORDS:
            self._compileSubroutine()

        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    def _compileClassVarDec(self):
        category = self.tokenizer.get_token()["token"]
        self.expect(CLASS_VAR_DEC_KEYWORDS)
        type_token = self.tokenizer.get_token()
        self.expect(None, DECLARATION_TYPE_TYPES)
        self._compileIdentifierList(
            on_find=lambda token: self.class_symbols.add_symbol(
                token["token"],
                type_token["token"],
                Keyword.FIELD if category == "field" else Keyword.STATIC,
            )
        )
        self.expect(Symbol.SEMICOLON.value)

    def _compileSubroutine(self):
        self.subroutine_symbols = SymbolTable(
            None
            if self.tokenizer.get_token() == Keyword.FUNCTION.value
            else self.class_symbols
        )
        self.expect(SUBROUTINE_KEYWORDS)
        self.expectType()
        self.expectIdentifier()
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileParameterList(
            on_find=lambda token, type_token: self.subroutine_symbols.add_symbol(
                token["token"], type_token, SymbolCategory.Argument
            )
        )
        self.expect(Symbol.RIGHT_BRACKET.value)
        self._compileSubroutineBody()

    def _compileParameterList(self, on_find: function | None = None):
        is_first = True
        while (token := self.tokenizer.get_token())[
            "type"
        ] in DECLARATION_TYPE_TYPES or token["token"] == Symbol.COMMA.value:
            if not is_first:
                self.expect(Symbol.COMMA.value)
            type_token = self.expectType()
            self.expectIdentifier(
                on_find=lambda token: on_find and on_find(token, type_token["token"])
            )
            is_first = False

    def expectType(self) -> dict:
        token = self.tokenizer.get_token()
        tval = token["token"]
        ttype = token["type"]
        if ttype == "keyword" and tval not in TYPE_KEYWORDS:
            self.panic(f"Unsupported keyword '{token.get('token')}'")
        # self.add_current_tag()
        self.tokenizer.advance()
        return token

    def _compileSubroutineBody(self):
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        while self.tokenizer.get_token()["token"] == Keyword.VAR.value:
            self._compileVarDec()
        self._compileStatements()
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    def _compileVarDec(self):
        self.expect(Keyword.VAR.value)
        type_token = self.tokenizer.get_token()
        self.expect(None, DECLARATION_TYPE_TYPES)
        self._compileIdentifierList(
            on_find=lambda token: self.subroutine_symbols.add_symbol(
                token["token"], type_token["token"], SymbolCategory.Var
            )
        )
        self.expect(Symbol.SEMICOLON.value)

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

    def _compileLet(self):
        self.expect(Keyword.LET.value)
        self.expectIdentifier(indexable=True)
        self.expect(Symbol.EQUAL_SIGN.value)
        self._compileExpression()
        self.expect(Symbol.SEMICOLON.value)

    def _compileWhile(self):
        self.expect(Keyword.WHILE.value)
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileExpression()
        self.expect(Symbol.RIGHT_BRACKET.value)
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        self._compileStatements()
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    def _compileReturn(self):
        self.expect(Keyword.RETURN.value)
        if self.tokenizer.get_token()["token"] != Symbol.SEMICOLON.value:
            self._compileExpression()
        self.expect(Symbol.SEMICOLON.value)

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

    def _compileExpression(self):
        self._compileTerm()
        while self.tokenizer.get_token()["token"] in OPERATORS:
            self.expect(OPERATORS)
            self._compileTerm()

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

    def _compileExpressionList(self):
        is_first = True
        while (
            self.tokenizer.get_token()["token"] != Symbol.RIGHT_BRACKET.value
        ):  #! this is not correct
            if is_first is False:
                self.expect(Symbol.COMMA.value)
            self._compileExpression()
            is_first = False

    def _compileIdentifierList(self, on_find: function | None = None):
        is_first = True
        while self.tokenizer.get_token()["token"] != Symbol.SEMICOLON.value:
            if is_first is False:
                self.expect(Symbol.COMMA.value)
            self.expectIdentifier(on_find=on_find)
            is_first = False

    def expectIdentifier(
        self, mandatory=True, indexable=False, on_find: function | None = None
    ):
        token = self.tokenizer.get_token()
        result = self.expect(None, "identifier", mandatory=mandatory)
        if result is False:
            return False
        if on_find:
            on_find(token)
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
