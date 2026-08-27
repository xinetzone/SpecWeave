---
name: pyinvoke-okf-wiki-spec
version: 1.0.0
created: 2026-08-21
source: pyinvoke source code analysis (external/libs/pyinvoke/invoke)
methodology: seven-concepts knowledge-sedimentation (R→I→E→V→C)
okf_version: "0.2"
---

# PyInvoke Wiki 教程（OKF Bundle）- 产品需求文档

## Overview
- **Summary**: 为 Python 任务执行库 PyInvoke（invoke）生成符合 OKF v0.2 规范的结构化 wiki 教程 bundle，存放于 `projects/awesome-okf-xs/bundles/pyinvoke/`，涵盖快速入门、核心概念、API 参考、实战指南和可复用模式。
- **Purpose**: 帮助 Python 开发者系统掌握 invoke 的设计哲学、核心 API 与最佳实践；同时萃取「开源项目学习→OKF wiki 生成」的通用提示词模板和 workflow。
- **Target Users**: Python 开发者、DevOps 工程师、需要构建 CLI 工具的工程师、SpecWeave 知识库用户。

## Problem Statement
PyInvoke 是 Python 生态中最流行的任务自动化库（Pythonic Make），但官方文档以英文为主且结构较为零散，缺乏中文的系统性教程。SpecWeave 项目需要一个高质量的 OKF 格式中文教程，同时沉淀出一套可复用的「开源项目学习→OKF wiki」方法论。

## Goals
- **G1**: 基于源码分析（非仅 README），系统梳理 invoke 的核心架构与数据流
- **G2**: 生成符合 OKF v0.2 规范的完整知识 bundle（含 concepts/、examples/、references/、index.md、log.md）
- **G3**: 覆盖从入门到高级的完整学习路径：快速上手→核心概念→API参考→实战模式→常见问题
- **G4**: 所有内容可追溯到源码事实，禁止编造 API 或功能
- **G5**: 萃取一份通用的「开源项目学习→OKF wiki 生成」提示词模板和 workflow，沉淀到 SpecWeave 模式库

## Non-Goals (Out of Scope)
- 不逐行翻译官方英文文档
- 不覆盖 invocations 包（invoke 的官方扩展包集合）的详细 API
- 不提供 invoke 与 Fabric、Celery 等其他库的深度对比
- 不为 invoke 本身贡献代码或修复 bug

## Background & Context
- **PyInvoke** 位于 `external/libs/pyinvoke/invoke/`，是成熟的 Python 任务执行库，核心模块包括 tasks.py、collection.py、context.py、config.py、executor.py、program.py、runners.py、parser/、loader.py 等
- **OKF v0.2 规范**位于 `vendor/knowledge-catalog/okf/SPEC.md`，awesome-okf-xs 项目已实现 dogfooding 示例（bundles/okf-spec/）
- 现有 bundle 参考：`projects/awesome-okf-xs/bundles/okf-spec/`（OKF 规范自身的 OKF bundle 实现，共 20 个概念文档）
- 产出路径：`projects/awesome-okf-xs/bundles/pyinvoke/`（新建 bundle 目录）
- 方法论：seven-concepts 知识沉淀场景（R→I→E→V→C），depth=standard

## Functional Requirements

### Bundle 结构要求
- **FR-1**: bundle 根目录 `pyinvoke/` 包含 `index.md`（带 okf_version 声明）和 `log.md`
- **FR-2**: `concepts/` 子目录包含核心概念文档，每个文件为 OKF 概念文档（type: Concept）
- **FR-3**: `examples/` 子目录包含可运行的代码示例，每个文件为 OKF 概念文档（type: Example）
- **FR-4**: `references/` 子目录包含信源登记簿（原始来源链接、进程登记等）
- **FR-5**: 每个子目录（concepts/、examples/、references/）包含各自的 `index.md`

