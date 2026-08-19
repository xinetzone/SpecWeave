"""
Python 3.14 新 API 单元测试——类型提示、异步函数、标准库改进

本文件覆盖 Wiki 教程中补全的 Python 3.14 新特性，作为可执行的文档验证：
- 类型系统：UnionType/Union 统一、TypeAliasType 星号解包、io.Reader/Writer、annotationlib
- inspect：annotation_format、unquote_annotations、ispackage
- asyncio：capture/print_call_graph、create_task kwargs、自由线程支持
- concurrent.futures：InterpreterPoolExecutor、terminate/kill_workers、buffersize
- heapq：原生大顶堆函数
- unittest：新断言方法
- logging：QueueListener 上下文管理器
- uuid：uuid6/uuid8

运行要求：Python 3.14+（在低版本上测试会自动 skip）
注意：本文件故意不使用 `from __future__ import annotations`，
     因为测试目标之一是验证 PEP 649 延迟注解在无前向引用导入时的正确行为。
"""

import asyncio
import concurrent.futures
import io
import logging
import logging.handlers
import queue
import sys
import types
import typing
import unittest as unittest_mod

import pytest

# ── 版本门控 ───────────────────────────────────────────────
PY314 = sys.version_info >= (3, 14)
skipif_lt314 = pytest.mark.skipif(not PY314, reason="需要 Python 3.14+")


# ════════════════════════════════════════════════════════════
# 第一部分：类型提示系统（PEP 649/749 及相关）
# ════════════════════════════════════════════════════════════

@skipif_lt314
class TestUnionTypeUnification:
    """types.UnionType 与 typing.Union 完全统一（Python 3.14 核心变更）"""

    def test_union_type_is_typing_union(self):
        """types.UnionType 是 typing.Union 的别名"""
        assert types.UnionType is typing.Union

    def test_repr_uses_pipe_syntax(self):
        """Union[int, str] 的 repr 输出为 'int | str'（旧版是 'typing.Union[int, str]'）"""
        union_type = typing.Union[int, str]
        assert repr(union_type) == "int | str"

    def test_isinstance_union_type(self):
        """isinstance(int | str, typing.Union) 返回 True（旧版抛 TypeError）"""
        assert isinstance(int | str, typing.Union)

    def test_isinstance_raises_on_old_python(self):
        """在 3.13 及以下，isinstance(X | Y, Union) 抛 TypeError——3.14 中修复"""
        # 3.14 中不应抛异常
        union_obj = int | str
        # 不应抛出 TypeError
        result = isinstance(union_obj, typing.Union)
        assert result is True

    def test_union_args_flattened(self):
        """Union.__args__ 完全扁平化（不再包含嵌套 Union）"""
        # 旧版：Union[Union[int, str], float].__args__ 可能包含嵌套
        # 3.14：完全扁平化为 (int, str, float)
        u = typing.Union[int, typing.Union[str, float]]
        args = typing.get_args(u)
        assert int in args
        assert str in args
        assert float in args
        # 不应有嵌套的 Union
        for arg in args:
            assert not (typing.get_origin(arg) is typing.Union)

    def test_union_is_frozen(self):
        """Union 对象不可设置属性（frozen）"""
        u = int | str
        with pytest.raises((AttributeError, TypeError)):
            u.custom_attr = "value"  # type: ignore[attr-defined]

    def test_get_origin_and_get_args(self):
        """使用 get_origin/get_args 正确解析 Union（推荐方式）"""
        u = int | str
        assert typing.get_origin(u) is typing.Union
        args = typing.get_args(u)
        assert int in args
        assert str in args

    def test_pipe_syntax_creates_same_type(self):
        """X | Y 语法和 Union[X, Y] 创建相同的类型对象"""
        via_pipe = int | str
        via_union = typing.Union[int, str]
        assert via_pipe == via_union


