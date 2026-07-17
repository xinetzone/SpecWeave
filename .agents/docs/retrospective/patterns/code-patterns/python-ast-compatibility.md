---
id: "python-ast-compatibility"
title: "Python AST 版本兼容模式：弃用节点统一封装"
type: "code"
date: "2026-07-17"
maturity: "L1-draft"
source: "external/xmhub/npu_tvm/python/tvm/script/hybrid/py_converter.py"
case_archive: null
related_patterns:
  - "defensive-attribute-access"
  - "cross-platform-encoding-enforcement"
  - "dependency-update-risk-control"
tags:
  - "Python"
  - "AST"
  - "compatibility"
  - "version-adapter"
  - "backward-compatibility"
validation_count: 1
reuse_count: 0
documentation_level: "comprehensive"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/code-patterns/python-ast-compatibility.toml"
---

# Python AST 版本兼容模式：弃用节点统一封装

## 模式概述

Python 3.8+ 开始逐步弃用 `ast.NameConstant`/`ast.Num`/`ast.Str`/`ast.Index` 等旧 AST 节点，统一为 `ast.Constant`；Python 3.9 移除 `ast.Index`，Python 3.12 发出 DeprecationWarning，Python 3.14 正式移除。直接使用旧节点的代码在新版本中会抛出 `ImportError` 或 `AttributeError`。本模式通过「版本检测 + 兼容函数封装 + 统一替代」三步法，实现同一份代码在 Python 3.8-3.14 全版本正常运行。

## 问题现象

在 Python 3.14 中导入使用了旧 AST 节点的模块时直接崩溃：

```python
# ❌ 问题代码（TVM 0.19.0 原始代码片段）
import ast

# 直接使用 NameConstant 判断 True/False/None
def is_constant(node):
    return isinstance(node, ast.NameConstant)  # Python 3.14: AttributeError: module 'ast' has no attribute 'NameConstant'

# 直接使用 ast.Num 包装数字
def make_num(n):
    return ast.Num(n=n)  # Python 3.14: AttributeError

# 直接使用 ast.Str 包装字符串
def make_str(s):
    return ast.Str(s=s)  # Python 3.14: AttributeError

# 直接使用 ast.Index 包装下标
def make_subscript(value, slice_val):
    return ast.Subscript(value=value, slice=ast.Index(value=slice_val))  # Python 3.9+: 不应再用 Index
```

典型错误信息：
```
AttributeError: module 'ast' has no attribute 'NameConstant'
AttributeError: module 'ast' has no attribute 'Num'
AttributeError: module 'ast' has no attribute 'Str'
```

受影响的弃用节点汇总：

| 旧节点（≤3.7） | 弃用版本 | 移除版本 | 统一替代 |
|---------------|---------|---------|---------|
| `ast.NameConstant` | 3.8 | 3.14 | `ast.Constant(value=True/False/None)` |
| `ast.Num` | 3.8 | 3.14 | `ast.Constant(value=n)` |
| `ast.Str` | 3.8 | 3.14 | `ast.Constant(value=s)` |
| `ast.Bytes` | 3.8 | 3.14 | `ast.Constant(value=b)` |
| `ast.Ellipsis`（作为节点） | 3.8 | 3.14 | `ast.Constant(value=...)` |
| `ast.Index` | 3.9 | 3.12（警告）/3.14（移除） | 直接使用 value，不包装 Index |

## 解决方案：三步兼容法

### 步骤1：版本检测

在模块入口处保存 Python 版本信息：

```python
import sys

# Python 版本号缓存
_PY_VERSION = sys.version_info[:2]
_PY_38 = _PY_VERSION >= (3, 8)
_PY_39 = _PY_VERSION >= (3, 9)
_PY_312 = _PY_VERSION >= (3, 12)
```

### 步骤2：兼容函数封装

创建统一的兼容工厂函数，内部根据版本选择正确的 AST 节点类型：

