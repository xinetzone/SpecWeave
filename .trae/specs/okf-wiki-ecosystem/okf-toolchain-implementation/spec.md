---
title: "OKF 工具链实现"
status: "draft"
---

# OKF 工具链实现 Spec

## Why

Open Knowledge Format（OKF）v0.2 是 Google Cloud 2026 年 6 月发布的开放知识表示规范，定位为「AI 时代的 HTML」——一组带 YAML frontmatter、互相链接、可被 Git 管理的 Markdown 文件，人和 Agent 共读共写。当前 xuanspace 项目已有 OKF 规范文档（[SPEC.md](../../../../vendor/knowledge-catalog/okf/SPEC.md)）与学习教程（`okf-wiki`），但缺少一套与之对应的**可执行工具链**，用于在生产/消费 OKF Bundle 时完成校验、脚手架生成、索引/日志合成、信任等级推导等标准化操作。

本任务在 `projects/xuanspace/tools/` 下创建一个新的 OKF 工具链子项目，使 OKF v0.2 的规范约束从「文档约定」变为「可由工具强制校验与自动生成」的能力。

## What Changes

- 在 `projects/xuanspace/tools/` 下新建子项目 `tools/okf/`，实现 OKF v0.2 规范（`vendor/knowledge-catalog/okf/SPEC.md`）对应的工具链。
- 提供 Python 库包 `okf`（核心 API）与 CLI 命令 `okf`（入口 `okf.__main__:main`），遵循 OKF 自身「零依赖、纯文本」哲学：
  - **零运行时依赖**：仅使用 Python 3.14.6 标准库（`dataclasses`、`pathlib`、`argparse`、`re` 等），YAML frontmatter 解析使用内置最小子集解析器，不依赖 PyYAML/typer/rich 等第三方包
  - **数据模型**：所有核心类型（`Bundle`、`Concept`、`Source`、`AttestedComputation`、`VerificationEvent` 等）使用 `@dataclass` 定义，遵循不可变优先（`frozen=True`）原则
  - **构建**：scikit-build-core + CMake + Ninja（纯 Python 起步，`wheel` 导出与 `tools/xs` 一致；保留 CMake 扩展点，用于后续挂载 C/C++ 原生模块）
  - **CLI**：`argparse`（标准库），子命令通过 `argparse.add_subparsers()` 实现
  - **文档**：Sphinx + MyST（仅文档构建依赖，非运行时依赖）
- 新增能力（详见下方 ADDED Requirements）：
  1. Bundle 模型与文件分类（concept / `index.md` / `log.md`）
  2. Concept frontmatter 解析与校验（`type` 必填）
  3. provenance / trust / lifecycle 三大家族字段解析
  4. Attested Computation 契约解析
  5. 一致性校验（Conformance，§11，含宽松模式）
  6. `index.md` 合成（§8）
  7. `log.md` 合成（§9）
  8. 信任等级推导（§5.3）与保鲜判定（§5.5）
  9. 跨链接路径解析（§6）
- 新增命令行子命令：`validate`、`init`、`index`、`inspect`、`trust`、`list`。
- 更新 `tools/README.md` 与 `tools/xs` 的 workspace 感知（如 list 命令可正确识别新子项目），确保 `xs list` 能列出该工具。

## Impact

- **Affected specs**：新增能力（无既有能力被修改或移除）。
- **Affected code**：
  - 新增 `projects/xuanspace/tools/okf/`（含 `pyproject.toml`、`CMakeLists.txt`、`src/okf/`、`tests/`、`docs/`，scikit-build-core 构建，预留 C/C++ 扩展点）
  - 修改 `projects/xuanspace/tools/README.md`（登记新子项目）
- **参考规范**：`vendor/knowledge-catalog/okf/SPEC.md`（权威规范）、`okf-wiki`（学习教程）、`tools/xs/`（打包与 CLI 范式）、`pyproject.toml`（代码风格与依赖约束）。

---

## ADDED Requirements

### Requirement: OKF Bundle 模型与文件分类

系统 SHALL 能遍历一个 Bundle 目录树，将所有 `.md` 文件分类为「concept 文档」「`index.md` 保留文件」「`log.md` 保留文件」，并构建内存中的 Bundle 对象模型（含目录层级、文件路径、概念 ID）。

