---
type: wiki
title: Parser 参数解析
description: PyInvoke Parser 参数解析系统的完整 API 参考，涵盖 Argument 参数定义、ParserContext 上下文、ParseMachine 状态机、标志处理、值解析与 ParseResult。
tags: [pyinvoke, parser, argument, parsercontext, flags, cli-parsing, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/parser/argument.py
  - external/libs/pyinvoke/invoke/invoke/parser/parser.py
  - external/libs/pyinvoke/invoke/invoke/parser/context.py
---

# Parser 参数解析

## 概述

Invoke 的参数解析系统由三个核心组件构成：

1. **Argument**：定义单个 CLI 参数/标志的元数据（名称、类型、默认值等）
2. **ParserContext**：一组相关参数的集合（对应核心程序选项或单个任务的选项）
3. **Parser** / **ParseMachine**：基于状态机的解析引擎，处理 argv 标记，将值填充到 Argument 对象中

相关文档：[Task](task.md)、[Program](program.md)、[Collection](collection.md)

---

## Argument 类

`Argument` 表示一个命令行参数/标志，包含名称、类型、默认值、帮助文本等元数据。

### 构造函数

```python
Argument(
    name: Optional[str] = None,
    names: Iterable[str] = (),
    kind: Any = str,
    default: Optional[Any] = None,
    help: Optional[str] = None,
    positional: bool = False,
    optional: bool = False,
    incrementable: bool = False,
    attr_name: Optional[str] = None,
)
```

> **注意**：`name` 和 `names` 不能同时给出；至少需要一个名称。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | `None` | 单个名称的语法糖（等价于 `names=(name,)`） |
| `names` | `Iterable[str]` | `()` | 所有有效名称列表，如 `("-h", "--help")` |
| `kind` | 类型 | `str` | 类型工厂/解析提示：`str`、`int`、`bool`、`list` |
| `default` | `Any` | `None` | 默认值，未指定参数时使用 |
| `help` | `str` | `None` | 帮助文本，用于 `--help` 输出 |
| `positional` | `bool` | `False` | 是否为位置参数（不需要显式标志名） |
| `optional` | `bool` | `False` | 是否为可选值参数（既可作为布尔标志，也可带值） |
| `incrementable` | `bool` | `False` | 是否为可递增类型（如 `-vvv` 对应 verbosity=3） |
| `attr_name` | `str` | `None` | Python 友好的属性名（保留下划线版本），默认取 `names[0]` |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `names` | `Tuple[str, ...]` | 所有名称元组 |
| `name` | `str` | property，规范名称（`attr_name` 或 `names[0]`） |
| `nicknames` | `Tuple[str, ...]` | property，除主名外的别名（`names[1:]`） |
| `kind` | 类型 | 值类型 |
| `default` | `Any` | 默认值 |
| `value` | `Any` | 当前值（未设置时返回 `default`） |
| `raw_value` | `Any` | 原始设置值（未类型转换） |
| `help` | `str` | 帮助文本 |
| `positional` | `bool` | 是否位置参数 |
| `optional` | `bool` | 是否可选值 |
| `incrementable` | `bool` | 是否可递增 |
| `attr_name` | `str` | 属性名 |
| `takes_value` | `bool` | property，是否需要值（`bool` 和 incrementable 返回 `False`） |
| `got_value` | `bool` | property，是否被设置了非默认值 |

### 值设置逻辑（set_value）

```python
set_value(value: Any, cast: bool = True) -> None
```

值设置的特殊逻辑：
- `kind=list`：值**追加**到列表，而非覆盖
- `incrementable=True`：忽略输入值，当前值 +1（类型转换为 `lambda x: self.value + 1`）
- `cast=True`（默认）：使用 `kind(value)` 进行类型转换
- `cast=False`：直接使用原始值
- `list` 类型初始值为空列表 `[]`
- incrementable 类型初始值为 `default`（而非 `None`）

```python
# 布尔标志
arg = Argument(names=("--verbose", "-v"), kind=bool, default=False)
arg.value = True  # 不接收值，直接设置 True

# 字符串选项
arg = Argument(names=("--config", "-f"), kind=str)
arg.value = "myconfig.yaml"  # 转换为 str（默认行为）

# 整数选项
arg = Argument(names=("--port", "-p"), kind=int, default=8080)
arg.value = "9090"  # kind(int) → 9090

# 列表选项（可多次指定）
arg = Argument(names=("--tag", "-t"), kind=list)
arg.set_value("v1")  # ["v1"]
arg.set_value("v2")  # ["v1", "v2"]

# 可递增选项
arg = Argument(names=("--verbose", "-v"), kind=int, incrementable=True, default=0)
arg.set_value("ignored")  # value = 1
arg.set_value("ignored")  # value = 2
arg.set_value("ignored")  # value = 3
```

### __repr__ 格式

```
<Argument: --name (-n) [int] *?>
```

- `*` 表示位置参数
- `?` 表示可选值
- `[type]` 显示非 str 类型

---

## ParserContext 类

`ParserContext` 是一组相关 Argument 的集合，对应核心程序选项（core）或单个任务的选项。它维护参数的标志索引、别名映射和反向标志。

### 构造函数

```python
ParserContext(
    name: Optional[str] = None,
    aliases: Iterable[str] = (),
    args: Iterable[Argument] = (),
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | `None` | 上下文名称（通常是任务名） |
| `aliases` | `Iterable[str]` | `()` | 名称别名（如任务的 aliases） |
| `args` | `Iterable[Argument]` | `()` | 初始参数列表 |

### 核心数据结构

| 属性 | 类型 | 说明 |
|------|------|------|
| `args` | `Lexicon` | 参数字典，键为参数名 |
| `flags` | `Lexicon` | 标志字典，键为 CLI 标志格式（`--foo`、`-f`） |
| `inverse_flags` | `Dict[str, str]` | 反向标志映射（如 `--no-foo` → `--foo`），用于默认值为 True 的布尔参数 |
| `positional_args` | `List[Argument]` | 位置参数有序列表 |
| `name` | `str` | 上下文名称 |
| `aliases` | `Iterable[str]` | 别名 |
| `missing_positional_args` | `List[Argument]` | property，尚未填充值的位置参数 |
| `as_kwargs` | `Dict[str, Any]` | property，所有参数的 `{attr_name: value}` 字典 |

### add_arg 方法

```python
add_arg(*args, **kwargs) -> None
```

添加 Argument（可直接传 Argument 对象或构造参数）。添加时：

1. 验证名称唯一性（重复名称抛 `ValueError`）
2. 将第一个名称作为主名注册到 `args`
3. 位置参数添加到 `positional_args`
4. 所有名称通过 `to_flag()` 转换为 CLI 标志格式注册到 `flags`
5. 别名通过 Lexicon 的 alias 机制注册
6. `attr_name`（下划线名）注册为 args 的别名
7. 默认值为 `True` 的布尔参数，自动添加反向标志 `--no-<name>` 到 `inverse_flags`

### 辅助函数

#### to_flag(name: str) -> str

将参数名转换为 CLI 标志格式：
- 单字符 → `-x`（短标志）
- 多字符 → `--xxx`（长标志）
- 自动调用 `translate_underscores()` 转换下划线为短横线

```python
to_flag("v")       # "-v"
to_flag("verbose") # "--verbose"
to_flag("output_dir") # "--output-dir"
```

#### translate_underscores(name: str) -> str

去除首尾下划线，将内部下划线替换为短横线：

```python
translate_underscores("output_dir")   # "output-dir"
translate_underscores("_private")    # "private"
translate_underscores("my_task_name") # "my-task-name"
```

### 帮助输出方法

#### help_for(flag: str) -> Tuple[str, str]

返回指定标志的 `(标志规格, 帮助文本)` 元组：
- 短标志带值格式：`-f STRING`、`-f [STRING]`（可选值）
- 长标志带值格式：`--foo=STRING`、`--foo[=STRING]`（可选值）
- 布尔反向标志：`--[no-]foo`
- 所有别名合并显示，短名在前

#### help_tuples() -> List[Tuple[str, Optional[str]]]

返回所有参数的排序后帮助元组列表，排序规则：
1. 长标志优先于短标志
2. 按字母顺序排列（不区分大小写）
3. 大小写完全相同时，小写字母优先

#### flag_names() -> Tuple[str, ...]

返回所有标志名（含反向标志）的扁平元组。

---

## Parser 类

`Parser` 是解析器入口，管理多个 ParserContext 并驱动 ParseMachine 进行解析。

### 构造函数

```python
Parser(
    contexts: Iterable[ParserContext] = (),
    initial: Optional[ParserContext] = None,
    ignore_unknown: bool = False,
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `contexts` | `Iterable[ParserContext]` | `()` | 可用的任务/子命令上下文集合 |
| `initial` | `ParserContext` | `None` | 初始上下文（核心选项） |
| `ignore_unknown` | `bool` | `False` | 遇到未知上下文时是否停止解析而非报错 |

构造时：
- 非 initial 的 contexts 必须有 `name`，否则抛 `ValueError`
- contexts 的 name 和 aliases 注册到内部 Lexicon
- 重复名称/别名抛 `ValueError`

### parse_argv 方法

```python
parse_argv(argv: List[str]) -> ParseResult
```

解析 argv 格式的标记列表。**注意**：argv 不应包含程序名（即 `sys.argv[1:]`）。

#### 解析特性

1. **`--` 分隔符**：`--` 之后的内容作为 `remainder`（原始文本），不参与解析
2. **等号赋值**：`--foo=bar` 自动拆分为 `--foo` 和 `bar`
3. **短标志聚合**：`-qv` 自动拆分为 `-q` 和 `-v`（布尔标志）
4. **短标志+值**：如果短标志需要值，`-fvalue` 拆分为 `-f` 和 `value`
5. **可选值标志的歧义检测**：当标志可选值时，后续 token 如果是有效标志名或位置参数缺失，抛出 `ParseError`

#### 返回值

返回 `ParseResult`（list 子类），包含：
- 按顺序排列的 ParserContext 对象（含解析后的值）
- `.remainder`：`--` 后的文本
- `.unparsed`：未解析的标记（`ignore_unknown=True` 时填充）

---

## ParseMachine 状态机

`ParseMachine`（基于 fluidity StateMachine）是实际执行解析的状态机引擎。

### 状态

| 状态 | 说明 |
|------|------|
| `context` | 默认状态，期待新标志或新上下文（任务名） |
| `unknown` | 遇到未知输入，后续标记存入 unparsed |
| `end` | 解析结束 |

### 状态转换

```
context --see_context(切换到新上下文)--> context
context --see_unknown(遇到未知标记)--> unknown
unknown --see_unknown(继续未知)--> unknown
(context, unknown) --finish(结束)--> end
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `context` | `ParserContext` | 当前上下文（deepcopy） |
| `flag` | `Argument` | 当前正在处理的标志 |
| `flag_got_value` | `bool` | 当前列表标志是否已获得值 |
| `result` | `ParseResult` | 解析结果 |
| `waiting_for_flag_value` | `bool` | property，是否正在等待标志的值 |
| `current_state` | `str` | 当前状态名 |

### Token 处理逻辑（handle 方法）

按优先级处理每个 token：

1. **unknown 状态**：所有 token 存入 `result.unparsed`
2. **当前上下文的标志**：匹配 `context.flags` → 切换到该标志
3. **反向标志**：匹配 `context.inverse_flags` → 切换到反向标志（值设为 False）
4. **等待标志值**：当前标志需要值 → 当前 token 作为值
5. **位置参数**：上下文有未填充的位置参数 → 当前 token 作为位置参数值
6. **新上下文**：token 匹配已知上下文名 → 切换到新上下文
7. **初始上下文标志**：token 匹配核心标志（如 `--help`）→ 切换到该标志（`--help` 特殊处理：当前上下文名作为值）
8. **未知**：`ignore_unknown=False` 抛 `ParseError`；否则切换到 unknown 状态

### 标志处理细节

#### switch_to_flag

1. 检查可选值标志的歧义
2. 完成上一个标志（complete_flag）
3. 查找 Argument 对象（优先当前上下文，其次初始上下文）
4. 布尔标志/incrementable 标志立即设置值（True/+1）
5. 需要值的标志等待后续 token

#### complete_flag

完成当前标志：
- 需要值但未获得值且非可选 → 抛 `ParseError`
- 可选值标志未获得值 → 设置为 `True`（不 cast，保留布尔类型）

#### see_value

为当前标志设置值。可选值标志时先检查歧义。

#### see_positional_arg

按位置参数顺序填充第一个未设置值的位置参数。

#### switch_to_context

切换到新的 ParserContext（deep copy），完成旧上下文并加入结果。

#### complete_context

完成当前上下文：
- 检查是否所有必填位置参数都已填充，否则抛 `ParseError`
- 将上下文加入结果（如果尚未加入）

---

## ParseResult 类

```python
class ParseResult(List[ParserContext]):
    remainder: str = ""      # -- 之后的文本
    unparsed: List[str] = [] # 未解析的标记
```

是 `list` 的子类，包含按解析顺序排列的 ParserContext 对象。

---

## 解析示例

### 核心 + 任务解析流程

```
inv --echo build --clean --target=release arg1 arg2
```

1. 初始上下文（core）：`--echo` → `run.echo = True`
2. 遇到 `build`：切换到 build 任务上下文
3. `--clean`：build 任务的布尔标志 → `clean = True`
4. `--target=release`：拆分为 `--target` + `release` → `target = "release"`
5. `arg1`, `arg2`：作为位置参数填充

### 标志形式

```bash
# 长标志
--verbose                  # 布尔标志 → True
--output-dir ./build       # 空格分隔值
--output-dir=./build       # 等号分隔值

# 短标志
-v                         # 布尔标志
-f config.yaml             # 空格分隔值
-f=config.yaml             # 等号分隔值
-fconfig.yaml              # 紧接值（当 -f 需要值时）

# 聚合布尔短标志
-qv                        # → -q -v（两个布尔标志）

# 可递增标志
-v                         # verbose = 1
-vv                        # verbose = 2
-vvv                       # verbose = 3

# 列表标志
--tag v1 --tag v2          # tag = ["v1", "v2"]

# 反向布尔标志（默认 True）
--no-dedupe                # dedupe = False

# 可选值标志
--help                     # help = True（无值，作为布尔）
--help build               # help = "build"（带值）

# 位置参数
deploy production          # env = "production"

# 剩余参数
run -- command --arg1      # remainder = "command --arg1"
```