```python
def _const(value):
    """创建常量 AST 节点，兼容 Python 3.8-3.14。

    替代旧的 ast.NameConstant / ast.Num / ast.Str / ast.Bytes / ast.Ellipsis，
    在所有版本中统一返回 ast.Constant（3.8+原生支持，旧版本降级到对应节点）。

    Args:
        value: 常量值（bool/int/float/str/bytes/Ellipsis/None）

    Returns:
        AST 节点
    """
    if _PY_38:
        return ast.Constant(value=value)
    # Python 3.7 及以下降级到对应旧节点
    if value is True or value is False or value is None:
        return ast.NameConstant(value=value)
    if isinstance(value, (int, float, complex)):
        return ast.Num(n=value)
    if isinstance(value, str):
        return ast.Str(s=value)
    if isinstance(value, bytes):
        return ast.Bytes(s=value)
    if value is ...:
        return ast.Ellipsis()
    raise TypeError(f"Unsupported constant type: {type(value)}")


def _index(value):
    """创建下标切片 AST 节点，兼容 Python 3.8-3.14。

    Python 3.9+ 中 ast.Index 被移除，Subscript.slice 直接使用值节点。

    Args:
        value: 下标值 AST 节点

    Returns:
        适用于当前 Python 版本的切片节点
    """
    if _PY_39:
        return value
    return ast.Index(value=value)
```

### 步骤3：统一替代与双向验证

在所有使用旧节点的地方，替换为兼容函数：

```python
# ✅ 修正后：使用 _const() 创建常量
def make_true():
    return _const(True)

def make_num(n):
    return _const(n)

def make_str(s):
    return _const(s)

# ✅ 修正后：使用 _index() 处理下标
def make_subscript(value, slice_val):
    return ast.Subscript(value=value, slice=_index(slice_val), ctx=ast.Load())

# ✅ 修正后：is_docstring 兼容 ast.Constant
def is_docstring(node):
    """检查节点是否为文档字符串。"""
    if not isinstance(node, ast.Expr):
        return False
    node_val = node.value
    # Python 3.8+: ast.Constant，旧版本: ast.Str
    if _PY_38:
        return isinstance(node_val, ast.Constant) and isinstance(node_val.value, str)
    return isinstance(node_val, ast.Str)
```

### 步骤4（可选）：AST Visitor 兼容

如果使用 `ast.NodeVisitor`/`ast.NodeTransformer`，需要添加 `visit_Constant` 方法：

```python
class HybridParser(ast.NodeVisitor):
    def __init__(self):
        self._const_maker = _const
        self._index_maker = _index

    def _make_const(self, value):
        """统一创建常量节点的内部辅助方法。"""
        return self._const_maker(value)

    def visit_Constant(self, node):
        """处理 ast.Constant 节点（Python 3.8+）。"""
        value = node.value
        if value is True:
            return self._visit_true(node)
        if value is False:
            return self._visit_false(node)
        if value is None:
            return self._visit_none(node)
        if isinstance(value, (int, float)):
            return self._visit_num(node)
        if isinstance(value, str):
            return self._visit_str(node)
        return self.generic_visit(node)

    # 旧版本中 visit_NameConstant/visit_Num/visit_Str 仍然保留
    def visit_NameConstant(self, node):
        """Python 3.7 及以下的 NameConstant 节点。"""
        return self.visit_Constant(node)  # 委托给统一处理

    def visit_Num(self, node):
        return self.visit_Constant(ast.Constant(value=node.n))

    def visit_Str(self, node):
        return self.visit_Constant(ast.Constant(value=node.s))
```

## 反模式

### ❌ 反模式1：直接使用弃用节点，不做版本检测

```python
# 错误：在 Python 3.14 中直接崩溃
return ast.NameConstant(value=True)
```

**问题**：在移除了旧节点的 Python 版本中 `AttributeError`。

**正确做法**：使用 `_const(True)` 统一入口。

### ❌ 反模式2：为每个版本编写独立代码路径

```python
# 错误：代码重复，维护噩梦
if sys.version_info >= (3, 8):
    node = ast.Constant(value=value)
elif sys.version_info >= (3, 7):
    if isinstance(value, bool):
        node = ast.NameConstant(value=value)
    elif isinstance(value, (int, float)):
        node = ast.Num(n=value)
    # ... 大量重复分支
```

**问题**：每个使用点都重复版本判断逻辑，代码膨胀且容易遗漏。

**正确做法**：封装为 `_const()`/`_index()` 函数，调用点不感知版本差异。

### ❌ 反模式3：忽略 ast.Index 移除，直接包装

```python
# 错误：Python 3.9+ 中 Subscript.slice 不应是 ast.Index
return ast.Subscript(value=v, slice=ast.Index(value=s))
```

