# Tasks

- [x] Task 1: 创建子项目脚手架与构建配置
  - [x] SubTask 1.1: 创建 `tools/okf/` 目录结构（`pyproject.toml`、`CMakeLists.txt`、`src/okf/`、`tests/`、`docs/`），采用 scikit-build-core + CMake 打包，与 `tools/xs` 模式一致
  - [x] SubTask 1.2: 配置 `pyproject.toml`（`requires-python >=3.14.6`，运行时 `dependencies` 为空列表——零运行时依赖，入口脚本 `okf = "okf.__main__:main"`，`[build-system]` 指定 scikit-build-core）
  - [x] SubTask 1.3: 编写 `CMakeLists.txt` 采用纯 Python `wheel` 导出（`install(TARGETS ...)` 留空供后续 C/C++ 扩展），当前无原生模块
  - [x] SubTask 1.4: 更新 `tools/README.md`，登记 `okf/` 子项目

- [x] Task 2: 实现 Dataclass 数据模型（`models.py`）
  - [x] SubTask 2.1: 定义 `TrustTier` 枚举（`UNVERIFIED` / `MACHINE_CONFIRMED` / `HUMAN_REVIEWED`）
  - [x] SubTask 2.2: 定义 `Concept` dataclass（`frozen=True`，字段：`path`、`type`、`title`、`description`、`resource`、`tags`、`frontmatter`、`body`、`extra`）
  - [x] SubTask 2.3: 定义 `Bundle` dataclass（`frozen=True`，字段：`root`、`concepts`、`indices`、`logs`）
  - [x] SubTask 2.4: 定义 `Source` / `UsageWindow` / `GeneratedInfo` / `VerificationEvent` dataclass（`frozen=True`）
  - [x] SubTask 2.5: 定义 `ComputationParameter` / `Executor` / `Attester` / `AttestedComputation` dataclass（`frozen=True`）
  - [x] SubTask 2.6: 定义 `ConformanceReport` dataclass（`frozen=True`，字段：`errors`、`warnings`、`bundle`）

- [x] Task 3: 实现最小 YAML Frontmatter 解析器（`frontmatter.py`）
  - [x] SubTask 3.1: 实现 `parse_frontmatter(text: str) -> tuple[dict, str]`：用正则匹配 `---` 分隔符，将 YAML 子集解析为 `dict`（支持标量、列表、嵌套映射，不依赖 PyYAML）
  - [x] SubTask 3.2: 实现 `parse_concept(filepath: Path) -> Concept`：读取 `.md` 文件，分离 frontmatter 与 body，构建 `Concept` 实例
  - [x] SubTask 3.3: 实现 `type` 字段必填校验（非空 str），缺失时抛出 `FrontmatterError`
  - [x] SubTask 3.4: 实现未知键保留逻辑——`extra` 字典存储所有未在 `Concept` 显式字段中声明的键（§4.1 Extensions）

- [x] Task 4: 实现 Bundle 加载器（`loader.py`）
  - [x] SubTask 4.1: 实现 `load_bundle(root: Path) -> Bundle`：遍历目录树，分类 `index.md`/`log.md`（§3.1 保留文件）与其他 `.md`（概念文件）
  - [x] SubTask 4.2: 实现概念 ID 计算（相对路径去掉 `.md` 后缀），`Bundle.concepts` 为 `dict[str, Concept]` 映射
  - [x] SubTask 4.3: 递归加载子目录，支持嵌套 Bundle 结构

- [x] Task 5: 实现 Provenance / Trust / Lifecycle 解析（`trust.py`）
  - [x] SubTask 5.1: `parse_sources(frontmatter: dict) -> tuple[list[Source], UsageWindow | None]`：解析 `sources` 数组与 `usage_window`
  - [x] SubTask 5.2: `parse_verification(frontmatter: dict) -> tuple[GeneratedInfo | None, list[VerificationEvent]]`：解析 `generated` 与 `verified`（裸映射→单元素列表，§5.2）
  - [x] SubTask 5.3: `derive_trust_tier(concept: Concept) -> TrustTier`：信任等级推导（§5.3）
  - [x] SubTask 5.4: `is_stale(concept: Concept, today: date | None = None) -> bool`：保鲜判定（`today >= stale_after`，§5.5）

- [x] Task 6: 实现 Attested Computation 解析（`attested.py`）
  - [x] SubTask 6.1: 识别 `type == "Attested Computation"` 概念
  - [x] SubTask 6.2: 解析 `runtime`/`parameters`（`name`/`type`/`required`）/`computation`/`executor`/`attester` 字段
  - [x] SubTask 6.3: 支持内联计算（正则匹配 body 中的 `# Computation` 代码围栏）与文件式计算（`computation` 路径指向外部文件）

