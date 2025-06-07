from l25.main import main
import tempfile
import textwrap

source = textwrap.dedent('''
program demo {
func add(a, b) {
let c = a + b;
return c;
}
main {
let x = add(1,2);
output(x);
}
}
''')

with tempfile.NamedTemporaryFile('w+', suffix='.l25', delete=False) as f:
    f.write(source)
    fname = f.name

main(fname)