**问题**：Python 3.9+ 虽然向后兼容 Index（目前仍接受），但会产生 DeprecationWarning，未来版本将报错。

**正确做法**：使用 `_index(value)` 函数，3.9+ 直接返回 value，旧版本包装 Index。

### ❌ 反模式4：只修复不验证，假设兼容函数正确

```python
# 错误：修改后不做跨版本 round-trip 验证
def _const(value):
    return ast.Constant(value=value)
# 忘记了 Python 3.7 的兜底逻辑
```

**问题**：兼容函数如果本身有误，旧版本仍然崩溃。

**正确做法**：编写双向 round-trip 测试：
1. 用兼容函数创建 AST 节点
2. `compile(ast.fix_missing_locations(tree), '<test>', 'exec')` 验证可编译
3. `ast.dump(tree)` 对比不同版本输出结构一致

## 检验标准

### 自动化检查清单

- [ ] 代码中不再直接出现 `ast.NameConstant`/`ast.Num`/`ast.Str`/`ast.Bytes`/`ast.Ellipsis`（作为节点类）/`ast.Index`
- [ ] 存在 `_const()` 或同等封装函数覆盖所有常量类型
- [ ] 存在 `_index()` 或同等封装函数处理 Subscript 切片
- [ ] 版本检测逻辑使用 `sys.version_info` 元组比较（不使用字符串比较）
- [ ] NodeVisitor 子类同时实现了 `visit_Constant` 和旧版 visit 方法（visit_NameConstant/visit_Num/visit_Str）
- [ ] `is_docstring` 等工具函数同时处理 ast.Constant 和 ast.Str

### 手动验证清单

- [ ] 在最低支持版本（如 Python 3.8）运行完整测试套件通过
- [ ] 在最高支持版本（如 Python 3.14）运行完整测试套件通过
- [ ] AST 节点创建 → compile → 执行的 round-trip 测试通过
- [ ] 无 DeprecationWarning（`python -W error` 模式下运行测试）

### 快速验证脚本

```python
"""快速验证 AST 兼容性脚本。"""
import sys
import ast

def _const(value):
    if sys.version_info >= (3, 8):
        return ast.Constant(value=value)
    if value is True or value is False or value is None:
        return ast.NameConstant(value=value)
    if isinstance(value, (int, float, complex)):
        return ast.Num(n=value)
    if isinstance(value, str):
        return ast.Str(s=value)
    raise TypeError(f"Unsupported: {type(value)}")

# 测试所有常量类型
test_values = [True, False, None, 42, 3.14, "hello", 0, -1, ""]
for v in test_values:
    node = _const(v)
    tree = ast.Expression(body=node)
    ast.fix_missing_locations(tree)
    compiled = compile(tree, '<test>', 'eval')
    result = eval(compiled)
    assert result == v, f"Round-trip failed for {v!r}: got {result!r}"
    print(f"  ✅ {v!r}: {ast.dump(node)}")

print(f"\nPython {sys.version}：所有常量 round-trip 验证通过！")
```

## 实际案例

> 📁 **案例说明**：本模式从 TVM 0.19.0 适配 Python 3.14 的修复中萃取。原始项目 external/xmhub/npu_tvm/ 下文件保留在原地作为参考源，模式库暂未归档完整案例材料。

### 案例1：TVM 0.19.0 适配 Python 3.14（首次验证）

**项目**：TVM (Tensor Virtual Machine) 深度学习编译器
**环境**：Python 3.14.6 + LLVM 22.1.8 + Docker 容器化构建
**修改文件**：
- `python/tvm/script/hybrid/py_converter.py`：添加 `_const()`/`_index()` 兼容函数
- `python/tvm/script/hybrid/parser.py`：添加 `visit_Constant()` 和 `_make_const()` 方法
- `python/tvm/script/hybrid/utils.py`：使 `is_docstring()` 兼容 `ast.Constant`
- `python/tvm/script/doc.py`：重写常量/Subscript/Index 注册逻辑

**验证结果**：
- 10 个测试全部通过（核心模块导入、常量转换、TIR 解析）
- 支持 Python 3.8-3.14 跨版本运行
- Vector add 计算正确性验证通过
- LLVM 后端和 C 后端功能正常

