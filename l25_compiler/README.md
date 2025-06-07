# L25 Compiler (Basic)

This directory contains a simple compiler and interpreter for the L25 language
written in Python. In addition to the base features, it implements support for
one‑dimensional static arrays, simple structures (structs), basic pointer
operations (`&` address-of and `*` dereference), and simple `map`/`set`
containers with helper functions for insertion, deletion, lookup and
iteration.

## Usage

```
python -m l25_compiler.main [options] <source.l25>
```

For a graphical interface, run:

```
python -m l25_compiler.gui
```

The GUI presents a notebook with tabs labeled in Chinese for tokens, AST, IR
and TAC. Selecting a tab shows the corresponding intermediate output. A second
pane of equal size displays the program's runtime output.

By default the program is interpreted directly. Additional options allow
inspection of intermediate stages:

- `--tokens` &ndash; output the token stream
- `--ast` &ndash; dump the parsed abstract syntax tree
- `--ir` &ndash; print a simplified intermediate representation
- `--tac` &ndash; emit linear three-address code
- `--no-run` &ndash; skip execution after generating the chosen outputs

## Testing

Three example programs are provided in the `examples` directory. You can run
one normally or request intermediate output:

```
python -m l25_compiler.main examples/factorial.l25

# show tokens and IR only
    python -m l25_compiler.main --tokens --ir --tac --no-run \
    examples/factorial.l25
```

### Map/Set Helpers

The interpreter provides a few built-in functions for manipulating `map` and
`set` values:

- `map_insert(m, key, value)` – add or update an entry
- `map_delete(m, key)` – remove an entry
- `map_get(m, key)` – fetch a value (returns `0` if absent)
- `map_has(m, key)` – test for membership
- `map_keys(m)` – return an array of keys
- `set_add(s, value)` – insert a value
- `set_remove(s, value)` – delete a value
- `set_contains(s, value)` – check for membership
- `set_items(s)` – return an array of elements

## Example Programs

- `factorial.l25`: Compute factorial of an integer.
- `fibonacci.l25`: Output Fibonacci sequence up to `n`.
- `sum.l25`: Sum numbers from 1 to `n`.
- `array_struct.l25`: Demonstrates arrays and structs.
- `pointer.l25`: Demonstrates basic pointer usage.
- `map_set.l25`: Demonstrates map and set operations using all helper functions.
