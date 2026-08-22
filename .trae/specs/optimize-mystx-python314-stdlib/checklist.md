# Checklist

- [x] 学习笔记已形成，含至少六条「stdlib 能力 → mystx 落点 → 优化动作/诚实记录」映射，并引用对应 wiki 章节事实
- [x] 优化前基线已采集：测试通过数（2 项均 FAIL）、覆盖率（0%）、lint 告警数（src 预置 E302/W293/W292）、`hasattr(__dict__)`（True）、`sys.getsizeof`、缺 `myst_nb` 时的导入表现（`ModuleNotFoundError`）
- [x] `ConfigManager` / `MySTX` 已启用 `slots=True`，实例化后 `hasattr(instance, "__dict__")` 为 `False`
- [x] `ConfigManager.logger` 已修正为 `Optional[...]`，构造签名与 `__post_init__` 赋值语义不变
- [x] `field(doc=)` 未用于代码中（`requires-python` 虽为 `>=3.14`，但字段已由类 docstring 覆盖），已作为条件性未来落点记录于学习笔记
- [x] `config.py` / `theme.py` 异常路径已用 `exc_info=True` 输出完整回溯并保留异常链（bare `raise` 保留 `__context__`）
- [x] `requires-python`（`>=3.14`）与 `tomllib` 实际依赖、README 运行环境声明（3.14+）一致
- [x] `mystx/__init__.py` 已惰性加载 `myst_nb`，缺 `myst-nb` 时 `import mystx` 不抛 `ModuleNotFoundError`
- [x] `version_switcher.py` 已移除未使用 import 与死注释；`ext/__init__.py` 已补 docstring
- [x] 单元测试已从 2 项扩展到 26 项，覆盖指令/配置合并/主题解析/版本推断/可选 import，全绿
- [x] `src/mystx` 核心逻辑（指令/配置合并/主题解析/版本推断）语句覆盖率不低于 80%（核心模块 83%~100%）
- [x] 既有公开接口（`setup`/`MySTX`/`ConfigManager`/四条指令）签名与语义不变
- [x] 优化前后对比记录已生成，逐项含「优化前 / 优化后 / 变化量」
- [x] 全量 `pytest` 通过、测试文件 lint 无新增告警