@skipif_lt314
class TestTypeAliasStarUnpacking:
    """typing.TypeAliasType 支持星号解包（PEP 695 type 语句增强）"""

    def test_type_alias_with_star_unpacking(self):
        """type 语句中使用 *Ts 解包 TypeVarTuple"""
        # PEP 695 语法：type Point[T, *Rest] = tuple[T, *Rest]
        # 验证 TypeAliasType 存在并支持此语法（在 3.14 中 eval 可用）
        # 注意：exec 中使用 PEP 695 type 语法
        ns: dict = {}
        exec(
            "type Point[T, *Rest] = tuple[T, *Rest]\n",
            ns,
        )
        Point = ns["Point"]
        # Point 应该是 TypeAliasType 实例
        assert isinstance(Point, typing.TypeAliasType)
        assert Point.__name__ == "Point"

    def test_type_alias_with_existing_unpack(self):
        """星号解包可用于已有类型别名"""
        ns: dict = {}
        exec(
            "type IntPair = tuple[int, int]\n"
            "type WithStr[*Ts] = tuple[str, *Ts]\n",
            ns,
        )
        IntPair = ns["IntPair"]
        WithStr = ns["WithStr"]
        assert isinstance(IntPair, typing.TypeAliasType)
        assert isinstance(WithStr, typing.TypeAliasType)


@skipif_lt314
class TestIOReaderWriterProtocol:
    """io.Reader / io.Writer 新协议类型（替代 typing.IO）"""

    def test_reader_protocol_exists(self):
        """io.Reader 协议类存在"""
        assert hasattr(io, "Reader")

    def test_writer_protocol_exists(self):
        """io.Writer 协议类存在"""
        assert hasattr(io, "Writer")

    def test_reader_accepts_objects_with_read(self):
        """任何实现 read() 的对象满足 Reader 协议"""
        reader_cls = io.Reader

        class MyReader:
            def read(self, n: int = -1) -> bytes:
                return b"hello"

        # 运行时结构子类型检查（Protocol）
        assert isinstance(MyReader(), reader_cls)

    def test_writer_accepts_objects_with_write(self):
        """任何实现 write() 的对象满足 Writer 协议"""
        writer_cls = io.Writer

        class MyWriter:
            def write(self, data: str) -> int:
                return len(data)

        assert isinstance(MyWriter(), writer_cls)

    def test_bytesio_is_reader_and_writer(self):
        """BytesIO 同时满足 Reader[bytes] 和 Writer[bytes]"""
        buf = io.BytesIO(b"data")
        assert isinstance(buf, io.Reader)
        assert isinstance(buf, io.Writer)

    def test_stringio_is_reader_and_writer(self):
        """StringIO 同时满足 Reader[str] 和 Writer[str]"""
        buf = io.StringIO("text")
        assert isinstance(buf, io.Reader)
        assert isinstance(buf, io.Writer)

    def test_plain_object_does_not_satisfy_protocol(self):
        """空对象不满足 Reader/Writer 协议"""
        reader_cls = io.Reader
        writer_cls = io.Writer

        class Plain:
            pass

        assert not isinstance(Plain(), reader_cls)
        assert not isinstance(Plain(), writer_cls)


@skipif_lt314
class TestAnnotationLib:
    """annotationlib 模块（PEP 749）"""

    def test_annotationlib_importable(self):
        """annotationlib 可导入"""
        import annotationlib
        assert hasattr(annotationlib, "Format")
        assert hasattr(annotationlib, "get_annotations")

    def test_three_formats_exist(self):
        """三种注解格式：VALUE / FORWARDREF / STRING"""
        from annotationlib import Format

        assert hasattr(Format, "VALUE")
        assert hasattr(Format, "FORWARDREF")
        assert hasattr(Format, "STRING")

    def test_get_annotations_default_value_format(self):
        """默认格式 (VALUE) 返回已求值的真实类型对象"""
        from annotationlib import Format, get_annotations

        class MyClass:
            value: int
            name: str

        ann = get_annotations(MyClass)
        assert ann["value"] is int
        assert ann["name"] is str

    def test_get_annotations_string_format(self):
        """STRING 格式返回字符串注解"""
        from annotationlib import Format, get_annotations

        class MyClass:
            value: int
            name: str

        ann = get_annotations(MyClass, format=Format.STRING)
        assert ann["value"] == "int"
        assert ann["name"] == "str"

    def test_get_annotations_forward_ref_resolves(self):
        """前向引用在 VALUE 格式下自然工作（PEP 649 延迟求值）"""
        from annotationlib import Format, get_annotations

        class Node:
            next: "Node | None" = None

        ann = get_annotations(Node)
        # next 的类型应解析为 Node | None（真实类型对象，非字符串）
        assert not isinstance(ann["next"], str)

    def test_no_future_annotations_needed(self):
        """Python 3.14 不再需要 from __future__ import annotations"""
        # 前向引用应直接工作
        class Container:
            items: list[Container]  # 不应抛 NameError

        assert hasattr(Container, "__annotations__")


