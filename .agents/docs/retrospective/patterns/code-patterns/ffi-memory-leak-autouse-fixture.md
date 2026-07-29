---
id: "ffi-memory-leak-autouse-fixture"
title: "FFI内存测试自动泄漏检测模式"
type: "code-pattern"
date: "2026-07-28"
maturity: "L2-validated"
source: "caffe-ffi conftest.py 自动泄漏检测 (2026-07-28)"
related_patterns:
  - "resource-counter-primitive-binding"
  - "cross-platform-backtrace-leak-diagnosis"
  - "cross-language-three-layer-logging"
tags: ["testing", "pytest", "fixture", "memory-leak", "ffi", "native-extension", "garbage-collection", "autouse"]
validation_count: 1
reuse_count: 0
---

# FFI内存测试自动泄漏检测模式

## 触发场景

- C/C++/Rust 原生扩展通过 FFI 暴露给 Python，需要自动化检测内存泄漏（未释放的C++对象/内存）
- 项目中存在手动内存管理（new/delete、malloc/free），Python GC无法回收C++堆内存
- 希望零配置地覆盖所有测试，无需在每个测试中手动写泄漏断言
- 新增测试自动获得泄漏检测能力，不需要开发者主动维护
- 需要同时检测字节泄漏（内存未释放）和对象泄漏（C++对象未析构）
- CI流水线中需要自动拦截引入泄漏的PR

**不适用于**：
- 纯Python项目（Python的GC自动管理内存，无原生堆泄漏）
- 引用计数/智能指针完全覆盖且无循环引用的C++代码（仍可能有循环引用导致泄漏）
- 性能基准测试（autouse fixture的GC开销会干扰性能测量）
- 有意跨测试持有原生资源的场景（如module级fixture缓存的对象）

## 核心做法

### 1. 暴露C++层原子计数器API

依赖 [resource-counter-primitive-binding](resource-counter-primitive-binding.md) 模式提供准确的只读查询：

```python
# your_package/__init__.py
def total_allocated_bytes() -> int:
    """当前存活原生对象占用的总字节数。"""
    if _ffi_api.is_available():
        fn = _ffi_api.get_global_func("your_project.TotalAllocatedBytes")
        if fn is not None:
            return int(fn(0))
    return 0

def live_object_count() -> int:
    """当前存活原生对象的数量（泄漏检测核心指标）。"""
    if _ffi_api.is_available():
        fn = _ffi_api.get_global_func("your_project.LiveObjectCount")
        if fn is not None:
            return int(fn(0))
    return 0
```

### 2. pytest fixture 注册标记

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "require_cpp_extension: mark test as requiring C++ extension"
    )
    config.addinivalue_line(
        "markers",
        "leak_check: mark test to check for memory leaks (default: autouse)"
    )
```

### 3. autouse fixture 核心实现

```python
# conftest.py
import gc
import pytest

@pytest.fixture(autouse=True)
def _check_memory_leaks(request):
    """自动内存泄漏检测：每个测试前后记录基线，强制GC后断言归零。"""

    # 1. C++扩展不可用时跳过（Python-only模式无原生泄漏）
    if not _ffi_api.is_available():
        yield
        return

    from your_package import total_allocated_bytes, live_object_count

    # 2. 支持选择退出：有意跨测试持有资源的场景
    if "leak_check" in request.keywords and request.keywords["leak_check"] is False:
        yield
        return

    # 3. 测试前：强制GC + 记录基线
    gc.collect()
    mem_before = total_allocated_bytes()
    objs_before = live_object_count()

    yield  # 执行测试

    # 4. 测试后：强制GC×2（一次GC可能无法回收循环引用）+ 记录结束值
    gc.collect()
    gc.collect()
    mem_after = total_allocated_bytes()
    objs_after = live_object_count()

    # 5. 计算泄漏量并断言
    leaked_bytes = mem_after - mem_before
    leaked_objs = objs_after - objs_before

    if leaked_objs != 0:
        pytest.fail(
            f"Memory leak detected in {request.node.name}: "
            f"{leaked_objs} object(s) still alive "
            f"(before={objs_before}, after={objs_after}), "
            f"{leaked_bytes} bytes leaked "
            f"(before={mem_before}, after={mem_after})"
        )
    if leaked_bytes > 0:
        pytest.fail(
            f"Memory leak detected in {request.node.name}: "
            f"{leaked_bytes} bytes still allocated "
            f"(before={mem_before}, after={mem_after})"
        )
```

### 4. 选择退出机制

```python
# 有意跨测试持有引用的场景（如module级缓存fixture）
@pytest.fixture(scope="module")
def cached_model():
    """加载一次模型，整个module复用——会跨测试持有对象。"""
    model = Model.load("weights.bin")
    yield model
    model.unload()  # module结束时显式清理

# 使用leak_check(False)标记退出
@pytest.mark.leak_check(False)
def test_cached_model_inference(cached_model):
    result = cached_model.forward(test_input)
    assert result.shape == expected_shape
```

### 5. 配套诊断流程

当fixture检测到泄漏时，使用配套模式定位泄漏源：

```
检测到泄漏（fixture fail）
    ↓