#### Scenario: 加载标准 Bundle
- **WHEN** 用户对包含 `index.md`、`log.md` 及多个子目录的 Bundle 调用加载 API 或 `okf inspect`
- **THEN** 系统返回 Bundle 对象，其中 `concepts` 集合排除所有名为 `index.md` 与 `log.md` 的文件（§3.1），概念 ID 等于文件相对路径去掉 `.md` 后缀

#### Scenario: 遇到保留文件名被误用为概念
- **WHEN** 目录树顶层出现以 `index.md` 或 `log.md` 命名但实为概念意图的文件
- **THEN** 系统将其归类为保留文件，不纳入概念集合，并在校验报告中记录提示（符合 §3.1 保留文件名定义）

---

### Requirement: Concept Frontmatter 解析与 `type` 校验

系统 SHALL 解析每个 concept 文件的 YAML frontmatter 与 markdown body，并强制校验 `type` 字段非空；`type` 不集中注册，系统 MUST 容错未知 `type` 值（视为通用概念）。

#### Scenario: frontmatter 含 `type` 且非空
- **WHEN** concept 文件 frontmatter 为 `type: Metric` 等非空字符串
- **THEN** 校验通过，概念对象携带可访问的 `type`、`title`、`description`、`resource`、`tags` 等字段

#### Scenario: 缺失或空 `type`
- **WHEN** concept 文件 frontmatter 缺少 `type` 或 `type` 为空字符串
- **THEN** 一致性校验失败并报告该文件（§11 规则 2）

#### Scenario: 未知扩展字段
- **WHEN** frontmatter 含生产者自定义的未知键
- **THEN** 系统 MUST 保留该未知键（往返时不舍弃），MUST NOT 因未知字段拒绝文档（§4.1 Extensions / §11）

---

### Requirement: Provenance / Trust / Lifecycle 字段解析

系统 SHALL 解析三个可选元数据家族：`sources`（来源与可信度信号）、`generated`/`verified`（信任）、`status`/`stale_after`（生命周期），并将裸 `verified` 映射视为单元素列表。

#### Scenario: 裸 `verified` 映射
- **WHEN** frontmatter 中 `verified: { by: human:alice, at: ... }` 以单个映射（非列表）形式出现
- **THEN** 系统 MUST 将其解析为单元素列表（§5.2）

#### Scenario: `sources` 携带可信度信号
- **WHEN** `sources` 条目包含 `author` / `usage_count` / `last_modified` 及顶层 `usage_window`
- **THEN** 系统正确读取这些信号字段，不计算或存储主观可信度评分（§5.1，评分由消费者按需推断）

#### Scenario: 缺失所有可选家族
- **WHEN** concept 仅含 `type`
- **THEN** 系统判定为完全符合规范（§11），且 MUST NOT 拒绝该文档（§5.3）

---

### Requirement: Attested Computation 契约解析

系统 SHALL 解析 `type: Attested Computation` 概念的契约字段 `runtime`、`parameters`、`computation`、`executor`、`attester`，并支持从 body 的 `# Computation` 围栏或 `computation` 指定文件两种方式加载计算逻辑。

#### Scenario: 内联计算
- **WHEN** Attested Computation 未指定 `computation` 路径，body 含 `# Computation` 围栏代码块
- **THEN** 系统将围栏内容解析为计算逻辑，并识别声明的 `parameters`（`name`/`type`/`required`）与 `executor.receipt`、`attester.resource`

#### Scenario: 文件式计算
- **WHEN** 概念通过 `computation: references/...` 指向文件
- **THEN** 系统按 §6.2 路径规则解析该路径，加载计算文件内容；`runtime` 字段决定了 `parameters` 的绑定语义

---

### Requirement: 一致性校验（Conformance）

系统 SHALL 实现 OKF v0.2 §11 定义的一致性判定，并在「严格模式」与「宽松模式」下输出可读报告。

#### Scenario: 严格项检查
- **WHEN** 消费者调用一致性校验
- **THEN** 系统检查：①每个非保留 `.md` 文件有可解析 YAML frontmatter；②每个 frontmatter 含非空 `type`；③保留文件名遵循 §8/§9 结构

#### Scenario: 宽松（宽容）项
- **WHEN** 存在缺失可选字段、未知 `type`、未知扩展键、断链、缺失 `index.md` 等情形
- **THEN** 系统 MUST NOT 判定 Bundle 不合规，而是输出警告级别提示（§11）