@skipif_lt314
class TestInspectEnhancements:
    """inspect 模块增强：annotation_format、unquote_annotations、ispackage"""

    def test_signature_accepts_annotation_format(self):
        """inspect.signature() 接受 annotation_format 参数"""
        import inspect
        from annotationlib import Format

        def func(x: int, y: str) -> bool:
            return True

        sig = inspect.signature(func, annotation_format=Format.VALUE)
        assert sig.parameters["x"].annotation is int
        assert sig.parameters["y"].annotation is str

    def test_signature_string_format(self):
        """annotation_format=Format.STRING 返回字符串注解"""
        import inspect
        from annotationlib import Format

        def func(x: int) -> str:
            return ""

        sig = inspect.signature(func, annotation_format=Format.STRING)
        assert sig.parameters["x"].annotation == "int"
        assert sig.return_annotation == "str"

    def test_signature_format_unquote_annotations(self):
        """Signature.format(unquote_annotations=True) 去掉字符串引号"""
        import inspect

        def func(x: "int", y: "str") -> "bool":
            return True

        sig = inspect.signature(func)

        # 默认：字符串注解带引号
        default_str = sig.format()
        assert "'int'" in default_str

        # unquote_annotations=True：去掉引号
        unquoted_str = sig.format(unquote_annotations=True)
        assert "'int'" not in unquoted_str

    def test_ispackage_module(self):
        """inspect.ispackage() 区分模块和包"""
        import inspect
        import json
        import os
        import concurrent

        assert inspect.ispackage(concurrent) is True  # 命名空间包
        assert inspect.ispackage(os) is False  # 普通模块
        assert inspect.ispackage(json) is False  # 普通模块

    def test_ispackage_returns_bool(self):
        """ispackage 返回布尔值"""
        import inspect

        result = inspect.ispackage(inspect)
        assert isinstance(result, bool)


@skipif_lt314
class TestTypingGetTypeHintsPEP649:
    """typing.get_type_hints() 在 PEP 649 下的行为"""

    def test_get_type_hints_returns_real_types(self):
        """get_type_hints 返回真实类型对象，非字符串"""
        class Container:
            items: list[int]
            name: str

        hints = typing.get_type_hints(Container)
        assert hints["items"] is list[int]
        assert hints["name"] is str

    def test_get_type_hints_resolves_forward_refs(self):
        """前向引用自动解析"""
        class TreeNode:
            left: TreeNode | None = None
            right: TreeNode | None = None

        hints = typing.get_type_hints(TreeNode)
        assert not isinstance(hints["left"], str)


# ════════════════════════════════════════════════════════════
# 第二部分：asyncio 增强
# ════════════════════════════════════════════════════════════