- [x] Task 7: 实现一致性校验（`conformance.py`）
  - [x] SubTask 7.1: 实现 `validate_strict(bundle: Bundle) -> list[str]`：严格项检查——每个非保留 `.md` 有可解析 YAML frontmatter + 含非空 `type` + 保留文件名遵守 §8/§9 结构
  - [x] SubTask 7.2: 实现 `validate_lenient(bundle: Bundle) -> list[str]`：宽松项检查——缺失可选字段、未知 `type`、未知扩展键、断链、缺失 `index.md` 等输出警告
  - [x] SubTask 7.3: 实现 `check_bundle(bundle: Bundle) -> ConformanceReport`：汇总严格项与宽松项，返回 `ConformanceReport`

- [x] Task 8: 实现 `index.md` 与 `log.md` 合成（`synthesis.py`）
  - [x] SubTask 8.1: 实现 `generate_index(directory: Path, concepts: list[Concept]) -> str`：按 §8 结构生成 `index.md`（无 frontmatter，按小节分组，条目引用概念链接并附 `description`）
  - [x] SubTask 8.2: 实现 `parse_log(filepath: Path) -> dict[date, list[str]]`：解析 `log.md`（§9，ISO 日期标题，粗体动词为约定）
  - [x] SubTask 8.3: 实现 `generate_log(entries: dict[date, list[str]]) -> str`：生成 `log.md`（日期倒序）

- [x] Task 9: 实现跨链接解析（`links.py`）
  - [x] SubTask 9.1: 实现 `parse_links(body: str, bundle_root: Path) -> list[tuple[str, Path | str | None]]`：用正则提取 Markdown 链接，解析 Bundle 相对绝对路径（`/` 开头）、相对路径、外部 URL
  - [x] SubTask 9.2: 实现 `check_broken_links(links, bundle: Bundle) -> list[str]`：检测断链，输出警告（不判定为错误，§6.1）

- [x] Task 10: 实现时空可组合性插件系统运行时
  - [x] SubTask 10.1: 实现 `disposable.py`：`Disposable` 类型别名、`EffectMeta` dataclass（`label` + `children`）、`DisposableList` 类（`push` 返回可撤销函数、`clear` 逆序返回）
  - [x] SubTask 10.2: 实现 `plugin.py`：`InjectSpec` dataclass、`Plugin` dataclass（`name`/`apply`/`inject`/`provide`）、`FiberState` 六态枚举、`Fiber` 类（`state`/`inject`/`_disposables`/`epoch`/`_error`）
  - [x] SubTask 10.3: 实现 `context.py`：`Context` 类（`effect`/`provide`/`get`/`plugin`/`notify`/`get_effects`）
  - [x] SubTask 10.4: 实现 `Fiber.effect()` 可逆效应注册（`execute` 返回逆函数，收集进 `_disposables`，`_unload` 逆序回收）
  - [x] SubTask 10.5: 实现 `Fiber._refresh()` epoch 计算（依赖服务实现 uid 拼接，缺失依赖 → `INACTIVE` 哨兵）
  - [x] SubTask 10.6: 实现 `Context.notify()` 响应式通知（遍历插件检查 inject 命中，`_check_impl` → `_refresh` → 激活/停用/中性）
  - [x] SubTask 10.7: 实现 `Fiber._reload()` / `Fiber._unload()`（加载执行 `apply`，失败捕获记录 `_error`；卸载执行 `_disposables.clear()`）
  - [x] SubTask 10.8: 实现 Capability Seam 三角色抽象（`service.py`）：`ServiceDefinition` dataclass、`ServiceProvider` dataclass、`ServiceRegistry` 类（`define`/`register`/`lookup`），Consumer 通过 `ctx.get(name)` 获取服务实例
  - [x] SubTask 10.9: 实现事件系统五种分发模式（`events.py`）：`Context.emit`（纯通知）、`Context.bail`（同步短路查找）、`Context.parallel`（并行扇出）、`Context.serial`（串行短路）、`Context.waterfall`（中间件链），均通过 `ctx.on(event, handler)` 注册监听器
  - [x] SubTask 10.10: 实现 Harness 自举（`harness.py`）：`Harness` 类，从 `pyproject.toml` 的 `[tool.okf.plugins]` 配置节读取插件清单，按拓扑排序依次加载插件，所有插件 ACTIVE 后返回就绪的 `Context`
  - [x] SubTask 10.11: 实现插件清单 7 个插件（`bundle_loader`/`conformance_checker`/`index_synthesizer`/`log_synthesizer`/`trust_deriver`/`link_resolver`/`cli_adapter`），每个插件均通过 `pyproject.toml` 的 `[tool.okf.plugins]` 配置节声明式装配

