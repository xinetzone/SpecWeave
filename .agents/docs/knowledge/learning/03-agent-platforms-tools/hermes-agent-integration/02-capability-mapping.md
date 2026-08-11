---
id: "hermes-agent-integration-02-capability-mapping"
title: "02 SpecWeave 能力盘点与映射矩阵"
source: "SpecWeave 仓库现状（capability-registry.md / skills/README.md / commands/README.md / AGENTS.md）"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/02-capability-mapping.toml"
type: "Wiki Tutorial"
description: "SpecWeave 能力体系盘点与到 Hermes tool/skill/hook/memory provider/context engine 的映射矩阵"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "盘点 SpecWeave 的 skills/commands/scripts/roles/AGENTS.md/knowledge/vendor 能力，并给出到 Hermes 各类插件能力的映射方案"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 02 SpecWeave 能力盘点与映射矩阵

## 2.1 SpecWeave 能力盘点

基于仓库真实目录盘点可暴露的能力资产（详见 [SpecWeave 能力注册中心](../../../../../capability-registry.md) 与 [skills 索引](../../../../../skills/README.md)）。

### 2.1.1 Skills（19 个，分三类）

| 类型 | 数量 | 代表 |
|------|:---:|------|
| 命令集门面 | 10 | seven-concepts-cmd、retrospective-cmd、insight-cmd、extraction-cmd、export-report-cmd、atomization-cmd、atomic-commit-cmd、mermaid-cmd、token-optimize-cmd 等 |
| 完整 Skill | 3 | forum-posting、home-assistant、git-commit-helper |
| 脚本命令门面 | 6 | link-check-cmd、atomization-finalize-cmd、docgen-cmd、ci-check-cmd、check-duplication-cmd、knowledge-graph-generator |

### 2.1.2 Commands 指令集（14 项）

复盘（retrospective）、洞察（insight）、导出报告、原子化、原子提交、文件创建、Mermaid 图表管理、Home Assistant 集成、第一性原理、对抗性审查、萃取、知识沉淀、方法论编排（seven-concepts）、行动优先输出、Token 优化。

### 2.1.3 Scripts 脚本库（25+）

链接检查（check-links.py）、命名规范、CI 检查（ci-check.ps1/.sh）、重复代码检测、docgen、spec-loader、spec-tool、check-vendor、check-mermaid、generate-graph 等。

### 2.1.4 Roles（7 角色）

orchestrator、architect、developer、reviewer、tester、co-founder、thesis-advisor（+ token-optimizer）。角色定义各角色职责与审批权限。

### 2.1.5 AGENTS.md 契约

启动协议、上下文路由表、内容敏感度分流、全局核心规则、三层路由。

### 2.1.6 Knowledge 知识库

`.agents/docs/knowledge/`：学习教程（okf-wiki、hermes-okf-wiki、echobird-wiki 等）、复盘报告、可复用模式库。

### 2.1.7 Vendor 子模块

flexloop（9 个技能，含 skill-creator、task-execution-summary、zhihu 系列、pdf-to-markdown 等）、ark-cli、awesome-okf。

## 2.2 映射矩阵

| SpecWeave 能力 | 映射到 Hermes | 理由 / 方式 |
|---------------|--------------|------------|
| Commands 指令集（复盘/洞察/萃取等） | **通用插件工具（tool）** | 每条指令集封装为工具函数，handler 调用对应逻辑/脚本 |
| Scripts 脚本（check-links.py 等） | **通用插件工具（tool）** | 把高频脚本封装为工具，schema 声明参数 |
| Skills 门面（触发词+步骤） | **通用插件工具（tool）** | SKILL.md 的触发词→schema description，步骤→handler |
| forum-posting / home-assistant | **通用插件工具（tool）** | 完整自动化能力，直接封装为工具 |
| Roles 角色定义 | **系统提示 / 钩子（hook）** | 角色是 prompt 层，不应作为工具；可作为会话初始化的系统提示注入 |
| AGENTS.md 契约 | **系统提示 + 钩子（hook）** | 启动协议作为 Agent 初始化 system prompt；内容敏感度等作为 on_session_start hook |
| Knowledge 知识库 | **Memory Provider / OKF bundle** | 通过 hermes-okf 挂接为可检索记忆层（见 04 章节） |
| Vendor flexloop 技能 | **通用插件工具（tool）**（跨边界调用） | 封装为工具，handler 内调用 vendor 脚本（遵守 vendor 边界） |

## 2.3 哪些适合直接暴露 / 需封装 / 不适合

### 适合直接暴露
- 纯计算/查询类脚本（check-links、spec-tool、generate-graph）
- 完整自动化 Skill（forum-posting、home-assistant）

### 需封装
- 多步骤方法论命令（复盘/洞察/萃取）：需拆分为"单步可调用"的工具，或保留为多轮会话引导流程，不宜做成一次性工具
- 涉及写操作（原子提交/文件创建）：必须在 handler 内保留 dry-run/幂等/验证（对应 SpecWeave 安全检查）

### 不适合暴露为工具
- **Roles 角色定义**：是 prompt 层，不是可调用函数
- **AGENTS.md 契约**：作为系统提示/hook，而非工具
- **Memory Provider / Context Engine 单实例能力**：除非确实需要替换 Hermes 记忆/上下文，否则走通用插件，避免占用单实例名额

## 2.4 反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 把角色当工具暴露 | 角色无法"调用"，模型会困惑 | 角色 → 系统提示/hook |
| 把多步骤方法论做成一次性工具 | 参数爆炸、状态难管理 | 拆分为单步工具或多轮引导 |
| 移除安全检查直接封装写操作脚本 | 破坏 dry-run/幂等保障 | handler 内保留安全检查 |

## 2.5 相关章节

- 接口规范：[Hermes Agent 插件接口规范](01-hermes-plugin-interface.md)
- 转换落地：[数据格式转换方法](04-data-conversion.md)
- 配置：[配置文件设置](03-configuration.md)
