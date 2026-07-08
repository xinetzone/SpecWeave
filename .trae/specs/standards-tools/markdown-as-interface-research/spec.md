---
version: 1.0
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/markdown-as-interface-research/spec.toml"
---
# Markdown即接口（Markdown as Interface）深度研究与原型验证 - Product Requirement Document

## Overview
- **Summary**: 对"Markdown文件作为接口定义载体"这一概念进行系统性深度研究，分析其可行性、技术路径、优劣势，并构建包含Markdown接口解析器、规范验证器、多语言代码生成器、测试用例生成器的核心工具链原型，验证该方案在AI Agent工具接口、Web API定义、CLI工具门面等多场景下的实用性和可扩展性。
- **Purpose**: 现有项目中已在AI Skill领域实践"Markdown即接口"模式（六要素模型+L0/L1/L2三层架构，14个Skill验证通过），但该模式尚未通用化，缺乏：（1）跨场景的统一规范；（2）结构化AST解析能力；（3）代码生成与测试自动化工具链；（4）与OpenAPI/MCP等现有生态的互操作方案。本研究旨在将该模式从AI Skill领域推广为通用的接口定义范式。
- **Target Users**: AI Agent开发者、API设计者、工具链工程师、技术文档作者、开源项目维护者

## Goals
- 系统性分析Markdown作为接口定义语言（IDL）的理论可行性与适用边界
- 设计统一的Markdown Interface Specification（MDI Spec）v1.0，覆盖AI Skill、Web API、CLI工具三类场景
- 实现核心工具链原型：解析器（Parser）、验证器（Validator）、代码生成器（Code Generator）、测试生成器（Test Generator）
- 验证MDI Spec与现有生态（OpenAPI、JSON Schema、MCP、Agent Skills开放标准）的互操作性
- 产出完整的研究报告、架构设计文档、可运行原型代码
- 通过至少3个真实场景案例验证原型可用性

## Non-Goals (Out of Scope)
- 不构建生产级别的完整API网关或服务框架
- 不替代OpenAPI/Protobuf/gRPC等成熟IDL在高性能RPC场景的地位
- 不实现复杂的Markdown WYSIWYG编辑器
- 不构建云端托管的接口注册中心
- 不支持所有Markdown扩展语法（如GFM任务列表之外的复杂扩展）
- 不做完整的TypeScript/Python类型系统推导（仅生成基础类型定义）

## Background & Context
- 现有项目已在.agents/skills/目录下有14个SKILL.md文件实践Markdown即接口模式，成熟度L4
- 现有check-skill-quality.py实现了基于正则的SKILL.md结构校验
- 现有lib/frontmatter.py提供YAML frontmatter正则匹配能力
- 现有lib/markdown.py提供基础的标题/描述/链接提取能力
- MDI frontmatter规范：MDI文件使用YAML格式(`---`分隔)作为唯一标准frontmatter格式，不直接支持TOML格式(`+++`分隔)frontmatter；通过`x-toml-ref`扩展字段引用外部TOML文件（如pyproject.toml）并合并元数据，TOML文件路径相对于.md文件所在目录解析，支持`{path, key}`形式指定子键路径
- Agent Skills开放标准（agentskills.io）已定义SKILL.md的最小规范，但缺乏结构化解析和代码生成能力
- 行业趋势：API文档即代码（Docs as Code）、AI可读取接口规范需求增长、MCP（Model Context Protocol）兴起

## Functional Requirements
- **FR-1**: MDI Spec v1.0规范设计
  - FR-1.1: 定义通用接口元数据模型（名称、版本、描述、触发条件、输入/输出、错误码、示例）
  - FR-1.2: 定义Markdown结构到接口模型的映射规则（章节→元素、表格→Schema、代码块→示例、列表→枚举）
  - FR-1.3: 支持多场景配置文件（AI Skill Profile、Web API Profile、CLI Tool Profile）
  - FR-1.4: 定义扩展机制（自定义frontmatter字段、自定义章节类型、自定义验证规则）

