# OKF 工具链实现 Checklist

## 脚手架与构建

- [x] 1. `tools/okf/pyproject.toml` 存在，`requires-python >=3.14.6`，运行时 `dependencies` 为空列表（零运行时依赖）
- [x] 2. `tools/okf/pyproject.toml` 入口脚本 `okf = "okf.__main__:main"`，`[build-system]` 指定 scikit-build-core
- [x] 3. `tools/okf/CMakeLists.txt` 存在，采用纯 Python `wheel` 导出（`install(TARGETS ...)` 留空供后续 C/C++ 扩展），与 `tools/xs/CMakeLists.txt` 模式一致
- [x] 4. `tools/README.md` 已登记 `okf/` 子项目

## Dataclass 数据模型

- [x] 5. `TrustTier` 枚举定义正确（`UNVERIFIED` / `MACHINE_CONFIRMED` / `HUMAN_REVIEWED`）
- [x] 6. `Concept` dataclass 使用 `frozen=True`，字段完整（`path`/`type`/`title`/`description`/`resource`/`tags`/`frontmatter`/`body`/`extra`）
- [x] 7. `Bundle` dataclass 使用 `frozen=True`，`concepts` 为 `dict[str, Concept]`
- [x] 8. `Source`/`UsageWindow`/`GeneratedInfo`/`VerificationEvent` 均为 `frozen=True` dataclass
- [x] 9. `ComputationParameter`/`Executor`/`Attester`/`AttestedComputation` 均为 `frozen=True` dataclass，`AttestedComputation.computation` 为 `str | None`（对应 OKF §10.2 `computation` 字段）
- [x] 10. `ConformanceReport` dataclass 使用 `frozen=True`，字段 `errors`/`warnings`/`bundle`
- [x] 11. 所有 dataclass 字段有完整类型注解，无手写 `__init__`/`__repr__`/`__eq__`

## 零运行时依赖验证

- [x] 12. 干净 Python 3.14.6 环境中 `pip install .` 安装成功，无 `ModuleNotFoundError`
- [x] 13. `okf --version` 正常运行（不依赖任何第三方运行时包）
- [x] 14. `okf` 运行时 `dependencies` 为空（scikit-build-core/CMake/Ninja 仅存在于 `build-system.requires`）

## Minimal YAML Frontmatter 解析器

- [x] 15. `parse_frontmatter(text)` 正确分离 `---` 包围的 YAML 与 body
- [x] 16. 支持标量（`type: Metric`）、列表（`tags: [a, b]`）、嵌套映射（`generated: {by: ..., at: ...}`）
- [x] 17. 不依赖 PyYAML 或任何第三方 YAML 库
- [x] 18. `type` 字段非空校验通过，缺失时抛出 `FrontmatterError`
- [x] 19. 未知键被保留在 `extra` 字典中，往返时不丢弃（§4.1 Extensions）

## Bundle 模型（§3）

- [x] 20. 遍历 Bundle 目录树正确分类：concept 文档、`index.md`、`log.md`（§3.1）
- [x] 21. 概念 ID 等于文件相对路径去掉 `.md` 后缀
- [x] 22. 保留文件名（`index.md`/`log.md`）不会被纳入 `Bundle.concepts`

## Provenance / Trust / Lifecycle（§5）

- [x] 23. `sources` 数组解析正确，含 `author`/`usage_count`/`last_modified` 及 `usage_window`
- [x] 24. `generated.by`/`generated.at` 正确解析
- [x] 25. 裸 `verified` 映射被解析为单元素列表（§5.2）
- [x] 26. 信任等级推导正确：无 `verified` → `UNVERIFIED`；仅非 `human:` → `MACHINE_CONFIRMED`；含 `human:<id>` → `HUMAN_REVIEWED`
- [x] 27. `status` 字段解析正确（`draft`/`stable`/`deprecated`）
- [x] 28. `stale_after` 保鲜判定正确（`today >= stale_after` → 过期，§5.5）

## Attested Computation（§10）

- [x] 29. `type: Attested Computation` 概念正确识别
- [x] 30. `runtime`/`parameters`（`name`/`type`/`required`）/`computation`/`executor`/`attester` 全部解析
- [x] 31. 内联计算（body `# Computation` 围栏）支持
- [x] 32. 文件式计算（`computation` 路径指向外部文件）支持

## 一致性校验（§11）

