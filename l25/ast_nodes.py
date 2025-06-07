from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class Program:
    name: str
    funcs: List['FuncDef']
    main: 'Block'

@dataclass
class FuncDef:
    name: str
    params: List[str]
    body: 'Block'
    return_expr: 'Expr'

@dataclass
class Block:
    statements: List['Stmt']

@dataclass
class StructDef:
    name: str
    fields: List[str]

# --- Statements ---
class Stmt:
    pass

@dataclass
class Declare(Stmt):
    name: str
    expr: Optional['Expr'] = None

@dataclass
class Assign(Stmt):
    target: 'Expr'
    expr: 'Expr'

@dataclass
class If(Stmt):
    condition: 'Expr'
    then_block: Block
    else_block: Optional[Block] = None

@dataclass
class While(Stmt):
    condition: 'Expr'
    body: Block

@dataclass
class FuncCallStmt(Stmt):
    call: 'FuncCall'

@dataclass
class InputStmt(Stmt):
    targets: List[str]

@dataclass
class OutputStmt(Stmt):
    exprs: List['Expr']

# --- Expressions ---
class Expr:
    pass

@dataclass
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr

@dataclass
class Number(Expr):
    value: int

@dataclass
class Var(Expr):
    name: str

@dataclass
class ArrayAccess(Expr):
    array: str
    index: Expr

@dataclass
class FieldAccess(Expr):
    var: str
    field: str

@dataclass
class FuncCall(Expr):
    name: str
    args: List[Expr]

