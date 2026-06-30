---
title: "TuyaOpen-dev-skills 学习笔记"
category: "learning"
tags: ["tuya", "tuyaopen", "skills", "agent-skills", "cursor", "claude", "iot", "embedded", "workflow", "ci"]
date: "2026-06-30"
status: "stable"
author: "Tuya"
summary: "TuyaOpen-dev-skills 是面向 TuyaOpen 硬件开发流程的 AI Skills 仓库，以“最小 SKILL.md + references/ 按需加载 + scripts/ 可执行脚本”的三分结构，把环境搭建、编译、代码检查、烧录监控与调试闭环规范化。"
---

# TuyaOpen-dev-skills 学习笔记

> 仓库：`https://github.com/tuya/TuyaOpen-dev-skills`
> 本地镜像：`d:\AI\.temp\libs\TuyaOpen-dev-skills`
> 许可证：Apache-2.0
> 目标：让 AI 助手“理解并执行”TuyaOpen 开发工作流（而不只是回答问题）

## 1. 仓库定位与设计目标

从 [README_zh.md](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/README_zh.md#L10-L36) 可以看出，它的定位不是传统 SDK / 库，而是面向 Cursor / Claude Code 等工具的“工作流知识包”：

- 把 TuyaOpen 的关键流程（环境、项目配置、编译、烧录、监控、授权、闭环）抽象成可复用的 Skills
- 用可执行脚本把“操作建议”落地为“可被智能体可靠调用的动作”
- 通过 references/ 承载长文档，避免把上下文一次性塞满（按需加载）

## 2. 核心目录结构（技能三分结构）

仓库结构与约定在 [README_zh.md](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/README_zh.md#L113-L136) 有明确说明：

- `SKILL.md`：最小入口（触发词 + 操作指令 + 关键示例）
- `references/`：长文档参考（比如 Kconfig 指南 / 错误码表 / 设备配网与授权）
- `scripts/`：智能体可直接执行的脚本（Python / shell / ps1 / bat），用于自动化

## 3. 技能清单与覆盖面

Skills 覆盖完整生命周期（从环境到闭环），并按 `skills/tuyaopen/*` 组织（见 [README_zh.md](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/README_zh.md#L24-L36)）：

- 环境搭建：`tuyaopen/env-setup`
- 项目编译：`tuyaopen/build`
- 项目与配置管理：`tuyaopen/project-config`
- 代码检查：`tuyaopen/code-check`
- 新增开发板：`tuyaopen/add-board`
- 开发闭环：`tuyaopen/dev-loop`
- 设备授权：`tuyaopen/device-auth`
- 调试助手：`tuyaopen/debug-helper`

此外还有两个“工具型技能”：

- `tuyaopen-cli-debug`：串口 CLI 辅助调试工具（Python）
- `tuyaopen-crash-decode`：崩溃地址解码（addr2line）能力封装

## 4. 关键脚本与值得复用的实现细节

### 4.1 背景监控守护：monitor_helper.py

[monitor_helper.py](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/debug-helper/scripts/monitor_helper.py) 把 `tos.py monitor -l` 做成“后台守护 + 会话文件”，适合智能体无阻塞地抓日志并在合适的时机 tail：

- 会话状态：写入 `<project_dir>/.target_logging/session.json`（[monitor_helper.py:L62-L65](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/debug-helper/scripts/monitor_helper.py#L62-L65)）
- 支持 `--json`：输出稳定字段，便于上层编排解析（[monitor_helper.py:L72-L78](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/debug-helper/scripts/monitor_helper.py#L72-L78)）
- 误杀防护：停止前校验 PID 是否真为 `tos.py monitor`（[monitor_helper.py:L118-L140](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/debug-helper/scripts/monitor_helper.py#L118-L140)）
- 路径越界防护：限制自定义日志文件必须在 `.target_logging/` 内（[monitor_helper.py:L162-L166](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/debug-helper/scripts/monitor_helper.py#L162-L166)）

### 4.2 代码检查 wrapper：check_files.py

[check_files.py](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/code-check/scripts/check_files.py) 是一个跨平台包装器，把 SDK 的 `tools/check_format.py` 以稳定方式提供给智能体：

- repo root 解析：优先 `OPEN_SDK_ROOT`，否则向上寻找 `.clang-format`（[check_files.py:L12-L25](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/code-check/scripts/check_files.py#L12-L25)）
- 路径越界防护：拒绝检查 repo_root 以外文件（[check_files.py:L46-L55](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/code-check/scripts/check_files.py#L46-L55)）
- 目录切换：执行前切到 repo_root，确保 check_format 的相对路径行为一致（[check_files.py:L63-L71](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/code-check/scripts/check_files.py#L63-L71)）

### 4.3 Linux 一键 build+run+分析：build_run.py（dev-loop）

在 [tuyaopen/dev-loop/SKILL.md](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/dev-loop/SKILL.md#L53-L61) 中，针对 LINUX 目标提供 `build_run.py` 作为快捷闭环入口，避免 flash/monitor 的硬件依赖。

## 5. 测试与发布（保障可用性与可发现性）

- 测试目录：`tests/`（pytest），覆盖核心脚本的可测试逻辑（会话文件、repo root 查找等）
- 发布清单：`release.json`（用于下游发现与自动化集成）
- CI：`.github/workflows/release.yml` 与 `scripts/sync-gitee-release.sh` 体现了“技能包可镜像/可同步”的发布策略

## 6. 可直接复用的“工程化模式”

该仓库最值得复用的不是某条命令，而是“让 AI 能可靠做事”的工程化手段：

- “最小入口 + references/ 按需加载”控制上下文成本
- `--json` 输出契约把脚本变成可编排组件
- 多处路径越界 / 误杀防护体现脚本安全基线
- pytest 覆盖脚本核心逻辑，保证可回归