---

### Requirement: `index.md` 合成

系统 SHALL 能为任意目录（含 Bundle 根）生成或按需合成 `index.md`，实现渐进式披露。

#### Scenario: 生成 index.md
- **WHEN** 用户调用 `okf index` 或合成 API
- **THEN** 系统按 §8 结构生成 `index.md`：无 frontmatter（根目录可携带 `okf_version` 除外），主体按小节分组，条目引用概念链接并附 `description`

#### Scenario: 无 index.md 时按需合成
- **WHEN** 消费者读取一个目录但没有 `index.md`
- **THEN** 系统 MAY 动态扫描 frontmatter 合成等效目录视图（§8）

---

### Requirement: `log.md` 合成

系统 SHALL 支持生成或解析 `log.md` 变更历史（§9），日期标题采用 ISO 8601 `YYYY-MM-DD`，条目按日期倒序。

#### Scenario: 解析 log.md
- **WHEN** 用户读取 `log.md`
- **THEN** 系统解析日期分组与条目（粗体动词 `**Update**`/`**Creation**`/`**Deprecation**` 为约定而非强制）

---

### Requirement: 信任等级与保鲜判定

系统 SHALL 从 `verified` 字段推导信任等级（unverified / machine-confirmed / human-reviewed），并根据 `stale_after` 判定概念是否过期。

#### Scenario: 信任等级推导
- **WHEN** 概念无 `verified` → `unverified`；仅非 `human:` actor → `machine-confirmed`；含 `human:<id>` actor → `human-reviewed`
- **THEN** 系统按 §5.3 返回对应等级，且该等级仅为咨询信号，不构成访问控制

#### Scenario: 保鲜判定
- **WHEN** `today >= stale_after` 时
- **THEN** 系统判定概念「过期」，否则「新鲜」（§5.5，纯日期比较）

---

### Requirement: 跨链接路径解析

系统 SHALL 解析概念间链接（§6），支持 bundle 相对绝对路径（`/` 开头）、相对路径与原样 URL，并 MUST 容忍断链。

#### Scenario: bundle 相对绝对链接
- **WHEN** body 中出现 `[customers](/tables/customers.md)`
- **THEN** 系统按 Bundle 根目录解析路径

#### Scenario: 断链容忍
- **WHEN** 链接目标在 Bundle 中不存在
- **THEN** 系统 MUST NOT 判定格式错误（§6.1，断链表示知识尚未编写）

---

### Requirement: OKF CLI 命令

系统 SHALL 提供 `okf` 命令行入口，包含子命令 `validate`、`init`、`index`、`inspect`、`trust`、`list`，并提供 `--version`。

#### Scenario: 校验 Bundle
- **WHEN** 用户执行 `okf validate <path>`
- **THEN** 系统输出一致性报告（通过/失败项、警告项），退出码反映严格项结果

#### Scenario: 脚手架初始化
- **WHEN** 用户执行 `okf init <path>`
- **THEN** 系统创建 Bundle 骨架（根 `index.md`、`log.md` 及 `concepts/`、`playbooks/`、`references/` 目录）

#### Scenario: 列出概念
- **WHEN** 用户执行 `okf list <path> [--type X] [--tag Y]`
- **THEN** 系统列出符合筛选条件的概念（按 `type`/`tags` 过滤）

---

### Requirement: 打包与项目规范

系统 SHALL 作为 xuanspace monorepo 的 `tools/` 子项目交付，遵循项目的打包、代码风格与提交规范，同时坚持零运行时依赖原则。

#### Scenario: 打包
- **WHEN** 通过 scikit-build-core（CMake + Ninja）构建纯 Python 包
- **THEN** 产出 `okf-toolchain` 包，`requires-python >=3.14.6`，运行时 `dependencies` 为空列表（零运行时依赖），入口脚本 `okf = "okf.__main__:main"`，`CMakeLists.txt` 采用纯 Python `wheel` 导出，与 `tools/xs` 模式一致

#### Scenario: C/C++ 扩展预留
- **WHEN** 后续需要挂载 C/C++ 原生模块
- **THEN** 仅需在 `CMakeLists.txt` 中新增源文件与 `python_add_library`（或 `pybind11_add_module`）目标及其对应的 `wheel` 模块映射，无需更换构建后端（scikit-build-core 原生支持 Native extension）

