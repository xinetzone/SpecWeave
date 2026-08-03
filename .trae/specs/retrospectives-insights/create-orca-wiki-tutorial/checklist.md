# Orca 多代理 AI 编排器学习与 Wiki 教程文档 - 验收检查清单

## 基础框架
- [x] AC-1: 原子化 wiki 教程创建完成（README.md 索引 + 分章文件），位于 .agents/docs/knowledge/learning/03-agent-platforms-tools/orca-wiki/
- [x] AC-2: 目录导航系统可用（相对链接，无 file:/// 绝对路径）

## 内容章节
- [x] AC-3: 项目定位与核心价值阐述清晰（AI Orchestrator for 100x builders、YC 背书）
- [x] AC-4: 核心架构与技术栈阐述完整（Electron+TS、xterm.js WebGL、node-pty、ssh2、Expo）
- [x] AC-5: 八大核心功能详解完整（移动 Companion/并行 Worktree/终端分屏/设计模式/GitHub&Linear/SSH Worktree/注释 AI Diff/拖拽文件）
- [x] AC-6: Orca CLI 与编排机制解析完整（worktree/terminal/repo/automations/browser/linear/computer/orchestration + Run/Task/Dispatch/worker_done）
- [x] AC-7: 支持的 Agent 清单完整（≥15 款 CLI Agent，实际 29 款）
- [x] AC-8: 快速上手指南步骤明确（安装/启动/添加 Agent/创建分发 worktree/并行监控）
- [x] AC-9: 核心价值总结与行业趋势阐释清晰（编辑器→编排器演进、自带 Agent 理念）
- [x] AC-10: FAQ 章节实用（≥8 个问题，实际 9 个）+ 术语表 ≥15 个核心术语（实际 19 个）

## 资源与索引
- [x] AC-11: 资源链接有效（GitHub/官网/下载页）
- [x] AC-12: 分类索引更新完成（03-agent-platforms-tools/README.md 新增 orca-wiki 条目）

## 格式与验收规范
- [x] 所有文件 frontmatter 使用 YAML（--- 分隔），非 TOML（+++ 分隔）
- [x] 文件名 kebab-case、纯英文、无中文字符（check-filename-convention.py 通过）
- [x] 链接有效性检查通过（check-links.py 通过）
- [x] 执行前已读取同目录现有 wiki 文件确认格式（以实际文件为权威标准）
- [x] 技术栈描述准确（Orca 为 Electron+TS，非 Tauri，避免与 EchoBird 混淆）