---
id: "create-intelligent-terminal-wiki-tutorial-checklist"
title: "Intelligent Terminal Wiki 教程 - 验证清单"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# Intelligent Terminal 完整 Wiki 教程 - Verification Checklist

## 目录结构与基础规范
- [ ] Wiki 目录 `.agents/docs/knowledge/learning/intelligent-terminal-wiki/` 已创建
- [ ] README.md 导航入口存在且包含 YAML frontmatter（id、title、source、date）
- [ ] README.md 包含完整章节索引（13个章节文件链接）
- [ ] README.md 包含学习路径建议和前置知识说明
- [ ] 每个章节文件包含 YAML frontmatter，source 字段为 `"spec:create-intelligent-terminal-wiki-tutorial"`
- [ ] 所有文件使用中文编写，技术术语保留英文原文
- [ ] 无 `file:///` 绝对路径引用，全部使用相对路径

## 章节完整性（13章+README）
- [ ] 第1章 01-overview.md：项目概述与快速开始
- [ ] 第2章 02-architecture.md：整体架构设计
- [ ] 第3章 03-wta-master.md：WTA Master 多路复用器
- [ ] 第4章 04-wta-helper-tui.md：WTA Helper 与 TUI
- [ ] 第5章 05-cpp-integration.md：C++ 集成层
- [ ] 第6章 06-protocols.md：通信协议栈
- [ ] 第7章 07-wtcli-reference.md：wtcli 命令参考
- [ ] 第8章 08-agent-hooks.md：wt-agent-hooks Shell 集成
- [ ] 第9章 09-autofix.md：Autofix 自动错误检测与修复
- [ ] 第10章 10-build-system.md：构建系统与开发环境
- [ ] 第11章 11-logging-debugging.md：日志系统与调试
- [ ] 第12章 12-configuration.md：配置与设置详解
- [ ] 第13章 13-design-patterns.md：架构设计模式萃取

## 源码溯源引用
- [ ] 第2章引用 AGENTS.md、OVERVIEW.md、Multi-window-agent-pane.md
- [ ] 第3章引用 `tools/wta/src/master/mod.rs`
- [ ] 第4章引用 `tools/wta/src/helper/mod.rs`、`app.rs`、`ui/` 目录
- [ ] 第5章引用 TerminalPage.cpp、SharedWta.cpp、TerminalProtocolComServer.cpp、AgentPaneContent.cpp、Tab.cpp
- [ ] 第6章引用 TerminalProtocol.idl、protocol/acp/client.rs
- [ ] 第7章引用 doc/wtcli-commands.md
- [ ] 第8章引用 wt-agent-hooks/ 目录、agent_hooks_installer.rs
- [ ] 第9章引用 app.rs (classify_wt_event, maybe_trigger_autofix)
- [ ] 第10章引用 doc/building.md、doc/quick-start-local-dev.md
- [ ] 第11章引用 runtime_paths.rs
- [ ] 第12章引用 GlobalAppSettings.idl
- [ ] 第13章每个设计模式引用对应源码位置

## Mermaid 图表
- [ ] 第2章：整体架构图（Mermaid flowchart）
- [ ] 第2章：进程生命周期图
- [ ] 第3章：master 启动时序图（Mermaid sequenceDiagram）
- [ ] 第4章：helper TUI 组件关系图
- [ ] 第5章：C++ 组件调用关系图
- [ ] 第6章：ACP 双跳协议栈图（Mermaid flowchart）
- [ ] 第6章：端到端 prompt 时序图（Mermaid sequenceDiagram）
- [ ] 第8章：hooks 自动升级流程图
- [ ] 第9章：Autofix 数据流管线图（Mermaid flowchart）
- [ ] 第10章：构建流程图
- [ ] 第11章：日志目录结构图
- [ ] Mermaid 图表语法正确，可渲染（遵循安全编码六规则）
- [ ] Mermaid 图表总数 ≥ 5张

## 七概念方法论应用
- [ ] R阶段（事实）：各章节系统采集源码中的组件、接口、数据流等客观事实，无主观臆断
- [ ] I阶段（洞察）：第2章包含架构设计决策背后的原因分析（为何helper+master、为何COM、为何双跳）
- [ ] E阶段（萃取）：第13章提炼至少6个可复用设计模式，每个模式包含触发场景、核心步骤、反模式
- [ ] A阶段（原子化）：13个章节按单一职责原子化拆分，每章聚焦一个主题

## 导航与交叉引用
- [ ] 每个章节底部有"上一章/下一章"导航链接
- [ ] 首章（01-overview）无上一章链接，有下一章链接
- [ ] 末章（13-design-patterns）有上一章链接，无下一章链接（可指向README）
- [ ] 章节间交叉引用使用正确的相对路径
- [ ] `.agents/docs/knowledge/learning/README.md` 已更新，包含 intelligent-terminal-wiki 索引条目
- [ ] 运行 link-check 无断链

## 内容质量
- [ ] 第1章包含键盘快捷键表格
- [ ] 第6章清晰讲解三层协议（COM/ACP/ConPTY）的分工与关系
- [ ] 第7章 wtcli 命令按查询/操作/读取/事件/输入/诊断分类
- [ ] 第9章讲解 Autofix 的 cold start drop 策略边界情况
- [ ] 第10章讲解 package identity 和 0x80073D54 错误诊断
- [ ] 第11章包含 target 字段 grep patterns 表格和端到端 trace 示例
- [ ] 第12章包含完整配置表格
- [ ] 第13章每个设计模式包含：问题背景、解决方案、源码位置、适用场景、反模式警示
- [ ] 渐进式学习路径：概述→架构→核心组件→协议→工具→实践→模式萃取