- [x] 33. 严格项：每个非保留 `.md` 有可解析 YAML frontmatter
- [x] 34. 严格项：每个 frontmatter 含非空 `type`
- [x] 35. 严格项：保留文件名遵守 §8/§9 结构
- [x] 36. 宽松项：缺失可选字段输出警告，不拒绝 Bundle
- [x] 37. 宽松项：未知 `type` 值输出提示，不拒绝 Bundle
- [x] 38. 宽松项：断链容忍，输出警告
- [x] 39. 宽松项：缺失 `index.md` 不拒绝 Bundle

## index.md 合成（§8）

- [x] 40. 生成的 `index.md` 无 frontmatter（根目录可携带 `okf_version` 除外）
- [x] 41. 条目引用概念链接并附 `description`
- [x] 42. 按小节分组组织内容

## log.md 合成（§9）

- [x] 43. 日期标题采用 ISO 8601 `YYYY-MM-DD`
- [x] 44. 条目按日期倒序排列

## 跨链接解析（§6）

- [x] 45. Bundle 相对绝对链接（`/` 开头）正确解析
- [x] 46. 相对链接正确解析
- [x] 47. 外部 URL 原样保留
- [x] 48. 断链不判定为错误，输出警告

## CLI 命令（argparse）

- [x] 49. `okf validate <path> [--strict]` 输出一致性报告，退出码反映严格项结果
- [x] 50. `okf init <path>` 创建 Bundle 骨架（`index.md`、`log.md`、`concepts/`、`playbooks/`、`references/`）
- [x] 51. `okf index <path>` 生成/更新 `index.md`
- [x] 52. `okf inspect <path> [concept_id]` 输出概念详情
- [x] 53. `okf trust <path> [concept_id]` 输出信任等级与保鲜状态
- [x] 54. `okf list <path> [--type X] [--tag Y]` 按条件过滤概念
- [x] 55. `okf --version` 输出版本信息
- [x] 56. CLI 使用 `argparse`（标准库），不依赖 typer/click

## 时空可组合性插件系统

### 可逆效应（DisposableList）

- [x] 57. `Disposable` 类型别名定义为 `Callable[[], None]`
- [x] 58. `EffectMeta` dataclass 使用 `frozen=True`，字段 `label` + `children`
- [x] 59. `DisposableList.push(dispose)` 返回可撤销函数（调用后从列表中移除）
- [x] 60. `DisposableList.clear()` 逆序返回所有 disposable（后注册先回收）

### 响应式协同效应（Context）

- [x] 61. `InjectSpec` dataclass 使用 `frozen=True`，字段 `name` + `config`
- [x] 62. `Plugin` dataclass 使用 `frozen=True`，字段 `name`/`apply`/`inject`/`provide`
- [x] 63. `Context.effect(execute, label)` 执行 `execute` 并将返回的逆函数收集进当前 Fiber 的 `_disposables`
- [x] 64. `Context.provide(name, impl)` 供应服务并返回逆函数（调用后撤销供应）
- [x] 65. `Context.get(name)` 从当前 Fiber 的 `_store` 获取服务实现
- [x] 66. `Context.plugin(plugin, config)` 创建 Fiber 并启动加载
- [x] 67. `Context.notify(names)` 遍历所有 Fiber，对 inject 命中者执行 `_check_impl` → `_refresh`

### 插件生命周期状态机

- [x] 68. `FiberState` 六态枚举定义正确（PENDING=0/LOADING=1/ACTIVE=2/UNLOADING=3/DISPOSED=4/FAILED=5）
- [x] 69. `Fiber._refresh()` 正确计算 epoch（依赖服务实现 uid 拼接，缺失依赖 → `INACTIVE` 哨兵）
- [x] 70. epoch 从 `INACTIVE` 变为有效值 → 触发 `_reload`（激活）
- [x] 71. epoch 从有效值变为 `INACTIVE` → 触发 `_unload`（停用）
- [x] 72. epoch 不变 → 保持当前状态（中性），不触发任何操作
- [x] 73. `Fiber._reload()` 执行 `plugin.apply(ctx, config)`，失败时捕获异常并记录 `_error`，进入 FAILED 状态
- [x] 74. `Fiber._unload()` 逆序执行 `_disposables.clear()` 中的所有逆函数
- [x] 75. FAILED 状态的 Fiber 在依赖重算后能从 FAILED → LOADING → ACTIVE 恢复

### 插件清单

- [x] 76. 7 个插件全部实现：`bundle_loader`/`conformance_checker`/`index_synthesizer`/`log_synthesizer`/`trust_deriver`/`link_resolver`/`cli_adapter`
- [x] 77. `bundle_loader` 提供 `bundle_accessor` 服务，加载 Bundle 目录树
- [x] 78. `conformance_checker` 依赖 `bundle_accessor`，提供 `conformance_report`
- [x] 79. Bundle 重新加载时，所有依赖 `bundle_accessor` 的插件自动 `_unload` → `_reload`

