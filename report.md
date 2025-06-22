# L25 编译器项目报告

## 项目结构

```
VAANet/
├── l25_compiler/                # L25 编译器源码
│   ├── README.md                # 编译器使用说明
│   ├── __init__.py              # 包导出
│   ├── ast_nodes.py             # 抽象语法树节点定义
│   ├── examples/                # 示例程序
│   ├── gui.py                   # 图形界面
│   ├── interpreter.py           # 解释执行器
│   ├── ir.py                    # 文本化中间表示生成
│   ├── lexer.py                 # 词法分析
│   ├── main.py                  # 命令行入口
│   ├── parser.py                # 语法分析
│   ├── pcode.py                 # pcode 生成器
│   ├── pcode_vm.py              # pcode 虚拟机
│   ├── tac.py                   # 三地址码生成器
│   └── utils.py                 # 辅助函数
└── report.md                    # 实验报告(当前文件)
```

`examples/` 目录下包含 `factorial.l25`、`fibonacci.l25`、`sum.l25`、`array_struct.l25`、`pointer.l25`、`map_set.l25`、`complex_edge.l25` 与 `do_until.l25` 共八个测试程序。

## 模块功能说明

- **lexer.py**：利用正则表达式定义 `TOKEN_SPEC`，实现 `tokenize` 函数，将源代码拆分为 token 流，能够识别关键字、运算符、括号以及数组/结构体、map/set、指针相关符号。
- **parser.py**：递归下降解析器，结合 `ast_nodes.py` 中的节点类构建抽象语法树。除基础语句外，还支持数组下标、结构体字段、指针地址与解引用、`map`/`set` 字面量，以及 `do...until` 循环等扩展语法。
- **ast_nodes.py**：定义所有 AST 节点数据结构，如 `Program`、`FuncDef`、`Declare`、`ArrayLiteral`、`MapLiteral` 等。
- **ir.py**：将 AST 转换为较易阅读的中间表示，保留语法结构便于调试。
- **tac.py**：生成线性三地址码 (TAC)，便于后续优化或翻译。
- **pcode.py**：将 AST 转为栈式 pcode 指令序列，作为虚拟机的输入。
- **pcode_vm.py**：栈式虚拟机，实现变量环境、指针、数组/结构体和 map/set 操作等指令的执行。
- **interpreter.py**：提供直接遍历 AST 的解释器，用于参考和测试。
- **gui.py**：基于 Tkinter 的图形界面，可选择输出 Tokens、AST、IR、TAC、Pcode，并在右侧窗口显示运行结果。
- **utils.py**：包含 AST 打印等辅助工具函数。
- **main.py**：命令行接口，解析参数后调用以上模块完成编译和执行。

## 编译流程

1. **词法分析**：`lexer.tokenize` 将源代码转为 token 序列。
2. **语法分析**：`parser.Parser` 根据 token 构建 AST。若语法错误则抛出异常。
3. **中间代码生成**：
   - `ir.IRGenerator` 生成结构化的 IR 文本。
   - `tac.ThreeAddressGenerator` 生成三地址码。
   - `pcode.PCodeGenerator` 生成栈式 pcode。
4. **执行阶段**：`pcode_vm.PCodeVM` 读取 pcode，通过栈和变量环境完成指令解释，输出结果。
5. 命令行或 GUI 均可选择输出任意阶段的中间结果，或直接运行程序。

## 扩展功能实现

在基础框架上实现了以下扩展：

- **一维数组与结构体**：在 `parser.py` 增加数组声明 `let a[n]`、数组字面量 `[1,2]`、结构体字面量 `struct {x=1;}`，并在 `interpreter.py`、`pcode.py`、`pcode_vm.py` 等处处理下标和字段访问。
- **指针支持**：引入 `&` 取地址与 `*` 解引用操作，虚拟机中用 `Pointer` 对象管理。示例 `pointer.l25` 展示了交换两个变量的程序。
- **map/set 类型**：支持字典和集合字面量及若干内建函数，如 `map_insert`、`map_keys`、`set_add` 等，这些在虚拟机 `_builtins` 字典中实现。
- **do-until 循环**：解析器新增 `do_until_stmt` 规则，生成对应的 pcode/TAC 指令。
- **图形界面**：`gui.py` 提供中文界面，可加载 `.l25` 文件、选择输出阶段并运行程序；界面会在无输入时提醒用户，并在发生运行错误时保留已产生的输出。

## 运行与验证

1. **命令行使用**（示例）:
   ```bash
   # 编译并运行阶乘示例
   python -m l25_compiler.main l25_compiler/examples/factorial.l25 <<EOF
   5
   EOF

   # 查看所有中间代码但不执行
   python -m l25_compiler.main --tokens --ast --ir --tac --pcode --no-run \
       l25_compiler/examples/pointer.l25 | head
   ```
2. **图形界面**:
   ```bash
   python -m l25_compiler.gui
   ```
   在界面中加载任一 `.l25` 文件，可勾选需要展示的阶段，并在右侧看到运行结果。
3. **测试示例**：`examples` 目录下的八个程序覆盖数组/结构体、指针、map/set、do-until 等特性。运行它们的输出应分别与 README 中描述一致，如
   ```bash
   python -m l25_compiler.main l25_compiler/examples/array_struct.l25
   ```
   得到：`3 5`。

以上即为项目的整体设计与使用说明。
