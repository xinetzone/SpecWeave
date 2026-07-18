---
id: "defensive-attribute-access"
source: "../../reports/project-governance/tools-and-automation/retrospective-skill-facades-encoding-robustness-20260701/insight-extraction.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/defensive-attribute-access.toml"
---
# 防御性属性访问：外部对象三层防护模式

## 模式概述

在Python鸭子类型系统中，访问外部传入对象的属性或方法时，不能假设对象一定具有期望的属性/方法/行为。必须通过三层防御（getattr→callable→try-except）确保在属性不存在、为None、不可调用、或调用抛异常时安全降级，而非直接崩溃。

## 问题现象

CLI工具库中直接访问`sys.stdout.isatty()`、`sys.stdout.encoding`等属性时，在以下场景崩溃：

```python
# ❌ 反模式：直接访问，无任何防护
def _supports_unicode(stream=sys.stdout):
    if not stream.isatty():          # AttributeError如果无isatty
        return False
    encoding = stream.encoding.lower()  # AttributeError如果无encoding
    return encoding in ('utf8', 'utf-8')
```

崩溃场景：
- pytest capsys替换sys.stdout为不带isatty的对象
- mock对象只模拟了部分接口
- StringIO/BytesIO等文件类对象没有isatty()
- encoding属性为None时调用.lower()抛AttributeError
- isatty()方法本身因内部状态抛出异常
- isatty存在但为None或非可调用值（如整数42）

## 解决方案：三层防御模板

### 核心函数模板

```python
def _safe_call(obj, method_name: str, default=False, *args, **kwargs):
    """安全调用对象方法的通用工具函数。

    三层防御：
    1. getattr: 检查属性是否存在
    2. callable: 检查属性是否可调用
    3. try-except: 捕获调用时可能的异常

    Args:
        obj: 目标对象
        method_name: 方法名
        default: 调用失败时的默认返回值
        *args, **kwargs: 传递给方法的参数

    Returns:
        方法返回值，或调用失败时返回default
    """
    method = getattr(obj, method_name, None)
    if method is None or not callable(method):
        return default
    try:
        return method(*args, **kwargs)
    except Exception:
        return default


def _safe_getattr(obj, attr_name: str, default=None, expected_type=None):
    """安全获取对象属性，支持类型验证。

    Args:
        obj: 目标对象
        attr_name: 属性名
        default: 属性不存在/类型错误时的默认值
        expected_type: 期望的类型（如str），不匹配则返回default
    """
    value = getattr(obj, attr_name, None)
    if value is None:
        return default
    if expected_type is not None and not isinstance(value, expected_type):
        return default
    return value
```

### 实际应用示例（_is_tty）

```python
def _is_tty(stream=sys.stdout) -> bool:
    """安全检测流是否连接到终端。

    覆盖以下边界场景：
    - 流对象没有isatty方法（如StringIO、某些mock）
    - isatty属性为None
    - isatty属性存在但不可调用（如被错误设置为整数）
    - isatty()调用本身因内部状态抛异常
    """
    isatty = getattr(stream, 'isatty', None)
    if isatty is None or not callable(isatty):
        return False
    try:
        return bool(isatty())
    except Exception:
        return False


def _supports_unicode(stream=sys.stdout) -> bool:
    """安全检测流是否支持Unicode输出。"""
    if not _is_tty(stream):
        return False
    encoding = getattr(stream, 'encoding', None)
    if not isinstance(encoding, str):
        return False
    normalized = encoding.lower().replace('-', '').replace('_', '')
    return normalized in _UTF8_ENCODINGS
```

### dict查找防御

```python
# ❌ 反模式：直接[key]查找，无效key抛KeyError
symbol = {'pass': '✓', 'warn': '⚠', 'error': '✗'}[kind]

# ✅ 正确：用dict.get()提供fallback
_SYMBOLS = {'pass': '✓', 'warn': '⚠', 'error': '✗'}
_ASCII_SYMBOLS = {'pass': '[PASS]', 'warn': '[WARN]', 'error': '[FAIL]'}

def _symbol(kind: str) -> str:
    if _supports_unicode():
        return _SYMBOLS.get(kind, '?')
    return _ASCII_SYMBOLS.get(kind, '[????]')
```

## 适用场景

