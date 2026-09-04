---
title: "OKF知识包完整性修复"
status: "draft"
---

# OKF知识包完整性修复 - Product Requirement Document

## Overview
- **Summary**: 修复 `projects/awesome-okf-xs/doc/bundles` 目录下的3475个断链问题，确保整个知识库自包含、自洽、符合逻辑，不存在无效链接。
- **Purpose**: 当前知识包存在大量链接错误，主要是根路径绝对引用解析问题、跨bundle路径错误、相对路径层级错误，影响文档可读性和Sphinx构建。
- **Target Users**: 知识包读者、文档维护者、Sphinx构建系统。

## Goals
- 修复所有3475个本地断链，将链接错误数降至0
- 确保所有Markdown链接使用正确的相对路径
- 验证Sphinx toctree完整性
- 保持文档结构和内容不变，仅修复链接路径
- 修复后重新运行检查确认零断链

## Non-Goals (Out of Scope)
- 不修改文档正文内容（除链接路径外）
- 不新增或删除文档文件
- 不检查外部URL可达性（本次仅修复本地断链）
- 不重构目录结构
- 不修改frontmatter元数据

## Background &amp; Context
- **现状**：toctree检查通过（因为toctree使用的是相对路径），但内联Markdown链接存在大量错误
- **问题模式识别**：
  1. **根路径错误（Pattern A）**：大量链接使用 `/path/to/file.md` 格式（相对于bundles根目录或bundle根目录），但被check-links.py解析为当前文件目录下的绝对路径
  2. **跨bundle相对路径错误（Pattern B）**：如think/psi下各子bundle互相引用使用错误的相对层级
  3. **跨域引用错误（Pattern C）**：如viz/3b1b/videos引用manim、document/sphinx/alabaster引用其他bundle
  4. **无效引用（Pattern D）**：如think/laozi引用不存在的 `../../../SpecWeave/bundles/laozi-lineage/`
  5. **裸链接/脚注误判（Pattern E）**：个别脚注格式被误识别为链接

## Functional Requirements
- **FR-1**: 修复Pattern A类错误：将以 `/` 开头的"bundle根相对路径"或"bundles根相对路径"转换为正确的相对路径
- **FR-2**: 修复Pattern B类错误：修正think/psi下4个子bundle（psi-core/psi-math/psi-universe/godgpt）之间的交叉引用路径
- **FR-3**: 修复Pattern C类错误：修正跨技术域引用（viz/3b1b内部、document/sphinx内部等）
- **FR-4**: 修复Pattern D类错误：移除或修正指向不存在的laozi-lineage的引用
- **FR-5**: 修复Pattern E类错误：修正误识别的脚注/锚点链接
- **FR-6**: 修复零散的单个文件错误（如python/cpython、meta/okf-spec、document/jupyter等）

## Non-Functional Requirements
- **NFR-1**: 修复后重新运行 `python scripts/check-toctrees.py doc/bundles` 必须通过
- **NFR-2**: 修复后重新运行 `python .agents/scripts/check-links.py --path projects/awesome-okf-xs/doc/bundles` 本地断链数必须为0
- **NFR-3**: 所有修复必须保持文档语义不变，仅修改链接路径部分
- **NFR-4**: 修复过程中不得引入新的断链

## Constraints
- **Technical**: 只能修改Markdown文件中的链接URL部分，不得修改链接文本或其他内容
- **Business**: 知识包是只读引用的最高可信源，修复必须保证准确性
- **Dependencies**: 依赖现有的check-links.py和check-toctrees.py验证脚本

## Assumptions
- 以 `/` 开头的链接，如果目标文件存在于 `doc/bundles/` 下，则视为相对于bundles根目录的路径
- 以 `/` 开头的链接，如果目标文件存在于当前bundle根目录下，则视为相对于当前bundle的路径
- 所有 `concepts/`、`examples/`、`references/` 目录下的文件互相引用时，`/path` 指的是相对于当前bundle根目录
- laozi-lineage内容当前不存在于bundles中，相关引用暂时注释或移除

## Acceptance Criteria

### AC-1: 本地断链清零
- **Given**: 修复完成后
- **When**: 运行 `python .agents/scripts/check-links.py --path projects/awesome-okf-xs/doc/bundles`
- **Then**: 本地文件引用失败数为0
- **Verification**: `programmatic`

### AC-2: Toctree完整性保持
- **Given**: 修复完成后
- **When**: 运行 `python scripts/check-toctrees.py doc/bundles`
- **Then**: 检查通过，全部index.md引用有效，所有内容文档均可达
- **Verification**: `programmatic`

### AC-3: UTF-8编码无破坏
- **Given**: 修复完成后
- **When**: 运行 `python scripts/check-utf8.py doc/bundles`
- **Then**: 所有文件均为有效UTF-8编码
- **Verification**: `programmatic`

### AC-4: 无内容破坏
- **Given**: 修复前后对比
- **When**: 检查git diff
- **Then**: 仅修改了Markdown链接的URL部分，链接文本和正文内容未被修改
- **Verification**: `human-judgment`

## Open Questions
- [ ] laozi-lineage的引用是暂时注释还是应该有其他处理方式？
- [ ] `/` 开头的链接是否有统一的解析规则（相对于bundles根 vs 相对于当前bundle根）？
