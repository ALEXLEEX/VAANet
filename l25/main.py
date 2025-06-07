from .parser import parse
from .interpreter import eval_program
import sys


def main(path: str):
    with open(path, 'r') as f:
        source = f.read()
    program = parse(source)
    eval_program(program)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python -m l25.main <source.l25>')
    else:
        main(sys.argv[1])