- **FR-2**: Markdown Interface Parser（解析器）
  - FR-2.1: 将Markdown文件解析为结构化AST（抽象语法树）
  - FR-2.2: 支持YAML格式frontmatter元数据提取（`---`分隔，唯一标准格式）；明确不支持直接解析TOML格式(`+++`分隔)frontmatter头信息；支持`x-toml-ref`特殊字段引用外部TOML文件（字符串形式指定路径，或`{path, key}`对象形式指定文件和子键路径），将TOML内容合并到元数据中（YAML字段优先级更高覆盖同名字段），TOML文件不存在/格式错误时产生警告而非致命错误，提供详细logging日志便于排查引用失败问题
  - FR-2.3: 支持章节层级解析（H1-H6 → 嵌套节点）
  - FR-2.4: 支持表格解析为结构化数据（参数表、响应表、错误码表）
  - FR-2.5: 支持代码块标注语言类型和用途（` ```python example `、` ```json schema `）
  - FR-2.6: 支持复选框列表作为安全检查清单/验证步骤
  - FR-2.7: 支持Mermaid流程图解析为决策树结构
  - FR-2.8: 输出标准JSON格式的接口模型（MDI Model）
  - FR-2.9: 支持MyST-style directives扩展语法（fenced code block形式，info以`{name}`开头），提供结构化语义块：
    - `{endpoint} METHOD /path`：Web API端点定义，选项`:summary:`、`:tags:`、`:param <name>: type = default - desc`、`:response <code>: schema - desc`、`:error <code>: message - desc`
    - `{note}`/`{warning}`/`{danger}`/`{tip}`：提示/警告块（admonition）
    - directives与传统"标题+表格"格式双模式并存，完全向后兼容现有14个SKILL.md

- **FR-3**: MDI Validator（规范验证器）
  - FR-3.1: 验证frontmatter必填字段完整性
  - FR-3.2: 验证章节结构符合对应场景Profile要求
  - FR-3.3: 验证参数表的类型引用合法性
  - FR-3.4: 验证内部链接有效性（相对路径、锚点）
  - FR-3.5: 验证示例代码块与参数定义的一致性
  - FR-3.6: 输出结构化错误报告（错误级别、位置、修复建议）
  - FR-3.7: 支持CLI调用和Python API两种使用方式

- **FR-4**: Code Generator（代码生成器）
  - FR-4.1: 支持生成Python类型存根（TypedDict/Dataclass）
  - FR-4.2: 支持生成TypeScript类型定义（interface/type）
  - FR-4.3: 支持生成Markdown接口文档（人类友好版）
  - FR-4.4: 支持导出为OpenAPI 3.0格式（Web API场景）
  - FR-4.5: 支持生成MCP Tool定义（JSON Schema格式）
  - FR-4.6: 支持模板自定义（Jinja2）

- **FR-5**: Test Generator（测试用例生成器）
  - FR-5.1: 从参数Schema生成边界值测试用例
  - FR-5.2: 从示例代码块提取可执行测试
  - FR-5.3: 从安全检查清单生成前置/后置验证步骤
  - FR-5.4: 生成pytest（Python）和jest（TypeScript）测试骨架
  - FR-5.5: 支持Mock数据生成

- **FR-6**: 研究报告与文档
  - FR-6.1: 可行性分析报告（优势、局限性、适用场景矩阵）
  - FR-6.2: 技术架构设计文档（含Mermaid架构图、数据流图）
  - FR-6.3: MDI Spec v1.0规范文档
  - FR-6.4: 工具链使用指南
  - FR-6.5: 与现有生态对比分析（OpenAPI/AsyncAPI/JSON Schema/Protocol Buffers）
  - FR-6.6: 版本控制与变更管理最佳实践指南

- **FR-7**: 原型验证案例
  - FR-7.1: 案例1：将现有14个SKILL.md解析为统一MDI Model并生成TypeScript类型
  - FR-7.2: 案例2：定义一个示例Web API（用户管理CRUD），从MDI生成OpenAPI文档和Mock Server
  - FR-7.3: 案例3：定义一个CLI工具接口，生成Python Click/Argparse命令行骨架

