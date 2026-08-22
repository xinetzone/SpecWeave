# 创建 Windows 下 Python 3.14.6t(free-threading) Conda 环境 — Spec

## Why

本地 CPython 源码位于 `d:\spaces\SpecWeave\external\libs\python\cpython`(当前 main = 3.16.0a0)。
开发/调试 Python free-threading(no-GIL) 需要独立的 Python 3.14.6t 解释器环境。目前已有的 conda 环境
(base/py313/py314/tao-mvp) 均为 GIL 版本(py314 实测 3.14.3、SOABI `cp314-win_amd64`)，
缺少一个无 GIL 的 3.14 free-threading 环境用于 CPython 相关测试与调试。

**已确认决策**：保留 3.14.6t 环境(不切换源码 checkout、不构建源码)。该环境用于 free-threading 相关调试，
遇到与源码版本强绑定的场景时另行处理。

## What Changes

- 在 Windows conda 中通过 **conda-forge 的 `python-freethreading`** 包创建新环境 `py314t`(free-threading, `cp314t`, 尽量 3.14.6)
- 校验解释器为无 GIL 构建(`sys._is_gil_enabled() == False`、SOABI 含 `cpython-314t`/`cp314t`)
- 写入 `conda-meta/pinned` 的 `python_abi 3.14 *_cp314t` 约束，防止后续安装包时 GIL 被静默回退(兼容现有 `py314` 命名惯例)
- 提供清晰的环境激活、使用与 free-threading 校验说明
- **不破坏**任何现有 conda 环境；**不改动** CPython 源码工作树

## Impact

- Affected specs: 无既有 spec 直接冲突(既有 `python314-cpython-wiki` 为文档任务，职责不同)
- Affected code / 系统: conda 环境列表新增 `py314t`；不修改源码、不修改现有环境
- 风险点：
  - conda-forge 频道需显式指定(当前默认频道为 Anaconda default)
  - 国内网络下 conda-forge 下载可能慢/失败，需镜像兜底(BFSU/TUNA)
  - 本终端为沙箱环境，`conda search` 曾因命中受限缓存路径失败；创建环境命令可能需要在其受限路径外执行或改用镜像缓存
  - 若 3.14.6 的 `python-freethreading` 不可用，回退到最新 3.14.x patch

## ADDED Requirements

### Requirement: 创建 free-threading conda 环境
系统 SHALL 在内置于 Windows 的 conda 中创建一个名为 `py314t` 的环境，使用 conda-forge 的
`python-freethreading` 提供 free-threading(no-GIL) 的 CPython 3.14.6(若 3.14.6 不可用则回退到最新 3.14.x)。

#### Scenario: 成功创建
- **WHEN** 执行 create 命令(cp314t 派生的 `python_abi=*=*_cp314t`)
- **THEN** 环境创建成功，解释器为 free-threading；`sys._is_gil_enabled() == False`；SOABI 含 `cp314t`/`cpython-314t`

#### Scenario: 3.14.6 不可用回退
- **WHEN** conda 无法解析到 3.14.6 的 `python-freethreading`
- **THEN** 安装可用的最新 3.14.x free-threading，并在说明中明确标注实际版本

### Requirement: 持久化 free-threading 约束
系统 SHALL 在 `py314t` 环境的 `conda-meta/pinned` 中写入 `python_abi 3.14 *_cp314t`，
以防止后续安装其他包时解释器被 GIL 版本替换。

#### Scenario: 约束写入生效
- **WHEN** 检查 `conda-meta/pinned`
- **THEN** 存在 `python_abi 3.14 *_cp314t` 行；`conda list python_abi` 显示 build 为 `*_cp314t`

### Requirement: 提供激活与使用说明
系统 SHALL 提供简明的激活、GIL 校验、退出激活说明，供用户快速上手。

#### Scenario: 用户按说明操作
- **WHEN** 用户执行说明中的命令
- **THEN** 环境可正常激活，校验命令返回符合预期(无 GIL、版本正确)

## Constraints

- 平台：Windows 11 x64 原生(用户明确要求，不使用 WSL)
- 工具：conda 26.1.1(现有)，不升级全局工具
- 频道：必须显式使用 conda-forge(默认频道不含 `python-freethreading`)
- 环境名：`py314t`
- 不破坏现有环境、不改动 CPython 源码工作树、不污染 base
- free-threading 检测必须校验 `_is_gil_enabled` 的值(False)，不能只看属性是否存在
  (project_memory 已记录 `hasattr(sys,'_is_gil_enabled')` 在全部 3.14 中均为 True)

## Non-Goals

- 不编译 CPython 源码(不 build --disable-gil)
- 不切换 cpython checkout 分支/tag
- 不创建 Jupyter kernel
- 不安装调试器/IDE 集成(如 delve/novel);仅作为一个可用的解释器环境交付