#### Scenario: 零运行时依赖验证
- **WHEN** 在一个仅有 Python 3.14.6 标准库的干净环境中 `pip install` 本包
- **THEN** 安装成功且 `okf --version` 正常运行，不触发任何 `ModuleNotFoundError`（scikit-build-core/CMake/Ninja 仅作为构建期依赖存在于 `build-system.requires`，不进入运行时 `dependencies`）

#### Scenario: 代码风格
- **WHEN** 提交前运行 lint
- **THEN** 通过 ruff + black + isort（行宽 120，目标版本 py314）检查

#### Scenario: 文档构建
- **WHEN** 使用 Sphinx + MyST 构建 `docs/`
- **THEN** 成功生成 HTML 文档，MyST 语法正确渲染

---

### Requirement: Dataclass 数据模型设计

系统 SHALL 使用 Python `dataclasses` 模块定义所有核心领域类型，遵循不可变优先（`frozen=True`）、类型安全（完整类型注解）原则，避免手写 `__init__`/`__repr__`/`__eq__` 样板代码。

核心 dataclass 类型及其职责：

| 类型 | 职责 | 关键字段 |
|------|------|----------|
| `Bundle` | Bundle 目录树模型 | `root: Path`, `concepts: dict[str, Concept]`, `indices: list[Path]`, `logs: list[Path]` |
| `Concept` | 单个概念文档 | `path: Path`, `type: str`, `title: str`, `description: str`, `frontmatter: dict`, `body: str`, `extra: dict` |
| `Source` | 来源引用 | `resource: str`, `id: str`, `title: str`, `author: str`, `usage_count: int`, `last_modified: date` |
| `UsageWindow` | 使用窗口 | `from_date: date`, `to_date: date` |
| `GeneratedInfo` | 生成者信息 | `by: str`, `at: datetime` |
| `VerificationEvent` | 验证事件 | `by: str`, `at: datetime` |
| `ComputationParameter` | 计算参数 | `name: str`, `type: str`, `required: bool` |
| `Executor` | 执行器定义 | `resource: str`, `receipt: list[str]` |
| `Attester` | 验证器定义 | `resource: str` |
| `AttestedComputation` | 可验证计算 | `runtime: str`, `parameters: list[ComputationParameter]`, `computation: str \| None`, `executor: Executor`, `attester: Attester` |
| `TrustTier` | 信任等级枚举 | `UNVERIFIED \| MACHINE_CONFIRMED \| HUMAN_REVIEWED` |
| `ConformanceReport` | 校验报告 | `errors: list[str]`, `warnings: list[str]`, `bundle: Bundle` |

#### Scenario: dataclass 不可变语义
- **WHEN** 创建 `Concept(type="Metric", path=Path("metric.md"))` 后尝试修改 `concept.type = "Table"`
- **THEN** 抛出 `dataclasses.FrozenInstanceError`（`frozen=True` 保证不可变）

#### Scenario: 类型安全
- **WHEN** 对 `Source(resource="https://...", usage_count="not-a-number")` 运行 mypy
- **THEN** mypy 报告类型错误（`usage_count` 应为 `int`）

#### Scenario: 零样板代码
- **WHEN** 打印 `Concept(type="Metric", path=Path("metric.md"))`
- **THEN** 自动获得可读的 `__repr__`：`Concept(type='Metric', path=WindowsPath('metric.md'), title='', ...)`

---

### Requirement: 时空可组合性架构（Cordis 启发）

系统 SHALL 借鉴 Cordis 框架的「时空可组合性」范式，将 OKF 工具链的核心能力（校验、合成、检查、信任推导）构建为**可插拔的插件系统**，每个插件作为一个独立的「组件」参与动态组合，遵循以下四个核心机制。

#### 1. 时间可组合性：可逆效应（Revertible Effects）

系统 SHALL 提供 `okf.effect()` API，使每个操作（Bundle 加载、校验、合成等）都返回一个 `Disposable`（逆函数），运行时自动追踪并逆序回收。

**核心抽象**：