**关键修复点**：最初通过降级到 Python 3.11 绕过问题，但这不是可持续方案——最终采用本模式实现了真正的兼容。

## 迁移示例

### 示例1：代码生成工具中的常量处理

```python
# 场景：代码生成器需要生成 True/False/None/数字/字符串字面量
# 迁移前（只能在 Python ≤3.12 运行）
class CodeGenerator(ast.NodeVisitor):
    def make_literal(self, value):
        if isinstance(value, bool):
            return ast.NameConstant(value=value)
        if value is None:
            return ast.NameConstant(value=None)
        if isinstance(value, (int, float)):
            return ast.Num(n=value)
        if isinstance(value, str):
            return ast.Str(s=value)

# 迁移后：引入 _const()/_index()，所有版本通用
class CodeGenerator(ast.NodeVisitor):
    def __init__(self):
        self._py38 = sys.version_info >= (3, 8)
        self._py39 = sys.version_info >= (3, 9)

    def _const(self, value):
        if self._py38:
            return ast.Constant(value=value)
        # ... 降级逻辑（同上文）

    def _index(self, value):
        return value if self._py39 else ast.Index(value=value)

    def make_literal(self, value):
        return self._const(value)
```

### 示例2：静态分析器中的 docstring 检测

```python
# 场景：静态分析工具需要识别函数文档字符串
# 迁移前
def get_docstring(func_node):
    body = func_node.body
    if not body:
        return None
    first = body[0]
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Str):
        return first.value.s
    return None

# 迁移后
def get_docstring(func_node):
    body = func_node.body
    if not body:
        return None
    first = body[0]
    if not isinstance(first, ast.Expr):
        return None
    val = first.value
    if sys.version_info >= (3, 8):
        if isinstance(val, ast.Constant) and isinstance(val.value, str):
            return val.value
    else:
        if isinstance(val, ast.Str):
            return val.s
    return None
```

### 示例3：AST 转换工具中的下标处理

```python
# 场景：AST 转换器处理下标操作 a[i]
# 迁移前
def transform_subscript(node):
    # 假设 node.slice 总是 ast.Index
    index_value = node.slice.value
    new_index = transform(index_value)
    return ast.Subscript(value=node.value, slice=ast.Index(value=new_index))

# 迁移后
def _index(value):
    if sys.version_info >= (3, 9):
        return value
    return ast.Index(value=value)

def transform_subscript(node):
    # Python 3.8 中 slice 是 Index，3.9+ 直接是 value
    if sys.version_info >= (3, 9):
        slice_val = node.slice
    else:
        slice_val = node.slice.value
    new_slice = transform(slice_val)
    return ast.Subscript(value=node.value, slice=_index(new_slice))
```

### 适用边界

本模式适用于：
- ✅ 代码生成工具（生成 AST 然后 compile/exec）
- ✅ 静态分析器（遍历和检查 AST）
- ✅ AST 转换/重写工具（NodeTransformer）
- ✅ DSL/模板引擎（Hybrid Script、JIT 装饰器等）
- ✅ 需要跨 Python 3.8+ 多版本运行的库

本模式不适用于：
- ❌ 只针对单一 Python 版本的应用代码
- ❌ 不涉及 AST 操作的纯业务代码
- ❌ Python 3.7 及更早版本的兼容（本模式最低支持 3.8，3.7 降级路径仅作参考）

## 相关模式

| 模式 | 关系 |
|------|------|
| [defensive-attribute-access](defensive-attribute-access.md) | 思路同源：都通过封装不确定属性访问实现安全降级 |
| [cross-platform-encoding-enforcement](cross-platform-encoding-enforcement.md) | 类似的跨版本/跨平台兼容思路 |
| [dependency-update-risk-control](dependency-update-risk-control.md) | Python 大版本升级属于依赖更新，本模式是风险控制的具体手段 |

## 成熟度说明

- **当前等级**：L1-draft（单案例验证）
- **验证案例**：TVM 0.19.0 Python 3.14 适配（1个项目，4个文件，10个测试）
- **升级条件**：
  - L2-formal：需要 ≥1 个额外独立项目验证（如其他涉及AST操作的Python库适配）
  - L3-validated：需要 ≥5 个案例，覆盖代码生成/静态分析/DSL等多种AST应用场景