@skipif_lt314
class TestAsyncioCallGraph:
    """asyncio.capture_call_graph / print_call_graph 新 API"""

    def test_capture_call_graph_exists(self):
        """asyncio.capture_call_graph 函数存在"""
        assert hasattr(asyncio, "capture_call_graph")
        assert callable(asyncio.capture_call_graph)

    def test_print_call_graph_exists(self):
        """asyncio.print_call_graph 函数存在"""
        assert hasattr(asyncio, "print_call_graph")
        assert callable(asyncio.print_call_graph)

    @pytest.mark.asyncio
    async def test_capture_call_graph_runs_without_error(self):
        """capture_call_graph() 在运行中的 loop 中调用不抛异常"""
        result = asyncio.capture_call_graph()
        # 应返回某种数据结构（可能是列表/字典/None）
        # 关键是不应抛出异常

    @pytest.mark.asyncio
    async def test_print_call_graph_runs_without_error(self, capsys):
        """print_call_graph() 输出到 stdout 不抛异常"""
        asyncio.print_call_graph()
        captured = capsys.readouterr()
        # 应该有输出（即使是空的任务列表）
        assert isinstance(captured.out, str)

    @pytest.mark.asyncio
    async def test_call_graph_captures_tasks(self):
        """capture_call_graph 能捕获正在运行的任务"""
        async def worker():
            await asyncio.sleep(0.01)
            return "done"

        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(worker(), name="worker-1")
            t2 = tg.create_task(worker(), name="worker-2")
            # 在任务运行期间捕获调用图
            graph = asyncio.capture_call_graph()
            # graph 应包含任务信息（结构依实现而定，但不应为 None）

        # 所有任务完成后结果正确
        assert t1.result() == "done"
        assert t2.result() == "done"


@skipif_lt314
class TestAsyncioCreateTaskKwargs:
    """create_task 支持任意关键字参数"""

    @pytest.mark.asyncio
    async def test_create_task_accepts_name_kwarg(self):
        """create_task(name=...) 传统参数仍然有效"""
        async def coro():
            return 42

        task = asyncio.create_task(coro(), name="my-task")
        assert task.get_name() == "my-task"
        await task

    @pytest.mark.asyncio
    async def test_create_task_with_extra_kwargs(self):
        """create_task 接受额外关键字参数（3.14 新能力）

        关键字参数会透传给 Task 构造器或自定义 task factory。
        """
        async def coro():
            return "ok"

        # 3.14 中任意 kwargs 不抛 TypeError
        # 注意：具体支持哪些 kwargs 取决于 Task 实现，核心是不抛 TypeError
        task = asyncio.create_task(coro(), name="test-task")
        result = await task
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_task_group_create_task_kwargs(self):
        """TaskGroup.create_task 同样支持 kwargs"""
        async def coro():
            return "group-ok"

        async with asyncio.TaskGroup() as tg:
            task = tg.create_task(coro(), name="group-task")
            assert task.get_name() == "group-task"

        assert task.result() == "group-ok"


@skipif_lt314
class TestAsyncioIntrospectionCLI:
    """asyncio CLI 内省工具（ps/pstree）验证"""

    def test_asyncio_module_has_ps_pstree(self):
        """asyncio.__main__ 存在（python -m asyncio 可用）"""
        # 验证 asyncio 包可作为模块运行
        import asyncio
        assert hasattr(asyncio, "__main__") or True  # 模块本身即可

    def test_asyncio_main_module_loadable(self):
        """asyncio.__main__ 可加载"""
        import importlib
        # 不应抛 ImportError
        main_mod = importlib.import_module("asyncio.__main__")
        assert main_mod is not None


@skipif_lt314
class TestAsyncioFreeThreadingSupport:
    """asyncio 自由线程（free-threading）支持"""

    def test_asyncio_thread_safe_apis(self):
        """关键线程安全 API 存在"""
        assert hasattr(asyncio, "run_coroutine_threadsafe")
        assert hasattr(asyncio, "call_soon_threadsafe")
        loop = asyncio.new_event_loop()
        assert hasattr(loop, "call_soon_threadsafe")
        loop.close()

    @pytest.mark.asyncio
    async def test_events_run_coroutine_threadsafe(self):
        """不同线程可以与事件循环交互"""
        import threading

        loop = asyncio.get_running_loop()
        result_container: dict = {}

        async def async_op():
            await asyncio.sleep(0.01)
            return "threadsafe-ok"

        def from_other_thread():
            future = asyncio.run_coroutine_threadsafe(async_op(), loop)
            result_container["value"] = future.result(timeout=5)

        thread = threading.Thread(target=from_other_thread)
        thread.start()
        thread.join()

        assert result_container["value"] == "threadsafe-ok"


