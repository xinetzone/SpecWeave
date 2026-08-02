---
id: p1-14-iflow-cli-guide
title: iFlow CLI AI 终端助手使用指南
source: d:\spaces\chaos\iflow-cli\IFLOW.md
source_type: file
category: scripts
tags:
  - iflow
  - cli
  - ai-tools
  - terminal
  - mcp
archive_status: archived
archive_priority: P1
created_at: 2026-08-02T12:05:00Z
updated_at: 2026-08-02T12:15:00Z
version: v0.1.0
reviewer: chaos-coordinator
review_notes: approved - 工具使用说明清晰，命令清单完整，分类准确
summary: iFlow CLI 是嵌入终端的 AI 命令行工具，支持多模型、MCP 服务器集成，提供丰富的斜杠命令和上下文注入能力
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\scripts\p1-14-iflow-cli-guide.md
archived_at: 2026-08-02T04:07:46Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T04:07:46Z archived from d:\spaces\chaos\.agents\knowledge\temp\scripts\p1-14-iflow-cli-guide.md to D:\spaces\SpecWeave\.agents\docs\knowledge\scripts\p1-14-iflow-cli-guide.md
---

# iFlow CLI AI 终端助手使用指南

## 工具概述

iFlow CLI 是一个综合性的命令行智能工具，可嵌入到终端中，具备以下核心能力：
- 分析代码仓库
- 执行编码任务
- 跨上下文理解需求
- 从简单文件操作到复杂工作流自动化

## 核心特性

1. **多模型支持**：Kimi K2、Qwen3 Coder、DeepSeek v3 等
2. **协议兼容**：支持 OpenAI 协议的模型提供商
3. **MCP 集成**：集成 Model Context Protocol 服务器扩展功能
4. **斜杠命令**：提供元级控制命令

## 安装

### 一键安装
```bash
bash -c "$(curl -fsSL https://cloud.iflow.cn/iflow-cli/install.sh)"
```

安装脚本自动完成：
1. 通过 nvm 安装 Node.js（如未安装）
2. 设置 npm 全局目录
3. 安装 iFlow CLI 包
4. 在 `~/.iflow/settings.json` 中配置 MCP 服务器

### 初始化项目
```bash
iflow
> /init
```
该命令会扫描代码库，创建/更新 IFLOW.md 项目特定文档。

## 斜杠命令速查

| 命令 | 功能 |
|------|------|
| `/init` | 初始化 iFlow CLI，建立项目理解 |
| `/memory` | 管理 AI 指令上下文 |
| `/tools` | 显示可用工具 |
| `/clear` | 清屏并清除会话历史 |
| `/copy` | 复制最后一次输出到剪贴板 |
| `/stats` | 显示会话统计 |
| `/compress` | 用摘要替换聊天上下文 |
| `/chat` | 保存和恢复对话历史 |
| `/help` | 显示帮助信息 |
| `/quit` | 退出 iFlow CLI |
| `/bug` | 提交问题反馈 |
| `/editor` | 选择代码编辑器 |
| `/mcp` | 列出 MCP 服务器和工具 |
| `/theme` | 更改视觉主题 |
| `/auth` | 更改认证方法 |
| `/about` | 显示版本信息 |
| `/extensions` | 列出活动扩展 |

## 特殊命令模式

### @ 命令 - 文件注入
```
@<path_to_file_or_directory>
```
将文件或目录内容注入到提示词中。

### ! 命令 - Shell 模式
```
!<shell_command>  # 直接执行系统 shell 命令
!                  # 切换 shell 模式
```

## MCP 服务器配置

默认集成的 MCP 服务器：

| 服务器 | 功能 |
|--------|------|
| sequential-thinking | 复杂问题解决 |
| context7 | 库文档检索 |
| magic | UI 组件生成 |
| playwright | 浏览器自动化 |

配置文件位置：`~/.iflow/settings.json`
列出 MCP 工具：`/mcp` 命令

## 架构说明

iFlow CLI 构建为 Node.js 应用：
- 多 AI 模型集成层
- MCP 服务器管理
- 命令解析与执行引擎
- 会话状态管理

## 目录结构

```
iflow-cli/
├── install.sh          # 安装脚本
├── README*.md          # 多语言文档
├── assets/             # 图片和截图
├── i18/                # 国际化命令文档
└── .git/               # Git 仓库元数据
```

---

**来源参考**：
- 项目指南：[IFLOW.md](file:///d:/spaces/chaos/iflow-cli/IFLOW.md)
- 项目 README：[README.md](file:///d:/spaces/chaos/iflow-cli/README.md)
