---
version: "1.0"
x-toml-ref: "../../../../.meta/toml/.trae/specs/core-foundation/create-tech-interface-wiki-tutorial/spec.toml"
---
# 技术接口概念Wiki教程 - Product Requirement Document

## Overview
- **Summary**: 创建一份系统性的技术wiki教程，深入解析接口（Interface）、API（应用编程接口）、ABI（应用二进制接口）、协议（Protocol）四个核心技术概念。教程采用原子化文档结构，包含标准定义、核心特征、典型场景、代码示例、对比分析等内容，帮助开发人员建立完整的接口概念体系。
- **Purpose**: 解决开发人员对接口相关概念混淆的问题，明确四个概念的层次关系、适用场景与区别联系，提升技术架构设计与系统集成能力。
- **Target Users**: 软件工程师、架构师、技术学习者、系统集成开发者

## Goals
- 清晰定义四个技术概念的标准内涵与外延
- 每个概念至少包含5个核心技术特征说明
- 每个概念提供多范式/多场景的应用说明
- 提供总计至少8个实际代码/应用案例
- 制作系统的对比分析表格与关联关系图
- 采用原子化文档结构，每个文档单一职责，行数<300行
- 符合项目YAML frontmatter规范，支持索引生成
- 包含参考资料与扩展阅读指引

## Non-Goals (Out of Scope)
- 不涉及具体编程语言的接口语法大全（仅作概念说明用示例）
- 不深入到特定API框架的使用教程（如Spring Boot、Express等）
- 不包含操作系统内核级ABI的深度实现细节
- 不提供网络协议的完整RFC规范解读
- 不替代官方文档或专业教材

## Background & Context
在软件系统架构中，"接口"相关概念是分层设计、模块解耦、系统集成的核心基础。然而开发人员常混淆以下层次：
- 源代码级的Interface（语言抽象）
- 源码/服务级的API（编程契约）
- 二进制级的ABI（编译后兼容）
- 通信级的Protocol（交互规则）

现有技术知识库已有多个wiki教程（agent-skills-wiki、myst-guide等）采用原子化多文件结构，本教程将遵循相同规范，放置于 `docs/knowledge/learning/interface-api-abi-protocol-wiki/` 目录。

## Functional Requirements
- **FR-1**: 创建教程目录与00-overview.md总览文档，包含完整目录结构与阅读指引
- **FR-2**: 编写01-interface.md，详解接口（Interface）概念，包含OOP与函数式编程场景、2+代码案例
- **FR-3**: 编写02-api.md，详解API概念，包含REST/GraphQL/SOAP类型区分、3+主流API案例
- **FR-4**: 编写03-abi.md，详解ABI概念，包含调用约定/内存布局/数据表示说明、1+底层系统案例
- **FR-5**: 编写04-protocol.md，详解协议概念，包含网络协议/软件协议层次、3+主流协议对比
- **FR-6**: 编写05-comparison.md，制作对比表格、关联关系图、架构定位总结
- **FR-7**: 编写06-resources.md，提供参考资料、术语表、扩展阅读建议
- **FR-8**: 所有文档包含正确的YAML frontmatter（id/title/category/tags/date/status/author/summary）
- **FR-9**: 文档间使用双向导航链接（上一章/返回目录/下一章）
- **FR-10**: 关键概念配代码示例（TypeScript/Go/Python/C等多语言示例）
- **FR-11**: 对比分析包含Mermaid关系图展示概念层次

## Non-Functional Requirements
- **NFR-1**: 每个原子文档不超过300行，遵循单一职责原则
- **NFR-2**: 技术术语准确，参考权威来源（如编程语言规范、RFC文档、操作系统手册）
- **NFR-3**: 语言专业准确同时保持可读性，适合初中级到高级开发人员阅读
- **NFR-4**: 所有内部链接使用相对路径，通过链接检查验证
- **NFR-5**: 代码示例可运行或具有明确的说明性，避免伪代码歧义
- **NFR-6**: 遵循项目文档命名规范（kebab-case，数字前缀排序）

## Constraints
- **Technical**: 使用Markdown + Mermaid图表，遵循项目现有wiki格式（参考agent-skills-wiki结构）
- **Business**: 2026-07-03当日完成，无外部依赖
- **Dependencies**: 依赖项目现有知识库结构、generate_index.py索引脚本

## Assumptions
- 读者具备基础编程知识，了解至少一门编程语言
- 文档放置于docs/knowledge/learning/interface-api-abi-protocol-wiki/目录
- 完成后可通过generate_index.py自动纳入知识库索引

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 教程创建完成
- **When**: 查看目标目录
- **Then**: 包含00-overview.md到06-resources.md共7个文件，每个文件<300行
- **Verification**: `programmatic`
- **Notes**: 运行 `python .agents/scripts/check-file-size.py --path docs/knowledge/learning/interface-api-abi-protocol-wiki/` 验证

### AC-2: Interface概念完整
- **Given**: 01-interface.md文档
- **When**: 阅读文档
- **Then**: 包含标准定义、≥5个核心特征、OOP/函数式编程场景、≥2个代码案例
- **Verification**: `human-judgment`

### AC-3: API概念完整
- **Given**: 02-api.md文档
- **When**: 阅读文档
- **Then**: 包含精确定义、REST/GraphQL/SOAP区分、核心特征说明、≥3个主流API案例
- **Verification**: `human-judgment`

### AC-4: ABI概念完整
- **Given**: 03-abi.md文档
- **When**: 阅读文档
- **Then**: 包含二进制接口内涵、与API本质区别、≥3个核心技术特征、≥1个底层系统案例
- **Verification**: `human-judgment`

### AC-5: Protocol概念完整
- **Given**: 04-protocol.md文档
- **When**: 阅读文档
- **Then**: 包含网络/软件协议综合定义、≥3个核心特征、≥3种主流协议对比分析
- **Verification**: `human-judgment`

### AC-6: 对比分析系统
- **Given**: 05-comparison.md文档
- **When**: 阅读文档
- **Then**: 包含对比表格、关联关系分析、架构定位总结、Mermaid层次图
- **Verification**: `human-judgment`

### AC-7: 元数据规范
- **Given**: 所有文档
- **When**: 检查frontmatter
- **Then**: 每个文档包含完整YAML frontmatter，字段正确，category为"learning"
- **Verification**: `programmatic`

### AC-8: 链接有效
- **Given**: 教程完成
- **When**: 运行链接检查
- **Then**: 所有内部相对路径链接有效，无file:///绝对路径断链
- **Verification**: `programmatic`
- **Notes**: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/interface-api-abi-protocol-wiki/` 验证

### AC-9: 双向导航
- **Given**: 所有分章文档（01-05）
- **When**: 检查导航链接
- **Then**: 每个文档包含上一章、返回目录、下一章的双向导航链接
- **Verification**: `human-judgment`

### AC-10: 参考资料完整
- **Given**: 06-resources.md
- **When**: 阅读文档
- **Then**: 包含权威参考资料、术语表、扩展阅读建议
- **Verification**: `human-judgment`

## Open Questions
- [ ] 代码示例语言偏好：是否需要平衡静态类型（Go/TS）与动态类型（Python）示例？
- [ ] Mermaid图类型：除了层次关系图，是否需要添加时序图或调用栈示例？
