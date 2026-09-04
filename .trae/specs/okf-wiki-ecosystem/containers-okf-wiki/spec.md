---
type: Playbook
title: Containers 生态 OKF Wiki 生成 PRD
sources:
  - id: containers-source
    resource: d:\spaces\SpecWeave\external\dao\action\Containers
    title: Containers 开源容器生态源码
---

# Containers 生态 OKF Wiki 生成 - Product Requirement Document

## Overview
- **Summary**: 系统化学习 `d:\spaces\SpecWeave\external\dao\action\Containers` 目录下的所有容器相关开源项目源码，遵循 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C），在 `d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles/containers/` 下生成符合 OKF v0.2 规范的中文 Wiki 教程。新增 `containers/` 技术域，包含 11 个容器生态子项目的知识包。
- **Purpose**: 将容器开源生态（conmon、fuse-overlayfs、podman 相关工具、QM 虚拟机管理等）的源码知识沉淀为结构化、可验证、可复用的中文 OKF 知识包，填补 awesome-okf-xs 文档库在容器技术领域的空白。
- **Target Users**: 容器技术学习者、云原生开发者、Podman/OCI 生态贡献者、需要系统化理解容器底层实现的工程师。

## Goals
- 新增 `containers/` 技术域作为 awesome-okf-xs 的第 11 个技术域
- 为 11 个容器子项目生成符合 OKF v0.2 规范的知识包（bundle）
- 每个 bundle 包含 concepts/（概念文档）、examples/（示例文档）、references/（信源登记）三层结构
- 所有文档通过 G4 质量门：无虚构 API（Grep 验证）、链接无断裂、frontmatter 完整
- 更新总索引 `doc/bundles/index.md`，将 containers 域纳入导航
- 更新域索引 `doc/bundles/containers/index.md`

## Non-Goals (Out of Scope)
- 不修改容器项目本身的源码（external/dao/action/Containers 下为只读源码）
- 不进行容器运行时的功能开发或 Bug 修复
- 不生成英文文档，仅生成中文教程
- 不对每个项目做全量源码逐行解析，而是聚焦核心架构、关键模块、典型用法
- 不深度分析历史版本演进，以当前 main/master 分支代码为准

