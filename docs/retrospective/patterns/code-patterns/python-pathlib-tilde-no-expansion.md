---
id: "python-pathlib-tilde-no-expansion"
title: "用户家目录路径必须用 Path.home()（pathlib 不展开波浪号）"
type: "code-pattern"
date: "2026-09-09"
maturity: "L1-draft"
source: "jpman-client ensure_known_hosts Windows 失效诊断 (2026-09-09)"
related_patterns:
  - "context-aware-path-resolution"
  - "path-anchor-semantization"
  - "wsl-windows-path-autoconvert"
tags: ["python", "pathlib", "windows", "home-directory", "environment-variable", "known-hosts", "cross-platform"]
validation_count: 1
reuse_count: 0
---

# 用户家目录路径必须用 Path.home()（pathlib 不展开波浪号）

## 模式概述

在 Python 中解析用户家目录路径时，**`pathlib.Path` 不做波浪号（`~`）展开**——`Path("~")` 得到的是一个名为 `~` 的**字面量目录**，而不是当前用户的主目录。波浪号展开是 **shell** 的行为，不是 pathlib 的行为。

安全写法是 `Path.home()`（Windows 下解析 `USERPROFILE`，POSIX 下解析 `HOME`），或用 `os.path.expanduser("~/.ssh/known_hosts")` 显式展开。

触发概率最高的环境是 **Windows PowerShell + Python**：该环境通常**不存在 `HOME` 环境变量**（Windows 原生用 `USERPROFILE`），因此 `os.environ.get("HOME", "~")` 这类带默认值的读取必然落入 `"~"` 字面量分支，配合不展开的 `Path()`，路径解析静默错误。

## 触发场景

- **适用于**：任何 Python 代码构造用户级配置文件路径（`~/.ssh`、`~/.config`、`~/.aws`、`~/.gitconfig`）；跨平台（Windows/macOS/Linux/CI）运行的工具；需要写入或读取用户私有配置的 CLI/脚本
- **不适用于**：路径已由外部传入绝对路径、或明确使用相对路径语义的场景；shell 脚本（bash 会正确展开 `~`）

## 核心做法

1. **识别家目录需求**：代码中是否出现 `"~"`、`os.environ.get("HOME", "~")`、`f"{home}/..."` 字符串拼接
2. **改用标准 API**：`from pathlib import Path` → `Path.home() / ".ssh" / "known_hosts"`；或 `os.path.expanduser("~/.ssh/known_hosts")`
3. **构造后立即验证解析目标**：断言 `path.parent.exists()` 或至少 `print(path)` 确认不是字面 `~` 开头的相对路径
4. **避免依赖 shell 展开**：不要将 `"~/.ssh/x"` 字符串直接传给 `subprocess`/`os.system`（只在子 shell 内才展开）
5. **防御逻辑失败要可见**：家目录文件"不存在"与"路径算错没找到"无法区分时，走 WARN 日志而非静默 return

## 反模式

| 反模式 | 表现 | 后果 | 正确做法 |
|--------|------|------|---------|
| ❌ `Path(os.environ.get("HOME", "~"))` | 想回退到 `~` 但 Windows 无 `HOME` | 得到 `WindowsPath('~')`，`.exists()` 恒 False，后续逻辑静默失效（本项目真实事故） | `Path.home()` 一步到位，不手动读环境变量 |
| ❌ `f"~/.ssh/known_hosts"` 直接传给 subprocess | 依赖子 shell 做波浪号展开 | 不使用 `shell=True` 时 `~` 原样传给程序，找不到文件 | 在 Python 内先 `expanduser`/`Path.home()` 解析为绝对路径再传 |
| ❌ 只写"清理失败就 return"不区分原因 | known_hosts 不存在与路径算错返回同样结果 | 路径 bug 被静默掩盖，数月不暴露 | 至少打一条 DEBUG/WARN 说明跳过的原因与目标路径 |
| ❌ `Path("~").resolve()` 后仍不确定语义 | 以为 resolve 会展开波浪号 | `resolve()` 只规范化不展开 `~`，结果仍是字面路径 | 明确用 `Path.home()` / `expanduser` |

## 检验标准

- 代码中不存在裸 `"~"` 拼接用户路径的写法，全部经 `Path.home()` 或 `expanduser`
- 在**无 `HOME` 环境变量**的 Windows PowerShell 中运行相关路径逻辑，结果指向 `C:\Users\<user>\...` 且文件可读写
- 路径构造失败路径有可见日志，非静默 return

## 迁移案例（跨场景）

- **CI（GitHub Actions windows-latest / GitLab Windows runner）**：runner 常无 `HOME`，任何读取 `~/.ssh` 或 `~/.cache` 的 Python 测试都会踩同一陷阱
- **macOS launchd 守护进程**：launchd 环境变量极少（无 `HOME`），Python 常驻进程读用户配置时必须用 `Path.home()`
- **服务器定时任务（cron/at）**：`cron` 环境几乎无用户环境变量，读取 `~/.aws/credentials` 类路径必须显式解析

## 相关复盘

- 事故全貌见 [retrospective-ssh-hostkey-changed-20260909](../../reports/incident-reports/retrospective-ssh-hostkey-changed-20260909/retrospective-report.md)
