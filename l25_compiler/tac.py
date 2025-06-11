from .ast_nodes import *

class ThreeAddressGenerator:
    def __init__(self):
        self.temp = 0
        self.label = 0
        self.lines = []

    def new_temp(self):
        self.temp += 1
        return f"t{self.temp}"

    def new_label(self):
        self.label += 1
        return f"L{self.label}"

    def expr(self, node):
        if isinstance(node, Number):
            return str(node.value)
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, ArrayAccess):
            arr = self.expr(node.array)
            idx = self.expr(node.index)
            return f"{arr}[{idx}]"
        if isinstance(node, FieldAccess):
            obj = self.expr(node.obj)
            return f"{obj}.{node.field}"
        if isinstance(node, ArrayLiteral):
            elems = ', '.join(self.expr(e) for e in node.elements)
            return f"[{elems}]"
        if isinstance(node, StructLiteral):
            parts = ', '.join(f"{k}={self.expr(v)}" for k, v in node.fields.items())
            return f"struct{{{parts}}}"
        if isinstance(node, MapLiteral):
            parts = ', '.join(f"{self.expr(k)}:{self.expr(v)}" for k, v in node.pairs)
            return f"map{{{parts}}}"
        if isinstance(node, SetLiteral):
            parts = ', '.join(self.expr(e) for e in node.elements)
            return f"set{{{parts}}}"
        if isinstance(node, UnaryOp):
            val = self.expr(node.operand)
            tmp = self.new_temp()
            self.lines.append(f"{tmp} = {node.op}{val}")
            return tmp
        if isinstance(node, BinaryOp):
            left = self.expr(node.left)
            right = self.expr(node.right)
            tmp = self.new_temp()
            self.lines.append(f"{tmp} = {left} {node.op} {right}")
            return tmp
        if isinstance(node, FuncCall):
            args = [self.expr(a) for a in node.args]
            tmp = self.new_temp()
            self.lines.append(f"{tmp} = call {node.name}({', '.join(args)})")
            return tmp
        raise RuntimeError('Unknown expression')

    def stmt(self, node):
        if isinstance(node, Declare):
            if node.size is not None:
                size = self.expr(node.size)
                self.lines.append(f"{node.name} = [0] x {size}")
            elif node.expr is not None:
                val = self.expr(node.expr)
                self.lines.append(f"{node.name} = {val}")
            else:
                self.lines.append(f"{node.name} = 0")
        elif isinstance(node, Assign):
            val = self.expr(node.expr)
            target = self.expr(node.target)
            self.lines.append(f"{target} = {val}")
        elif isinstance(node, Input):
            for n in node.names:
                self.lines.append(f"input {n}")
        elif isinstance(node, Output):
            vals = ', '.join(self.expr(e) for e in node.exprs)
            self.lines.append(f"print {vals}")
        elif isinstance(node, FuncCall):
            self.expr(node)
        elif isinstance(node, If):
            cond = self.expr(node.cond)
            label_else = self.new_label()
            label_end = self.new_label() if node.else_ else label_else
            self.lines.append(f"if_false {cond} goto {label_else}")
            for s in node.then.stmts:
                self.stmt(s)
            if node.else_:
                self.lines.append(f"goto {label_end}")
                self.lines.append(f"{label_else}:")
                for s in node.else_.stmts:
                    self.stmt(s)
                self.lines.append(f"{label_end}:")
            else:
                self.lines.append(f"{label_else}:")
        elif isinstance(node, While):
            label_start = self.new_label()
            label_end = self.new_label()
            self.lines.append(f"{label_start}:")
            cond = self.expr(node.cond)
            self.lines.append(f"if_false {cond} goto {label_end}")
            for s in node.body.stmts:
                self.stmt(s)
            self.lines.append(f"goto {label_start}")
            self.lines.append(f"{label_end}:")
        elif isinstance(node, DoUntil):
            label_start = self.new_label()
            self.lines.append(f"{label_start}:")
            for s in node.body.stmts:
                self.stmt(s)
            cond = self.expr(node.cond)
            self.lines.append(f"if_false {cond} goto {label_start}")
        else:
            raise RuntimeError('Unknown statement')

    def stmt_list(self, sl):
        for s in sl.stmts:
            self.stmt(s)

    def func(self, f):
        self.lines.append(f"func {f.name}:")
        for s in f.body.stmts:
            self.stmt(s)
        ret = self.expr(f.ret)
        self.lines.append(f"return {ret}")

    def generate(self, ast):
        self.lines.append(f"program {ast.name}")
        for f in ast.funcs:
            self.func(f)
        self.lines.append("main:")
        self.stmt_list(ast.main)
        self.lines.append("end")
        return self.lines
