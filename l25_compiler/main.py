import argparse
from .lexer import tokenize
from .parser import Parser
from .pcode_vm import PCodeVM
from .utils import dump_ast
from .ir import IRGenerator
from .tac import ThreeAddressGenerator
from .pcode import PCodeGenerator


def main():
    parser = argparse.ArgumentParser(description="L25 compiler")
    parser.add_argument("source", help="L25 source file")
    parser.add_argument("--tokens", action="store_true", help="print tokens and exit")
    parser.add_argument("--ast", action="store_true", help="print AST and exit unless --ir or execution requested")
    parser.add_argument("--ir", action="store_true", help="print intermediate representation")
    parser.add_argument("--tac", action="store_true", help="print three-address code")
    parser.add_argument("--pcode", action="store_true", help="print pcode instructions")
    parser.add_argument("--no-run", action="store_true", help="do not execute program")
    args = parser.parse_args()

    with open(args.source) as f:
        code = f.read()

    tokens = list(tokenize(code))
    if args.tokens:
        for t in tokens:
            print(t)
        if not (args.ast or args.ir or args.tac or args.pcode or not args.no_run):
            return

    parser_obj = Parser(tokens)
    ast = parser_obj.parse()
    if args.ast:
        for line in dump_ast(ast):
            print(line)
        if not (args.ir or args.tac or args.pcode or not args.no_run):
            return

    ir_lines = IRGenerator().generate(ast)
    tac_lines = ThreeAddressGenerator().generate(ast)
    pcode_lines = PCodeGenerator().generate(ast)
    if args.ir:
        for line in ir_lines:
            print(line)
        if args.no_run and not (args.tac or args.pcode):
            return

    if args.tac:
        for line in tac_lines:
            print(line)
        if args.no_run and not args.pcode:
            return

    if args.pcode:
        for line in pcode_lines:
            print(line)
        if args.no_run:
            return

    if not args.no_run:
        vm = PCodeVM(pcode_lines, ast)
        output = vm.run()
        if output:
            print(output)

if __name__ == "__main__":
    main()
