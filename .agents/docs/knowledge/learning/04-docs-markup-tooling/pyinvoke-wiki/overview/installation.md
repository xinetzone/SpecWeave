---
type: "Installation Guide"
title: "PyInvoke 安装指南"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/overview/installation.toml"
description: "pip 安装、版本要求、安装验证"
tags: ["invoke", "installation", "setup", "pip"]
date: "2026-08-21"
status: "stable"
author: "SpecWeave"
sources:
  - id: invoke-pyproject
    resource: "d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/pyproject.toml"
    title: "PyInvoke pyproject.toml - Dependencies and Python version requirements"
---
# 安装指南

## 环境要求

- **Python 版本**：Invoke 3.x 要求 Python ≥ 3.10（基于 pyproject.toml 中的 `requires-python = ">=3.10"`）
- **操作系统**：跨平台支持 Linux、macOS、Windows
- **依赖**：核心模块不依赖第三方包（纯标准库实现）

## 使用 pip 安装

```bash
pip install invoke
```

## 验证安装

安装完成后，验证 `inv` 命令可用：

```bash
inv --version
```

或使用 Python 导入验证：

```bash
python -c "import invoke; print(invoke.__version__)"
```

输出应显示 Invoke 的版本号（如 `3.0.3`）。

## CLI 入口

安装后提供两个等价的命令行入口：

| 命令 | 说明 |
|------|------|
| `inv` | 简短形式，推荐日常使用 |
| `invoke` | 完整形式 |

两个命令由同一入口点生成，行为完全一致。在 `pyproject.toml` 中定义为：

```toml
[project.scripts]
invoke = "invoke.main:program.run"
inv = "invoke.main:program.run"
```

## 从源码安装

如果需要使用开发版本或基于源码学习：

```bash
git clone https://github.com/pyinvoke/invoke.git
cd invoke
pip install -e .
```

## 虚拟环境建议

推荐在虚拟环境中安装和使用 Invoke：

```bash
# 使用 venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
pip install invoke

# 使用 PDM
pdm add invoke
```

## 安装检查清单

安装完成后，可以运行以下检查：

1. ✅ `inv --version` 输出版本号
2. ✅ `python -c "from invoke import task, Collection, Context, run"` 无报错
3. ✅ 在项目根目录创建 `tasks.py` 后，`inv --list` 能发现任务
