import argparse
from .lexer import tokenize
from .parser import Parser
from .interpreter import Interpreter
from .utils import dump_ast
from .ir import IRGenerator


def main():
    parser = argparse.ArgumentParser(description="L25 compiler")
    parser.add_argument("source", help="L25 source file")
    parser.add_argument("--tokens", action="store_true", help="print tokens and exit")
    parser.add_argument("--ast", action="store_true", help="print AST and exit unless --ir or execution requested")
    parser.add_argument("--ir", action="store_true", help="print intermediate representation")
    parser.add_argument("--no-run", action="store_true", help="do not execute program")
    args = parser.parse_args()

    with open(args.source) as f:
        code = f.read()

    tokens = list(tokenize(code))
    if args.tokens:
        for t in tokens:
            print(t)
        if not (args.ast or args.ir or not args.no_run):
            return

    parser_obj = Parser(tokens)
    ast = parser_obj.parse()
    if args.ast:
        for line in dump_ast(ast):
            print(line)
        if not (args.ir or not args.no_run):
            return

    ir_lines = IRGenerator().generate(ast)
    if args.ir:
        for line in ir_lines:
            print(line)
        if args.no_run:
            return

    if not args.no_run:
        interpreter = Interpreter(ast)
        interpreter.run()

if __name__ == "__main__":
    main()
