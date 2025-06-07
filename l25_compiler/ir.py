from .ast_nodes import *

class IRGenerator:
    def expr(self, node):
        if isinstance(node, Number):
            return str(node.value)
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, ArrayAccess):
            return f"{self.expr(node.array)}[{self.expr(node.index)}]"
        if isinstance(node, FieldAccess):
            return f"{self.expr(node.obj)}.{node.field}"
        if isinstance(node, ArrayLiteral):
            elems = ', '.join(self.expr(e) for e in node.elements)
            return f"[{elems}]"
        if isinstance(node, StructLiteral):
            elems = ', '.join(f"{k}={self.expr(v)}" for k, v in node.fields.items())
            return f"struct{{{elems}}}"
        if isinstance(node, UnaryOp):
            return f"({node.op}{self.expr(node.operand)})"
        if isinstance(node, BinaryOp):
            return f"({self.expr(node.left)} {node.op} {self.expr(node.right)})"
        if isinstance(node, FuncCall):
            args = ', '.join(self.expr(a) for a in node.args)
            return f"{node.name}({args})"
        raise RuntimeError('Unknown expr')

    def stmt(self, node, indent=0):
        sp = ' ' * indent
        if isinstance(node, Declare):
            if node.size is not None:
                size = self.expr(node.size)
                return [f"{sp}let {node.name}[{size}]"]
            if node.expr is not None:
                return [f"{sp}let {node.name} = {self.expr(node.expr)}"]
            return [f"{sp}let {node.name}"]
        if isinstance(node, Assign):
            return [f"{sp}{self.expr(node.target)} = {self.expr(node.expr)}"]
        if isinstance(node, Input):
            return [f"{sp}input {', '.join(node.names)}"]
        if isinstance(node, Output):
            exprs = ', '.join(self.expr(e) for e in node.exprs)
            return [f"{sp}output {exprs}"]
        if isinstance(node, FuncCall):
            return [f"{sp}{self.expr(node)}"]
        if isinstance(node, If):
            lines = [f"{sp}if {self.expr(node.cond)} {{"]
            for s in node.then.stmts:
                lines += self.stmt(s, indent + 2)
            if node.else_:
                lines.append(f"{sp}}} else {{")
                for s in node.else_.stmts:
                    lines += self.stmt(s, indent + 2)
            lines.append(f"{sp}}}")
            return lines
        if isinstance(node, While):
            lines = [f"{sp}while {self.expr(node.cond)} {{"]
            for s in node.body.stmts:
                lines += self.stmt(s, indent + 2)
            lines.append(f"{sp}}}")
            return lines
        raise RuntimeError('Unknown stmt')

    def stmt_list(self, stmt_list, indent=0):
        lines = []
        for s in stmt_list.stmts:
            lines += self.stmt(s, indent)
        return lines

    def func(self, func):
        lines = [f"func {func.name}({', '.join(func.params)}) {{"]
        lines += self.stmt_list(func.body, 2)
        lines.append(f"  return {self.expr(func.ret)};")
        lines.append("}")
        return lines

    def generate(self, ast):
        lines = [f"program {ast.name} {{"]
        for f in ast.funcs:
            lines += self.func(f)
        lines.append("main {")
        lines += self.stmt_list(ast.main, 2)
        lines.append("}")
        lines.append("}")
        return lines
