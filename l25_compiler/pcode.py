from .ast_nodes import *

class PCodeGenerator:
    def __init__(self):
        self.lines = []
        self.label = 0

    def new_label(self):
        self.label += 1
        return f"L{self.label}"

    def emit(self, line):
        self.lines.append(line)

    def expr(self, node):
        if isinstance(node, Number):
            self.emit(f"PUSH {node.value}")
        elif isinstance(node, Identifier):
            self.emit(f"LOAD {node.name}")
        elif isinstance(node, ArrayAccess):
            self.expr(node.array)
            self.expr(node.index)
            self.emit("ALOAD")
        elif isinstance(node, FieldAccess):
            self.expr(node.obj)
            self.emit(f"FLOAD {node.field}")
        elif isinstance(node, ArrayLiteral):
            for e in node.elements:
                self.expr(e)
            self.emit(f"ARRAY {len(node.elements)}")
        elif isinstance(node, StructLiteral):
            for k, v in node.fields.items():
                self.expr(v)
                self.emit(f"SETFIELD {k}")
            self.emit("STRUCT")
        elif isinstance(node, MapLiteral):
            for k, v in node.pairs:
                self.expr(k)
                self.expr(v)
                self.emit("MAP_INSERT")
            self.emit("MAP")
        elif isinstance(node, SetLiteral):
            for e in node.elements:
                self.expr(e)
                self.emit("SET_ADD")
            self.emit("SET")
        elif isinstance(node, UnaryOp):
            if node.op == '&':
                if isinstance(node.operand, Identifier):
                    self.emit(f"ADDR {node.operand.name}")
                elif isinstance(node.operand, ArrayAccess):
                    self.expr(node.operand.array)
                    self.expr(node.operand.index)
                    self.emit("AADDR")
                elif isinstance(node.operand, FieldAccess):
                    self.expr(node.operand.obj)
                    self.emit(f"FADDR {node.operand.field}")
                else:
                    raise RuntimeError('invalid address-of operand')
            else:
                self.expr(node.operand)
                if node.op == '-':
                    self.emit('NEG')
                elif node.op == '+':
                    pass
                elif node.op == '*':
                    self.emit('DEREF')
        elif isinstance(node, BinaryOp):
            self.expr(node.left)
            self.expr(node.right)
            opmap = {'+':'ADD','-':'SUB','*':'MUL','/':'DIV',
                     '==':'EQ','!=':'NE','<':'LT','<=':'LE','>':'GT','>=':'GE'}
            self.emit(opmap.get(node.op, node.op))
        elif isinstance(node, FuncCall):
            for a in node.args:
                self.expr(a)
            self.emit(f"CALL {node.name} {len(node.args)}")
        else:
            raise RuntimeError('Unknown expression')

    def stmt(self, node):
        if isinstance(node, Declare):
            if node.size is not None:
                self.expr(node.size)
                self.emit(f"DECL_ARR {node.name}")
            elif node.expr is not None:
                self.expr(node.expr)
                self.emit(f"STORE {node.name}")
            else:
                self.emit(f"DECL {node.name}")
        elif isinstance(node, Assign):
            self.expr(node.expr)
            self.store_target(node.target)
        elif isinstance(node, Input):
            for n in node.names:
                self.emit(f"READ {n}")
        elif isinstance(node, Output):
            for e in node.exprs:
                self.expr(e)
                self.emit("PRINT")
            self.emit("NEWLINE")
        elif isinstance(node, FuncCall):
            self.expr(node)
            self.emit("POP")
        elif isinstance(node, If):
            else_label = self.new_label()
            end_label = self.new_label() if node.else_ else else_label
            self.expr(node.cond)
            self.emit(f"JZ {else_label}")
            for s in node.then.stmts:
                self.stmt(s)
            if node.else_:
                self.emit(f"JMP {end_label}")
                self.emit(f"{else_label}:")
                for s in node.else_.stmts:
                    self.stmt(s)
                self.emit(f"{end_label}:")
            else:
                self.emit(f"{else_label}:")
        elif isinstance(node, While):
            start = self.new_label()
            end = self.new_label()
            self.emit(f"{start}:")
            self.expr(node.cond)
            self.emit(f"JZ {end}")
            for s in node.body.stmts:
                self.stmt(s)
            self.emit(f"JMP {start}")
            self.emit(f"{end}:")
        elif isinstance(node, DoUntil):
            start = self.new_label()
            self.emit(f"{start}:")
            for s in node.body.stmts:
                self.stmt(s)
            self.expr(node.cond)
            self.emit(f"JZ {start}")
        else:
            raise RuntimeError('Unknown statement')

    def store_target(self, target):
        if isinstance(target, Identifier):
            self.emit(f"STORE {target.name}")
        elif isinstance(target, ArrayAccess):
            self.expr(target.array)
            self.expr(target.index)
            self.emit("ASTORE")
        elif isinstance(target, FieldAccess):
            self.expr(target.obj)
            self.emit(f"FSTORE {target.field}")
        elif isinstance(target, UnaryOp) and target.op == '*':
            self.expr(target.operand)
            self.emit("PSTORE")
        else:
            raise RuntimeError('Invalid assignment target')

    def stmt_list(self, sl):
        for s in sl.stmts:
            self.stmt(s)

    def func(self, f):
        self.emit(f"FUNC {f.name}")
        for s in f.body.stmts:
            self.stmt(s)
        self.expr(f.ret)
        self.emit("RET")

    def generate(self, ast):
        self.emit(f"PROGRAM {ast.name}")
        for f in ast.funcs:
            self.func(f)
        self.emit("MAIN")
        self.stmt_list(ast.main)
        self.emit("END")
        return self.lines
