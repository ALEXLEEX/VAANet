import ply.lex as lex

# Reserved keywords for L25 language
reserved = {
    'program': 'PROGRAM',
    'func': 'FUNC',
    'main': 'MAIN',
    'let': 'LET',
    'return': 'RETURN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'input': 'INPUT',
    'output': 'OUTPUT',
    'struct': 'STRUCT',
}

tokens = [
    'IDENT', 'NUMBER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQUALS',
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'COMMA', 'SEMICOLON',
    'DOT',
] + list(reserved.values())

# Regular expressions for simple tokens

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='

t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_LT = r'<'
t_GE = r'>='
t_GT = r'>'


t_LPAREN = r'\('
t_RPAREN = r'\)'

t_LBRACE = r'\{'
t_RBRACE = r'\}'

t_LBRACKET = r'\['
t_RBRACKET = r'\]'

t_COMMA = r','
t_SEMICOLON = r';'
t_DOT = r'\.'

t_ignore = ' \t'


def t_IDENT(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise SyntaxError(f"Illegal character {t.value[0]!r} at line {t.lineno}")


def build_lexer(**kwargs):
    return lex.lex(**kwargs)

