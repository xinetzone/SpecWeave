---
id: create-codewhale-wiki-tutorial-tasks
title: CodeWhale Wiki 教程生成 - 任务列表
source: spec.md
methodology: "七概念方法论·场景4：知识沉淀（R→I→E→V→C）"
---

# CodeWhale Wiki 教程生成 - 任务列表

## [x] Task 1: 官网信息采集与事实记录（R阶段-来源1）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 采集 `https://codewhale.net/zh` 官网全部页面内容
  - 覆盖：首页（产品定位/功能介绍/安装方式/运行时说明）、文档页（产品名词、安装指南、新手指引、提供商与模型、Fleet工作流）、运行时说明页
  - 按纯客观标准记录事实，剥离因果推断和主观评价
  - 输出事实清单（≥20条，编号 F-001 起），通过 G1 质量门检查
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 覆盖产品定位、功能、安装、运行时四个维度
  - `human-judgement` TR-1.2: 事实数量≥20条，无因果词
  - `human-judgement` TR-1.3: 关键数据（版本号、提供商数量、Star数）准确

## [x] Task 2: 源码结构分析（R阶段-来源2）
- **Priority**: high
- **Depends On**: None（可与 Task 1 并行）
- **Description**: 
  - 分析 `d:\AI\external\tools\CodeWhale` 本地源码结构
  - 覆盖：crates/ 模块划分与职责、核心模块功能（tui/cli/config/agent/lane/fleet/workflow）、关键配置文件、文档资源（docs/ 目录）
  - 阅读关键源码文件：README.md、AGENTS.md、ARCHITECTURE.md、config.example.toml、constitution.json
  - 输出源码结构事实清单（≥15条），通过 G1 质量门检查
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 核心 crate 模块功能描述准确
  - `human-judgement` TR-2.2: 关键配置文件内容记录完整
  - `human-judgement` TR-2.3: 源码目录结构层级清晰

## [x] Task 3: 核心洞察提炼（I阶段）
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 基于 Task 1 和 Task 2 的事实清单，提炼 CodeWhale 核心设计洞察
  - 每条洞察包含完整四元组：陈述（结论性判断）、证据（引用事实编号）、反常识（挑战默认假设）、行动（可执行建议）
  - 至少覆盖：模型路由架构价值、嵌套宪法安全设计、终端优先交互哲学、Fleet 多智能体编排
  - 输出 3-5 条核心洞察，通过 G2 质量门检查
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 洞察数量≥3条，每条四元组完整
  - `human-judgement` TR-3.2: 证据引用事实编号，可追溯
  - `human-judgement` TR-3.3: 有反常识性，不是正确的废话

## [x] Task 4: Wiki 教程框架搭建（E阶段-结构）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 创建 `docs/knowledge/learning/codewhale/` 目录结构
  - 按知识库模板规范创建目录：tech/、general/domain/、topics/
  - 创建 index.md 首页框架（含架构总览 Mermaid 图）
  - 确保目录结构与模板规范一致
- **Acceptance Criteria Addressed**: [AC-4 部分]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 目录结构符合知识库模板规范
  - `human-judgement` TR-4.2: YAML frontmatter 格式正确

## [x] Task 5: tech/ 模块教程编写（E阶段-核心技术）
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 编写 tech/intro.md：项目概述（定位、核心价值、技术栈、架构概览）
  - 编写 tech/quickstart.md：安装与首次使用指南（npm/cargo/docker 多渠道，含首次会话步骤）
  - 编写 tech/features.md：核心功能详解（Route Resolver 模型路由、Nested Constitution 嵌套宪法、Plan/Act/Operate 三种模式、Fleet 多智能体工作流）
  - 编写 tech/deploy.md：安装渠道与提供商配置（36个提供商路由、认证方式、本地模型）
  - 编写 tech/changelog.md：版本演进记录（从 deepseek-tui 到 CodeWhale 的演进路径）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 每个页面内容基于事实，有源码或官网依据
  - `human-judgement` TR-5.2: 代码示例可直接复制执行
  - `human-judgement` TR-5.3: 专业术语首次出现时附中英文对照

## [x] Task 6: general/ 与 topics/ 模块编写（E阶段-扩展知识）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 编写 general/domain/index.md：终端 AI 编程助手领域知识（终端优先哲学、TUI vs GUI、模型无关设计理念）
  - 编写 topics/index.md：设计哲学与行业洞察（模型路由范式意义、开源社区驱动模式、与 Claude Code/Cursor 的差异化定位）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 领域知识有独立价值，不重复 tech/ 内容
  - `human-judgement` TR-6.2: 设计哲学有原文依据，不过度解读

## [x] Task 7: 对抗审查（V阶段）
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Description**: 
  - 对完整 Wiki 教程执行四视角对抗审查
  - 魔鬼代言人：挑逻辑漏洞、数据准确性、因果关系
  - 新人视角：验证教程可读性，零基础用户能否按步骤完成安装和首次使用
  - 老板视角：评估教程的实用价值和学习投入产出比
  - 未来视角：评估教程的时效性和可持续性
  - 输出审查意见≥5条，至少采纳2条修正
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 四视角全部覆盖，审查意见≥5条
  - `human-judgement` TR-7.2: 新人视角验证通过，操作步骤清晰可执行
  - `human-judgement` TR-7.3: 至少采纳2条意见修正产出

## [x] Task 8: 质量验证与原子提交（C阶段）
- **Priority**: high
- **Depends On**: Task 7
- **Description**: 
  - 运行链接有效性检查（check-links.py）
  - 运行文件名规范检查（check-filename-convention.py）
  - 按原子提交原则分组提交：Wiki 教程文件 + 知识库索引更新
  - 提交信息遵循 Conventional Commits 规范
- **Acceptance Criteria Addressed**: [AC-6, AC-7, AC-8]
- **Test Requirements**:
  - `auto` TR-8.1: check-links.py 全部通过
  - `auto` TR-8.2: check-filename-convention.py 全部通过
  - `human-judgement` TR-8.3: 每个提交符合单一职责原则

# Task Dependencies

```
Task 1 (官网采集) ──┐
                    ├──> Task 3 (洞察) ──> Task 4 (框架) ──> Task 5 (tech/) ──> Task 6 (扩展) ──> Task 7 (审查) ──> Task 8 (提交)
Task 2 (源码分析) ──┘
```

# Parallelizable Work

- Task 1（官网采集）与 Task 2（源码分析）可并行执行
- Task 5（tech/ 模块）的 5 个子页面可并行编写