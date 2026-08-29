---
id: conda-dev-source-wiki-08-best-practices
title: "最佳实践指南"
source: "spec:create-conda-dev-source-wiki-tutorial"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-source-wiki/08-best-practices.toml"
category: "learning"
tags: ["conda", "best-practices", "plugin-development", "api-usage", "contribution"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda 环境管理、通道求解、API 调用、插件开发、源码贡献与文档写作的实践准则与反模式"
---
# 最佳实践指南

本章把源码阅读所得落回工程实践：环境管理、通道求解、程序化调用、插件开发、源码贡献、文档写作，并给出 ≥3 个反模式。所有 API 名称以 `conda/core/solve.py`、`conda/plugins/` 源码为准。

## 1. 环境管理最佳实践（命名 / 隔离 / 复现）

- **命名**：环境名避开保留名 `base`、`root`（`constants.py` 的 `RESERVED_ENV_NAMES`），也不要用含 `/`、` `、`:`、`#` 的字符（`PREFIX_NAME_DISALLOWED_CHARS`）。
- **隔离**：一个项目一个环境，按用途命名（如 `proj-ds-py311`），不往 `base` 里塞工作依赖；根环境只放 conda 自身与基础设施包。
- **复现**：所有依赖写入 `environment.yml`（含 `channels`、`dependencies`，pip 依赖放 `dependencies: - pip: [...]` 子节），避免"手工装完忘了记"。
- **冻结**：发布前用 `conda list --explicit` 导出显式清单以钉住精确版本；长期复现优先 `environment.yml`，精确复现用 explicit spec。

## 2. 通道与求解器配置建议

- **通道顺序即优先级**：把最想优先采用的通道放在最前（`conda config --prepend channels <url>`），顺序对 `strict` 决定性、对 `flexible` 影响下探顺序。
- **通道优先级**：默认 `channel_priority: flexible` 通常是体验与可解性的平衡点；追求来源可预测用 `strict`，但要做好冲突排查准备；`disabled` 仅在需要"唯版本论"时用。
- **求解器**：默认求解器为 `libmamba`（`base/constants.py` 的 `DEFAULT_SOLVER`），经典求解器名为 `classic`（`CLASSIC_SOLVER`）；经典求解器的 SAT 后端由 `sat_solver` 控制（`SatSolverChoice.PYCOSAT` 等）。
- **越少约束越易解**：如无必要不要同时钉死大量版本；先放开约束拿到可行解，再逐步收紧。

## 3. 程序化调用 conda API 的健壮性建议

高层求解入口是 `conda.core.solve.BaseSolver`（`Solver` 为经典实现），三个公开方法：

- `solve_final_state(...)` → `tuple[PackageRecord, ...]`，求解后环境的最终状态；
- `solve_for_diff(...)` → `(unlink_precs, link_precs)`，需要卸载/安装的差分；
- `solve_for_transaction(...)` → `UnlinkLinkTransaction`，可直接执行的交易对象。

健壮性要点：

1. **捕获 `CondaError` 子类**，不要用宽泛 `except Exception` 吞掉求解语义。常见：`UnsatisfiableError`（不可满足）、`PackagesNotFoundInChannelsError`、`NoChannelsConfiguredError`、`SpecsConfigurationConflictError`（钉住冲突）、`CondaVerificationError`（校验失败）。
2. **区分求解与执行**：先 `solve_for_transaction` 拿到交易，检查无误后再 `execute()`，便于把"算"与"做"分离、支持 dry-run 与回滚。
3. **尊重 `context` 单例**：`conda.base.context.context` 是进程级单例，读取配置（通道、`channel_priority` 等）会自动生效；不要自行拼接 condarc 解析逻辑。
4. **不依赖内部私有 API**：`_prepare`、`_run_sat`、`ssc` 等前缀是内部实现，随版本变动，脚本应只面向 `BaseSolver` 的公开面。
5. **自动化脚本**优先调用命令行（`conda install ...` 子进程）而非内部 API——CLI 是稳定契约，内部 API 不承诺向前兼容。

## 4. 插件开发规范

插件系统基于 pluggy，hookspec 统一定义在 `conda/plugins/hookspec.py::CondaSpecs`：

- **注册方式**：实现函数用 `@conda.plugins.hookimpl` 装饰，返回 `conda.plugins.types` 中的 `Conda*` 类型对象（如 `CondaSubcommand`、`CondaSolver`、`CondaVirtualPackage`、`CondaHealthCheck`、`CondaPreSolve`、`CondaPostSolve`、`CondaErrorHint` 等）。
- **命名唯一**：`name` 字段是标识符，避免与内置/他人插件重名，否则加载冲突。
- **入口点声明**：在 `pyproject.toml` 的 `[project.entry-points.conda]` 下声明插件模块，让 conda 能发现。
- **保持确定性**：hook 内不要有随机、时序或网络副作用；`conda_error_hints` 等 hook 会按插件名确定顺序合并提示，核心引导优先于同 `hint_code` 的插件提示。
- **异常隔离**：`conda_exception_observers` 等观察者 hook 的异常会被捕获并吞掉，但实现仍应快速返回、避免阻塞（见 hookspec 文档说明）。

## 5. conda 源码贡献规范

- **测试**：改动配测试，核心模块覆盖率要求高；运行 `pytest tests/`，涉及求解逻辑可参考 `tests/core/test_solve.py`。
- **类型标注**：仓库带 `py.typed`，新代码补类型标注，保持 mypy/pyright 通过。
- **news 片段**：用户可见改动需在 `news/` 下新增片段文件（参考 `news/TEMPLATE`），命名与内容随 PR 一起提交。
- **贡献门槛**：遵循仓库 `CONTRIBUTING.md`、`HOW_WE_USE_GITHUB.md`，签署 CLA 由 CI 的 `cla.yml` 校验。
- **提交规范**：小而聚焦的提交，跑通 `pre-commit`（`.pre-commit-config.yaml`）再推。

## 6. conda-docs 写作规范

- **术语可引用**：新增术语先登记进 `glossary.rst`，正文用 `:term:` 交叉引用。
- **目录登记**：新命令页/教程在 `index.rst` 或对应 toctree 中登记，避免成为孤页。
- **零告警构建**：`make html` 后以 `-W` 将告警当错误，保证提交前干净。
- **面向用户**：描述行为而非堆砌实现细节；命令示例给出可复制粘贴的完整片段。

## 7. 反模式与规避方式

1. **反模式：`base` 环境当工作环境用**，装一堆业务依赖。
   规避：只放 conda/基础设施；业务依赖一律建专属环境。

2. **反模式：`channel_priority: disabled` 追求"最新版"**，导致来源不可预测、复现困难。
   规避：默认 `flexible`；需要可控来源时用 `strict` 并规范通道顺序。

3. **反模式：混用 conda/pip 且无记录**，依赖被覆盖又无法复现。
   规避：先 conda 后 pip，pip 依赖写进 `environment.yml` 的 `pip` 子节。

4. **反模式：自动化脚本直连内部 API（`ssc`、`_run_sat`）**，升级即崩。
   规避：优先走 CLI；确需 API 时只用 `BaseSolver`/`Solver` 公开方法并捕获 `CondaError` 子类。

5. **反模式：为绕开锁/权限直接关 `no_lock` 或 `sudo conda`**，埋下并发损坏与权限隐患。
   规避：修正目录属主、避免并发 conda 进程；`no_lock` 仅临时且知情使用。

---

**上一章**：[07-faq.md](07-faq.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[09-resources.md](09-resources.md)