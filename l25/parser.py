import ply.yacc as yacc
from .lexer import tokens, build_lexer
from . import ast_nodes as ast




class Parser:
    tokens = tokens
    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.lexer = build_lexer()
        self.parser = yacc.yacc(module=self)

    def parse(self, text):
        return self.parser.parse(text, lexer=self.lexer)

    # --- Grammar rules ---
    def p_program(self, p):
        """program : PROGRAM IDENT LBRACE func_defs MAIN LBRACE stmt_list RBRACE RBRACE"""
        p[0] = ast.Program(p[2], p[4], ast.Block(p[7]))

    def p_func_defs(self, p):
        """func_defs : func_defs func_def
                     | empty"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []

    def p_func_def(self, p):
        """func_def : FUNC IDENT LPAREN param_list RPAREN LBRACE stmt_list RETURN expr SEMICOLON RBRACE"""
        p[0] = ast.FuncDef(p[2], p[4], ast.Block(p[7]), p[9])

    def p_param_list(self, p):
        """param_list : IDENT param_list_tail
                      | empty"""
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_param_list_tail(self, p):
        """param_list_tail : COMMA IDENT param_list_tail
                           | empty"""
        if len(p) == 4:
            p[0] = [p[2]] + p[3]
        else:
            p[0] = []

    def p_stmt_list(self, p):
        """stmt_list : stmt SEMICOLON stmt_list
                     | stmt SEMICOLON"""
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_stmt(self, p):
        """stmt : declare_stmt
                | assign_stmt
                | if_stmt
                | while_stmt
                | input_stmt
                | output_stmt
                | func_call"""
        p[0] = p[1]

    def p_declare_stmt(self, p):
        """declare_stmt : LET IDENT
                        | LET IDENT EQUALS expr"""
        if len(p) == 3:
            p[0] = ast.Declare(p[2])
        else:
            p[0] = ast.Declare(p[2], p[4])

    def p_assign_stmt(self, p):
        """assign_stmt : ident_expr EQUALS expr"""
        p[0] = ast.Assign(p[1], p[3])

    def p_if_stmt(self, p):
        """if_stmt : IF LPAREN expr RPAREN LBRACE stmt_list RBRACE else_part"""
        p[0] = ast.If(p[3], ast.Block(p[6]), p[8])

    def p_else_part(self, p):
        """else_part : ELSE LBRACE stmt_list RBRACE
                    | empty"""
        if len(p) == 5:
            p[0] = ast.Block(p[3])
        else:
            p[0] = None

    def p_while_stmt(self, p):
        """while_stmt : WHILE LPAREN expr RPAREN LBRACE stmt_list RBRACE"""
        p[0] = ast.While(p[3], ast.Block(p[6]))

    def p_input_stmt(self, p):
        """input_stmt : INPUT LPAREN ident_list RPAREN"""
        p[0] = ast.InputStmt(p[3])

    def p_output_stmt(self, p):
        """output_stmt : OUTPUT LPAREN expr_list RPAREN"""
        p[0] = ast.OutputStmt(p[3])

    def p_func_call(self, p):
        """func_call : IDENT LPAREN arg_list RPAREN"""
        p[0] = ast.FuncCallStmt(ast.FuncCall(p[1], p[3]))

    def p_arg_list(self, p):
        """arg_list : expr_list
                    | empty"""
        p[0] = p[1] if p[1] is not None else []

    def p_ident_list(self, p):
        """ident_list : IDENT ident_list_tail"""
        p[0] = [p[1]] + p[2]

    def p_ident_list_tail(self, p):
        """ident_list_tail : COMMA IDENT ident_list_tail
                           | empty"""
        if len(p) == 4:
            p[0] = [p[2]] + p[3]
        else:
            p[0] = []

    def p_expr_list(self, p):
        """expr_list : expr expr_list_tail"""
        p[0] = [p[1]] + p[2]

    def p_expr_list_tail(self, p):
        """expr_list_tail : COMMA expr expr_list_tail
                          | empty"""
        if len(p) == 4:
            p[0] = [p[2]] + p[3]
        else:
            p[0] = []

    def p_expr(self, p):
        """expr : expr PLUS term
                | expr MINUS term"""
        p[0] = ast.BinaryOp(p[2], p[1], p[3])

    def p_expr_term(self, p):
        """expr : term"""
        p[0] = p[1]

    def p_term(self, p):
        """term : term TIMES factor
                 | term DIVIDE factor"""
        p[0] = ast.BinaryOp(p[2], p[1], p[3])

    def p_term_factor(self, p):
        """term : factor"""
        p[0] = p[1]

    def p_factor_number(self, p):
        """factor : NUMBER"""
        p[0] = ast.Number(p[1])

    def p_factor_ident(self, p):
        """factor : ident_expr"""
        p[0] = p[1]

    def p_factor_group(self, p):
        """factor : LPAREN expr RPAREN"""
        p[0] = p[2]

    def p_ident_expr(self, p):
        """ident_expr : IDENT
                      | IDENT LBRACKET expr RBRACKET
                      | IDENT DOT IDENT
                      | func_call_expr"""
        if len(p) == 2:
            if isinstance(p[1], ast.FuncCall):
                p[0] = p[1]
            else:
                p[0] = ast.Var(p[1])
        elif len(p) == 5:
            p[0] = ast.ArrayAccess(p[1], p[3])
        elif len(p) == 4 and p[2] == '.':
            p[0] = ast.FieldAccess(p[1], p[3])
        else:
            p[0] = p[1]

    def p_func_call_expr(self, p):
        """func_call_expr : IDENT LPAREN arg_list RPAREN"""
        p[0] = ast.FuncCall(p[1], p[3])

    def p_expr_unary(self, p):
        """factor : MINUS factor %prec UMINUS"""
        p[0] = ast.UnaryOp('-', p[2])

    def p_empty(self, p):
        'empty :'
        p[0] = None

    def p_error(self, p):
        if p:
            raise SyntaxError(f"Syntax error at '{p.value}' on line {p.lineno}")
        else:
            raise SyntaxError('Unexpected EOF')


def parse(text: str) -> ast.Program:
    return Parser().parse(text)

