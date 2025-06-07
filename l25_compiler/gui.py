import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
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

    tokens_list = list(tokenize(code))
    tokens_str = "\n".join(str(t) for t in tokens_list) if show_tokens else ""

    parser = Parser(tokens_list)
    ast = parser.parse()
    ast_str = "\n".join(dump_ast(ast)) if show_ast else ""

    ir_str = "\n".join(IRGenerator().generate(ast)) if show_ir else ""
    tac_str = "\n".join(ThreeAddressGenerator().generate(ast)) if show_tac else ""

    program_output = ""
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
        program_output = buf.getvalue().strip()

    return {
        "tokens": tokens_str,
        "ast": ast_str,
        "ir": ir_str,
        "tac": tac_str,
        "output": program_output,
    }


class L25GUI:
    def __init__(self, root):
        self.root = root
        root.title("L25 编译器")

        file_frame = tk.Frame(root)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(file_frame, text="源文件:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.path_var, width=40).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(file_frame, text="浏览", command=self.browse).pack(side=tk.LEFT, padx=5)

        opts = tk.Frame(root)
        opts.pack(fill=tk.X, padx=5)
        self.token_var = tk.IntVar()
        self.ast_var = tk.IntVar()
        self.ir_var = tk.IntVar()
        self.tac_var = tk.IntVar()
        self.run_var = tk.IntVar(value=1)
        tk.Checkbutton(opts, text="词法", variable=self.token_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="AST", variable=self.ast_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="IR", variable=self.ir_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="TAC", variable=self.tac_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="运行", variable=self.run_var).pack(side=tk.LEFT)

        self.code_display = scrolledtext.ScrolledText(root, height=10, state=tk.DISABLED)
        self.code_display.pack(fill=tk.BOTH, padx=5)

        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        tk.Label(input_frame, text="程序输入(每行一个值):").pack(anchor=tk.W)
        self.input_text = tk.Text(input_frame, height=4)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        tk.Button(root, text="编译", command=self.compile).pack(pady=5)

        output_frame = tk.Frame(root)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        notebook = ttk.Notebook(output_frame)
        notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.token_output = self._create_tab(notebook, "词法")
        self.ast_output = self._create_tab(notebook, "AST")
        self.ir_output = self._create_tab(notebook, "IR")
        self.tac_output = self._create_tab(notebook, "TAC")

        run_frame = tk.Frame(output_frame)
        run_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        tk.Label(run_frame, text="运行结果").pack()
        self.run_output = scrolledtext.ScrolledText(run_frame, height=15, state=tk.DISABLED)
        self.run_output.pack(fill=tk.BOTH, expand=True)

    def load_file(self, path):
        try:
            with open(path, 'r') as f:
                code = f.read()
        except OSError:
            code = ""
        self._set_text(self.code_display, code)
        return code

    def _ast_needs_input(self, ast):
        from .ast_nodes import Input, While, If, StmtList, FuncDef, Program

        def check_stmt(stmt):
            if isinstance(stmt, Input):
                return True
            if isinstance(stmt, While):
                return check_list(stmt.body)
            if isinstance(stmt, If):
                if check_list(stmt.then):
                    return True
                if stmt.else_ and check_list(stmt.else_):
                    return True
            return False

        def check_list(stmt_list):
            for s in stmt_list.stmts:
                if check_stmt(s):
                    return True
            return False

        if isinstance(ast, Program):
            if check_list(ast.main):
                return True
            for f in ast.funcs:
                if check_list(f.body):
                    return True
        return False

    def _create_tab(self, notebook, title):
        frame = tk.Frame(notebook)
        notebook.add(frame, text=title)
        box = scrolledtext.ScrolledText(frame, height=15, state=tk.DISABLED)
        box.pack(fill=tk.BOTH, expand=True)
        return box

    def _set_text(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        if text:
            widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("L25 files", "*.l25"), ("All files", "*")])
        if path:
            self.path_var.set(path)
            self.load_file(path)

    def compile(self):
        path = self.path_var.get()
        if not path:
            return
        code = self.load_file(path)

        tokens_list = list(tokenize(code))
        parser = Parser(tokens_list)
        try:
            ast = parser.parse()
        except Exception as e:
            messagebox.showerror("解析错误", str(e))
            return

        input_text = self.input_text.get("1.0", tk.END)
        if self.run_var.get() and self._ast_needs_input(ast) and not input_text.strip():
            messagebox.showwarning("缺少输入", "该程序需要输入，请在上方输入框中提供。")
            return

        try:
            result = run_compiler(
                path,
                show_tokens=bool(self.token_var.get()),
                show_ast=bool(self.ast_var.get()),
                show_ir=bool(self.ir_var.get()),
                show_tac=bool(self.tac_var.get()),
                run_program=bool(self.run_var.get()),
                input_text=input_text,
            )
        except ValueError:
            messagebox.showerror("输入错误", "输入数据格式不正确或数量不足。")
            return
        except Exception as e:
            messagebox.showerror("执行错误", str(e))
            return

        self._set_text(self.token_output, result["tokens"])
        self._set_text(self.ast_output, result["ast"])
        self._set_text(self.ir_output, result["ir"])
        self._set_text(self.tac_output, result["tac"])
        self._set_text(self.run_output, result["output"])


def main():
    root = tk.Tk()
    L25GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
