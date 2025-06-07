from .ast_nodes import *


def dump_ast(node, indent=0):
    sp = ' ' * indent
    if isinstance(node, Program):
        lines = [f"{sp}Program({node.name})"]
        for f in node.funcs:
            lines.extend(dump_ast(f, indent + 2))
        lines.append(f"{sp}main:")
        lines.extend(dump_ast(node.main, indent + 2))
        return lines
    if isinstance(node, FuncDef):
        lines = [f"{sp}FuncDef({node.name} params={node.params})"]
        lines.extend(dump_ast(node.body, indent + 2))
        lines.append(f"{sp}return:")
        lines.extend(dump_ast(node.ret, indent + 2))
        return lines
    if isinstance(node, StmtList):
        lines = []
        for s in node.stmts:
            lines.extend(dump_ast(s, indent))
        return lines
    if isinstance(node, Declare):
        if node.size is not None:
            return [f"{sp}Declare {node.name}[{dump_ast(node.size)[0].strip()}]"]
        if node.expr is not None:
            return [f"{sp}Declare {node.name} = {dump_ast(node.expr)[0].strip()}"]
        return [f"{sp}Declare {node.name}"]
    if isinstance(node, Assign):
        return [f"{sp}{dump_ast(node.target)[0].strip()} = {dump_ast(node.expr)[0].strip()}"]
    if isinstance(node, Identifier):
        return [f"{sp}{node.name}"]
    if isinstance(node, Number):
        return [f"{sp}{node.value}"]
    if isinstance(node, ArrayAccess):
        arr = dump_ast(node.array)[0].strip()
        idx = dump_ast(node.index)[0].strip()
        return [f"{sp}{arr}[{idx}]"]
    if isinstance(node, FieldAccess):
        obj = dump_ast(node.obj)[0].strip()
        return [f"{sp}{obj}.{node.field}"]
    if isinstance(node, ArrayLiteral):
        elems = ', '.join(e.strip() for e in sum((dump_ast(e) for e in node.elements), []))
        return [f"{sp}[{elems}]"]
    if isinstance(node, StructLiteral):
        fields = ', '.join(f"{k}={dump_ast(v)[0].strip()}" for k, v in node.fields.items())
        return [f"{sp}struct{{{fields}}}"]
    if isinstance(node, UnaryOp):
        return [f"{sp}{node.op}{dump_ast(node.operand)[0].strip()}"]
    if isinstance(node, BinaryOp):
        left = dump_ast(node.left)[0].strip()
        right = dump_ast(node.right)[0].strip()
        return [f"{sp}({left} {node.op} {right})"]
    if isinstance(node, Input):
        return [f"{sp}input {', '.join(node.names)}"]
    if isinstance(node, Output):
        exprs = ', '.join(dump_ast(e)[0].strip() for e in node.exprs)
        return [f"{sp}output {exprs}"]
    if isinstance(node, FuncCall):
        args = ', '.join(dump_ast(a)[0].strip() for a in node.args)
        return [f"{sp}{node.name}({args})"]
    if isinstance(node, If):
        lines = [f"{sp}if {dump_ast(node.cond)[0].strip()}:"]
        for s in node.then.stmts:
            lines.extend(dump_ast(s, indent + 2))
        if node.else_:
            lines.append(f"{sp}else:")
            for s in node.else_.stmts:
                lines.extend(dump_ast(s, indent + 2))
        return lines
    if isinstance(node, While):
        lines = [f"{sp}while {dump_ast(node.cond)[0].strip()}:"]
        for s in node.body.stmts:
            lines.extend(dump_ast(s, indent + 2))
        return lines
    if isinstance(node, Return):
        return [f"{sp}return {dump_ast(node.expr)[0].strip()}"]
    raise RuntimeError('Unknown node')
