"""并发安全AST访问器 - 实现八维检查法。"""

import ast
from pathlib import Path

from .constants import (
    DIMENSIONS, LOCK_METHODS, WAIT_METHODS, ASYNC_WAIT,
    MUTABLE_TYPES, CHINESE_CHAR_RANGE, LOGGING_CALLS,
    LOCK_CLASSES, POOL_CLASSES, POOL_SHUTDOWN_METHODS,
    I18N_EXEMPT_CALLS, I18N_DICT_METHODS,
)
from .models import ConcurrencyIssue


def _has_chinese(text: str) -> bool:
    return any(CHINESE_CHAR_RANGE[0] <= ch <= CHINESE_CHAR_RANGE[1] for ch in text)


def _extract_guard_targets(test_node) -> set[str]:
    """提取if条件中检查的容器名称，用于幂等性守卫判断。
    例如: `if x not in self.rejected_by` → 返回 {'self.rejected_by'}
    """
    targets = set()
    for node in ast.walk(test_node):
        if isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, (ast.In, ast.NotIn)):
                    if isinstance(comp, ast.Name):
                        targets.add(comp.id)
                    elif isinstance(comp, ast.Attribute):
                        chain = _attr_chain(comp)
                        if chain:
                            targets.add(chain)
    return targets


def _attr_chain(node) -> str:
    parts = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return ".".join(reversed(parts))


