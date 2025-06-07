# L25 Compiler (Python)

This directory contains a simple interpreter for the L25 language written in Python using the [PLY](https://www.dabeaz.com/ply/) parsing library. The design isolates the lexer and parser so that it can be replaced by an ANTLR‑generated parser in the future.

## Usage

1. Install the dependency:
   ```bash
   pip install ply
   ```
2. Run a program:
   ```bash
   python -m l25.main path/to/source.l25
   ```

## Project Layout

- `lexer.py` – token definitions and lexer implementation using PLY.
- `parser.py` – grammar rules that produce an abstract syntax tree.
- `ast_nodes.py` – dataclasses describing the AST nodes.
- `interpreter.py` – executes the AST. Arrays are represented with Python lists, structs with dictionaries.
- `main.py` – command line entry point.

The parser and interpreter modules are decoupled from the lexer so that future work can plug in an ANTLR-based parser by implementing the same AST generation.

## Testing

A basic smoke test is provided in `tests/test_sample.py`. Run:
```bash
python l25/tests/test_sample.py
```
