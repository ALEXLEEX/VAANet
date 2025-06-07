import tkinter as tk
from tkinter import filedialog, scrolledtext
import io
from contextlib import redirect_stdout
from .lexer import tokenize
from .parser import Parser
from .utils import dump_ast
from .ir import IRGenerator
from .tac import ThreeAddressGenerator
from .interpreter import Interpreter


def run_compiler(path, show_tokens=False, show_ast=False, show_ir=False, show_tac=False, run_program=True, input_text=""):
    with open(path) as f:
        code = f.read()

    output_lines = []
    tokens = list(tokenize(code))
    if show_tokens:
        output_lines += [str(t) for t in tokens]

    parser = Parser(tokens)
    ast = parser.parse()
    if show_ast:
        output_lines += dump_ast(ast)

    ir_lines = IRGenerator().generate(ast)
    tac_lines = ThreeAddressGenerator().generate(ast)
    if show_ir:
        output_lines += ir_lines
    if show_tac:
        output_lines += tac_lines

    if run_program:
        inputs = iter(input_text.splitlines())

        def fake_input(prompt=""):
            try:
                return next(inputs)
            except StopIteration:
                return ""

        buf = io.StringIO()
        import builtins
        real_input = builtins.input
        builtins.input = fake_input
        try:
            with redirect_stdout(buf):
                Interpreter(ast).run()
        finally:
            builtins.input = real_input
        output_lines.append(buf.getvalue().strip())

    return "\n".join(output_lines)


class L25GUI:
    def __init__(self, root):
        self.root = root
        root.title("L25 Compiler")

        file_frame = tk.Frame(root)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(file_frame, text="Source file:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.path_var, width=40).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(file_frame, text="Browse", command=self.browse).pack(side=tk.LEFT, padx=5)

        opts = tk.Frame(root)
        opts.pack(fill=tk.X, padx=5)
        self.token_var = tk.IntVar()
        self.ast_var = tk.IntVar()
        self.ir_var = tk.IntVar()
        self.tac_var = tk.IntVar()
        self.run_var = tk.IntVar(value=1)
        tk.Checkbutton(opts, text="Tokens", variable=self.token_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="AST", variable=self.ast_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="IR", variable=self.ir_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="TAC", variable=self.tac_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="Run", variable=self.run_var).pack(side=tk.LEFT)

        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        tk.Label(input_frame, text="Program Input (one value per line):").pack(anchor=tk.W)
        self.input_text = tk.Text(input_frame, height=4)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        tk.Button(root, text="Compile", command=self.compile).pack(pady=5)

        self.output = scrolledtext.ScrolledText(root, height=20)
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("L25 files", "*.l25"), ("All files", "*")])
        if path:
            self.path_var.set(path)

    def compile(self):
        path = self.path_var.get()
        if not path:
            return
        result = run_compiler(
            path,
            show_tokens=bool(self.token_var.get()),
            show_ast=bool(self.ast_var.get()),
            show_ir=bool(self.ir_var.get()),
            show_tac=bool(self.tac_var.get()),
            run_program=bool(self.run_var.get()),
            input_text=self.input_text.get("1.0", tk.END),
        )
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, result)


def main():
    root = tk.Tk()
    L25GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