开启TRACE日志: enable_debug_logging(LOG_LEVEL_TRACE)
    ↓
重新运行失败的测试
    ↓
析构日志自动输出每个已释放对象的构造栈
    ↓
检查未匹配析构的最后一个构造栈输出
    ↓
定位源代码文件名:行号 → 修复泄漏点
```

详见 [cross-platform-backtrace-leak-diagnosis](cross-platform-backtrace-leak-diagnosis.md)。

## 反模式（不要这么做）

- ❌ **测试前不执行 gc.collect()**：基线测量前如果有未回收的Python包装对象引用着C++对象，会导致mem_before偏高，掩盖真实泄漏。
- ❌ **测试后只gc.collect()一次**：Python的GC是分代回收，一次GC可能无法回收跨代循环引用。使用`gc.collect()×2`或`gc.collect();gc.collect()`确保彻底回收。
- ❌ **C++扩展不可用时仍执行检查**：stub/Python-only模式下C++计数器始终返回0，检查无意义且可能误报。必须先检查`_ffi_api.is_available()`。
- ❌ **fixture中直接assert而非pytest.fail()**：assert的错误信息不如pytest.fail()详细，且无法自定义测试名称和泄漏诊断信息。
- ❌ **不提供退出机制**：module/session级fixture、缓存机制等跨测试持有资源是合理设计，不提供退出marker会导致这些测试无法通过。
- ❌ **只检测字节泄漏不检测对象泄漏**：存在"字节归零但对象未析构"的场景（如对象内部buffer已free但对象本身泄漏），反之亦然。两个维度都检查才能全面覆盖。
- ❌ **依赖开发者手动在每个测试中写断言**：手动断言容易遗漏，且新增测试时开发者可能忘记添加。autouse确保零配置全覆盖。
- ❌ **在fixture中做性能敏感操作**：fixture应只做必要的GC和计数器读取，不要在其中执行复杂计算或IO，否则拖慢整个测试套件。
- ❌ **泄漏时只输出"有泄漏"不输出细节**：必须输出泄漏字节数、泄漏对象数、测试名称、before/after值，否则开发者无法快速定位问题规模。

## 检验标准

做完之后怎么知道做对了？

1. **零配置覆盖**：运行pytest时无需任何额外参数，所有使用C++扩展的测试自动获得泄漏检测
2. **人为泄漏被捕获**：故意写一个泄漏的测试（创建对象不释放），fixture能检测到并pytest.fail
3. **正常测试不受影响**：正确释放资源的测试全部通过，无误报
4. **退出机制有效**：`@pytest.mark.leak_check(False)` 标记的测试被正确跳过
5. **Python-only模式无干扰**：C++扩展不可用时fixture直接yield，不抛异常
6. **GC彻底**：测试后两次gc.collect()确保循环引用被回收
7. **诊断信息充分**：泄漏时输出包含测试名、泄漏字节数、泄漏对象数、before/after基线值
8. **CI集成**：在CI中运行pytest，泄漏测试失败时CI变红，阻止泄漏代码合入

## 迁移示例

这个模式还能用在什么其他场景？

- **PyTorch C++ Extension**：自定义算子测试中追踪CUDA内存泄漏（`torch.cuda.memory_allocated()`）
- **Pybind11 绑定库**：任何用pybind11绑定的C++类都可以用这个模式检测泄漏
- **Rust PyO3 扩展**：Rust分配的内存通过PyO3暴露给Python，同样需要检测
- **数据库连接池**：将计数器替换为"活跃连接数"，检测测试后连接是否全部归还
- **文件句柄泄漏**：追踪`open()`文件描述符数量，测试后验证全部关闭
- **GPU资源泄漏**：CUDA kernel中分配的device memory，测试后验证显存归零
- **线程泄漏**：追踪`threading.active_count()`，检测测试后是否有僵尸线程
- **套接字泄漏**：追踪打开的socket数量，检测网络资源泄漏

核心抽象通用：**在测试前后记录资源基线 → 强制清理 → 断言回归 → autouse零配置覆盖**。任何具有"分配-释放"生命周期的资源都可以套用这个模式。

## 来源

- [conftest.py:_check_memory_leaks](../../../../../../projects/xuanspace/vendor/caffe/caffe-ffi/tests/python/conftest.py#L38-L85) — caffe-ffi 自动泄漏检测fixture完整实现
- 复盘报告：[retrospective-caffe-ffi-memlog-20260728](../../reports/task-reports/retrospective-caffe-ffi-memlog-20260728/README.md) — 三层防护闭环中的第三层

> **关联模式**：
> - [resource-counter-primitive-binding](resource-counter-primitive-binding.md) — 本模式依赖准确的C++原子计数器API
> - [cross-platform-backtrace-leak-diagnosis](cross-platform-backtrace-leak-diagnosis.md) — fixture检测到泄漏后的定位工具
> - [cross-language-three-layer-logging](cross-language-three-layer-logging.md) — 通过TRACE日志输出构造栈辅助诊断

## Changelog

<!-- changelog -->
- 2026-07-28 | feat | 从caffe-ffi内存调试日志体系复盘萃取初始版本，autouse基线对比双维度检测+反模式+跨项目迁移示例