class ConcurrentSafetyVisitor(ast.NodeVisitor):
    def __init__(self, filepath: Path, content_lines: list[str]):
        self.filepath = filepath
        self.content_lines = list(content_lines)
        self.issues: list[ConcurrencyIssue] = []
        self._reported_on_line: dict[int, set[str]] = {}

        self.function_name = ""
        self.in_test_function = False
        self.in_logging_call = False
        self.current_class = ""
        self._loop_depth = 0
        self._is_resolver_class = False
        self._function_params: dict[str, str] = {}
        self._if_guard_stack: list[set[str]] = []
        self._thread_vars: set[str] = set()

        self._lock_vars: dict[str, str] = {}
        self._lock_acquire_sequences: list[tuple[str, list[str], int]] = []
        self._current_function_locks: list[str] = []
        self._pool_vars: set[str] = set()
        self._pool_shutdown: set[str] = set()
        self._pool_context_managed: set[str] = set()
        self._in_with_block = False

    def _get_snippet(self, line_no: int) -> str:
        if line_no and 0 < line_no <= len(self.content_lines):
            return self.content_lines[line_no - 1].strip()
        return ""

    def _make_issue(self, dimension: str, message: str, line: int, snippet: str = "") -> ConcurrencyIssue:
        dim_info = DIMENSIONS[dimension]
        return ConcurrencyIssue(
            dimension=dimension,
            code=dim_info["code"],
            severity=dim_info["default_severity"],
            message=message,
            line=line,
            snippet=snippet or self._get_snippet(line),
            dimension_name=dim_info["name"],
        )

    def _add_issue(self, dimension: str, message: str, line: int, snippet: str = ""):
        dedup_key = f"{dimension}:{message[:80]}"
        line_cats = self._reported_on_line.setdefault(line, set())
        if dedup_key in line_cats:
            return
        line_cats.add(dedup_key)
        self.issues.append(self._make_issue(dimension, message, line, snippet))

    def visit_Module(self, node: ast.Module):
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        old_class = self.current_class
        old_resolver = self._is_resolver_class
        self.current_class = node.name
        self._is_resolver_class = any(
            kw in node.name.lower() for kw in [
                "resolver", "scheduler", "manager", "dispatcher", "arbiter",
                "lock", "queue", "pool", "worker", "concurrent", "dispatcher",
            ]
        )
        self.generic_visit(node)
        self.current_class = old_class
        self._is_resolver_class = old_resolver

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_func = self.function_name
        old_in_test = self.in_test_function
        old_params = self._function_params
        old_thread_vars = self._thread_vars
        old_func_locks = self._current_function_locks
        old_pool_shutdown = self._pool_shutdown
        old_pool_ctx = self._pool_context_managed

        self.function_name = node.name
        self.in_test_function = node.name.startswith("test_") or node.name.startswith("_test_")
        self._function_params = {}
        self._thread_vars = set()
        self._current_function_locks = []
        self._pool_shutdown = set()
        self._pool_context_managed = set()
        for arg in node.args.args:
            self._function_params[arg.arg] = self._get_annotation_name(arg.annotation)

        for default_idx, default in enumerate(node.args.defaults):
            arg_idx = len(node.args.args) - len(node.args.defaults) + default_idx
            if arg_idx < len(node.args.args):
                arg_name = node.args.args[arg_idx].arg
                self._check_default_arg(arg_name, default, default.lineno)

        self.generic_visit(node)

        self._check_lock_ordering(node)
        self._check_pool_shutdown_in_function(node)

        self.function_name = old_func
        self.in_test_function = old_in_test
        self._function_params = old_params
        self._thread_vars = old_thread_vars
        self._current_function_locks = old_func_locks
        self._pool_shutdown = old_pool_shutdown
        self._pool_context_managed = old_pool_ctx

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)

    def _get_annotation_name(self, ann) -> str:
        if ann is None:
            return ""
        if isinstance(ann, ast.Name):
            return ann.id
        if isinstance(ann, ast.Subscript):
            return self._get_annotation_name(ann.value)
        return ""

    def _check_default_arg(self, arg_name: str, default: ast.expr, lineno: int):
        if self.in_test_function:
            return
        if isinstance(default, ast.List):
            self._add_issue("DEFENSIVE", f"可变默认参数 list: {arg_name}=[]，应使用 None 作为默认值", lineno)
        elif isinstance(default, ast.Dict):
            self._add_issue("DEFENSIVE", f"可变默认参数 dict: {arg_name}={{}}，应使用 None 作为默认值", lineno)
        elif isinstance(default, ast.Set):
            self._add_issue("DEFENSIVE", f"可变默认参数 set: {arg_name}={{...}}，应使用 None 作为默认值", lineno)

    def visit_If(self, node: ast.If):
        guard_targets = _extract_guard_targets(node.test)
        self._if_guard_stack.append(guard_targets)
        self.generic_visit(node)
        self._if_guard_stack.pop()

    def _caller_name(self, func) -> str:
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
        return ""

    def _caller_full(self, func) -> str:
        if isinstance(func, ast.Attribute):
            return _attr_chain(func)
        if isinstance(func, ast.Name):
            return func.id
        return ""

    def _check_timeout_in_call(self, node: ast.Call, caller_name: str):
        if not caller_name:
            return

        is_lock_acquire = (
            caller_name in LOCK_METHODS
            or (caller_name == "acquire" and self._is_lock_object(node.func))
        )

        if is_lock_acquire:
            has_timeout = False
            has_nonblocking = False
            for kw in node.keywords:
                if kw.arg == "timeout":
                    has_timeout = True
                if kw.arg == "blocking" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                    has_nonblocking = True
            if len(node.args) >= 1:
                first = node.args[0]
                if isinstance(first, ast.Constant) and first.value is False:
                    has_nonblocking = True
            if not has_timeout and not has_nonblocking:
                self._add_issue(
                    "TIMEOUT",
                    f"锁操作 {caller_name}() 未设置timeout，可能导致死锁",
                    node.lineno,
                )

        if caller_name == "wait" and self._is_concurrency_wait(node.func):
            if not self._has_timeout_arg(node):
                self._add_issue(
                    "TIMEOUT",
                    "wait() 调用未设置timeout，可能永久阻塞",
                    node.lineno,
                )

        if caller_name == "join" and self._is_thread_join(node.func):
            if not self._has_timeout_arg(node):
                self._add_issue(
                    "TIMEOUT",
                    "join() 调用未设置timeout，可能永久阻塞",
                    node.lineno,
                )

        if caller_name == "wait_for":
            if len(node.args) < 2 and not any(kw.arg == "timeout" for kw in node.keywords):
                self._add_issue(
                    "TIMEOUT",
                    "asyncio.wait_for() 缺少timeout参数",
                    node.lineno,
                )

    def _is_lock_object(self, func) -> bool:
        if isinstance(func, ast.Attribute):
            val = func.value
            if isinstance(val, ast.Name):
                return any(kw in val.id.lower() for kw in ["lock", "mutex", "semaphore", "rwlock", "_lock", "cond", "event"])
        return False

    def _is_thread_join(self, func) -> bool:
        """区分 threading.Thread.join() 与 str.join()。"""
        if not isinstance(func, ast.Attribute):
            return False
        val = func.value
        if isinstance(val, ast.Constant) and isinstance(val.value, str):
            return False
        if isinstance(val, ast.Name):
            name = val.id.lower()
            if name in {"sep", "delim", "delimiter", "separator"}:
                return False
            if name in self._thread_vars:
                return True
        thread_hints = ["thread", "worker", "proc", "process", "task", "fut", "future", "coro", "greenlet"]
        name_to_check = self._attr_base_name(val)
        return any(h in name_to_check for h in thread_hints)

    def _is_concurrency_wait(self, func) -> bool:
        """检查 wait() 是否在并发原语上调用（Event/Condition/Barrier/Queue等）。"""
        if not isinstance(func, ast.Attribute):
            return False
        wait_hints = ["lock", "event", "cond", "condition", "barrier", "queue", "latch",
                      "semaphore", "gate", "_wait", "waiter", "ready", "done"]
        name_to_check = self._attr_base_name(func.value)
        return any(h in name_to_check for h in wait_hints)

    def _attr_base_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id.lower()
        if isinstance(node, ast.Attribute):
            return node.attr.lower()
        return ""

    def _has_timeout_arg(self, node: ast.Call) -> bool:
        for kw in node.keywords:
            if kw.arg == "timeout":
                return True
        for i, arg in enumerate(node.args):
            if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                return True
        return False

    def _check_idempotent_append(self, node: ast.Call, caller_name: str):
        if caller_name != "append":
            return

        target_name = self._append_target_name(node.func)
        if target_name is None:
            return

        target_short = target_name.split(".")[-1].lower()

        if target_short.endswith("_stack"):
            return
        if target_short in {"sequences", "collected", "records", "results", "items_all"}:
            return
        if target_short.endswith("_sequences") or target_short.endswith("_records"):
            return

        for guards in self._if_guard_stack:
            if target_name in guards:
                return
            short = target_name.split(".")[-1]
            for g in guards:
                if g.endswith("." + short) or g == short:
                    return

        if target_short in {"issues"} and hasattr(self, "_reported_on_line"):
            return

        if not self._is_resolver_class and not any(
            kw in target_name.lower() for kw in ["rejected", "pending", "queue", "waiting", "blocked"]
        ):
            return

        self._add_issue(
            "IDEMPOTENT",
            f"对列表/集合 {target_name} 执行 append() 前未做 'not in' 去重检查，重复调用可能导致重复记录（活锁风险）",
            node.lineno,
        )

    def _append_target_name(self, func) -> str | None:
        if isinstance(func, ast.Attribute) and isinstance(func.value, (ast.Name, ast.Attribute)):
            return _attr_chain(func.value)
        return None

    def _check_config_magic_numbers(self, node: ast.Call, caller_name: str):
        if not self._is_resolver_class:
            return

        if caller_name in {"sleep", "acquire"}:
            timeout_val = self._extract_numeric_arg(node)
            if timeout_val is not None and timeout_val > 0:
                has_constant_ref = any(
                    isinstance(a, ast.Name) and a.id.isupper()
                    for a in node.args
                )
                if not has_constant_ref and timeout_val >= 1:
                    self._add_issue(
                        "CONFIG",
                        f"并发参数 {caller_name}({timeout_val}) 使用硬编码数值，建议提取为类常量或构造函数可配置参数",
                        node.lineno,
                    )

    def _extract_numeric_arg(self, node: ast.Call):
        for kw in node.keywords:
            if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                return kw.value.value if isinstance(kw.value.value, (int, float)) else None
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                return arg.value
        return None

    def _check_chinese_in_call(self, node: ast.Call, caller_name: str):
        if self.in_logging_call or self.in_test_function:
            return
        if caller_name in LOGGING_CALLS:
            return
        if caller_name in {"strip", "lower", "upper", "format", "replace", "encode", "decode"}:
            return

        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                text = arg.value
                if _has_chinese(text) and len(text) >= 2:
                    if caller_name in {"startswith", "endswith", "find", "index", "__contains__", "__eq__"}:
                        self._add_issue(
                            "I18N",
                            f"业务逻辑中直接匹配中文文本「{text[:20]}」，建议使用枚举/常量而非字面量",
                            node.lineno,
                        )

    def visit_While(self, node: ast.While):
        is_infinite = (
            (isinstance(node.test, ast.Constant) and node.test.value is True)
            or (isinstance(node.test, ast.Name) and node.test.id == "True")
        )

        if is_infinite:
            has_exit = self._has_exit_in_loop(node)
            has_timeout = self._has_timeout_in_loop(node)
            if not has_exit and not has_timeout and not self.in_test_function:
                self._add_issue(
                    "TIMEOUT",
                    "while True 无限循环未检测到break/return/raise/超时退出机制，存在死循环风险",
                    node.lineno,
                )

        old_depth = self._loop_depth
        self._loop_depth += 1
        self.generic_visit(node)
        self._loop_depth = old_depth

    def visit_For(self, node):
        old_depth = self._loop_depth
        self._loop_depth += 1
        self.generic_visit(node)
        self._loop_depth = old_depth

    def _has_exit_in_loop(self, loop_node) -> bool:
        for child in ast.walk(loop_node):
            if child is loop_node:
                continue
            if isinstance(child, (ast.Break, ast.Return, ast.Raise)):
                if hasattr(child, 'lineno') and child.lineno > loop_node.lineno:
                    return True
        return False

    def _has_timeout_in_loop(self, loop_node) -> bool:
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Call):
                cn = self._caller_name(child.func)
                if cn in {"wait", "acquire", "join", "sleep"} and self._has_timeout_arg(child):
                    return True
        return False

    def visit_Compare(self, node: ast.Compare):
        if self.in_test_function or self.in_logging_call:
            self.generic_visit(node)
            return

        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                self._check_in_operator(comparator, node.lineno)

            for side in [node.left, comparator]:
                if isinstance(side, ast.Constant) and isinstance(side.value, str):
                    if _has_chinese(side.value) and len(side.value) >= 2:
                        self._add_issue(
                            "I18N",
                            f"比较中使用中文字面量「{side.value[:20]}」，建议提取为枚举常量",
                            node.lineno,
                        )

        self.generic_visit(node)

    def _check_in_operator(self, collection, lineno: int):
        coll_name = ""
        if isinstance(collection, ast.Name):
            coll_name = collection.id
        elif isinstance(collection, ast.Attribute):
            coll_name = _attr_chain(collection)

        if not coll_name:
            return

        if self._loop_depth == 0 and not self._is_resolver_class:
            return

        name_lower = coll_name.lower()
        if name_lower.endswith("_set") or name_lower.endswith("_dict") or name_lower.endswith("_map"):
            return

        list_hints = ["_list", "agents_list", "items_list", "results", "candidates", "entries", "pending_list", "queue", "waiting_list"]
        is_list_var = (
            name_lower.endswith("_list")
            or any(kw in name_lower for kw in list_hints)
            or (self._is_resolver_class and "agents" in name_lower and not name_lower.endswith("_set"))
        )
        is_self_or_name = isinstance(collection, ast.Name) or (
            isinstance(collection, ast.Attribute)
            and isinstance(collection.value, ast.Name)
            and collection.value.id in {"self", "cls"}
        )

        if is_list_var and is_self_or_name and self._loop_depth >= 1:
            self._add_issue(
                "BOUNDARY",
                f"循环热路径中对列表 {coll_name} 使用'in'线性查找(O(n))，总体复杂度O(n²)，建议用dict/set实现O(1)查找",
                lineno,
            )

    def visit_Return(self, node: ast.Return):
        if self.in_test_function or node.value is None:
            self.generic_visit(node)
            return

        if isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name):
            if node.value.value.id == "self":
                attr_name = node.value.attr
                if any(kw in attr_name.lower() for kw in [
                    "cache", "list", "dict", "map", "state", "queue", "set",
                    "agents", "results", "pending", "waiting", "rejected",
                ]):
                    self._add_issue(
                        "DEFENSIVE",
                        f"直接返回self.{attr_name}（内部可变状态），外部修改会破坏封装，建议返回copy()或不可变视图",
                        node.lineno,
                    )

        if isinstance(node.value, ast.Name) and node.value.id in self._function_params:
            param_type = self._function_params.get(node.value.id, "")
            if param_type.lower() in MUTABLE_TYPES:
                self._add_issue(
                    "DEFENSIVE",
                    f"直接返回外部传入的可变参数 {node.value.id}，建议做防御性拷贝",
                    node.lineno,
                )

        self.generic_visit(node)

    def _is_thread_constructor(self, val) -> bool:
        if not isinstance(val, ast.Call):
            return False
        func = val.func
        if isinstance(func, ast.Name) and func.id in {"Thread", "Process", "Future", "Worker"}:
            return True
        if isinstance(func, ast.Attribute):
            if func.attr in {"Thread", "Process", "Future"}:
                return True
        return False

    def _is_copy_call(self, node) -> bool:
        if isinstance(node, ast.Call):
            cn = self._caller_name(node.func)
            return cn in {"copy", "deepcopy", "dict", "list", "set"} or ".copy" in self._caller_full(node.func)
        return False

    def _is_lock_constructor(self, val) -> bool:
        if not isinstance(val, ast.Call):
            return False
        func = val.func
        if isinstance(func, ast.Name) and func.id in LOCK_CLASSES:
            return True
        if isinstance(func, ast.Attribute):
            if func.attr in LOCK_CLASSES:
                return True
        return False

    def _is_pool_constructor(self, val) -> bool:
        if not isinstance(val, ast.Call):
            return False
        func = val.func
        if isinstance(func, ast.Name) and func.id in POOL_CLASSES:
            return True
        if isinstance(func, ast.Attribute):
            if func.attr in POOL_CLASSES:
                return True
        return False

    def visit_With(self, node: ast.With):
        old_in_with = self._in_with_block
        self._in_with_block = True

        for item in node.items:
            ctx = item.context_expr
            ctx_name = ""
            is_lock_ctx = False
            is_pool_ctx = False

            if isinstance(ctx, ast.Call):
                cn = self._caller_name(ctx.func)
                if cn in LOCK_CLASSES or (isinstance(ctx.func, ast.Attribute) and ctx.func.attr in LOCK_CLASSES):
                    is_lock_ctx = True
                if cn in POOL_CLASSES or (isinstance(ctx.func, ast.Attribute) and ctx.func.attr in POOL_CLASSES):
                    is_pool_ctx = True
            elif isinstance(ctx, (ast.Name, ast.Attribute)):
                ctx_name = _attr_chain(ctx) if isinstance(ctx, ast.Attribute) else (ctx.id if isinstance(ctx, ast.Name) else "")
                if ctx_name in self._lock_vars or any(kw in ctx_name.lower() for kw in ["lock", "mutex", "semaphore", "_lock", "rwlock"]):
                    is_lock_ctx = True

            as_name = ""
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                as_name = item.optional_vars.id

            if is_lock_ctx:
                lock_target = as_name or ctx_name or self._extract_lock_expr_name(ctx)
                if lock_target:
                    if as_name:
                        self._lock_vars[as_name] = "with_lock"
                    if lock_target not in self._current_function_locks:
                        self._current_function_locks.append(lock_target)

            if is_pool_ctx:
                if as_name:
                    self._pool_vars.add(as_name)
                    self._pool_context_managed.add(as_name)

        self.generic_visit(node)

        self._in_with_block = old_in_with

    def _extract_lock_expr_name(self, ctx) -> str:
        if isinstance(ctx, ast.Attribute):
            return _attr_chain(ctx)
        if isinstance(ctx, ast.Name):
            return ctx.id
        if isinstance(ctx, ast.Call):
            return self._lock_type_from_call(ctx).lower() + "_anon"
        return ""

    def visit_Subscript(self, node: ast.Subscript):
        if self.in_test_function or self.in_logging_call:
            self.generic_visit(node)
            return

        if self._is_chinese_subscript_key(node):
            key_val = self._get_subscript_key_value(node)
            if key_val and _has_chinese(key_val) and len(key_val) >= 2:
                if not self.in_logging_call:
                    self._add_issue(
                        "I18N",
                        f"使用中文字面量「{key_val[:20]}」作为字典/列表索引键，建议使用枚举常量替代",
                        node.lineno,
                    )

        self.generic_visit(node)

    def _is_chinese_subscript_key(self, node: ast.Subscript) -> bool:
        if not isinstance(node.value, (ast.Name, ast.Attribute)):
            return False
        slice_val = node.slice
        if isinstance(slice_val, ast.Constant) and isinstance(slice_val.value, str):
            return True
        return False

    def _get_subscript_key_value(self, node: ast.Subscript) -> str:
        if isinstance(node.slice, ast.Constant):
            return str(node.slice.value)
        return ""

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if self._is_thread_constructor(node.value):
                    self._thread_vars.add(target.id.lower())
                if self._is_lock_constructor(node.value):
                    self._lock_vars[target.id] = self._lock_type_from_call(node.value)
                if self._is_pool_constructor(node.value):
                    self._pool_vars.add(target.id)
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                attr_name = target.attr
                val = node.value
                if isinstance(val, ast.Name) and val.id in self._function_params:
                    param_type = self._function_params.get(val.id, "")
                    is_mutable_attr = any(
                        kw in attr_name.lower() for kw in [
                            "list", "dict", "map", "cache", "state", "set",
                            "agents", "queue", "pending", "results",
                        ]
                    )
                    if param_type.lower() in MUTABLE_TYPES or is_mutable_attr:
                        if not self._is_copy_call(val):
                            self._add_issue(
                                "DEFENSIVE",
                                f"self.{attr_name} = {val.id} 直接引用外部可变对象，外部修改会污染内部状态，建议copy()",
                                node.lineno,
                            )
                if isinstance(val, ast.Call):
                    if self._is_lock_constructor(val):
                        self._lock_vars[f"self.{attr_name}"] = self._lock_type_from_call(val)
                    if self._is_pool_constructor(val):
                        self._pool_vars.add(f"self.{attr_name}")

        self.generic_visit(node)

    def _lock_type_from_call(self, call_node: ast.Call) -> str:
        func = call_node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return "Lock"

    def visit_Call(self, node: ast.Call):
        if self.in_test_function:
            self.generic_visit(node)
            return

        caller_name = self._caller_name(node.func)
        caller_full = self._caller_full(node.func)

        if caller_name in LOGGING_CALLS:
            old_logging = self.in_logging_call
            self.in_logging_call = True
            self.generic_visit(node)
            self.in_logging_call = old_logging
            return

        self._check_timeout_in_call(node, caller_name)
        self._check_idempotent_append(node, caller_name)
        self._check_config_magic_numbers(node, caller_name)
        self._check_chinese_in_call(node, caller_name)
        self._check_chinese_in_operator(node, caller_name)
        self._check_lock_acquire_sequence(node, caller_name, caller_full)
        self._check_pool_shutdown_call(node, caller_name, caller_full)

        self.generic_visit(node)

    def _check_chinese_in_operator(self, node: ast.Call, caller_name: str):
        """检测 `if "中文" in some_dict` 等in操作符中使用中文字面量的场景。"""
        if self.in_logging_call or self.in_test_function:
            return
        if caller_name not in {"__contains__", "get"} and caller_name not in I18N_DICT_METHODS:
            pass

        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                text = arg.value
                if _has_chinese(text) and len(text) >= 2:
                    receiver = self._caller_receiver_name(node.func)
                    if receiver and not self.in_logging_call:
                        is_exempt = caller_name in I18N_EXEMPT_CALLS
                        if not is_exempt and caller_name in {"__contains__", "get", "pop"}:
                            self._add_issue(
                                "I18N",
                                f"成员检测或字典查找中使用中文字面量「{text[:20]}」，建议使用枚举常量替代",
                                node.lineno,
                            )

    def _caller_receiver_name(self, func) -> str:
        if isinstance(func, ast.Attribute):
            val = func.value
            if isinstance(val, ast.Name):
                return val.id
            if isinstance(val, ast.Attribute):
                return _attr_chain(val)
        return ""

    def _check_lock_acquire_sequence(self, node: ast.Call, caller_name: str, caller_full: str):
        if caller_name not in LOCK_METHODS:
            return
        if not self._is_lock_acquire_on_var(node):
            return

        lock_name = self._get_lock_target_name(node.func)
        if lock_name:
            if lock_name not in self._current_function_locks:
                self._current_function_locks.append(lock_name)

    def _is_lock_acquire_on_var(self, node: ast.Call) -> bool:
        if not isinstance(node.func, ast.Attribute):
            return False
        val = node.func.value
        lock_name = self._get_lock_target_name(node.func)
        if lock_name and (lock_name in self._lock_vars or any(
            kw in lock_name.lower() for kw in ["lock", "mutex", "semaphore", "_lock", "rwlock"]
        )):
            return True
        if isinstance(val, ast.Name) and any(
            kw in val.id.lower() for kw in ["lock", "mutex", "semaphore", "rwlock", "_lock"]
        ):
            return True
        return False

    def _get_lock_target_name(self, func) -> str:
        if isinstance(func, ast.Attribute):
            val = func.value
            if isinstance(val, ast.Name):
                return val.id
            if isinstance(val, ast.Attribute):
                return _attr_chain(val)
        return ""

    def _check_lock_ordering(self, func_node: ast.FunctionDef):
        if len(self._current_function_locks) < 2:
            return

        sequences = self._lock_acquire_sequences
        current_seq = self._current_function_locks
        func_qname = f"{self.current_class}.{func_node.name}" if self.current_class else func_node.name

        if not sequences:
            sequences.append((func_qname, current_seq, func_node.lineno))
            return

        canonical = None
        for existing_func, existing_seq, existing_line in sequences:
            if len(existing_seq) >= 2 and len(current_seq) >= 2:
                for i, l1 in enumerate(existing_seq):
                    for j, l2 in enumerate(existing_seq):
                        if i < j:
                            try:
                                ci = current_seq.index(l1)
                                cj = current_seq.index(l2)
                                if ci > cj:
                                    self._add_issue(
                                        "DEADLOCK",
                                        f"锁获取顺序不一致！在 {existing_func} (L{existing_line}) 中按 {l1}→{l2} 顺序获取，"
                                        f"但在 {func_qname} (L{func_node.lineno}) 中按 {l2}→{l1} 顺序获取，可能导致死锁",
                                        func_node.lineno,
                                    )
                                    return
                            except ValueError:
                                pass
            if set(existing_seq) == set(current_seq) and canonical is None:
                canonical = existing_seq

        sequences.append((func_qname, current_seq, func_node.lineno))

    def _check_pool_shutdown_call(self, node: ast.Call, caller_name: str, caller_full: str):
        if caller_name not in POOL_SHUTDOWN_METHODS:
            return
        target = self._get_lock_target_name(node.func)
        if target and target in self._pool_vars:
            self._pool_shutdown.add(target)
        if target:
            for pool_var in self._pool_vars:
                if pool_var.endswith("." + target.split(".")[-1]) or target == pool_var:
                    self._pool_shutdown.add(pool_var)

    def _check_pool_shutdown_in_function(self, func_node: ast.FunctionDef):
        if self.in_test_function:
            return

        for pool_var in self._pool_vars:
            if pool_var in self._pool_context_managed:
                continue
            if pool_var in self._pool_shutdown:
                continue

            pool_short = pool_var.split(".")[-1]
            is_local_pool = not pool_var.startswith("self.")

            if is_local_pool:
                self._add_issue(
                    "LEAK",
                    f"线程池/进程池 {pool_short} 未调用 shutdown()/close() 且未使用 with 语句管理，"
                    f"可能导致资源泄漏",
                    func_node.lineno,
                )
