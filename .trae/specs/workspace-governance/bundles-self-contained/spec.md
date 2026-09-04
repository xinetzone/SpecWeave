# Bundles 自包含自洽化重构 - Product Requirement Document

## Overview
- **Summary**: 对 `d:\spaces\SpecWeave\bundles` 目录进行系统性重构，修复所有断链，统一链接格式，补全缺失的入口文件，清理重复文件和本地绝对路径，确保 bundles 目录是一个自包含、自洽、无断链、结构一致的知识包集合。
- **Purpose**: 当前 bundles 目录存在 545 个断链（链接缺少 `.md` 后缀）、缺失两级入口文件、重复验证报告、本地绝对路径硬编码、结构不一致等问题，导致知识包无法被正确导航、链接检查失败、可移植性差。本重构旨在一次性解决这些系统性问题，使 bundles 成为一个干净、可移植、自包含的知识包仓库。
- **Target Users**: OKF 知识包消费者、知识工程师、AI Agent（通过链接检查和导航工具访问）。

## Goals
- 修复所有 545 个断链，统一使用带 `.md` 后缀的 bundle-relative 路径格式
- 创建 `bundles/index.md` 总入口和 `bundles/chaos/index.md` 分类入口，提供完整导航
- 删除重复的 `verification-report.md` 文件，统一位置规范（bundle 根目录）
- 清理 `apache-tvm` 中 244 处 `file:///d:/AI/...` 本地绝对路径
- 验证所有 bundle 结构一致性，确保每个标准 bundle 具有完整的 concepts/examples/references 目录结构
- 确保 `check-links.py` 扫描 bundles 目录时零断链、零警告
- bundles 目录可独立移植（不依赖外部特定路径，所有引用自包含）

## Non-Goals (Out of Scope)
- 不修改知识包的内容本身（API 描述、概念解释等正文内容）
- 不补充 english-grammar 的 verification-report.md（该 bundle 为英文语法资料，非源码转 wiki 产物，V 阶段流程不同）
- 不重构 laozi-lineage 的目录结构（老子谱系是特殊的人文学术 bundle，结构与源码转 wiki 的标准结构不同，保持其特殊性）
- 不修复 CROSS_BUNDLE_REVIEW.md 中提到的 frontmatter 元数据问题（verified/status 字段回写）——这属于内容质量问题，不是自洽性/断链问题
- 不修改 vendor/ 或 projects/ 下的内容

## Background & Context
- bundles 目录采用 OKF（Open Knowledge Format）v0.2 规范，每个 bundle 是一个独立的知识包
- 链接设计使用 `/` 开头的 bundle-relative 路径（如 `/concepts/00-overview.md`），这是规范约定，check-links.py 已内置此解析逻辑
- 问题根源：早期 bundle（7 个源码转 wiki bundle）生成时链接省略了 `.md` 后缀（这在 MkDocs 等静态网站生成器中可正常工作，但本地 Markdown 预览和 check-links.py 需要后缀）；后期 bundle（tiktoken）已修正为带后缀格式
- 入口文件缺失：bundles 和 bundles/chaos 目录没有 index.md，导致无法从根目录导航
- 本地绝对路径：apache-tvm 的 facts-relax-te-topi.md 在开发过程中硬编码了作者本地的源码路径
- 重复文件：3 个 bundle 在根目录和 references/ 下都有 verification-report.md，属于构建过程中的产物位置不一致

## Functional Requirements
- **FR-1**: 所有本地 Markdown 链接必须包含 `.md` 后缀，统一格式为 `/path/to/file.md`（bundle-relative）或 `./path/to/file.md`/`../path/to/file.md`（相对路径）
- **FR-2**: 创建 `bundles/index.md` 作为总入口，列出所有分类（chaos/ 及未来可能的其他分类）
- **FR-3**: 创建 `bundles/chaos/index.md` 作为 chaos 分类入口，列出该分类下所有 10 个 bundle 并提供简介
- **FR-4**: 删除重复的 verification-report.md：mobile-use、okf-ecosystem、veadk-python 的 references/ 下的副本，保留根目录的版本
- **FR-5**: 清理 apache-tvm facts-relax-te-topi.md 中的 `file:///d:/AI/.chaos/...` 本地绝对路径，改为 bundle-relative 路径或移除不恰当的行号引用
- **FR-6**: 每个 bundle 的根 index.md 中的链接必须正确指向带 `.md` 后缀的文件
- **FR-7**: 每个 bundle 内部的 concepts/、examples/、references/ 之间的交叉链接必须正确带后缀
- **FR-8**: 所有 frontmatter 中的 source 路径（如 `/references/source.md`）必须正确带后缀且可解析

