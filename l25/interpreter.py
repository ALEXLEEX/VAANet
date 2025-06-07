from typing import Any, Dict, List
from . import ast_nodes as ast


class Environment:
    def __init__(self, parent=None):
        self.vars: Dict[str, Any] = {}
        self.struct_defs: Dict[str, List[str]] = {}
        self.parent = parent

    def get(self, name: str):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable {name}")

    def set(self, name: str, value: Any):
        env = self if name in self.vars or self.parent is None else self.parent
        env.vars[name] = value


def eval_program(prog: ast.Program):
    global_env = Environment()
    functions = {f.name: f for f in prog.funcs}

    def call_func(func: ast.FuncDef, args: List[Any]):
        local = Environment(global_env)
        for name, value in zip(func.params, args):
            local.vars[name] = value
        res = eval_block(func.body, local)
        return eval_expr(func.return_expr, local)

    def eval_block(block: ast.Block, env: Environment):
        for stmt in block.statements:
            eval_stmt(stmt, env)

    def eval_stmt(stmt: ast.Stmt, env: Environment):
        if isinstance(stmt, ast.Declare):
            value = eval_expr(stmt.expr, env) if stmt.expr else 0
            env.vars[stmt.name] = value
        elif isinstance(stmt, ast.Assign):
            target = stmt.target
            if isinstance(target, ast.Var):
                env.set(target.name, eval_expr(stmt.expr, env))
            elif isinstance(target, ast.ArrayAccess):
                arr = env.get(target.array)
                index = eval_expr(target.index, env)
                arr[index] = eval_expr(stmt.expr, env)
            elif isinstance(target, ast.FieldAccess):
                obj = env.get(target.var)
                obj[target.field] = eval_expr(stmt.expr, env)
        elif isinstance(stmt, ast.If):
            if eval_expr(stmt.condition, env):
                eval_block(stmt.then_block, env)
            elif stmt.else_block:
                eval_block(stmt.else_block, env)
        elif isinstance(stmt, ast.While):
            while eval_expr(stmt.condition, env):
                eval_block(stmt.body, env)
        elif isinstance(stmt, ast.FuncCallStmt):
            eval_func_call(stmt.call, env)
        elif isinstance(stmt, ast.InputStmt):
            for name in stmt.targets:
                env.vars[name] = int(input(f"{name} = "))
        elif isinstance(stmt, ast.OutputStmt):
            values = [eval_expr(e, env) for e in stmt.exprs]
            print(*values)
        else:
            raise NotImplementedError(type(stmt))

    def eval_expr(expr: ast.Expr, env: Environment):
        if isinstance(expr, ast.Number):
            return expr.value
        elif isinstance(expr, ast.Var):
            return env.get(expr.name)
        elif isinstance(expr, ast.ArrayAccess):
            arr = env.get(expr.array)
            idx = eval_expr(expr.index, env)
            return arr[idx]
        elif isinstance(expr, ast.FieldAccess):
            obj = env.get(expr.var)
            return obj[expr.field]
        elif isinstance(expr, ast.BinaryOp):
            left = eval_expr(expr.left, env)
            right = eval_expr(expr.right, env)
            if expr.op == '+':
                return left + right
            if expr.op == '-':
                return left - right
            if expr.op == '*':
                return left * right
            if expr.op == '/':
                return left // right
            if expr.op == '==':
                return left == right
            if expr.op == '!=':
                return left != right
            if expr.op == '<':
                return left < right
            if expr.op == '<=':
                return left <= right
            if expr.op == '>':
                return left > right
            if expr.op == '>=':
                return left >= right
            raise ValueError(expr.op)
        elif isinstance(expr, ast.UnaryOp):
            val = eval_expr(expr.operand, env)
            if expr.op == '-':
                return -val
            raise ValueError(expr.op)
        elif isinstance(expr, ast.FuncCall):
            return eval_func_call(expr, env)
        else:
            raise NotImplementedError(type(expr))

    def eval_func_call(call: ast.FuncCall, env: Environment):
        if call.name == 'print':
            vals = [eval_expr(a, env) for a in call.args]
            print(*vals)
            return None
        if call.name not in functions:
            raise NameError(f"Undefined function {call.name}")
        func = functions[call.name]
        args = [eval_expr(a, env) for a in call.args]
        return call_func(func, args)

    eval_block(prog.main, global_env)