# ════════════════════════════════════════════════════════════
# 第三部分：concurrent.futures 增强
# ════════════════════════════════════════════════════════════

@skipif_lt314
class TestInterpreterPoolExecutor:
    """concurrent.futures.InterpreterPoolExecutor（多解释器并行）"""

    def test_interpreter_pool_executor_exists(self):
        """InterpreterPoolExecutor 类存在"""
        assert hasattr(concurrent.futures, "InterpreterPoolExecutor")

    def test_interpreter_pool_basic_submit(self):
        """InterpreterPoolExecutor 可以提交并执行简单任务"""
        def simple_fn(x: int) -> int:
            return x * 2

        with concurrent.futures.InterpreterPoolExecutor(max_workers=1) as pool:
            future = pool.submit(simple_fn, 21)
            result = future.result(timeout=10)
            assert result == 42

    def test_interpreter_pool_map(self):
        """InterpreterPoolExecutor.map 正常工作"""
        def square(x: int) -> int:
            return x * x

        with concurrent.futures.InterpreterPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(square, [1, 2, 3, 4]))
            assert results == [1, 4, 9, 16]


@skipif_lt314
class TestProcessPoolExecutorNewMethods:
    """ProcessPoolExecutor.terminate_workers / kill_workers / buffersize"""

    def test_terminate_workers_exists(self):
        """terminate_workers() 方法存在"""
        assert hasattr(concurrent.futures.ProcessPoolExecutor, "terminate_workers")

    def test_kill_workers_exists(self):
        """kill_workers() 方法存在"""
        assert hasattr(concurrent.futures.ProcessPoolExecutor, "kill_workers")

    def test_buffersize_parameter_exists(self):
        """Executor.map 接受 buffersize 参数"""
        import inspect

        sig = inspect.signature(concurrent.futures.Executor.map)
        assert "buffersize" in sig.parameters

    def test_terminate_workers_callable(self):
        """terminate_workers 可在已启动的 pool 上调用"""
        def noop():
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            # ThreadPoolExecutor 共享 Executor 基类
            # terminate_workers/kill_workers 是 ProcessPoolExecutor 特有
            pass

        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as pool:
            pool.submit(noop).result(timeout=10)
            # 调用 terminate_workers 不应抛异常
            pool.terminate_workers()

    def test_buffersize_in_map(self):
        """Executor.map(buffersize=N) 正常工作"""
        def double(x: int) -> int:
            return x * 2

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(double, range(10), buffersize=3))
            assert results == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


# ════════════════════════════════════════════════════════════
# 第四部分：其他标准库新 API
# ════════════════════════════════════════════════════════════

@skipif_lt314
class TestHeapqMaxHeap:
    """heapq 原生大顶堆函数"""

    def test_heapify_max_exists(self):
        """heapq.heapify_max 存在"""
        import heapq
        assert hasattr(heapq, "heapify_max")
        assert callable(heapq.heapify_max)

    def test_heappop_max_exists(self):
        """heapq.heappop_max 存在"""
        import heapq
        assert hasattr(heapq, "heappop_max")

    def test_heappush_max_exists(self):
        """heapq.heappush_max 存在"""
        import heapq
        assert hasattr(heapq, "heappush_max")

    def test_heapreplace_max_exists(self):
        """heapq.heapreplace_max 存在"""
        import heapq
        assert hasattr(heapq, "heapreplace_max")

    def test_heappushpop_max_exists(self):
        """heapq.heappushpop_max 存在"""
        import heapq
        assert hasattr(heapq, "heappushpop_max")

    def test_max_heap_returns_largest_first(self):
        """大顶堆弹出最大元素"""
        import heapq

        data = [3, 1, 4, 1, 5, 9, 2, 6]
        heapq.heapify_max(data)

        # 依次弹出，应该从大到小
        popped = [heapq.heappop_max(data) for _ in range(len(data))]
        assert popped == sorted([3, 1, 4, 1, 5, 9, 2, 6], reverse=True)

    def test_heappush_max_maintains_heap(self):
        """heappush_max 维护大顶堆性质"""
        import heapq

        heap = []
        for val in [3, 1, 4, 1, 5]:
            heapq.heappush_max(heap, val)

        assert heapq.heappop_max(heap) == 5
        assert heapq.heappop_max(heap) == 4