## Non-Functional Requirements
- **NFR-1**: 运行 `python .agents/scripts/check-links.py --path bundles --check-frontmatter-paths` 必须返回零断链（broken_local = 0）、零目录链接警告（warning_local = 0）、零 frontmatter 路径错误（broken_frontmatter = 0）
- **NFR-2**: 所有链接修复不改变链接文本和锚点，仅补充 `.md` 后缀
- **NFR-3**: 入口文件遵循现有 bundle index.md 的风格和格式（参考 tiktoken/index.md）
- **NFR-4**: 文件操作必须原子化，修复过程中不产生中间损坏状态
- **NFR-5**: bundles 目录在不连接外部网络、不依赖本地特定路径（如 d:/AI/）的情况下可完整使用

## Constraints
- **Technical**: 
  - 必须保持 `/` 开头的 bundle-relative 路径约定（这是 OKF 规范，check-links.py 已支持）
  - 不使用 `file:///` 绝对路径
  - 链接修复使用批量替换（正则），但必须精确，避免误伤代码块或示例中的 URL
- **Business**: 修复后不能破坏现有知识包的可读性和导航结构
- **Dependencies**: check-links.py 作为验证工具，Python 环境可用

## Assumptions
- laozi-lineage 和 english-grammar 作为非源码转 wiki 的特殊 bundle，其现有结构可以保留（不强制要求 concepts/examples 分离）
- tiktoken 是最新且格式正确的 bundle，可作为格式参考模板
- `file:///d:/AI/.chaos/...` 路径仅存在于 facts-relax-te-topi.md 中，其他文件无此问题
- 重复的 verification-report.md 内容相同，删除 references/ 下的副本不会丢失信息

## Acceptance Criteria

### AC-1: 零断链
- **Given**: bundles 目录已完成重构
- **When**: 运行 `python .agents/scripts/check-links.py --path bundles --check-frontmatter-paths`
- **Then**: 输出显示 "通过: 所有本地引用均存在"，broken_local = 0，broken_frontmatter = 0
- **Verification**: `programmatic`
- **Notes**: 外部链接检查可选（--check-external），不要求外部链接全部可达

### AC-2: 入口文件存在且可导航
- **Given**: bundles 目录已完成重构
- **When**: 检查 bundles/index.md 和 bundles/chaos/index.md
- **Then**: 两个文件都存在，包含正确的相对链接（带 .md 后缀），可从 bundles 根目录导航到每个 bundle
- **Verification**: `programmatic` + `human-judgment`

### AC-3: 无重复 verification-report.md
- **Given**: bundles 目录已完成重构
- **When**: 检查 mobile-use、okf-ecosystem、veadk-python 三个 bundle
- **Then**: 每个 bundle 根目录有且仅有一个 verification-report.md，references/ 下无重复
- **Verification**: `programmatic`

### AC-4: 无 file:/// 本地绝对路径
- **Given**: bundles 目录已完成重构
- **When**: Grep 搜索 `file:///` 在 bundles 目录下
- **Then**: 零匹配结果（或仅在合理的示例/文档说明中存在，但不指向特定用户本地路径）
- **Verification**: `programmatic`

### AC-5: 链接格式统一
- **Given**: bundles 目录已完成重构
- **When**: 抽样检查 10 个不同 bundle 中的内部链接
- **Then**: 所有链接到 .md 文件的引用都带 `.md` 后缀，无遗漏
- **Verification**: `human-judgment` + `programmatic`

### AC-6: bundles 自包含
- **Given**: bundles 目录已完成重构
- **When**: 检查所有链接的目标路径
- **Then**: 所有本地链接目标都在 bundles/ 目录树内，不指向 bundles/ 外部的本地文件（外部 HTTP/HTTPS 链接除外）
- **Verification**: `programmatic`

## Open Questions
- [ ] bundles/index.md 是否需要列出 vendor/awesome-okf-xs/doc/bundles/ 作为参考？（当前任务仅处理 SpecWeave 根下的 bundles/）
- [ ] 入口文件的 frontmatter 格式是否需要遵循 OKF 规范？（参考 tiktoken 的完整 frontmatter）
