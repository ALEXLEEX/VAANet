import sys
from .lexer import tokenize
from .parser import Parser
from .interpreter import Interpreter


def main(filename):
    with open(filename) as f:
        code = f.read()
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter(ast)
    interpreter.run()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python -m l25_compiler.main <source.l25>')
        sys.exit(1)
    main(sys.argv[1])