- [x] Task 11: 实现 CLI 命令（`__main__.py` + `cli.py`）
  - [x] SubTask 11.1: 创建 `src/okf/__main__.py` 入口（`from okf.cli import main; main()`）
  - [x] SubTask 11.2: 创建 `src/okf/cli.py`，使用 `argparse` 实现主命令与子命令路由（`validate` / `init` / `index` / `inspect` / `trust` / `list`）
  - [x] SubTask 11.3: 实现 `okf validate <path> [--strict]`（通过 `Context` 装配 `bundle_loader` + `conformance_checker`，输出一致性报告，退出码反映严格项结果）
  - [x] SubTask 11.4: 实现 `okf init <path>`（创建 Bundle 骨架：`index.md`、`log.md`、`concepts/`、`playbooks/`、`references/`）
  - [x] SubTask 11.5: 实现 `okf index <path>`（通过 `index_synthesizer` 插件生成/更新 `index.md`）
  - [x] SubTask 11.6: 实现 `okf inspect <path> [concept_id]`（输出概念详情，含 frontmatter 与 body 摘要）
  - [x] SubTask 11.7: 实现 `okf trust <path> [concept_id]`（通过 `trust_deriver` 插件输出信任等级与保鲜状态）
  - [x] SubTask 11.8: 实现 `okf list <path> [--type X] [--tag Y]`（按条件过滤概念列表）

- [x] Task 12: 编写测试
  - [x] SubTask 12.1: 创建测试 fixtures（`tests/fixtures/` 下构造符合 OKF v0.2 的样本 Bundle，含 §附录 A 收入表等价样例）
  - [x] SubTask 12.2: 编写 `test_models.py`（dataclass 不可变性、默认值、类型安全）
  - [x] SubTask 12.3: 编写 `test_frontmatter.py`（YAML 解析、`type` 校验、未知键保留）
  - [x] SubTask 12.4: 编写 `test_loader.py`（Bundle 加载与文件分类）
  - [x] SubTask 12.5: 编写 `test_trust.py`（信任家族解析、等级推导、保鲜判定）
  - [x] SubTask 12.6: 编写 `test_attested.py`（Attested Computation 契约解析）
  - [x] SubTask 12.7: 编写 `test_conformance.py`（一致性校验回归，含严格/宽松模式）
  - [x] SubTask 12.8: 编写 `test_synthesis.py`（index/log 生成与解析）
  - [x] SubTask 12.9: 编写 `test_links.py`（链接解析与断链检测）
  - [x] SubTask 12.10: 编写 `test_disposable.py`（DisposableList 逆序回收、EffectMeta 树结构）
  - [x] SubTask 12.11: 编写 `test_plugin.py`（FiberState 六态迁移、epoch 激活/停用/中性、reload/unload 逆序回收）
  - [x] SubTask 12.12: 编写 `test_context.py`（Context 依赖注入、notify 响应式通知、插件装配端到端）
  - [x] SubTask 12.13: 编写 `test_service.py`（ServiceDefinition 注册、ServiceProvider 多实现切换、Consumer 透明替换）
  - [x] SubTask 12.14: 编写 `test_events.py`（五种分发模式覆盖率：emit/bail/parallel/serial/waterfall、事件监听自动绑定/卸载）
  - [x] SubTask 12.15: 编写 `test_harness.py`（pyproject.toml 配置加载、拓扑排序、自举端到端）
  - [x] SubTask 12.16: 编写 `test_cli.py`（CLI 命令端到端集成测试）

- [x] Task 13: 零运行时依赖验证
  - [x] SubTask 13.1: 在干净 Python 3.14.6 环境中 `pip install .` 安装，确认无 `ModuleNotFoundError`
  - [x] SubTask 13.2: 运行 `okf --version` 确认正常输出
  - [x] SubTask 13.3: 验证 `okf` 运行时无任何第三方依赖（scikit-build-core/CMake/Ninja 仅存在于 `build-system.requires`，不进入运行时）

# Task Dependencies

- Task 2 → Task 1（数据模型依赖脚手架）
- Task 3 → Task 2（Frontmatter 解析依赖 `Concept` dataclass）
- Task 4 → Task 2, Task 3（Bundle 加载依赖模型与解析器）
- Task 5 → Task 2, Task 3（Trust 解析依赖模型与 frontmatter）
- Task 6 → Task 2, Task 3（Attested Computation 依赖 Concept 解析）
- Task 7 → Task 4, Task 5, Task 6（一致性校验依赖所有核心模块）
- Task 8 → Task 4（index/log 合成依赖 Bundle 加载）
- Task 9 → Task 4（链接解析依赖 Bundle 模型）
- Task 10 → Task 2, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9（插件系统运行时封装所有核心能力为可插拔插件）
- Task 11 → Task 10（CLI 命令通过 Context 装配插件）
- Task 12 → Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11（测试依赖所有实现）
- Task 13 → Task 11（零依赖验证依赖 CLI 就绪）
- Task 2, Task 3 可并行开发（无相互依赖）
- Task 5, Task 6, Task 8, Task 9 可并行开发（均依赖 Task 2+3，但彼此无依赖）