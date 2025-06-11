from .ast_nodes import FuncDef

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable {name}")

    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise NameError(f"Undefined variable {name}")

    def define(self, name, value=0):
        self.vars[name] = value

    def lookup_env(self, name):
        if name in self.vars:
            return self
        if self.parent:
            return self.parent.lookup_env(name)
        raise NameError(f"Undefined variable {name}")

class Pointer:
    def __init__(self, container, key):
        self.container = container
        self.key = key

    def get(self):
        if isinstance(self.container, Environment):
            return self.container.vars[self.key]
        return self.container[self.key]

    def set(self, value):
        if isinstance(self.container, Environment):
            self.container.vars[self.key] = value
        else:
            self.container[self.key] = value

class PCodeVM:
    def __init__(self, lines, ast):
        self.lines = lines
        self.ast = ast
        self.stack = []
        self.env_stack = [Environment()]
        self.call_stack = []
        self.labels = {}
        self.func_addrs = {}
        self.func_defs = {f.name: f for f in ast.funcs}
        self._preprocess()
        self.output_lines = []
        self.current_line = []
        self.input_iter = iter([])
        self.prev_instr = None

    def _preprocess(self):
        for idx, line in enumerate(self.lines):
            if line.endswith(':'):
                self.labels[line[:-1]] = idx
            elif line.startswith('FUNC '):
                name = line.split()[1]
                self.func_addrs[name] = idx + 1
            elif line.startswith('MAIN'):
                self.main_addr = idx + 1

    def run(self, inputs=None):
        if inputs is None:
            inputs = []
        self.output_lines = []
        self.current_line = []
        self.input_iter = iter(inputs)
        ip = self.main_addr
        try:
            while ip < len(self.lines):
                parts = self.lines[ip].split()
                if not parts:
                    ip += 1
                    continue
                instr = parts[0]
                if instr.endswith(':'):
                    ip += 1
                    continue
                if instr == 'END':
                    self._flush_line()
                    break
                ip = self._exec(instr, parts[1:], ip)
                self.prev_instr = instr
            self._flush_line()
            return '\n'.join(self.output_lines).strip()
        except Exception:
            self._flush_line()
            raise

    def _flush_line(self):
        if self.current_line:
            self.output_lines.append(' '.join(self.current_line))
            self.current_line = []

    def _pop(self):
        if not self.stack:
            raise RuntimeError('Stack underflow')
        return self.stack.pop()

    def _exec(self, instr, args, ip):
        env = self.env_stack[-1]
        if instr == 'PUSH':
            self.stack.append(int(args[0]))
        elif instr == 'LOAD':
            self.stack.append(env.get(args[0]))
        elif instr == 'DECL':
            env.define(args[0], 0)
        elif instr == 'DECL_ARR':
            size = self._pop()
            env.define(args[0], [0]*size)
        elif instr == 'STORE':
            val = self._pop()
            try:
                env.lookup_env(args[0]).set(args[0], val)
            except NameError:
                env.define(args[0], val)
        elif instr == 'READ':
            try:
                val_str = next(self.input_iter)
            except StopIteration:
                val_str = input(f"{args[0]}: ")
            val = int(val_str)
            try:
                env.lookup_env(args[0]).set(args[0], val)
            except NameError:
                env.define(args[0], val)
        elif instr == 'PRINT':
            val = self._pop()
            self.current_line.append(str(val))
        elif instr == 'NEWLINE':
            self._flush_line()
        elif instr == 'POP':
            self._pop()
        elif instr == 'JZ':
            val = self._pop()
            if val == 0:
                return self.labels[args[0]]
        elif instr == 'JMP':
            return self.labels[args[0]]
        elif instr == 'ADD':
            b, a = self._pop(), self._pop()
            self.stack.append(a + b)
        elif instr == 'SUB':
            b, a = self._pop(), self._pop()
            self.stack.append(a - b)
        elif instr == 'MUL':
            b, a = self._pop(), self._pop()
            self.stack.append(a * b)
        elif instr == 'DIV':
            b, a = self._pop(), self._pop()
            self.stack.append(a // b)
        elif instr == 'EQ':
            b, a = self._pop(), self._pop()
            self.stack.append(int(a == b))
        elif instr == 'NE':
            b, a = self._pop(), self._pop()
            self.stack.append(int(a != b))
        elif instr == 'LT':
            b, a = self._pop(), self._pop()
            self.stack.append(int(a < b))
        elif instr == 'LE':
            b, a = self._pop(), self._pop()
            self.stack.append(int(a <= b))
        elif instr == 'GT':
            b, a = self._pop(), self._pop()
            self.stack.append(int(a > b))
        elif instr == 'GE':
            b, a = self._pop(), self._pop()
            self.stack.append(int(a >= b))
        elif instr == 'NEG':
            a = self._pop()
            self.stack.append(-a)
        elif instr == 'ADDR':
            self.stack.append(Pointer(env.lookup_env(args[0]), args[0]))
        elif instr == 'DEREF':
            ptr = self._pop()
            if not isinstance(ptr, Pointer):
                raise RuntimeError('DEREF of non-pointer')
            self.stack.append(ptr.get())
        elif instr == 'AADDR':
            idx = self._pop()
            arr = self._pop()
            self.stack.append(Pointer(arr, idx))
        elif instr == 'FADDR':
            obj = self._pop()
            self.stack.append(Pointer(obj, args[0]))
        elif instr == 'PSTORE':
            ptr = self._pop()
            val = self._pop()
            if not isinstance(ptr, Pointer):
                raise RuntimeError('PSTORE to non-pointer')
            ptr.set(val)
        elif instr == 'ALOAD':
            idx = self._pop()
            arr = self._pop()
            self.stack.append(arr[idx])
        elif instr == 'ASTORE':
            idx = self._pop()
            arr = self._pop()
            val = self._pop()
            arr[idx] = val
        elif instr == 'FLOAD':
            obj = self._pop()
            self.stack.append(obj.get(args[0]))
        elif instr == 'FSTORE':
            obj = self._pop()
            val = self._pop()
            obj[args[0]] = val
        elif instr == 'SETFIELD':
            val = self._pop()
            self.stack.append(('FIELD', args[0], val))
        elif instr == 'STRUCT':
            d = {}
            while self.stack and isinstance(self.stack[-1], tuple) and self.stack[-1][0] == 'FIELD':
                _, k, v = self.stack.pop()
                d[k] = v
            self.stack.append(d)
        elif instr == 'SET_ADD':
            val = self._pop()
            self.stack.append(('SET', val))
        elif instr == 'SET':
            s = set()
            while self.stack and isinstance(self.stack[-1], tuple) and self.stack[-1][0] == 'SET':
                _, v = self.stack.pop()
                s.add(v)
            self.stack.append(s)
        elif instr == 'MAP_INSERT':
            val = self._pop()
            key = self._pop()
            self.stack.append(('MAP', key, val))
        elif instr == 'MAP':
            m = {}
            while self.stack and isinstance(self.stack[-1], tuple) and self.stack[-1][0] == 'MAP':
                _, k, v = self.stack.pop()
                m[k] = v
            self.stack.append(m)
        elif instr == 'CALL':
            name = args[0]
            argc = int(args[1])
            params = [self._pop() for _ in range(argc)][::-1]
            if name in self._builtins():
                res = self._builtins()[name](*params)
                self.stack.append(res)
            else:
                func_ip = self.func_addrs[name]
                func_def = self.func_defs[name]
                new_env = Environment(self.env_stack[-1])
                for p, v in zip(func_def.params, params):
                    new_env.define(p, v)
                self.env_stack.append(new_env)
                self.call_stack.append(ip + 1)
                return func_ip
        elif instr == 'RET':
            ret = self._pop()
            self.env_stack.pop()
            ip = self.call_stack.pop()
            self.stack.append(ret)
            return ip
        else:
            raise RuntimeError(f'Unknown instruction {instr}')
        return ip + 1

    def _builtins(self):
        return {
            'map_insert': lambda m, k, v: (m.__setitem__(k, v), 0)[1],
            'map_delete': lambda m, k: (m.pop(k, None), 0)[1],
            'map_get': lambda m, k: m.get(k, 0),
            'map_has': lambda m, k: int(k in m),
            'map_keys': lambda m: list(m.keys()),
            'set_add': lambda s, v: (s.add(v), 0)[1],
            'set_remove': lambda s, v: (s.discard(v), 0)[1],
            'set_contains': lambda s, v: int(v in s),
            'set_items': lambda s: list(s),
        }