## Non-Functional Requirements
- **NFR-1**: 性能：单个Markdown文件（<1000行）解析时间<50ms
- **NFR-2**: 兼容性：Python 3.13+，无强制C扩展依赖，纯Python实现
- **NFR-3**: 可扩展性：插件化架构，支持自定义Profile、自定义代码生成模板、自定义验证规则
- **NFR-4**: 错误容忍：解析器遇到非标准Markdown时降级处理而非崩溃，提供警告
- **NFR-5**: 可测试性：核心模块单元测试覆盖率≥85%
- **NFR-6**: 文档质量：所有公共API有类型注解和docstring
- **NFR-7**: Windows兼容：支持Windows路径分隔符、UTF-8编码、PowerShell环境

## Constraints
- **Technical**: 
  - 基于现有Python技术栈
  - Markdown解析使用markdown-it-py（CommonMark 100%兼容解析器），配合front_matter_plugin（内置YAML头提取）和tasklists_plugin（复选框列表支持），替代原mistune方案
  - 选择理由：(1) 内置frontmatter支持，无需正则提取；(2) 所有block token自带源码行号map；(3) 100% CommonMark合规，解析行为可预测；(4) 丰富的插件生态（mdit-py-plugins提供container/colon_fence/dollarmath等）；(5) 性能实测3.6ms/文件（14个SKILL.md平均），远优于50ms NFR
  - MyST-style directives扩展：通过fenced code block的info字段识别`{name}`前缀的语义块，解析`:key: value`选项语法，支持endpoint/param/response/error/admonition等语义指令
  - 代码生成使用string.Template实现（不引入Jinja2重型依赖），保持纯Python轻量实现
  - TOML解析使用Python 3.13标准库tomllib，用于x-toml-ref外部文件加载
  - 不引入重量级依赖（如不需要完整的Sphinx/docutils工具链或pandoc）
- **Business**: 
  - 研究周期：原型阶段目标在本Spec内完成
  - 产出物必须包含可运行代码，不能仅停留在理论文档
- **Dependencies**:
  - 现有.agents/scripts/lib/共享工具库
  - 现有14个SKILL.md作为测试样本
  - Python标准库 + 可选的轻量第三方库

## Assumptions
- Markdown的章节标题（H1-H6）、表格、代码块、列表、frontmatter等核心语法足够表达接口定义的结构化信息
- AI Agent能够理解并使用MDI Spec定义的接口（已通过现有14个Skill实践初步验证）
- 开发者愿意在"文档即接口"和"严格IDL"之间选择平衡方案
- 现有项目Python环境（3.13+）可满足原型开发需求

## Acceptance Criteria

### AC-1: MDI Spec v1.0规范完整性
- **Given**: 研究阶段完成
- **When**: 评审MDI Spec v1.0文档
- **Then**: 规范包含元数据模型、结构映射规则、3类场景Profile、扩展机制四大部分，且每个部分有≥2个正例和≥1个反例
- **Verification**: `human-judgment`
- **Notes**: 规范文档需经过自洽性检查，无矛盾规则

### AC-2: 解析器能正确解析现有14个SKILL.md
- **Given**: 解析器实现完成
- **When**: 运行解析器批量解析.agents/skills/下所有SKILL.md
- **Then**: 14个文件全部成功解析，无崩溃；输出的MDI Model JSON包含name/version/description/triggers/inputs/steps/checklists等核心字段；字段提取准确率≥95%（人工抽样验证）
- **Verification**: `programmatic`
- **Notes**: 使用现有SKILL.md作为黄金测试集

### AC-3: 验证器能检测SKILL.md质量问题
- **Given**: 验证器实现完成
- **When**: 对合规SKILL.md和故意构造的不合规SKILL.md运行验证器
- **Then**: 合规文件0错误；不合规文件能检测出frontmatter缺失、必填章节缺失、链接无效等问题，每个错误有行号和修复建议
- **Verification**: `programmatic`

