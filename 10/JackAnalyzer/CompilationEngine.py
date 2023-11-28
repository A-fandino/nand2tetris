from Tokenizer import JackTokenizer


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer, output_file):
        self.tokenizer = tokenizer
        self.output_file = output_file

    def expect(self, token_value, token_type: str = None, advance=True):
        print("expecting", token_value)
        token = self.tokenizer.get_token()
        type_matches = token_type is None or token.get("type") == token_type
        value_match = token_value == token.get("token")
        if not (type_matches and value_match):
            raise Exception(
                f"Expected '{token_value}' found '{token.get('token')}' at line {token.get('line')}"
            )
        if advance:
            self.tokenizer.advance()

    def compile(self):
        self.tokenizer.advance()
        self._compileClass()

    def _compileClass(self):
        self.expect("class")
        self._compileIdentifier()
        self.expect("{")
        self._compileClassVarDec()
        while self.tokenizer.get_token()["token"] in ("static", "function"):
            self._compileSubroutine()
        self.expect("}")

    def _compileClassVarDec(self):
        pass

    def _compileSubroutine(self):
        while self.tokenizer.advance()["token"] != "}":
            pass

    def _compileParameterList(self):
        pass

    def _compileSubroutineBody(self):
        pass

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
        self.tokenizer.advance()
