"""并发安全检查常量定义。"""

DIMENSIONS = {
    "TIMEOUT": {
        "code": "CC-TIMEOUT",
        "name": "超时检查",
        "description": "锁/等待/阻塞操作必须设置超时，防止死锁",
        "default_severity": "error",
    },
    "IDEMPOTENT": {
        "code": "CC-IDEMPOTENT",
        "name": "幂等检查",
        "description": "列表追加/状态更新操作应有去重或幂等保护",
        "default_severity": "error",
    },
    "BOUNDARY": {
        "code": "CC-BOUNDARY",
        "name": "边界检查",
        "description": "热路径中避免O(n)线性查找，使用dict/set实现O(1)",
        "default_severity": "warn",
    },
    "DEFENSIVE": {
        "code": "CC-DEFENSIVE",
        "name": "防御检查",
        "description": "可变默认参数、外部传入可变对象需做防御性拷贝",
        "default_severity": "warn",
    },
    "CONFIG": {
        "code": "CC-CONFIG",
        "name": "配置检查",
        "description": "并发阈值/超时时间/重试次数应可配置，而非硬编码",
        "default_severity": "warn",
    },
    "I18N": {
        "code": "CC-I18N",
        "name": "国际化检查",
        "description": "业务逻辑中避免直接匹配中文字符串，应使用枚举或常量",
        "default_severity": "info",
    },
    "DEADLOCK": {
        "code": "CC-DEADLOCK",
        "name": "死锁顺序检查",
        "description": "多锁获取必须遵循全局一致的顺序，防止死锁",
        "default_severity": "error",
    },
    "LEAK": {
        "code": "CC-LEAK",
        "name": "资源泄漏检查",
        "description": "线程池/进程池必须正确shutdown，防止资源泄漏",
        "default_severity": "error",
    },
}

LOCK_METHODS = {"acquire", "acquire_lock", "lock"}
WAIT_METHODS = {"wait", "join", "get", "get_nowait", "put", "put_nowait"}
ASYNC_WAIT = {"wait_for", "wait", "gather", "sleep"}

MUTABLE_TYPES = {"list", "dict", "set"}

CHINESE_CHAR_RANGE = ("\u4e00", "\u9fff")

LOGGING_CALLS = {"debug", "info", "warning", "warn", "error", "critical", "exception", "log", "_log", "print"}

CONCURRENT_MODULES = {
    "threading", "multiprocessing", "asyncio", "concurrent.futures",
    "queue", "multiprocessing.Queue",
}

LOCK_CLASSES = {"Lock", "RLock", "Semaphore", "BoundedSemaphore", "Condition", "Event"}

POOL_CLASSES = {
    "ThreadPoolExecutor", "ProcessPoolExecutor", "ThreadPool", "ProcessPool",
    "Pool", "ThreadPool",
}

POOL_SHUTDOWN_METHODS = {"shutdown", "close", "stop", "terminate"}

I18N_EXEMPT_CALLS = {
    "print", "debug", "info", "warning", "warn", "error", "critical",
    "exception", "log", "_log", "logger",
    "__", "gettext", "ngettext", "pgettext",
    "raise", "AssertionError", "ValueError", "Exception",
}

I18N_DICT_METHODS = {"get", "pop", "__getitem__", "__setitem__", "__contains__", "setdefault"}