## Background & Context
- **现有结构**: awesome-okf-xs 现有 10 个技术域（meta/python/build/document/data/ml/ai/comm/web/think），共 248 个知识包
- **源码位置**: 容器项目源码位于 `d:\spaces\SpecWeave\external\dao\action\Containers\`，包含以下 11 个子项目：
  1. **conmon** - C 语言编写的 OCI 容器运行时监控器（container monitor）
  2. **conmon-rs** - Rust 重写版本的 conmon
  3. **fuse-overlayfs** - 基于 FUSE 的容器 overlay 文件系统实现（Rust）
  4. **libocispec** - OCI 运行时和镜像规范的 C/Rust 解析库
  5. **olot** - Python 编写的 OCI 模型打包工具（用于 AI/ML 模型容器化）
  6. **omlmd** - Python 编写的 OCI 模型元数据工具
  7. **podman-py** - Podman 的 Python 绑定库
  8. **podman-compose** - Podman 的 Compose 兼容实现
  9. **qm** - QEMU/KVM 虚拟机管理工具（在容器中运行虚拟机）
  10. **toolbox** - 用于创建容器化开发环境的工具（Go）
  11. **ai-lab-recipes** - AI 实验室配方/示例（容器化 AI 应用）
- **OKF 规范**: 遵循 OKF v0.2，frontmatter 必须包含 type/title/description/tags/sources/generated/verified/status/stale_after
- **工作流**: 使用 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）+ seven-concepts-cmd 方法论编排
- **构建验证**: 生成后需通过 `invoke gates.all` 质量门（UTF-8 + toctree 完整性）

## Functional Requirements
- **FR-1**: 创建 `doc/bundles/containers/` 技术域目录及根 `index.md`
- **FR-2**: 为 11 个子项目各生成一个独立 OKF bundle
- **FR-3**: 每个 bundle 包含：
  - `index.md` - bundle 导航（无 frontmatter，仅 toctree）
  - `log.md` - 更新日志
  - `concepts/` - 概念文档（≥3个，涵盖核心架构/关键模块/核心API）
  - `examples/` - 示例文档（≥2个，典型用法/代码示例）
  - `references/` - 信源登记（README 解析、核心源码文件引用）
- **FR-4**: 每个概念/示例文档包含合规的 OKF v0.2 frontmatter
- **FR-5**: 更新 `doc/bundles/index.md` 总索引，加入 containers 域导航
- **FR-6**: 所有代码示例中的类名/方法名/函数名需经 Grep 验证在源码中存在
- **FR-7**: 交叉引用使用 `/` 开头的 bundle-relative 绝对路径

## Non-Functional Requirements
- **NFR-1**: 文档语言为中文，技术术语首次出现时附英文原文
- **NFR-2**: 每个概念文档长度控制在 500-2000 字，聚焦单一概念
- **NFR-3**: 代码块标注语言（c/rust/python/go/bash）
- **NFR-4**: 文档通过 `invoke gates.all` 质量门（UTF-8 + toctree 完整性）
- **NFR-5**: 每批生成文档 ≤7 个，防止上下文过载
- **NFR-6**: facts.md 中事实零推测（无"用于"/"目的是"等推断词）

## Constraints
- **Technical**: 
  - 源码语言混合（C/Rust/Python/Go）
  - 文档格式必须符合 OKF v0.2 + Sphinx myst_parser 兼容性要求
  - frontmatter 日期字段可裸写（conf.py 已自动处理引号）
- **Business**: 
  - 源码为只读，不修改 external/ 下任何文件
  - 文档存放于 projects/awesome-okf-xs/doc/bundles/containers/
- **Dependencies**: 
  - source-code-to-okf-wiki 工作流 Skill
  - seven-concepts-cmd 方法论编排 Skill
  - awesome-okf-xs 项目的 invoke 质量门工具

## Assumptions
- external/dao/action/Containers 下的子项目均已初始化（git submodule 已 checkout）
- awesome-okf-xs 项目的 Python 环境可用（可运行 invoke 命令）
- 每个项目至少有 README.md 可作为初始信源
- 核心源码文件不超过 50 个/项目，可在 R 阶段完成通读

## Acceptance Criteria

### AC-1: 技术域目录结构完整
- **Given**: containers 域目录已创建
- **When**: 检查目录结构
- **Then**: `doc/bundles/containers/` 存在，包含 `index.md`，且 `doc/bundles/index.md` 已更新引用
- **Verification**: `programmatic`
- **Notes**: 通过 `invoke gates.toctrees` 验证

### AC-2: 11 个 bundle 目录存在且结构合规
- **Given**: 所有 bundle 生成完成
- **When**: 列出 `doc/bundles/containers/` 下的子目录
- **Then**: 存在 11 个项目目录，每个目录包含 index.md/log.md/concepts/examples/references 子目录
- **Verification**: `programmatic`

### AC-3: 每个 bundle 的文档数量达标
- **Given**: 单个 bundle 生成完成
- **When**: 统计 concepts/ 和 examples/ 下的 .md 文件数
- **Then**: concepts/ ≥3 个文档，examples/ ≥2 个文档，references/ ≥1 个信源文件
- **Verification**: `programmatic`

### AC-4: Frontmatter 合规
- **Given**: 任意非 index.md/log.md 的文档
- **When**: 解析 YAML frontmatter
- **Then**: 包含 type/title/description/tags/sources/generated/verified/status 字段，type 为 Concept/Example/Reference 之一
- **Verification**: `programmatic`

### AC-5: 无虚构 API（Grep 验证）
- **Given**: 文档中引用的类名/函数名/方法名
- **When**: 在对应项目源码中 Grep 搜索
- **Then**: 每个引用的标识符在源码中存在（允许标准库函数和通用术语）
- **Verification**: `programmatic`
- **Notes**: 抽样验证核心 API，重点检查"看起来合理"的通用模式

### AC-6: 交叉引用无断裂
- **Given**: 文档中的 Markdown 链接
- **When**: 检查链接目标文件是否存在
- **Then**: 所有 `/` 开头的 bundle-relative 路径指向存在的文件
- **Verification**: `programmatic`

### AC-7: 质量门通过
- **Given**: 所有文档生成完成
- **When**: 在 awesome-okf-xs 目录运行 `invoke gates.all`
- **Then**: UTF-8 检查和 toctree 检查均通过，无错误
- **Verification**: `programmatic`

### AC-8: 文档内容可读且准确（人工评审）
- **Given**: 生成的概念文档
- **When**: 人类评审阅读文档
- **Then**: 架构描述清晰，代码示例可运行（或逻辑正确），术语使用准确，学习路径合理
- **Verification**: `human-judgment`

## Open Questions
- [ ] ai-lab-recipes 是否为容器核心项目？若内容过少可作为示例合并到其他 bundle 或精简处理
- [ ] podman-compose 源码深度如何？若只有最小实现，概念文档可适当减少
- [ ] 是否需要为 containers 域添加分组（如 runtime/filesystem/python-bindings/vm-tooling 等）？
