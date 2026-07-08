---
version: "1.0"
x-toml-ref: "../../../../.meta/toml/.trae/specs/docs-restructure/methodology-patterns-categorization/spec.toml"
---
# 方法论模式主题分类整理 - Product Requirement Document

## Overview
- **Summary**: 对 `docs/retrospective/patterns/methodology-patterns/` 目录下的94个方法论模式文件按照核心主题进行系统性分类整理，创建7个主题子目录，将同主题模式集中存放，更新README索引，生成主题划分说明文档，提升模式库的可发现性和可维护性。
- **Purpose**: 当前94个模式文件平铺在同一目录下，随着模式数量增长，查找和导航变得困难。通过按主题分类组织，可以：（1）降低认知负担，用户可按场景快速定位相关模式；（2）明确主题边界，避免新模式创建时的分类模糊；（3）为后续模式库扩展建立清晰的结构框架。
- **Target Users**: AI智能体开发者、项目维护者、使用可复用模式库的团队成员

## Goals
- 将94个方法论模式文件按照核心主题划分为7个清晰的主题类别
- 为每个主题类别创建独立子目录，实现同主题内容集中存放
- 确保不同主题类别之间界限明确，无交叉重叠
- 更新目录README.md，建立主题导航索引
- 生成主题划分说明文档，详细列出各主题类别定义、边界及包含的具体模式
- 修复因文件移动产生的所有内部链接引用

## Non-Goals (Out of Scope)
- 不修改任何模式文件的内容实质
- 不改变模式文件的命名（除移动到子目录外）
- 不新增或删除任何模式文件
- 不调整架构模式（architecture-patterns）和代码模式（code-patterns）的结构
- 不重新评估或更新模式的成熟度等级
- 不改变模式库的成熟度评估机制

## Background & Context
- methodology-patterns目录目前存放了94个可复用的方法论模式文件，全部平铺在同一层级
- 现有README.md通过Mermaid关系图将模式分为开发流程、文档治理、知识管理、赛事运营四大领域，但仍有大量模式未被归类，且未实现物理目录的分组
- 项目已完成docs-restructure主题下的多次文档重组，具备成熟的文档原子化和分类经验
- 模式库已有成熟的成熟度评估体系（L1-L4），本次分类不影响该体系
- 之前已成功完成reports目录按主题二级分类、insights库重组等类似任务，有可复用的操作流程

## Functional Requirements
- **FR-1**: 在methodology-patterns目录下创建7个主题子目录
- **FR-2**: 将94个模式文件按主题移动到对应子目录
- **FR-3**: 更新methodology-patterns/README.md，建立主题导航索引
- **FR-4**: 创建主题划分说明文档（CATEGORIES.md），详细说明每个主题的定义、边界、包含模式列表
- **FR-5**: 修复所有因文件移动产生的相对路径引用（包括README中的链接、模式文件间的交叉引用）
- **FR-6**: 更新patterns/README.md中的模式统计数字和目录结构说明
- **FR-7**: 更新docs/retrospective/README.md中对methodology-patterns的列举和链接
- **FR-8**: 运行链接检查工具验证所有链接有效性

## Non-Functional Requirements
- **NFR-1**: 分类完成后，所有模式文件的frontmatter元数据保持完整，无丢失或损坏
- **NFR-2**: 移动操作必须保持原子性，避免中间状态导致的断链
- **NFR-3**: 主题命名遵循kebab-case规范，与项目现有命名风格一致
- **NFR-4**: 分类完成后，模式库的可发现性显著提升——通过主题导航查找特定场景模式的路径长度不超过3次点击
- **NFR-5**: 所有跨文件引用100%修复，无断链

## Constraints
- **Technical**: 
  - 必须使用项目现有的文件移动脚本辅助操作
  - 必须使用check-links.py --fix自动修复链接
  - 必须运行finalize-atomization.py完成收尾工作
- **Business**: 
  - 分类必须基于模式内容的核心主题，而非成熟度或来源
  - 不改变任何模式的唯一标识符（id字段）
- **Dependencies**: 
  - 依赖现有的finalize-atomization.py脚本进行断链修复
  - 依赖check-links.py进行链接验证

## Assumptions
- 所有模式文件内容已完整，无需内容修改
- 现有的模式关系图和分类描述可作为分类的主要依据
- 7个主题类别已能覆盖所有现有模式，无需新增"其他"类别
- 文件移动后，Git能够正确识别重命名操作（而非删除+新增）

## Acceptance Criteria

### AC-1: 主题子目录创建完成
- **Given**: methodology-patterns目录当前仅包含README.md和94个平铺的模式文件
- **When**: 执行分类整理
- **Then**: 目录下应存在7个主题子目录，名称符合kebab-case规范
- **Verification**: `programmatic`
- **Notes**: 通过目录列举验证

### AC-2: 所有模式文件正确归类
- **Given**: 7个主题子目录已创建
- **When**: 完成文件移动
- **Then**: 94个模式文件全部位于对应主题子目录中，根目录仅保留README.md和CATEGORIES.md，无遗漏文件
- **Verification**: `programmatic`
- **Notes**: 通过文件计数验证：7个子目录文件数之和=94

### AC-3: 每个模式唯一归属一个主题
- **Given**: 文件移动完成
- **When**: 检查文件分布
- **Then**: 每个模式文件只存在于一个主题子目录中，无重复、无遗漏
- **Verification**: `programmatic`
- **Notes**: 统计每个子目录文件数，总和必须等于94

### AC-4: README.md主题导航索引完整
- **Given**: 文件移动完成
- **When**: 查看更新后的README.md
- **Then**: README应包含7个主题的导航表格，每个主题有简短描述和模式数量统计，并链接到CATEGORIES.md获取详细列表
- **Verification**: `human-judgment`

### AC-5: 主题划分说明文档（CATEGORIES.md）内容完整
- **Given**: 分类完成
- **When**: 查看CATEGORIES.md
- **Then**: 文档应包含：（1）分类原则说明；（2）7个主题的详细定义、核心主题词、边界说明；（3）每个主题下列出所有包含的模式文件（带链接和简要说明）
- **Verification**: `human-judgment`

### AC-6: 所有内部链接正确无误
- **Given**: 文件移动和链接修复完成
- **When**: 运行 `python .agents/scripts/check-links.py --path docs/retrospective/patterns/methodology-patterns`
- **Then**: 检查结果显示0个断链，所有相对路径正确
- **Verification**: `programmatic`

### AC-7: 上层文档引用同步更新
- **Given**: 链接修复完成
- **When**: 检查patterns/README.md和docs/retrospective/README.md
- **Then**: 这两个文件中对methodology-patterns下模式的引用路径已更新为新的子目录结构
- **Verification**: `programmatic`

### AC-8: 跨目录引用验证通过
- **Given**: 所有修复完成
- **When**: 运行全量链接检查
- **Then**: 整个项目中对methodology-patterns下文件的引用全部有效，无断链
- **Verification**: `programmatic`
- **Notes**: 运行 `python .agents/scripts/check-links.py --path docs/retrospective` 验证

### AC-9: 模式元数据完整性保持
- **Given**: 分类完成
- **When**: 抽查若干模式文件的frontmatter
- **Then**: 所有模式文件的TOML frontmatter（id, domain, layer, maturity等字段）保持完整，无损坏
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要在每个主题子目录下创建独立的README.md？（初步决定：不创建，统一在根目录CATEGORIES.md和README.md中维护索引）
