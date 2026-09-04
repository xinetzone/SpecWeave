# Tasks

## 前置：资料采集与事实整理（R 阶段）
- [x] Task 1: 采集 Hermes Agent 官方中文文档关键事实
  - [x] 1.1 通过 WebFetch/WebSearch 获取 hermes-agent.nousresearch.com/docs/zh-Hans/ 的快速开始、CLI、配置、消息网关、工具、技能、记忆、MCP、cron、架构等板块内容
  - [x] 1.2 整理 ≥20 条客观事实（无因果词），编号 F-001 起，含 URL/命令/版本来源
  - [x] 1.3 通过 G1 质量门：事实无因果推断词，可追溯

- [x] Task 2: 采集本地源码仓库关键事实
  - [x] 2.1 阅读 external/libs/hermes-agent/README.zh-CN.md、AGENTS.md 提取核心特性、CLI、架构、插件、技能标准
  - [x] 2.2 阅读 website/docs/ 目录结构，梳理文档板块与官方文档对应关系
  - [x] 2.3 补全事实清单至 ≥25 条，含源码依据（文件路径、关键常量、命令名）

## 洞察与架构设计（I 阶段）
- [x] Task 3: 提炼核心洞察并确定章节结构
  - [x] 3.1 提炼 3 条核心洞察（陈述/证据/反常识/行动四元组），通过 G2 质量门
  - [x] 3.2 确定原子化章节结构（12 篇 + README），输出路径 `03-agent-platforms-tools/hermes-agent-wiki/`
  - [x] 3.3 确认 frontmatter 格式与现有 wiki 一致（参考 hermes-agent-integration）

## Wiki 生成（E 阶段，实施）
- [x] Task 4: 生成 README.md 与核心章节（00-03）
  - [x] 4.1 00-overview.md：产品定位、核心理念、章节导航、前置知识、交叉引用
  - [x] 4.2 01-core-features.md：核心特性详解（终端界面/随你所在/闭环学习/定时自动化/委派并行/随处运行/研究就绪）
  - [x] 4.3 02-quickstart.md：安装（curl/install.ps1）、快速上手命令（model/tools/config/setup）
  - [x] 4.4 03-cli-commands.md：hermes 子命令与斜杠命令详解

- [x] Task 5: 生成配置与消息网关章节（04-05）
  - [x] 5.1 04-configuration.md：config.yaml、.env、HERMES_HOME、profiles
  - [x] 5.2 05-messaging-gateway.md：消息网关多平台、gateway setup/start

- [x] Task 6: 生成工具/技能/记忆章节（06-08）
  - [x] 6.1 06-tools-toolsets.md：40+ 工具、TOOLSETS、Footprint Ladder、check_fn
  - [x] 6.2 07-skills.md：SKILL.md、skills/ vs optional-skills/、curator 生命周期
  - [x] 6.3 08-memory.md：持久记忆、memory provider、memory_manager、Honcho

- [x] Task 7: 生成扩展能力与架构章节（09-10）
  - [x] 7.1 09-extensions-cron-delegation.md：MCP 集成、cron 定时调度、delegate_task 委派并行
  - [x] 7.2 10-architecture-source.md：AIAgent 核心循环、CLI/TUI/桌面架构、项目结构、插件系统
  - [x] 7.3 11-glossary-faq-resources.md：术语表、FAQ、资源链接

## 交叉引用与索引更新（E/C 阶段）
- [x] Task 8: 交叉引用与索引更新
  - [x] 8.1 各章节间相对链接正确，与 hermes-okf-wiki / hermes-agent-integration 交叉引用
  - [x] 8.2 更新 03-agent-platforms-tools/README.md 子 Wiki 索引表，添加 hermes-agent-wiki 入口

## 验证与交付（V/C 阶段）
- [x] Task 9: 对抗审查（V）与质量门
  - [x] 9.1 对 wiki 进行多视角对抗审查（6 条意见，采纳 4 条修正），通过 V 门
  - [x] 9.2 逐项核对 spec.md 的 AC-1~AC-13 验收标准
  - [x] 9.3 验证 frontmatter 合规、章节 <300 行、交叉链接有效
  - [x] 9.4 生成 .meta/toml 元数据文件，解决悬空 x-toml-ref

# Task Dependencies
- [Task 1]/[Task 2] 无依赖，可并行（资料采集）
- [Task 3] 依赖 [Task 1]/[Task 2]（需事实清单）
- [Task 4]/[Task 5]/[Task 6]/[Task 7] 依赖 [Task 3]（需章节结构），相互独立可并行
- [Task 8] 依赖 [Task 4-7]（需章节内容）
- [Task 9] 依赖 [Task 4-8]（需完整 wiki 与索引）
