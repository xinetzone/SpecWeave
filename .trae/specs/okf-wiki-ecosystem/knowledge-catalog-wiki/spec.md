# Knowledge Catalog Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 基于 `d:\AI\.chaos\libs\knowledge-catalog` 仓库（Google Cloud Knowledge Catalog，包含OKF开放知识格式规范、参考Agent、示例Bundle、可视化工具、工具箱与样例），在 `d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\knowledge-catalog-wiki` 目录下生成完整的wiki教程，并与现有的 okf-wiki 建立双向链接。
- **Purpose**: 系统梳理Google Knowledge Catalog工具链的完整能力，补充okf-wiki仅覆盖OKF格式规范的不足，为开发者提供从格式规范到工具使用、示例参考的全链路学习材料，完善Agent协议与接口技术栈知识库。
- **Target Users**: AI Agent开发者、知识工程师、数据工程师、架构师、对Google Cloud知识管理生态感兴趣的技术人员。

## Goals
- 基于 knowledge-catalog 仓库的源码、文档和示例，生成结构化的wiki教程（遵循同目录其他wiki的格式约定）
- 新wiki位于 `d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\knowledge-catalog-wiki`
- 在新wiki与现有 okf-wiki 之间建立双向交叉链接
- 更新父目录 README.md，将新wiki加入子Wiki索引
- 所有文档遵循项目现有Markdown规范（YAML frontmatter、相对路径链接、章节编号、导航表等）

## Non-Goals (Out of Scope)
- 不修改 knowledge-catalog 仓库本身的任何代码或文档
- 不重写或大幅修改现有 okf-wiki 的内容（仅添加交叉链接）
- 不运行或部署knowledge-catalog中的任何工具或代码
- 不创建超出wiki教程范围的额外功能（如自动化脚本、工具封装等）
- 不翻译或本地化非中文内容之外的其他语言文档（教程主体使用中文）

## Background & Context
- 现有 okf-wiki 仅覆盖OKF（Open Knowledge Format）格式规范本身，未包含Knowledge Catalog仓库中的参考Agent实现、可视化工具、enrichment/mdcode工具箱、示例Bundle等实践内容
- knowledge-catalog 是Google Cloud官方的开源仓库（原名Dataplex），提供了OKF格式的完整参考实现、生产工具和示例
- 同目录已有多个遵循一致格式约定的wiki教程（agent-skills-wiki、ffi-wiki、okf-wiki等），新wiki需严格遵循这些约定
- 七概念方法论（R-I-E-C-A-F-V）的知识沉淀场景指导本次wiki生成，确保系统性和完整性

## Functional Requirements
- **FR-1**: 创建 `knowledge-catalog-wiki` 目录，包含 README.md 和编号章节文件（遵循现有wiki的原子化结构）
- **FR-2**: README.md 作为wiki入口，包含概述、文档索引表、阅读路径建议、相关资源链接
- **FR-3**: 章节文件覆盖：
  - 00-overview.md: Knowledge Catalog概述、定位、与OKF的关系、核心组件
  - 01-core-components.md: 核心组件详解（OKF规范、参考Agent、Bundle结构、可视化工具）
  - 02-reference-agent.md: 参考Agent架构与使用（enrich命令、BQ pass/Web pass、参数配置）
  - 03-toolbox.md: 工具箱详解（enrichment工具、mdcode工具、MCP服务能力）
  - 04-bundles-and-samples.md: 示例Bundle解析（GA4、StackOverflow、Bitcoin、Acme Retail）
  - 05-visualization.md: 可视化工具使用（viz.html生成、交互功能、Cytoscape.js架构）
  - 06-quickstart.md: 快速入门指南（环境准备、运行第一个enrich、生成可视化）
  - 07-best-practices-and-faq.md: 最佳实践、常见问题、生产使用建议
  - 08-resources-and-glossary.md: 资源链接、术语表、交叉引用
