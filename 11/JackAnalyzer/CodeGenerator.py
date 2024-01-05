from __future__ import annotations
import uuid
from Tokenizer import JackTokenizer
from constants import (
    CLASS_VAR_DEC_KEYWORDS,
    KEYWORD_CODE,
    OPERATORS,
    OPERATORS_CODE,
    SUBROUTINE_KEYWORDS,
    TYPE_KEYWORDS,
    DECLARATION_TYPE_TYPES,
    UNARY_OPERATORS,
    UNARY_CODE,
    Symbol,
    Keyword,
)
from SymbolTable import SymbolCategory, SymbolTable


def generate_label():
    # This is temporary (I hope)
    return str(uuid.uuid4())


class CodeGenerator:
    content: str = ""
    tokenizer: JackTokenizer = None
    output_file: str = None
    indent = 0
    class_name: str = None
    class_symbols: SymbolCategory = None
    subroutine_symbols: SymbolCategory = None

    def __init__(self, tokenizer: JackTokenizer, output_file: str):
        self.tokenizer = tokenizer
        self.output_file = output_file
        self.content = ""
        self.indent = 0
        self.class_symbols = SymbolTable()

    def panic(self, message: str):
        with open("errout.xml", "w") as f:
            f.write(self.content)

        meta = self.current_token["metadata"]
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
        token = self.current_token
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

    @property
    def current_token(self):
        return self.tokenizer.get_token()

    def write(self, text: str, indent=True):
        tabs = "\t" * self.indent if indent else ""
        self.content += tabs + text

    def writeln(self, text: str, indent=True):
        self.write(f"{text}\n", indent=indent)

    def compile(self):
        self.tokenizer.advance()
        self._compileClass()
        assert self.current_token["type"] == "EOF"

    def _compileClass(self):
        self.expect(Keyword.CLASS.value)
        self.class_name = self.current_token["token"]
        self.expectIdentifier()
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)

        while self.current_token["token"] in CLASS_VAR_DEC_KEYWORDS:
            self._compileClassVarDec()
        while self.current_token["token"] in SUBROUTINE_KEYWORDS:
            self._compileSubroutine()

        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    def _compileClassVarDec(self):
        category = self.current_token["token"]
        self.expect(CLASS_VAR_DEC_KEYWORDS)
        type_token = self.current_token
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
            None if self.current_token == Keyword.FUNCTION.value else self.class_symbols
        )
        self.expect(SUBROUTINE_KEYWORDS)
        self.expectType()
        fname = self.current_token["token"]
        self.expectIdentifier()
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileParameterList(
            on_find=lambda token, type_token: self.subroutine_symbols.add_symbol(
                token["token"], type_token, SymbolCategory.Argument
            )
        )
        self.expect(Symbol.RIGHT_BRACKET.value)
        self._start_function(
            fname,
            len(self.subroutine_symbols.category_symbols(SymbolCategory.Argument)),
        )
        self._compileSubroutineBody()

    def _start_function(self, name, argc):
        self.writeln(f"function {self.class_name}.{name} {argc}")

    def _compileParameterList(self, on_find: function | None = None):
        is_first = True
        while (token := self.current_token)["type"] in DECLARATION_TYPE_TYPES or token[
            "token"
        ] == Symbol.COMMA.value:
            if not is_first:
                self.expect(Symbol.COMMA.value)
            type_token = self.expectType()
            self.expectIdentifier(
                on_find=lambda token: on_find and on_find(token, type_token["token"])
            )
            is_first = False

    def expectType(self) -> dict:
        token = self.current_token
        tval = token["token"]
        ttype = token["type"]
        if ttype == "keyword" and tval not in TYPE_KEYWORDS:
            self.panic(f"Unsupported keyword '{token.get('token')}'")
        self.tokenizer.advance()
        return token

    def _compileSubroutineBody(self):
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        while self.current_token["token"] == Keyword.VAR.value:
            self._compileVarDec()
        self._compileStatements()
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    def _compileVarDec(self):
        self.expect(Keyword.VAR.value)
        type_token = self.current_token
        self.expect(None, DECLARATION_TYPE_TYPES)
        self._compileIdentifierList(
            on_find=lambda token: self.subroutine_symbols.add_symbol(
                token["token"], type_token["token"], SymbolCategory.Var
            )
        )
        self.expect(Symbol.SEMICOLON.value)

    def _compileStatements(self):
        while token := self.current_token:
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
        name = self.current_token["token"]
        self.expectIdentifier()
        self._expectCall(name)
        self.expect(Symbol.SEMICOLON.value)

    def _compileLet(self):
        self.expect(Keyword.LET.value)
        identifier = self.current_token
        self.expectIdentifier(indexable=True)
        self.expect(Symbol.EQUAL_SIGN.value)
        self._compileExpression()
        symbol = self.subroutine_symbols.get_by_name(identifier["token"])
        self.writeln(f"pop local {symbol['index']}")
        self.expect(Symbol.SEMICOLON.value)

    def _compileWhile(self):
        label = generate_label()
        label_end = f"{label}-end"
        self.writeln(f"label {label}")
        self.expect(Keyword.WHILE.value)
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileExpression()
        self.expect(Symbol.RIGHT_BRACKET.value)
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        self.writeln("neg")
        self.writeln(f"if-goto {label_end}")
        self._compileStatements()
        self.writeln(f"goto {label}")
        self.writeln(f"label {label_end}")
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)

    def _compileReturn(self):
        self.expect(Keyword.RETURN.value)
        if self.current_token["token"] != Symbol.SEMICOLON.value:
            self._compileExpression()
        self.expect(Symbol.SEMICOLON.value)
        self.writeln("return")

    def _compileIf(self):
        end_if_label = generate_label()
        end_else_label = f"{end_if_label}-else"
        self.expect(Keyword.IF.value)
        self.expect(Symbol.LEFT_BRACKET.value)
        self._compileExpression()
        self.expect(Symbol.RIGHT_BRACKET.value)
        self.expect(Symbol.LEFT_CURLY_BRACKET.value)
        self.writeln("neg")
        self.writeln(f"if-goto {end_if_label}")
        self._compileStatements()
        self.writeln(f"goto {end_else_label}")
        self.writeln(f"label {end_if_label}")
        self.expect(Symbol.RIGHT_CURLY_BRACKET.value)
        token = self.current_token
        if token["token"] == Keyword.ELSE.value:
            self.expect(Keyword.ELSE.value)
            self.expect(Symbol.LEFT_CURLY_BRACKET.value)
            self._compileStatements()
            self.expect(Symbol.RIGHT_CURLY_BRACKET.value)
        self.writeln(f"label {end_else_label}")

    def _compileExpression(self):
        self._compileTerm()
        while self.current_token["token"] in OPERATORS:
            operator = self.current_token
            self.expect(
                OPERATORS,
            )
            self._compileTerm()
            self._compileOperator(operator["token"])

    def _compileTerm(self):
        is_parenthesis = self.expect(Symbol.LEFT_BRACKET.value, mandatory=False)
        if is_parenthesis:
            self._compileExpression()
            self.expect(Symbol.RIGHT_BRACKET.value)
            return
        unary = self.current_token
        is_unary = self.expect(UNARY_OPERATORS, mandatory=False)
        if is_unary:
            self._compileTerm()
            self.writeln(UNARY_CODE[unary["token"]])
            return

        # This could be unified with the doStatement logic
        name = self.current_token["token"]
        if self.expectIdentifier(mandatory=False, indexable=True):
            is_call = self._expectCall(name, mandatory=False)
            if not is_call:
                symbol = self.subroutine_symbols.get_by_name(name)
                self.writeln(f"push local {symbol['index']}")
            self.optionalIndex()
            return

        token = self.current_token
        if token["type"] == "integerConstant":
            self.writeln(f"push constant {token['token']}")
        elif token["type"] == "stringConstant":
            pass
        elif token["token"] in KEYWORD_CODE:
            self.writeln(KEYWORD_CODE[token["token"]])
        else:
            self.panic(f"Unexpected value '{token['token']}' in term")
        self.tokenizer.advance()

    def _expectCall(self, first_identifier: str, mandatory=True):
        class_name = self.class_name
        fname = first_identifier
        has_dot = self.expect(Symbol.DOT.value, mandatory=False)
        if has_dot:
            class_name = first_identifier
            fname = self.current_token["token"]
            self.expectIdentifier()
        # Has dot dictates if parentheses are mandatory because you
        # cannot access attributes
        if self.expect(Symbol.LEFT_BRACKET.value, mandatory=(mandatory or has_dot)):
            expression_count = self._compileExpressionList()
            self.expect(Symbol.RIGHT_BRACKET.value)
            self.writeln(f"call {class_name}.{fname} {expression_count}")
            return True
        return False

    def _compileExpressionList(self) -> int:
        count = 0
        while (
            self.current_token["token"] != Symbol.RIGHT_BRACKET.value
        ):  #! this is not correct
            if count > 0:
                self.expect(Symbol.COMMA.value)
            self._compileExpression()
            count += 1
        return count

    def _compileIdentifierList(self, on_find: function | None = None):
        is_first = True
        while self.current_token["token"] != Symbol.SEMICOLON.value:
            if is_first is False:
                self.expect(Symbol.COMMA.value)
            self.expectIdentifier(on_find=on_find)
            is_first = False

    def expectIdentifier(
        self, mandatory=True, indexable=False, on_find: function | None = None
    ):
        token = self.current_token
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

    def _compileOperator(self, operator: str):
        self.writeln(OPERATORS_CODE[operator])
