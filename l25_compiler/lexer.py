# Token types for L25 language
import re

TOKEN_SPEC = [
    ('NUMBER', r'\d+'),
    ('ID', r'[A-Za-z][A-Za-z0-9]*'),
    ('OP', r'==|!=|<=|>=|[+\-*/=<>]'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'),
]

tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)

KEYWORDS = {
    'program', 'func', 'return', 'if', 'else', 'while',
    'let', 'input', 'output', 'main'
}

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"


def tokenize(code):
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            value = int(value)
        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'ID' and value in KEYWORDS:
            kind = value.upper()
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        yield Token(kind, value, line_num, column)
    yield Token('EOF', '', line_num, 0)