```python
from dataclasses import dataclass, field
from collections.abc import Callable

# 逆函数：撤销一次上下文变换
Disposable = Callable[[], None]

@dataclass(frozen=True)
class EffectMeta:
    """效应元信息，用于调试与可观测性。"""
    label: str
    children: list["EffectMeta"] = field(default_factory=list)


class DisposableList:
    """逆序回收的效应列表，对应 Cordis 的 `DisposableList`。

    后注册的效应先回收（栈式语义），对应论文「扭转组合」中
    逆变换 g2∘g1 的逆序累积规则：(f1,g1)∘(f2,g2) = (f1∘f2, g2∘g1)。
    """
    def push(self, dispose: Disposable) -> Disposable: ...
    def clear(self) -> list[Disposable]:  # 逆序返回所有 disposable
        ...
```

#### Scenario: 效应注册与逆序回收
- **WHEN** 插件 A 注册 effect `e1`（返回逆 `d1`），随后插件 B 注册 effect `e2`（返回逆 `d2`）
- **THEN** 卸载时先执行 `d2` 再执行 `d1`（后注册先回收），`DisposableList.clear()` 返回 `[d2, d1]`

#### Scenario: 效应元信息可观测
- **WHEN** 运行 `ctx.get_effects()`
- **THEN** 返回效应树（`list[EffectMeta]`），每个节点含 `label` 与子效应列表，用于调试与监控

---

#### 2. 空间可组合性：响应式协同效应（Reactive Coeffects）

系统 SHALL 提供 `@inject` 装饰器与 `provide`/`get` API，使插件**声明式地**表达对 Bundle 访问器、校验器、合成器等服务的依赖，运行时**响应式地**自动满足、通知与更新。

**核心抽象**：

```python
@dataclass(frozen=True)
class InjectSpec:
    """依赖声明：插件需要哪些服务。"""
    name: str
    config: dict | None = None


@dataclass(frozen=True)
class Plugin:
    """插件定义，对应 Cordis 的 `Plugin` 三种形态之一。"""
    name: str
    apply: Callable[["Context", dict], None]
    inject: list[InjectSpec] = field(default_factory=list)
    provide: list[str] = field(default_factory=list)


class Context:
    """统一上下文，同时承载效应追踪与服务注册。

    对应 Cordis 的 `Context`——论文「统一上下文类型」的实现。
    """
    def effect(self, execute: Callable[[], Disposable | list[Disposable]], label: str = "") -> Disposable: ...
    def provide(self, name: str, impl: object) -> Disposable: ...
    def get(self, name: str) -> object: ...
    def plugin(self, plugin: Plugin, config: dict | None = None) -> None: ...
    def notify(self, names: list[str]) -> None: ...
```

**响应式通知流程**（对应 Cordis 的 `ReflectService.notify`）：

```
服务变更 (provide/set)
  → notify(names)                    # 遍历所有插件
    → 对每个插件检查 inject 是否包含变更的服务名
      → _check_impl(name)            # 重新检查服务是否仍可用
      → _refresh()                   # 重新计算 epoch，触发激活/停用/中性
```

#### Scenario: 插件声明依赖并自动激活
- **WHEN** 插件 P 声明 `inject = [InjectSpec("bundle_accessor")]`，上下文尚未提供 `bundle_accessor`
- **THEN** 插件处于 PENDING 状态（依赖未满足）；当 `ctx.provide("bundle_accessor", impl)` 被调用后，`notify` 自动触发 `_refresh`，插件进入 ACTIVE 状态

#### Scenario: 依赖失效自动停用
- **WHEN** 已激活的插件 P 依赖的服务 `bundle_accessor` 被撤销（dispose 执行）
- **THEN** `notify` 检测到实现不可用，插件自动进入 UNLOADING → PENDING 状态

#### Scenario: 无关变化保持中性
- **WHEN** 插件 P 依赖 `bundle_accessor`，但上下文变更的是 `link_resolver` 服务
- **THEN** `_refresh` 计算 epoch 未变，插件保持 ACTIVE 状态（中性）

---

#### 3. 插件生命周期状态机

系统 SHALL 为每个插件（Plugin 实例）维护一个六态状态机，与 Cordis 的 `Fiber` 一致：

```
PENDING(0) → LOADING(1) → ACTIVE(2) → UNLOADING(3) → DISPOSED(4)
                         ↘ FAILED(5) ↗
```