### 核心概念文档（concepts/）
- **FR-6**: `00-introduction.md` — invoke 是什么、设计哲学、与 Make/Shell 脚本的对比、安装
- **FR-7**: `01-getting-started.md` — 5 分钟快速上手：第一个 tasks.py、@task 装饰器、inv 命令
- **FR-8**: `02-task-basics.md` — Task 类详解：@task 参数、任务名/别名/默认任务、help、pre/post 钩子、任务组合
- **FR-9**: `03-context-object.md` — Context 对象：c.run()、c.sudo()、c.cd()、c.prefix()、配置访问
- **FR-10**: `04-collection-namespace.md` — Collection 与命名空间：组织任务、模块化、ns.configure()、嵌套集合
- **FR-11**: `05-configuration.md` — 配置系统：9层配置优先级、配置文件格式（yaml/json/python）、环境变量、运行时覆盖
- **FR-12**: `06-runners.md` — Runner 系统：Local runner、命令执行、Result 对象、pty、echo/warn/hide 选项
- **FR-13**: `07-cli-program.md` — CLI 与 Program 类：自定义 CLI 工具构建、Program 参数、Parser 机制
- **FR-14**: `08-execution-model.md` — 执行模型：Executor、预处理/后处理、异常处理（Exit/Failure/UnexpectedExit）
- **FR-15**: `09-watchers.md` — StreamWatcher：自动响应（如密码输入）、Responder/FailingResponder、自定义 watcher
- **FR-16**: `10-terminals-io.md` — 终端与 IO：伪终端（PTY）、输出控制、颜色处理
- **FR-17**: `11-advanced-patterns.md` — 高级模式：并发执行、任务调用任务、MockContext 测试、自定义 Executor/Runner

### 示例文档（examples/）
- **FR-18**: `basic-task.md` — 基础任务定义与执行
- **FR-19**: `namespace-organization.md` — 命名空间组织大型项目
- **FR-20**: `custom-cli.md` — 使用 Program 构建自定义 CLI
- **FR-21**: `file-watcher-automation.md` — Watcher 自动化响应
- **FR-22**: `testing-tasks.md` — 使用 MockContext 测试任务

### 信源登记（references/）
- **FR-23**: `pyinvoke-source.md` — PyInvoke 源码信源登记（路径、版本、commit）
- **FR-24**: `okf-spec.md` — OKF v0.2 规范信源（链接到已有 okf-spec bundle 或 vendor 中原始 SPEC）

### 方法论萃取（额外产出）
- **FR-25**: 在 SpecWeave `.trae/specs/pyinvoke-okf-wiki/` 下生成 `prompt-template.md` — 「开源项目学习→OKF wiki」通用提示词模板
- **FR-26**: 在同目录生成 `workflow.md` — 对应的标准化 workflow（步骤、质量门、检查清单）

## Non-Functional Requirements
- **NFR-1**: 所有正文为中文，技术术语保留英文并附首次中文解释（如 Context（上下文对象））
- **NFR-2**: 每个概念文档符合 OKF v0.2 规范：YAML frontmatter（type 必填）、Markdown 正文、sources 溯源、generated/verified 信任字段
- **NFR-3**: 所有代码示例可运行、语法正确，Python 代码遵循 PEP 8
- **NFR-4**: 文件命名使用 kebab-case 纯英文（如 `task-basics.md`）
- **NFR-5**: 概念文档间使用 bundle 相对绝对路径（`/concepts/xxx.md`）进行交叉引用
- **NFR-6**: 事实声明必须通过 sources 脚注追溯到源码或官方文档
- **NFR-7**: 每个概念文件大小控制在 500-5000 字符（保持原子性，避免单文件过大）
- **NFR-8**: 所有文档 status: stable，stale_after 设置为合理日期（如 2027-12-31）
- **NFR-9**: 提取的通用模板和 workflow 需包含反模式、质量门检查清单、可迁移到其他开源项目

