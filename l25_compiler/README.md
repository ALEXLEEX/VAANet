# L25 Compiler (Basic)

This directory contains a simple compiler and interpreter for the L25 language
written in Python. In addition to the base features, it implements support for
one‑dimensional static arrays and simple structures (structs).

## Usage

```
python -m l25_compiler.main <source.l25>
```

The compiler performs lexical analysis, parsing, builds an AST, and interprets
the program directly.

## Testing

Three example programs are provided in the `examples` directory. You can run
one via:

```
python -m l25_compiler.main examples/factorial.l25
```

## Example Programs

- `factorial.l25`: Compute factorial of an integer.
- `fibonacci.l25`: Output Fibonacci sequence up to `n`.
- `sum.l25`: Sum numbers from 1 to `n`.
- `array_struct.l25`: Demonstrates arrays and structs.