| 状态 | 含义 | 触发条件 |
|------|------|----------|
| `PENDING` | 待激活 | 依赖未满足或尚未开始加载 |
| `LOADING` | 加载中 | `_reload()` 被调用，正在执行 `plugin.apply(ctx, config)` |
| `ACTIVE` | 已激活 | 执行成功，epoch 稳定 |
| `FAILED` | 加载失败 | `plugin.apply()` 抛出异常 |
| `UNLOADING` | 卸载中 | 依赖失效，`_unload()` 被调用，逆序执行所有 disposable |
| `DISPOSED` | 已销毁 | 彻底移除，不可恢复 |

**epoch 机制**（对应 Cordis 的 `Fiber._refresh`）：epoch 是插件所有依赖服务实现的唯一标识拼接字符串。当 epoch 从 `INACTIVE` 变为有效值 → 激活；从有效值变为 `INACTIVE` → 停用；epoch 不变 → 中性。

#### Scenario: 插件加载失败进入 FAILED 状态
- **WHEN** `plugin.apply()` 在执行过程中抛出异常
- **THEN** 插件进入 FAILED 状态，`_error` 记录异常信息，不影响其他插件

#### Scenario: 依赖重算后从 FAILED 恢复
- **WHEN** 处于 FAILED 状态的插件其依赖服务被重新提供
- **THEN** `notify` 触发 `_refresh`，epoch 重新计算，若依赖满足则进入 LOADING → ACTIVE

---

#### 4. 具体插件清单

OKF 工具链中，以下能力均以插件形式实现，共享统一的 Context 与生命周期：

| 插件名 | 注入依赖 | 提供服务 | 职责 |
|--------|---------|---------|------|
| `bundle_loader` | — | `bundle_accessor` | 加载 Bundle 目录树，分类概念文件，构建 `Bundle` 对象 |
| `conformance_checker` | `bundle_accessor` | `conformance_report` | 执行 OKF v0.2 §11 一致性校验，输出 `ConformanceReport` |
| `index_synthesizer` | `bundle_accessor` | `index_generator` | 按 §8 合成 `index.md` |
| `log_synthesizer` | `bundle_accessor` | `log_generator` | 按 §9 合成/解析 `log.md` |
| `trust_deriver` | `bundle_accessor` | `trust_analyzer` | 信任等级推导（§5.3）与保鲜判定（§5.5） |
| `link_resolver` | `bundle_accessor` | `link_analyzer` | 跨链接解析（§6）与断链检测 |
| `cli_adapter` | 所有上述服务 | — | CLI 命令适配层，将命令行参数转换为插件装配 |

#### Scenario: 最小插件装配
- **WHEN** 用户创建 `Context()`，依次 `ctx.plugin(BundleLoader(...))`、`ctx.plugin(ConformanceChecker(...))`
- **THEN** `bundle_loader` 先激活，其 `apply` 中 `ctx.provide("bundle_accessor", ...)` 触发 `notify`，`conformance_checker` 的依赖自动满足并激活，返回校验报告

#### Scenario: Bundle 重新加载时全链路自动响应
- **WHEN** 用户调用 `bundle_loader` 的 `reload(new_path)` 方法
- **THEN** `bundle_accessor` 被重新 `provide`，`notify` 遍历所有依赖它的插件（`conformance_checker`、`index_synthesizer`、`trust_deriver` 等），各插件自动 `_unload` → `_reload` 完成重新校验/合成/推导

---

### Requirement: Harness 架构与 Capability Seam（DeepSeek Harness 启发）

系统 SHALL 借鉴 DeepSeek Harness 的「一切皆插件」范式与 Capability Seam 三角色抽象，将 OKF 工具链设计为**一个无特权内核的 Harness**——工具链本身不预设任何特定实现，所有能力（Bundle 加载、校验、合成、信任推导、链接解析）均为地位平等的可插拔插件，通过 Capability Seam 实现「一次替换，全局生效」。

#### 1. Harness 设计原则

OKF 工具链作为一个 Harness（驾驭框架），与 DeepSeek Harness 遵循相同的设计哲学：

| 原则 | 说明 |
|------|------|
| **无特权内核** | 没有任何一个插件拥有高于其他插件的特权，`bundle_loader` 与 `conformance_checker` 地位平等 |
| **一切皆插件** | 所有能力——包括 Bundle 加载、校验、合成、CLI 适配——都是可插拔的插件，不与框架主干耦合 |
| **配置驱动** | 插件装配由 `pyproject.toml` 的 `[tool.okf.plugins]` 配置节驱动，而非硬编码在 CLI 入口中 |
| **可替换性** | 任何一个插件都可以被第三方实现替换，只要保持相同的 `provide` 服务名与接口契约 |

