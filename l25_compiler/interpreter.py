from .ast_nodes import *

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f'Undefined variable {name}')

    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise NameError(f'Undefined variable {name}')

    def define(self, name, value=0):
        self.vars[name] = value

class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.functions = {f.name: f for f in ast.funcs}

    def run(self):
        env = Environment()
        self.exec_stmt_list(self.ast.main, env)

    def eval_expr(self, node, env):
        if isinstance(node, Number):
            return node.value
        if isinstance(node, Identifier):
            return env.get(node.name)
        if isinstance(node, ArrayAccess):
            arr = self.eval_expr(node.array, env)
            idx = self.eval_expr(node.index, env)
            return arr[idx]
        if isinstance(node, FieldAccess):
            obj = self.eval_expr(node.obj, env)
            return obj.get(node.field)
        if isinstance(node, ArrayLiteral):
            return [self.eval_expr(e, env) for e in node.elements]
        if isinstance(node, StructLiteral):
            return {k: self.eval_expr(v, env) for k, v in node.fields.items()}
        if isinstance(node, UnaryOp):
            val = self.eval_expr(node.operand, env)
            if node.op == '+':
                return +val
            else:
                return -val
        if isinstance(node, BinaryOp):
            left = self.eval_expr(node.left, env)
            right = self.eval_expr(node.right, env)
            if node.op == '+':
                return left + right
            if node.op == '-':
                return left - right
            if node.op == '*':
                return left * right
            if node.op == '/':
                return left // right
            if node.op == '==':
                return int(left == right)
            if node.op == '!=':
                return int(left != right)
            if node.op == '<':
                return int(left < right)
            if node.op == '<=':
                return int(left <= right)
            if node.op == '>':
                return int(left > right)
            if node.op == '>=':
                return int(left >= right)
            raise RuntimeError(f'Unknown operator {node.op}')
        if isinstance(node, FuncCall):
            return self.call_func(node, env)
        raise RuntimeError('Unknown expression')

    def exec_stmt_list(self, stmt_list, env):
        for stmt in stmt_list.stmts:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, stmt, env):
        if isinstance(stmt, Declare):
            if stmt.size is not None:
                size = self.eval_expr(stmt.size, env)
                env.define(stmt.name, [0] * size)
            else:
                value = self.eval_expr(stmt.expr, env) if stmt.expr else 0
                env.define(stmt.name, value)
        elif isinstance(stmt, Assign):
            val = self.eval_expr(stmt.expr, env)
            target = stmt.target
            if isinstance(target, Identifier):
                env.set(target.name, val)
            elif isinstance(target, ArrayAccess):
                arr = self.eval_expr(target.array, env)
                idx = self.eval_expr(target.index, env)
                arr[idx] = val
            elif isinstance(target, FieldAccess):
                obj = self.eval_expr(target.obj, env)
                obj[target.field] = val
            else:
                raise RuntimeError('Invalid assignment target')
        elif isinstance(stmt, If):
            cond = self.eval_expr(stmt.cond, env)
            if cond:
                self.exec_stmt_list(stmt.then, Environment(env))
            elif stmt.else_:
                self.exec_stmt_list(stmt.else_, Environment(env))
        elif isinstance(stmt, While):
            while self.eval_expr(stmt.cond, env):
                self.exec_stmt_list(stmt.body, Environment(env))
        elif isinstance(stmt, Input):
            for name in stmt.names:
                val = int(input(f'{name}: '))
                env.set(name, val) if name in env.vars else env.define(name, val)
        elif isinstance(stmt, Output):
            vals = [self.eval_expr(e, env) for e in stmt.exprs]
            print(*vals)
        elif isinstance(stmt, FuncCall):
            self.call_func(stmt, env)
        else:
            raise RuntimeError('Unknown statement')

    def call_func(self, call, env):
        func = self.functions.get(call.name)
        if not func:
            raise NameError(f'Undefined function {call.name}')
        if len(call.args) != len(func.params):
            raise TypeError('Argument count mismatch')
        new_env = Environment(env)
        for name, arg in zip(func.params, call.args):
            new_env.define(name, self.eval_expr(arg, env))
        self.exec_stmt_list(func.body, new_env)
        return self.eval_expr(func.ret, new_env)