### 必须使用本模式的场景

1. **全局/外部对象访问**：sys.stdout/sys.stderr/sys.stdin、os.environ、配置对象
2. **插件/回调接口**：用户提供的回调函数、插件钩子、策略模式对象
3. **可选依赖API**：try-import后的可选库调用
4. **资源对象**：数据库连接、文件句柄、网络socket
5. **Mock/测试替身**：单元测试中被替换的依赖对象
6. **鸭子类型协议**：任何依赖"但凡是X就有Y方法"假设的代码

### 何时可以简化

- 当你**完全控制**对象的创建和生命周期（如函数内部创建的局部变量）
- 类型检查器（mypy/pyright）能保证属性存在时
- 数据类（dataclass）/NamedTuple等有明确结构的类型

## 边界测试检查清单

为使用本模式的函数编写测试时，必须覆盖以下场景：

| 场景 | 测试方法 |
|------|---------|
| 属性不存在 | 创建一个无目标方法的Dummy类 |
| 属性为None | 设置`obj.method = None` |
| 属性不可调用 | 设置`obj.method = 42`（整数） |
| 方法调用抛异常 | 方法内`raise Exception("test")` |
| 默认参数（不传stream） | 测试默认使用sys.stdout |
| 正确工作（happy path） | 使用真实TTY流验证正常返回 |

```python
class TestIsTty:
    def test_tty_stream_returns_true(self):
        class TTY:
            def isatty(self): return True
        assert _is_tty(TTY()) is True

    def test_stream_without_isatty_method_returns_false(self):
        class Dummy: pass
        assert _is_tty(Dummy()) is False

    def test_stream_with_isatty_none_returns_false(self):
        class S: isatty = None
        assert _is_tty(S()) is False

    def test_stream_with_isatty_not_callable_returns_false(self):
        class S: isatty = 42
        assert _is_tty(S()) is False

    def test_isatty_raises_exception_returns_false(self):
        class S:
            def isatty(self): raise RuntimeError("broken")
        assert _is_tty(S()) is False
```

## 反模式

### 反模式1：hasattr()后直接调用（缺少第二层和第三层）

```python
# ❌ hasattr只检查存在性，不检查是否可调用，也不捕获调用时异常
if hasattr(stream, 'isatty'):
    return stream.isatty()  # isatty=None时TypeError，调用抛异常时崩溃
```

### 反模式2：try-except过于宽泛且无日志

```python
# ❌ 捕获BaseException包括KeyboardInterrupt/SystemExit，静默吞掉所有错误
try:
    return stream.isatty()
except:  # bare except
    return False
```

### 反模式3：LBYL过度检查导致代码膨胀

```python
# ❌ 不是所有访问都需要三层防御——局部变量完全不需要
def process(data):
    # data是函数内部创建的list，length肯定存在
    if hasattr(data, '__len__') and callable(data.__len__):
        try:
            n = len(data)
        except Exception:
            n = 0
```

正确判断：**如果对象来自函数外部（参数、全局、依赖注入），需要防御；如果完全在内部控制，不需要。**

## 与其他模式的关系

- **被cross-platform-encoding-enforcement使用**：编码兼容性的第二层（能力检测）依赖本模式
- **应用于structured-lightweight-logging**：日志输出到外部stream时需要防御性访问
- **应用于dual-channel-tiered-logging**：双通道日志的人类通道在非TTY环境下需降级
- **与safe-table-edit相关**：表格编辑前的安全检查也需要类似的防御性思维
- **与path-traversal-guard互补**：路径安全防护是防御性编程在文件系统领域的应用

## 边界与选型

本模式解决的核心问题是：**"代码能否优雅地处理不符合预期的输入对象"，而非"对象方法是否被正确调用"。**

典型信号：
- 代码在"正常环境"下工作多年，但在某个特殊环境（测试、CI、客户机器）突然崩溃
- 错误堆栈指向AttributeError/TypeError/KeyError，且发生在属性访问或方法调用处
- bug报告说"在我的机器上没问题"——环境差异导致对象接口不同

不适用场景：
- 纯内部逻辑、完全控制的数据流——过度防御会增加代码噪音
- 性能极端敏感的热路径——但getattr/callable/try-except的开销在纳秒级，通常不是问题