#### Scenario: 配置驱动插件装配
- **WHEN** `pyproject.toml` 中 `[tool.okf.plugins]` 配置节声明 `conformance_checker = "okf.plugins.conformance:ConformanceChecker"`
- **THEN** CLI 启动时自动从配置加载并装配该插件，无需修改 CLI 入口代码

#### Scenario: 替换默认实现
- **WHEN** 用户将 `tool.okf.plugins.conformance_checker` 改为指向自定义实现 `my_org.okf:CustomChecker`
- **THEN** 所有依赖 `conformance_report` 服务的插件（如 `cli_adapter`）自动使用新实现，无需修改任何其他代码

---

#### 2. Capability Seam 三角色抽象

系统 SHALL 借鉴 DeepSeek Harness 的 Capability Seam 设计，将每个可插拔能力拆分为三层：

```python
from dataclasses import dataclass, field
from collections.abc import Callable

# ===== Service Definition（接口契约）=====
@dataclass(frozen=True)
class ServiceDefinition:
    """能力的接口契约，只声明「能做什么」，不定义「怎么做」。"""
    name: str
    interface: type  # 接口类型（Protocol 或 ABC）
    description: str = ""


# ===== Service Provider（具体实现）=====
@dataclass(frozen=True)
class ServiceProvider:
    """ServiceDefinition 的具体实现，可多个并存。"""
    definition: ServiceDefinition
    factory: Callable[["Context", dict], object]  # 构造函数，接收 (ctx, config)
    config: dict = field(default_factory=dict)


# ===== Consumer（消费方）=====
# Consumer 通过 ctx.get(service_name) 获取服务，只依赖接口契约，不依赖具体 Provider
```

**三角色关系**：

| 角色 | 关心什么 | 变化频率 | 数量 |
|------|----------|----------|------|
| `ServiceDefinition` | 能力的接口契约 | 低（稳定） | 一个服务一个 |
| `ServiceProvider` | 能力的具体实现 | 中（可多个实现） | 一个服务可多个 Provider |
| `Consumer` | 使用能力完成任务 | 高（插件很多） | 一个服务被多个 Consumer 使用 |

#### Scenario: 定义新的 ServiceDefinition
- **WHEN** 开发者定义 `ServiceDefinition(name="bundle_accessor", interface=BundleAccessorProtocol)`
- **THEN** 该定义被注册到全局 `ServiceRegistry`，后续任何 Provider 可按此接口注册实现

#### Scenario: 注册 Provider 并自动触发 Consumer
- **WHEN** `ctx.provide("bundle_accessor", LocalFileBundleAccessor(ctx))` 被调用
- **THEN** 所有声明 `inject = [InjectSpec("bundle_accessor")]` 的插件自动激活（通过 `notify` 机制），获取到 `LocalFileBundleAccessor` 实例

#### Scenario: 切换 Provider 全局生效
- **WHEN** `bundle_accessor` 的 Provider 从 `LocalFileBundleAccessor` 切换为 `GitRepoBundleAccessor`
- **THEN** 所有依赖 `bundle_accessor` 的插件（`conformance_checker`、`index_synthesizer`、`trust_deriver`、`link_resolver`）自动通过 `_unload` → `_reload` 切换到新实现，无需修改任何 Consumer 代码

---

#### 3. 事件系统五种分发模式

系统 SHALL 借鉴 Cordis 的五种事件分发模式，为插件间通信提供灵活的事件机制：

| 模式 | 方法签名 | 行为 | 典型场景 |
|------|------|------|----------|
| `emit` | `ctx.emit(name, *args)` | 同步执行，不等待，监听器按注册顺序观察，无返回值 | 纯通知：`bundle:loaded`、`concept:parsed`、`log:info` |
| `bail` | `ctx.bail(name, *args)` | 同步执行，第一个返回非 `None` 的结果获胜，短路后续监听器 | 注册表查找：`service:lookup` |
| `parallel` | `ctx.parallel(name, *args)` | 并行执行所有异步监听器，等待全部完成 | 扇出通知：`bundle:reload` 触发多个并行校验 |
| `serial` | `ctx.serial(name, *args)` | 按注册顺序串行执行，第一个返回非 `None` 的结果获胜 | 链式校验：`concept:validate` 多校验器链 |
| `waterfall` | `ctx.waterfall(name, *args, next)` | 环绕中间件模式，监听器必须调用 `next()` 才能继续，可修改参数、短路流程 | 请求拦截：`concept:before_parse` 修改 frontmatter 元数据 |