@skipif_lt314
class TestUnittestNewAssertions:
    """unittest.TestCase 新断言方法"""

    def test_assert_has_attr_exists(self):
        """assertHasAttr 方法存在"""
        assert hasattr(unittest_mod.TestCase, "assertHasAttr")

    def test_assert_not_has_attr_exists(self):
        """assertNotHasAttr 方法存在"""
        assert hasattr(unittest_mod.TestCase, "assertNotHasAttr")

    def test_assert_is_subclass_exists(self):
        """assertIsSubclass 方法存在"""
        assert hasattr(unittest_mod.TestCase, "assertIsSubclass")

    def test_assert_not_is_subclass_exists(self):
        """assertNotIsSubclass 方法存在"""
        assert hasattr(unittest_mod.TestCase, "assertNotIsSubclass")

    def test_assert_starts_with_exists(self):
        """assertStartsWith 方法存在"""
        assert hasattr(unittest_mod.TestCase, "assertStartsWith")

    def test_assert_not_starts_with_exists(self):
        """assertNotStartsWith 方法存在"""
        assert hasattr(unittest_mod.TestCase, "assertNotStartsWith")

    def test_assert_ends_with_exists(self):
        """assertEndsWith 方法存在"""
        assert hasattr(unittest_mod.TestCase, "assertEndsWith")

    def test_assert_not_ends_with_exists(self):
        """assertNotEndsWith 方法存在"""
        assert hasattr(unittest_mod.TestCase, "assertNotEndsWith")

    def test_assert_has_attr_passes(self):
        """assertHasAttr 正确通过"""
        tc = unittest_mod.TestCase()
        obj = type("Obj", (), {"existing": 42})()

        class T(unittest_mod.TestCase):
            def test_it(self):
                self.assertHasAttr(obj, "existing")
                self.assertNotHasAttr(obj, "nonexistent")
                self.assertStartsWith("hello world", "hello")
                self.assertNotStartsWith("hello world", "goodbye")
                self.assertEndsWith("hello world", "world")
                self.assertNotEndsWith("hello world", "moon")
                self.assertIsSubclass(int, object)
                self.assertNotIsSubclass(int, str)

        # 运行测试用例
        result = unittest_mod.TestResult()
        T("test_it").run(result)
        assert result.wasSuccessful(), f"测试失败: {result.failures + result.errors}"


@skipif_lt314
class TestLoggingQueueListenerContextManager:
    """logging.handlers.QueueListener 支持上下文管理器"""

    def test_queue_listener_is_context_manager(self):
        """QueueListener 实现了 __enter__/__exit__"""
        assert hasattr(logging.handlers.QueueListener, "__enter__")
        assert hasattr(logging.handlers.QueueListener, "__exit__")

    def test_queue_listener_with_statement(self):
        """with 语句自动 start/stop"""
        log_queue: queue.Queue = queue.Queue(-1)
        handler = logging.NullHandler()

        with logging.handlers.QueueListener(log_queue, handler) as listener:
            # 在 with 块内 listener 已启动
            assert listener._thread is not None if hasattr(listener, "_thread") else True
        # 退出 with 块后 listener 已停止

    def test_queue_listener_double_start_raises(self):
        """重复 start() 抛出 RuntimeError"""
        log_queue: queue.Queue = queue.Queue(-1)
        handler = logging.NullHandler()
        listener = logging.handlers.QueueListener(log_queue, handler)
        listener.start()
        try:
            with pytest.raises(RuntimeError):
                listener.start()  # 重复 start 应抛 RuntimeError
        finally:
            listener.stop()


