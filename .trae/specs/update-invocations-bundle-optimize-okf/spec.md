# 更新 Invocations OKF bundle 并对 awesome-okf-xs 项目优化 Spec

## Why

现有 `invocations` OKF 知识包（`projects/awesome-okf-xs/doc/bundles/build/tooling/invocations/`）基于 v4.1.0 创建于 2026-08-21，但源码已重新落入本地 vendor 路径 `external/libs/tools/pyinvoke/invocations`，且 bundle 声称引用的若干模块与真实源码存在偏差（如 `packaging/version.py` 实际不存在）。此外 awesome-okf-xs 项目的文档构建/清理自动化目前直接硬编码在 CI 与 `doc/conf.py` 中，未使用 `invocations` 任务集进行封装。

机会：①以真实 vendor 源码为准对抗性审查并修正 bundle 漂移；②用 `invocations` 为 awesome-okf-xs 建立统一的 invoke 任务化自动化，收敛散落的构建命令。

## What Changes

- **源头复基线**：以 `external/libs/tools/pyinvoke/invocations`（v4.1.0）为唯一事实源，重新核对 `invocations` 包的模块清单与公开 API。
- **对抗性审查现有 bundle**：逐条 Grep 验证 bundle 中引用的模块名/任务名/参数/配置键，识别并定位漂移（含 `packaging/version.py` 虚报、模块数、`tasks.py` 归属等）。
- **更新 references/invocations-source.md**：修正模块清单与信源；新增指向本地 vendor 源码路径的本地信源条目。
- **更新受影响 concepts/examples**：凡引用不存在模块或错误 API 处修正；更新各文档 `verified` 字段。
- **更新 log.md**：追加对抗性审查与更新记录。
- **项目优化（awesome-okf-xs）**：新增 `tasks.py`（`invoke` + `invocations` Collection），封装 `build`/`clean`（可能含 `docs`、`test` 占位）任务；在 `pyproject.toml` `[project.optional-dependencies].doc` 增加 `invoke`（及按需 `invocations`）；CI `pages.yml` 改用任务化命令入口；本地验证 `invoke build` 可运行产出 html。
- **模式沉淀（C 阶段）**：将「源码→OKF 对抗性更新」与「以 invocations Collection 封装 Sphinx 构建」两组可复用模式沉淀至 awesome-okf-xs 或 SpecWeave patterns 目录。

## Impact

- 受影响 specs：`pyinvoke-okf-wiki`（既有创建 spec，本 delta 为其后续更新）。
- 影响代码/文档：
  - `projects/awesome-okf-xs/doc/bundles/build/tooling/invocations/`（references/concepts/examples/log/index）
  - `projects/awesome-okf-xs/tasks.py`（新增）
  - `projects/awesome-okf-xs/pyproject.toml`（新增 invoke 依赖）
  - `projects/awesome-okf-xs/.github/workflows/pages.yml`（改用 invoke）
  - 模式文档与 Spec 区 facts/insights 文件

## ADDED Requirements

### Requirement: 源头复基线
系统 SHALL 以 `external/libs/tools/pyinvoke/invocations`（v4.1.0）为唯一权威事实源，产出零推测的模块/API 事实清单。

#### Scenario: 事实采集
- **WHEN** 读取 vendor 源码各核心模块
- **THEN** 输出事实清单覆盖全部真实模块（`__init__/autodoc/checks/ci/console/docs/environment/pytest/testing/util/watch/packaging.(release|semantic_version_monkey|vendorize)`），且不含 `packaging/version.py`、不含模块级推断表述

### Requirement: 对抗性审查现有 bundle
系统 SHALL 对既有 `invocations` bundle 全部文件执行对抗性审查，用 Grep 验证每个引用的模块名/任务名/参数/配置键在真实源码中存在，并以书面报告排出所有漂移项。

#### Scenario: 漂移检测
- **WHEN** 审查发现 bundle 声称 `packaging/version.py` 存在
- **THEN** 报告判定其为虚构/漂移，并定位到引用它的具体文件与行

### Requirement: 项目自动化优化（invocations 封装）
系统 SHALL 在 awesome-okf-xs 引入 `tasks.py`，用 `invocations` Collection 封装 Sphinx 构建与清理任务，替换 CI 中硬编码的 `sphinx-build` 命令入口。

#### Scenario: invoke 构建
- **WHEN** 在项目根执行 `invoke build`
- **THEN** 等价执行 `sphinx-build -E -b html doc _build/html` 并成功产出 `_build/html/index.html`

## MODIFIED Requirements

### Requirement: 更新 invocations bundle references 信源登记
原 `references/invocations-source.md` 中的「模块清单」与信源指向需以真实 vendor 源码修正；新增本地源码路径信源。该 requirement 由「源头复基线」与「对抗性审查」共同驱动。

## REMOVED Requirements

### Requirement: bundle 对 `packaging/version.py` 的引用
**Reason**: 真实源码不存在该模块（实际为 `semantic_version_monkey.py`、`vendorize.py`），属事实虚构/漂移。
**Migration**: 在 references 与受影响概念文档中改用真实模块名，并在审查报告中标注删除原因。