**实现要点**：

```python
class Context:
    # ... 已有方法 ...

    def emit(self, event: str, *args) -> None:
        """纯通知，同步执行所有监听器。"""
        ...

    def bail(self, event: str, *args) -> object | None:
        """同步查找，第一个返回非 None 的结果获胜。"""
        ...

    def parallel(self, event: str, *args) -> list:
        """并行执行所有异步监听器，返回结果列表。"""
        ...

    def serial(self, event: str, *args) -> object | None:
        """串行执行，第一个返回非 None 的结果获胜。"""
        ...

    def waterfall(self, event: str, *args) -> object:
        """中间件链，每个监听器调用 next() 继续。"""
        ...

    def on(self, event: str, handler: Callable) -> Disposable:
        """注册事件监听器，返回逆函数用于取消监听。"""
        ...
```

#### Scenario: emit 事件通知
- **WHEN** Bundle 加载完成后调用 `ctx.emit("bundle:loaded", bundle)`
- **THEN** 所有监听 `bundle:loaded` 的插件同步收到通知，各插件独立处理（日志记录、UI 更新等），互相不阻塞

#### Scenario: waterfall 中间件拦截
- **WHEN** Concept 解析前触发 `ctx.waterfall("concept:before_parse", frontmatter)`
- **THEN** 监听器可以修改 `frontmatter` 字典（如注入默认值、转换格式），然后调用 `next()` 继续；若某监听器不调用 `next()`，则后续解析流程被短路

#### Scenario: serial 链式校验
- **WHEN** 运行 `ctx.serial("concept:validate", concept)`
- **THEN** 多个校验器按注册顺序串行执行，第一个返回非 `None` 错误信息的校验器获胜，后续校验器不再执行

#### Scenario: 事件监听自动绑定到 Fiber
- **WHEN** 插件在 `apply()` 中调用 `ctx.on("bundle:loaded", handler)`
- **THEN** 返回的 `Disposable` 自动注册到当前 Fiber 的 `_disposables`，插件卸载时自动移除监听器

---

#### 4. 插件配置清单（`pyproject.toml` 声明式装配）

系统 SHALL 支持通过 `pyproject.toml` 的 `[tool.okf]` 节配置插件装配，而非硬编码 CLI 入口：

```toml
[tool.okf]
version = "0.1.0"

[tool.okf.plugins]
bundle_loader = "okf.plugins.loader:BundleLoader"
conformance_checker = "okf.plugins.conformance:ConformanceChecker"
index_synthesizer = "okf.plugins.synthesis:IndexSynthesizer"
log_synthesizer = "okf.plugins.synthesis:LogSynthesizer"
trust_deriver = "okf.plugins.trust:TrustDeriver"
link_resolver = "okf.plugins.links:LinkResolver"
```

Harness 启动时自举流程：

```
1. 读取 pyproject.toml 的 [tool.okf.plugins] 配置节
2. 创建 Context 根实例
3. 按拓扑排序（依赖声明的 inject 约束）依次加载插件
4. 每个插件加载成功后，其 provide 的服务自动通知 notify
5. 所有插件 ACTIVE 后，Harness 就绪，等待 CLI 命令
```

#### Scenario: 自举加载
- **WHEN** 运行 `okf validate <path>` 且 `pyproject.toml` 中定义了完整的 `[tool.okf.plugins]`
- **THEN** Harness 自动创建 `Context`，依次加载所有插件，`bundle_loader` 提供 `bundle_accessor` 后自动触发 `conformance_checker` 激活，完成校验并输出报告

---

系统 SHALL 提供单元测试，覆盖核心解析、校验与合成逻辑，覆盖率达到项目标准（关键模块 ≥90%，整体 ≥80%）。

#### Scenario: 一致性校验回归
- **WHEN** 运行 `pytest`
- **THEN** 与 OKF 规范 §附录 A 等价样例（收入表 Bundle）对应的测试用例全部通过