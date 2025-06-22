# L25 Compiler (Basic)

This directory contains a simple compiler for the L25 language written in
Python. Source files are translated into a stack-based pcode which is executed
by a small virtual machine. In addition to the base features, it implements support for
one‑dimensional static arrays, simple structures (structs), basic pointer
operations (`&` address-of and `*` dereference), simple `map`/`set` containers
with helper functions for insertion, deletion, lookup and iteration, and a
`do...until` loop construct.

## Usage

```
python -m l25_compiler.main [options] <source.l25>
```

For a graphical interface, run:

```
python -m l25_compiler.gui
```

The GUI presents a notebook with tabs labeled in Chinese for tokens, AST, IR,
TAC and PCODE. Selecting a tab shows the corresponding intermediate output. A second
pane of equal size displays the program's runtime output. When a source file is
loaded its contents appear in an **editable** box above the input area so you can
modify the code and recompile at any time. If the program requires input but none
is provided, the GUI issues a warning. Should a runtime error occur, any output
produced before the error is still shown.

By default the compiled pcode is executed on the virtual machine. Additional options allow
inspection of intermediate stages:

- `--tokens` &ndash; output the token stream
- `--ast` &ndash; dump the parsed abstract syntax tree
- `--ir` &ndash; print a simplified intermediate representation
- `--tac` &ndash; emit linear three-address code
- `--pcode` &ndash; emit stack-based pcode instructions
- `--no-run` &ndash; skip execution after generating the chosen outputs

## Testing

Three example programs are provided in the `examples` directory. You can run
one normally or request intermediate output:

```
python -m l25_compiler.main examples/factorial.l25

# show tokens and intermediate code only
    python -m l25_compiler.main --tokens --ir --tac --pcode --no-run \
    examples/factorial.l25
```

### Map/Set Helpers

The virtual machine provides a few built-in functions for manipulating `map` and
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
- `complex_edge.l25`: Exercises struct arrays, pointer manipulation and
  boundary behaviors of map/set helpers.
- `do_until.l25`: Shows the new `do...until` looping construct.
