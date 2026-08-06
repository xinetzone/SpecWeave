# 发布 xs-cli 到 PyPI Spec

## Why
`xs-cli` 是玄境工作区唯一的可执行 CLI 工具（含 `xs` 命令），但当前仅通过本地 `pip install -e tools/xs/` 安装，且 CI 注释明确标注"本地包，不在 PyPI"。外部用户无法 `pip install xs-cli` 使用 xs 工具。将其发布到 PyPI 使 xs 工具能以标准方式分发给所有用户。

## What Changes
- **单源版本**：将 `tools/xs/src/xs/__init__.py` 的 `__version__` 作为唯一版本来源，`pyproject.toml` 改用 `dynamic = ["version"]` + `[tool.setuptools.dynamic]`，消除 pyproject 与 `__init__.py` 的版本重复。
- **补齐打包元数据**：`xs-cli` pyproject 增加 SPDX 许可证（`license = "MIT"`）、`readme`、`keywords`、`classifiers`、`project.urls`（Homepage/Repository/Issues）。
- **移除 `[tool.pdm.build]`**：统一以 setuptools backend 构建，删除 PDM 专属打包配置以免与 setuptools 构建混淆。
- **同步版本 bump**：`xs version bump` 更新 pyproject 版本的同时同步更新 `__init__.py` 的 `__version__`，保持单一事实来源。
- **新增 README.md**：为 xs-cli 提供 PyPI 描述所需的 README（含安装/使用说明）。
- **新增发布工作流**：`.github/workflows/release.yml`，打 tag 触发构建 sdist+wheel 并上传 PyPI（预留 TestPyPI dry-run 步骤）。

## Impact
- Affected specs: xs-cli 打包与版本管理能力
- Affected code:
  - [tools/xs/pyproject.toml](../../../projects/xuanspace/tools/xs/pyproject.toml)
  - [tools/xs/src/xs/__init__.py](../../../projects/xuanspace/tools/xs/src/xs/__init__.py)
  - [tools/xs/src/xs/commands/version_cmd.py](../../../projects/xuanspace/tools/xs/src/xs/commands/version_cmd.py)
  - `tools/xs/README.md`（新增）
  - `.github/workflows/release.yml`（新增）

## ADDED Requirements

### Requirement: 可构建发布
系统 SHALL 使用 `python -m build` 从 xs-cli 生成有效 sdist 和 wheel。

#### Scenario: 本地构建
- **WHEN** 在 `tools/xs/` 下执行 `python -m build`
- **THEN** 生成 `dist/xs_cli-<ver>-py3-none-any.whl` 与 `dist/xs_cli-<ver>.tar.gz`

#### Scenario: 产物校验
- **WHEN** 对构建产物执行 `twine check dist/*`
- **THEN** 校验通过，无元数据错误

### Requirement: 单源版本
xs-cli 的版本号 SHALL 只定义在 `xs/__init__.py` 的 `__version__`，pyproject 通过动态版本引用。

#### Scenario: 动态版本取值
- **WHEN** 构建 xs-cli
- **THEN** wheel 的版本号等于 `xs.__version__` 的值

### Requirement: 发布工作流
仓库 SHALL 提供基于 Git tag 的自动发布工作流，构建并上传 xs-cli 到 PyPI。

#### Scenario: 标签触发发布
- **WHEN** 推送 tag `xs-cli-vX.Y.Z`
- **THEN** CI 构建 sdist+wheel 并通过 twine 上传到 PyPI

## MODIFIED Requirements

### Requirement: 版本 bump 同步
`xs version bump` SHALL 在更新 pyproject 版本号的同时，同步更新 `xs/__init__.py` 的 `__version__`，保持单一事实来源。

## REMOVED Requirements

（无）