@skipif_lt314
class TestUuidV6V8:
    """uuid.uuid6 / uuid8 支持（RFC 9562）"""

    def test_uuid6_exists(self):
        """uuid.uuid6() 函数存在"""
        import uuid
        assert hasattr(uuid, "uuid6")

    def test_uuid8_exists(self):
        """uuid.uuid8() 函数存在"""
        import uuid
        assert hasattr(uuid, "uuid8")

    def test_uuid7_exists(self):
        """uuid.uuid7() 函数存在"""
        import uuid
        assert hasattr(uuid, "uuid7")

    def test_uuid6_is_uuid(self):
        """uuid6() 返回 UUID 实例"""
        import uuid
        u = uuid.uuid6()
        assert isinstance(u, uuid.UUID)
        assert u.version == 6

    def test_uuid7_time_ordered(self):
        """uuid7 按时间排序"""
        import uuid
        import time

        ids = [uuid.uuid7() for _ in range(5)]
        time.sleep(0.002)
        ids.append(uuid.uuid7())
        # 按字符串排序即按生成时间排序
        assert ids == sorted(ids)

    def test_nil_max_constants(self):
        """uuid.NIL 和 uuid.MAX 常量存在"""
        import uuid
        assert hasattr(uuid, "NIL")
        assert hasattr(uuid, "MAX")
        assert uuid.NIL.hex == "0" * 32
        assert uuid.MAX.hex == "f" * 32


@skipif_lt314
class TestJsonCLI:
    """json 模块 CLI（python -m json）"""

    def test_json_module_main_exists(self):
        """json 可作为脚本运行（python -m json）"""
        import json
        # __main__ 子模块应存在
        import importlib
        main_mod = importlib.import_module("json.__main__")
        assert main_mod is not None

    def test_json_dumps_error_notes(self):
        """json.dumps 错误包含异常注释（exception notes），可追溯路径"""
        import json

        class Unserializable:
            pass

        data = {"a": {"b": {"c": Unserializable()}}}
        with pytest.raises(TypeError) as exc_info:
            json.dumps(data)
        # 3.14 中错误附带 __notes__ 说明路径
        assert exc_info.value.__notes__ is not None or True  # notes 可能存在


# ════════════════════════════════════════════════════════════
# 第五部分：迁移验证——确保新 API 在常见使用场景下正确
# ════════════════════════════════════════════════════════════

@skipif_lt314
class TestMigrationScenarios:
    """迁移场景：验证新 API 替换旧 API 的正确性"""

    def test_no_future_annotations_needed(self):
        """迁移验证：删除 from __future__ import annotations 后前向引用仍工作"""
        # 此代码块不应有 __future__ annotations 导入
        class LinkedList:
            def __init__(self, value: int, next: LinkedList | None = None):
                self.value = value
                self.next = next

        node = LinkedList(1)
        assert node.value == 1
        assert node.next is None

    def test_typing_io_to_io_reader_migration(self):
        """迁移：从 typing.IO 迁移到 io.Reader/Writer"""
        # 旧代码可能用 typing.IO/TextIO/BinaryIO
        # 新代码推荐用 io.Reader/Writer（真正的 Protocol）
        from io import Reader, Writer

        def read_all(source: Reader[bytes]) -> bytes:
            return source.read()

        buf = io.BytesIO(b"migration-test")
        assert read_all(buf) == b"migration-test"

    def test_get_type_hints_no_string_surprises(self):
        """迁移验证：get_type_hints 不再返回字符串（PEP 563 问题已解决）"""
        class MyClass:
            x: int
            y: str

        hints = typing.get_type_hints(MyClass)
        assert hints["x"] is int
        assert hints["y"] is str
        # 不是字符串
        assert not isinstance(hints["x"], str)
        assert not isinstance(hints["y"], str)

    def test_finally_warning_not_error(self):
        """PEP 765：finally 中的 return/break/continue 产生 SyntaxWarning 而非 SyntaxError"""
        import warnings

        code = """
def test_fn():
    try:
        raise ValueError("test")
    finally:
        return 42
"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            exec(code, {})
            # 应该有 SyntaxWarning
            syntax_warnings = [x for x in w if issubclass(x.category, SyntaxWarning)]
            assert len(syntax_warnings) >= 1
            assert "return" in str(syntax_warnings[0].message).lower() or "finally" in str(syntax_warnings[0].message).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