- **FR-4**: 在新wiki的所有相关章节中添加指向 okf-wiki 对应章节的链接
- **FR-5**: 在 okf-wiki 的相关章节（README.md、00-overview.md、05-architecture-and-integration.md、07-resources-and-glossary.md）中添加指向 knowledge-catalog-wiki 的反向链接
- **FR-6**: 更新父目录 `01-agent-protocols-interfaces/README.md`，将新wiki加入子Wiki索引表
- **FR-7**: 所有Markdown文件包含符合项目规范的YAML frontmatter（id、title、category、date、tags、source等字段）
- **FR-8**: 每个章节文件底部包含上一章/目录/下一章的导航链接
- **FR-9**: 术语表对首次出现的专业术语提供一句话通俗解释

## Non-Functional Requirements
- **NFR-1**: 文档风格与同目录其他wiki保持一致（结构、命名、frontmatter格式、链接格式）
- **NFR-2**: 所有相对路径链接正确可访问，无断链
- **NFR-3**: 内容准确反映knowledge-catalog仓库的实际状态，基于源码和官方文档，不臆造功能
- **NFR-4**: 使用标准现代汉语书面语，避免网络流行语，逻辑清晰条理分明
- **NFR-5**: 文件命名使用kebab-case英文，遵循项目文件名规范
- **NFR-6**: 每个章节聚焦单一主题，原子化拆分，避免单文件过长

## Constraints
- **Technical**: 必须使用现有项目的Markdown规范、YAML frontmatter格式、目录结构约定；所有链接使用相对路径；不引入新的依赖或工具
- **Business**: 仅使用本地已有的 knowledge-catalog 仓库内容，不访问外部网络获取额外信息
- **Dependencies**: 依赖现有 okf-wiki 的文件结构和路径；依赖父目录 README.md 的现有格式

## Assumptions
- knowledge-catalog 仓库位于 `d:\AI\.chaos\libs\knowledge-catalog`，内容完整可访问
- 现有 okf-wiki 和父目录 README.md 的格式是权威标准，新wiki必须严格遵循
- 用户希望wiki教程覆盖整个knowledge-catalog工具链，而非仅补充okf-wiki的少量内容
- 双向链接主要在概述、架构、资源等关键章节添加，无需在每个段落都交叉引用

## Acceptance Criteria

### AC-1: 新wiki目录结构完整
- **Given**: 任务执行完成
- **When**: 检查 `knowledge-catalog-wiki` 目录
- **Then**: 存在README.md和00-08共9个章节md文件，遵循编号命名约定
- **Verification**: `programmatic`
- **Notes**: 通过LS工具验证文件存在

### AC-2: 文档格式符合现有规范
- **Given**: 所有wiki文件已创建
- **When**: 检查任意一个文件的frontmatter和结构
- **Then**: 包含完整YAML frontmatter（id/title/category/date/tags/source等），章节结构清晰，底部有导航链接
- **Verification**: `human-judgment`

### AC-3: 双向链接已建立
- **Given**: wiki创建完成
- **When**: 检查新wiki和okf-wiki的相关文件
- **Then**: 新wiki中有指向okf-wiki的链接，okf-wiki中也有指向新wiki的链接，链接路径正确
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 通过Grep搜索链接文本验证

### AC-4: 父目录索引已更新
- **Given**: 所有wiki文件创建完成
- **When**: 检查 `01-agent-protocols-interfaces/README.md`
- **Then**: 子Wiki索引表中包含knowledge-catalog-wiki条目，描述准确
- **Verification**: `human-judgment`

### AC-5: 内容准确覆盖核心组件
- **Given**: wiki内容生成完成
- **When**: 阅读各章节
- **Then**: 覆盖参考Agent、工具箱、示例Bundle、可视化工具、快速入门等核心主题，内容与knowledge-catalog仓库一致
- **Verification**: `human-judgment`

### AC-6: 无断链
- **Given**: 所有链接已添加
- **When**: 检查所有相对路径链接
- **Then**: 所有链接指向的文件/目录存在，无404断链
- **Verification**: `programmatic`

## Open Questions
- 无（基于现有目录结构和用户需求，范围明确）