## Constraints
- **Technical**: 仅基于源码分析和官方文档，不编造未经验证的 API 或行为
- **Format**: 严格遵循 OKF v0.2（vendor/knowledge-catalog/okf/SPEC.md）和 awesome-okf-xs frontmatter 规范
- **Path**: 产出物存放于 `projects/awesome-okf-xs/bundles/pyinvoke/`（新建 bundle）
- **Methodology**: 使用 seven-concepts 知识沉淀链路（R→I→E→V→C），含对抗审查
- **Language**: 正文中文，文件名英文 kebab-case

## Assumptions
- 读者具备基本 Python 编程能力（知道装饰器、上下文管理器）
- 读者了解基本命令行操作
- 不需要覆盖 Windows 特有问题（invoke 本身跨平台，但教程以类 Unix 为主）
- pyinvoke 源码位于 `external/libs/pyinvoke/invoke/` 可直接读取

## Acceptance Criteria

### AC-1: Bundle 结构合规（rule）
- **Given**: bundle 目录 `projects/awesome-okf-xs/bundles/pyinvoke/`
- **When**: 检查目录结构
- **Then**: 包含 index.md（带 okf_version: "0.2"）、log.md、concepts/、examples/、references/ 及各子目录 index.md
- **Evidence**: 目录列表和 index.md frontmatter 检查

### AC-2: 概念文档覆盖完整（rule）
- **Given**: concepts/ 目录
- **When**: 列出所有 .md 文件
- **Then**: 包含 FR-6 至 FR-17 共 12 个概念文档，每个文件 frontmatter 含 type: Concept
- **Evidence**: 文件列表 + 每个文件 frontmatter 检查

### AC-3: 示例文档可用（rule）
- **Given**: examples/ 目录
- **When**: 列出所有 .md 文件
- **Then**: 包含 FR-18 至 FR-22 共 5 个示例文档，代码块语法正确
- **Evidence**: 文件列表 + Python 语法检查

### AC-4: OKF 格式合规（rule）
- **Given**: 所有非 index.md/log.md 的 .md 文件
- **When**: 检查每个文件
- **Then**: 1) 有可解析 YAML frontmatter；2) type 字段非空；3) sources 字段记录溯源；4) generated/verified 字段存在；5) 无保留文件名误用
- **Evidence**: 逐文件 frontmatter 校验

### AC-5: 源码事实可追溯（rubric）
- **Given**: 概念文档中的技术声明
- **When**: 随机抽取 10 个核心声明（API 参数、行为描述等）对照源码验证
- **Then**: 至少 9/10 与源码一致，无编造内容
- **Scale**: 0-2（2=全部准确；1=1-2处小错不影响使用；0=3+处错误或有编造）
- **Threshold**: ≥1
- **Evidence**: 源码对照检查记录

### AC-6: 交叉链接有效（rule）
- **Given**: 文档中的 markdown 链接
- **When**: 检查所有 bundle 内部链接
- **Then**: 内部链接目标文件存在（OKF 容忍断链，但本项目要求无断链）
- **Evidence**: 链接遍历检查

### AC-7: 通用模板可复用（rubric）
- **Given**: prompt-template.md 和 workflow.md
- **When**: 由独立审查者评估
- **Then**: 模板包含触发场景、输入要求、输出结构、质量门、反模式；workflow 可直接用于其他开源项目 wiki 生成
- **Scale**: 0-2（2=完整可直接复用；1=需小调整；0=过于具体不可复用）
- **Threshold**: ≥1
- **Evidence**: 独立审查评估

### AC-8: 对抗审查通过（rule）
- **Given**: 全 bundle 产出物
- **When**: 执行四视角对抗审查（魔鬼代言人/新人/老板/未来）
- **Then**: 所有 P0 问题已修复，P1 问题有回应或修复，审查记录在 review.md 中
- **Evidence**: 对抗审查记录 + 问题修复状态

## Open Questions
- 无