## Harness 架构与 Capability Seam

### Harness 设计

- [x] 80. `Harness` 类从 `pyproject.toml` 的 `[tool.okf.plugins]` 配置节读取插件清单
- [x] 81. 插件按拓扑排序（基于 `inject` 依赖声明）依次加载
- [x] 82. 所有插件 ACTIVE 后返回就绪的 `Context`，无需手动编排加载顺序
- [x] 83. 第三方实现可替换任意默认插件，只要保持相同的 `provide` 服务名

### Capability Seam 三角色

- [x] 84. `ServiceDefinition` dataclass 使用 `frozen=True`，字段 `name`/`interface`/`description`
- [x] 85. `ServiceProvider` dataclass 使用 `frozen=True`，字段 `definition`/`factory`/`config`
- [x] 86. `ServiceRegistry` 类支持 `define(definition)` 注册接口契约
- [x] 87. `ServiceRegistry` 类支持 `register(provider)` 注册具体实现
- [x] 88. Consumer 通过 `ctx.get(name)` 获取服务，只依赖接口契约，不依赖具体 Provider
- [x] 89. 切换 Provider 后，所有 Consumer 自动使用新实现（一次替换，全局生效）

### 事件系统五种分发模式

- [x] 90. `ctx.emit(name, *args)` 纯通知，同步执行所有监听器，无返回值
- [x] 91. `ctx.bail(name, *args)` 同步短路查找，第一个返回非 `None` 的结果获胜
- [x] 92. `ctx.parallel(name, *args)` 并行执行所有异步监听器，返回结果列表
- [x] 93. `ctx.serial(name, *args)` 串行执行，第一个返回非 `None` 的结果获胜
- [x] 94. `ctx.waterfall(name, *args)` 中间件链，必须调用 `next()` 继续，否则短路
- [x] 95. `ctx.on(event, handler)` 返回 `Disposable`，自动绑定到当前 Fiber 的 `_disposables`
- [x] 96. 插件卸载时，所有通过 `ctx.on()` 注册的事件监听器自动移除

### 插件配置清单

- [x] 97. `pyproject.toml` 的 `[tool.okf.plugins]` 配置节声明了 7 个插件
- [x] 98. CLI 启动时通过 `Harness` 自举加载，而非硬编码 CLI 入口

## 测试覆盖

- [x] 99. `test_models.py` 覆盖 dataclass 不可变性、默认值、类型安全
- [x] 100. `test_frontmatter.py` 覆盖 YAML 解析、`type` 校验、未知键保留
- [x] 101. `test_loader.py` 覆盖 Bundle 加载与文件分类
- [x] 102. `test_trust.py` 覆盖信任家族解析、等级推导、保鲜判定
- [x] 103. `test_attested.py` 覆盖 Attested Computation 契约解析
- [x] 104. `test_conformance.py` 覆盖一致性校验（含 §附录 A 收入表等价样例）
- [x] 105. `test_synthesis.py` 覆盖 index/log 生成与解析
- [x] 106. `test_links.py` 覆盖链接解析与断链检测
- [x] 107. `test_disposable.py` 覆盖 DisposableList 逆序回收、EffectMeta 树结构
- [x] 108. `test_plugin.py` 覆盖 FiberState 六态迁移、epoch 激活/停用/中性、reload/unload 逆序回收
- [x] 109. `test_context.py` 覆盖 Context 依赖注入、notify 响应式通知、插件装配端到端
- [x] 110. `test_service.py` 覆盖 ServiceDefinition 注册、ServiceProvider 多实现切换、Consumer 透明替换
- [x] 111. `test_events.py` 覆盖五种分发模式（emit/bail/parallel/serial/waterfall）、事件监听自动绑定/卸载
- [x] 112. `test_harness.py` 覆盖 pyproject.toml 配置加载、拓扑排序、自举端到端
- [x] 113. `test_cli.py` 覆盖 CLI 命令端到端集成
- [x] 114. 关键模块（frontmatter 解析、一致性校验、插件系统运行时、事件系统）测试覆盖率 ≥90%
- [x] 115. 整体测试覆盖率 ≥80%

## 项目规范

- [x] 116. 代码通过 ruff + black + isort 检查（行宽 120，py314）
- [x] 117. `pyproject.toml` 遵循 PEP 621 标准格式
- [x] 118. 文档使用 Sphinx + MyST 构建无错误
- [x] 119. `xs list` 能正确列出 `tools/okf/`