### AC-4: Python/TypeScript代码生成可用性
- **Given**: 代码生成器实现完成
- **When**: 从一个包含3个接口的MDI文件生成Python和TypeScript代码
- **Then**: 生成的代码语法正确（可通过Python/TypeScript编译器检查）；类型定义与参数表一致；包含必要的注释
- **Verification**: `programmatic`

### AC-5: OpenAPI导出正确性
- **Given**: Web API场景MDI文件定义完成
- **When**: 使用代码生成器导出OpenAPI 3.0 JSON
- **Then**: 导出的JSON通过OpenAPI Schema校验（使用官方校验器）；可在Swagger UI中正常展示
- **Verification**: `programmatic`

### AC-6: 测试生成器输出可运行测试骨架
- **Given**: 测试生成器实现完成
- **When**: 从MDI文件生成pytest测试文件
- **Then**: 生成的测试文件pytest可收集（无导入错误、语法错误）；包含≥3个测试用例（正常路径、边界值、错误路径）
- **Verification**: `programmatic`

### AC-7: 三个验证案例全部跑通
- **Given**: 工具链原型完成
- **When**: 依次运行案例1（Skill解析）、案例2（Web API→OpenAPI）、案例3（CLI工具生成）
- **Then**: 每个案例有明确的输入MDI文件、执行命令、预期输出、实际结果记录；三个案例全部达到预期结果
- **Verification**: `human-judgment` + `programmatic`

### AC-8: 性能指标达标
- **Given**: 解析器实现完成
- **When**: 对14个SKILL.md文件进行100轮基准测试
- **Then**: 平均解析时间<50ms，p95<100ms
- **Verification**: `programmatic`

### AC-9: 研究报告完整性
- **Given**: 所有研究和原型工作完成
- **When**: 评审研究报告
- **Then**: 报告包含可行性分析、架构设计、优劣势对比、适用场景矩阵、版本控制指南、生态兼容性分析6个核心章节；总字数≥5000字；包含≥5张Mermaid图表
- **Verification**: `human-judgment`

### AC-10: 单元测试覆盖率
- **Given**: 工具链开发完成
- **When**: 运行pytest-cov测量覆盖率
- **Then**: 核心模块（parser/validator/generator）语句覆盖率≥85%，分支覆盖率≥75%
- **Verification**: `programmatic`

## Open Questions (Resolved)
- [x] Markdown解析是否需要引入第三方库？→ 决策：使用markdown-it-py（CommonMark 100%兼容解析器），配合front_matter_plugin和tasklists_plugin；相比mistune优势：内置frontmatter、精确行号map、CommonMark合规、更丰富插件生态；性能实测3.6ms/文件，远优于50ms NFR
- [x] 是否采用MyST语法扩展（directives）？→ 决策：支持MyST-style directives（fenced code block形式`{name}`），提供endpoint/param/response/error/admonition等语义块；directives与传统"标题+表格"格式双模式并存，完全向后兼容现有14个SKILL.md；不引入完整myst-parser（Sphinx扩展，依赖docutils/Jinja2过重），仅借鉴其directive语法设计，在markdown-it-py fence token基础上自行解析
- [x] Mermaid决策树解析深度？→ 决策：v1.0仅提取节点和连接关系，不做语义理解
- [x] 版本控制机制是否需要breaking change检测？→ 决策：v1.0提供结构化diff和变更影响分析，不做自动兼容性判定
- [x] 生成的代码是否需要包含运行时验证逻辑？→ 决策：v1.0仅生成类型存根和接口定义，运行时验证可选
- [x] Frontmatter格式支持？→ 决策：YAML(`---`)为唯一标准格式；不直接支持TOML(`+++`)frontmatter；通过`x-toml-ref`扩展字段引用外部TOML文件
- [x] 代码生成模板引擎？→ 决策：使用string.Template实现，不引入Jinja2重型依赖
