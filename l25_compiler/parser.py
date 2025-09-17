from .lexer import tokenize
from .ast_nodes import *

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def accept(self, *types):
        tok = self.current()
        if tok.type in types:
            self.pos += 1
            return tok
        return None

    def expect(self, *types):
        tok = self.accept(*types)
        if not tok:
            raise ParserError(f'Expected {types}, got {self.current().type}')
        return tok

    def parse(self):
        return self.program()

    # program = "program" ident "{" { func_def } "main" "{" stmt_list "}" "}"
    def program(self):
        self.expect('PROGRAM')
        name = self.expect('ID').value
        self.expect('LBRACE')
        funcs = []
        while self.accept('FUNC'):
            self.pos -= 1
            funcs.append(self.func_def())
        self.expect('MAIN')
        self.expect('LBRACE')
        main_body = self.stmt_list()
        self.expect('RBRACE')
        self.expect('RBRACE')
        return Program(name, funcs, main_body)

    # func_def = "func" ident "(" [ param_list ] ")" "{" stmt_list "return" expr ";" "}"
    def func_def(self):
        self.expect('FUNC')
        name = self.expect('ID').value
        self.expect('LPAREN')
        params = []
        if not self.accept('RPAREN'):
            params.append(self.expect('ID').value)
            while self.accept('COMMA'):
                params.append(self.expect('ID').value)
            self.expect('RPAREN')
        self.expect('LBRACE')
        body = self.stmt_list()
        self.expect('RETURN')
        ret = self.expr()
        self.expect('SEMICOLON')
        self.expect('RBRACE')
        return FuncDef(name, params, body, ret)

    # stmt_list = stmt ";" { stmt ";" }
    def stmt_list(self):
        stmts = [self.stmt()]
        self.expect('SEMICOLON')
        while True:
            mark = self.pos
            try:
                stmts.append(self.stmt())
                self.expect('SEMICOLON')
            except ParserError:
                self.pos = mark
                break
        return StmtList(stmts)

    # stmt options
    def stmt(self):
        tok = self.current()
        if tok.type == 'LET':
            return self.declare_stmt()
        if tok.type == 'ID':
            # could be assign or func_call
            if self.tokens[self.pos + 1].type == 'LPAREN':
                return self.func_call()
            else:
                return self.assign_stmt()
        if tok.type == 'OP' and tok.value == '*':
            return self.assign_stmt()
        if tok.type == 'IF':
            return self.if_stmt()
        if tok.type == 'WHILE':
            return self.while_stmt()
        if tok.type == 'INPUT':
            return self.input_stmt()
        if tok.type == 'OUTPUT':
            return self.output_stmt()
        raise ParserError(f'Unexpected token {tok.type}')

    # declare_stmt = "let" ident [ "[" expr "]" ] [ "=" expr ]
    def declare_stmt(self):
        self.expect('LET')
        name = self.expect('ID').value
        size = None
        if self.accept('LBRACKET'):
            size = self.expr()
            self.expect('RBRACKET')
        expr = None
        if self.accept('OP') and self.tokens[self.pos-1].value == '=':
            expr = self.expr()
        else:
            self.pos -= 1 if self.tokens[self.pos-1].type == 'OP' else 0
        return Declare(name, expr, size)

    # assign_stmt = assign_target "=" expr
    def assign_stmt(self):
        target = self.assign_target()
        self.expect('OP')  # '='
        expr = self.expr()
        return Assign(target, expr)

    def assign_target(self):
        if self.accept('OP') and self.tokens[self.pos-1].value == '*':
            return UnaryOp('*', self.assign_target())
        return self.variable()

    # if_stmt = "if" "(" bool_expr ")" "{" stmt_list "}" [ "else" "{" stmt_list "}" ]
    def if_stmt(self):
        self.expect('IF')
        self.expect('LPAREN')
        cond = self.bool_expr()
        self.expect('RPAREN')
        self.expect('LBRACE')
        then = self.stmt_list()
        self.expect('RBRACE')
        else_ = None
        if self.accept('ELSE'):
            self.expect('LBRACE')
            else_ = self.stmt_list()
            self.expect('RBRACE')
        return If(cond, then, else_)

    # while_stmt = "while" "(" bool_expr ")" "{" stmt_list "}"
    def while_stmt(self):
        self.expect('WHILE')
        self.expect('LPAREN')
        cond = self.bool_expr()
        self.expect('RPAREN')
        self.expect('LBRACE')
        body = self.stmt_list()
        self.expect('RBRACE')
        return While(cond, body)

    # func_call = ident "(" [ arg_list ] ")"
    def func_call(self):
        name = self.expect('ID').value
        self.expect('LPAREN')
        args = []
        if not self.accept('RPAREN'):
            args.append(self.expr())
            while self.accept('COMMA'):
                args.append(self.expr())
            self.expect('RPAREN')
        return FuncCall(name, args)

    # variable = ident { '[' expr ']' | '.' ident }
    def variable(self):
        node = Identifier(self.expect('ID').value)
        while True:
            if self.accept('LBRACKET'):
                idx = self.expr()
                self.expect('RBRACKET')
                node = ArrayAccess(node, idx)
            elif self.accept('DOT'):
                field = self.expect('ID').value
                node = FieldAccess(node, field)
            else:
                break
        return node

    def array_literal(self):
        self.expect('LBRACKET')
        elems = []
        if not self.accept('RBRACKET'):
            elems.append(self.expr())
            while self.accept('COMMA'):
                elems.append(self.expr())
            self.expect('RBRACKET')
        return ArrayLiteral(elems)

    def struct_literal(self):
        self.expect('STRUCT')
        self.expect('LBRACE')
        fields = {}
        if self.current().type != 'RBRACE':
            while True:
                name = self.expect('ID').value
                self.expect('OP')  # '='
                fields[name] = self.expr()
                if self.accept('SEMICOLON'):
                    if self.current().type == 'RBRACE':
                        break
                else:
                    break
        self.expect('RBRACE')
        return StructLiteral(fields)

    # input_stmt = "input" "(" ident { "," ident } ")"
    def input_stmt(self):
        self.expect('INPUT')
        self.expect('LPAREN')
        names = [self.expect('ID').value]
        while self.accept('COMMA'):
            names.append(self.expect('ID').value)
        self.expect('RPAREN')
        return Input(names)

    # output_stmt = "output" "(" expr { "," expr } ")"
    def output_stmt(self):
        self.expect('OUTPUT')
        self.expect('LPAREN')
        exprs = [self.expr()]
        while self.accept('COMMA'):
            exprs.append(self.expr())
        self.expect('RPAREN')
        return Output(exprs)

    # bool_expr = expr ( "==" | "!=" | "<" | "<=" | ">" | ">=" ) expr
    def bool_expr(self):
        left = self.expr()
        op = self.expect('OP').value
        right = self.expr()
        return BinaryOp(op, left, right)

    # expr = [ "+" | "-" ] term { ( "+" | "-" ) term }
    def expr(self):
        if self.current().type == 'OP' and self.current().value in ('+', '-'):
            op = self.current().value
            self.pos += 1
            node = UnaryOp(op, self.term())
        else:
            node = self.term()
        while self.current().type == 'OP' and self.current().value in ('+', '-'):
            op = self.current().value
            self.pos += 1
            right = self.term()
            node = BinaryOp(op, node, right)
        return node

    # term = factor { ( "*" | "/" ) factor }
    def term(self):
        node = self.factor()
        while self.current().type == 'OP' and self.current().value in ('*', '/'):
            op = self.current().value
            self.pos += 1
            right = self.factor()
            node = BinaryOp(op, node, right)
        return node

    # factor = ["*" factor | "&" variable | ident | number | "(" expr ")" | func_call | array_literal | struct_literal]
    def factor(self):
        tok = self.current()
        if tok.type == 'NUMBER':
            self.pos += 1
            return Number(tok.value)
        if tok.type == 'OP' and tok.value == '&':
            self.pos += 1
            return UnaryOp('&', self.variable())
        if tok.type == 'OP' and tok.value == '*':
            self.pos += 1
            return UnaryOp('*', self.factor())
        if tok.type == 'ID':
            if self.tokens[self.pos+1].type == 'LPAREN':
                return self.func_call()
            else:
                return self.variable()
        if tok.type == 'LBRACKET':
            return self.array_literal()
        if tok.type == 'STRUCT':
            return self.struct_literal()
        if self.accept('LPAREN'):
            node = self.expr()
            self.expect('RPAREN')
            return node
        raise ParserError(f'Unexpected factor {tok.type}')
