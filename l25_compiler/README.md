# L25 Compiler (Basic)

This directory contains a simple compiler and interpreter for the L25 language
written in Python. In addition to the base features, it implements support for
one‑dimensional static arrays and simple structures (structs).

## Usage

```
python -m l25_compiler.main [options] <source.l25>
```

By default the program is interpreted directly. Additional options allow
inspection of intermediate stages:

- `--tokens` &ndash; output the token stream
- `--ast` &ndash; dump the parsed abstract syntax tree
- `--ir` &ndash; print a simplified intermediate representation
- `--no-run` &ndash; skip execution after generating the chosen outputs

## Testing

Three example programs are provided in the `examples` directory. You can run
one normally or request intermediate output:

```
python -m l25_compiler.main examples/factorial.l25

# show tokens and IR only
python -m l25_compiler.main --tokens --ir --no-run examples/factorial.l25
```

## Example Programs

- `factorial.l25`: Compute factorial of an integer.
- `fibonacci.l25`: Output Fibonacci sequence up to `n`.
- `sum.l25`: Sum numbers from 1 to `n`.
- `array_struct.l25`: Demonstrates arrays and structs.
