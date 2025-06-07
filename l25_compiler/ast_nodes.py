class Node:
    pass

class Program(Node):
    def __init__(self, name, funcs, main):
        self.name = name
        self.funcs = funcs
        self.main = main

class FuncDef(Node):
    def __init__(self, name, params, body, ret):
        self.name = name
        self.params = params
        self.body = body
        self.ret = ret

class StmtList(Node):
    def __init__(self, stmts):
        self.stmts = stmts

class Declare(Node):
    def __init__(self, name, expr=None, size=None):
        self.name = name
        self.expr = expr
        self.size = size

class Assign(Node):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

class If(Node):
    def __init__(self, cond, then, else_=None):
        self.cond = cond
        self.then = then
        self.else_ = else_

class While(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class Input(Node):
    def __init__(self, names):
        self.names = names

class Output(Node):
    def __init__(self, exprs):
        self.exprs = exprs

class FuncCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Return(Node):
    def __init__(self, expr):
        self.expr = expr

class BinaryOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOp(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class Number(Node):
    def __init__(self, value):
        self.value = value

class Identifier(Node):
    def __init__(self, name):
        self.name = name

class ArrayAccess(Node):
    def __init__(self, array, index):
        self.array = array
        self.index = index

class FieldAccess(Node):
    def __init__(self, obj, field):
        self.obj = obj
        self.field = field

class ArrayLiteral(Node):
    def __init__(self, elements):
        self.elements = elements

class StructLiteral(Node):
    def __init__(self, fields):
        self.fields = fields

class MapLiteral(Node):
    def __init__(self, pairs):
        self.pairs = pairs  # list of (key, value)

class SetLiteral(Node):
    def __init__(self, elements):
        self.elements = elements
