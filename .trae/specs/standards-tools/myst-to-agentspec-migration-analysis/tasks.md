# MyST Directives/Roles 在 Agent Spec 中可迁移性技术评估 - The Implementation Plan

## [x] Task 1: 研究准备与代码基线分析
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 精读 MDI Parser 实现（parser.py）中 directives 相关代码（_DIRECTIVE_RE、_parse_directive_content、_extract_interfaces_from_directives、_ADMONITION_TYPES 等关键函数/常量），记录当前支持范围和限制
  - 调研 mdit-py-plugins 的 colon_fence 插件 API 和稳定性（阅读文档、检查 GitHub star、最近 commit、已知 issues）
  - 分析现有 40+ 个 Spec 文档和 14 个 SKILL.md，统计当前使用的 Markdown 语法模式（表格频率、代码块频率、提示块使用频率等）
  - 收集 LLM 对 MyST 语法理解的相关证据（如官方文档、社区讨论、如有测试数据）
- **Acceptance Criteria Addressed**: [AC-2, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 代码分析覆盖 parser.py 中所有 directive 相关函数（行号范围准确记录）
  - `programmatic` TR-1.2: mdit-py-plugins 版本和 colon_fence 插件存在性通过 pip show 验证
  - `human-judgement` TR-1.3: Spec/SKILL 语法模式统计有具体数据支撑（如"表格出现率X%"）
- **Notes**: 代码分析结果作为报告技术论据的基础

## [x] Task 2: 撰写核心概念适配性分析章节（FR-1）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 建立 MyST 概念 → Agent Spec 需求映射矩阵（表格形式），覆盖：Directives 块级扩展、Roles 行内扩展、两种围栏（`:::`/`` ``` ``）、三种选项格式、Arguments 参数、Nesting 嵌套规则、Frontmatter 双格式
  - 逐项分析 10+ 个内置 Directive 在 Agent Spec 中的用途（admonitions/figure/code-block/math/table/list-table/toc/include/dropdown/card/tab-set 等）
  - 逐项分析 8+ 个常见 Role 在 Agent Spec 中的用途（abbr/sub/sup/math/ref/numref/doc/cite/download/link/kbd/file/emphasis/strong/literal 等）
  - 分析两种围栏在 Agent Spec 场景下的适用性差异（编辑器、GitHub、AI 解析三维度）
  - 每个概念标注"高度适配/部分适配/不适配"评级及理由
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 映射矩阵覆盖≥6个核心概念、≥10个Directive、≥8个Role
  - `human-judgement` TR-2.2: 每个条目有适配度评级和具体理由（非空泛判断）
  - `human-judgement` TR-2.3: 包含代码示例或语法示例说明映射关系
- **Notes**: 这是报告的基础章节，其他章节的分析依赖本章结论

## [x] Task 3: 撰写关键技术挑战章节（FR-2）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 解析器扩展挑战：详细分析在 markdown-it-py 上增加冒号围栏、YAML 选项块、Roles 解析的技术方案和复杂度
  - 双格式兼容挑战：directives 与"标题+表格"双模式长期并存的维护成本分析
  - 降级显示挑战：GitHub/IDE/普通阅读器中 MyST 语法的可读性测试和分析
  - AI 理解挑战：基于训练数据分布推断 LLM 对 MyST 语法的理解能力
  - Frontmatter 格式统一挑战：TOML vs YAML 在工具链中的权衡分析
  - 向后兼容挑战：现有文档迁移成本的量化评估（影响文件数、修改类型）
  - 每个挑战包含：问题描述、影响范围、复杂度评级（低/中/高）、潜在解决方向
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 识别≥5个技术挑战
  - `human-judgement` TR-3.2: 每个挑战有具体技术论据（代码引用、API 文档、实测数据）
  - `human-judgement` TR-3.3: 复杂度评级合理（非全部为"中"）
- **Notes**: 引用 parser.py 具体代码行号作为论据

## [x] Task 4: 设计并撰写实施路径方案（FR-3）
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 方案一（保守）：仅补充 YAML 选项块支持，不引入冒号围栏和 Roles
  - 方案二（平衡/推荐）：引入冒号围栏（colon_fence 插件）+ 有限 Roles 集合
  - 方案三（激进）：引入更完整 MyST 解析能力
  - 每个方案包含：具体变更清单（文件/函数级）、新增依赖、性能影响预估、兼容性影响、适用场景、风险评估
  - 给出明确推荐方案和推荐理由（基于 Task 2/3 的分析结论）
  - 绘制实施路径决策树 Mermaid 图
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 3种方案描述完整（变更/依赖/性能/兼容/风险）
  - `human-judgement` TR-4.2: 推荐方案有明确论据支撑
  - `programmatic` TR-4.3: Mermaid 决策树语法正确（可渲染）
- **Notes**: 变更清单应具体到文件/模块级别

## [x] Task 5: 撰写架构兼容性分析章节（FR-4）
- **Priority**: medium
- **Depends On**: Task 1, Task 3
- **Description**:
  - mdit-py-plugins 生态分析：colon_fence、dollarmath、container 等插件可用性和成熟度评估
  - 三类 Profile（Skill/WebApi/CliTool）各自最需要的 Directive/Role 类型分析和建议
  - 代码生成器（python_gen/typescript_gen/openapi_gen/mcp_gen）如何从增强 directives 中提取更多结构化信息
  - Spec 验证器（check-spec-format.py, validator.py）如何利用 directives 做更精确的验证
  - 与 frontmatter.py、markdown.py 等共享库的集成点
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 插件分析有具体版本号和API信息
  - `human-judgement` TR-5.2: 三类Profile的需求分析各有≥2个具体建议
  - `human-judgement` TR-5.3: 代码生成器和验证器的增强点有具体技术描述

## [x] Task 6: 撰写优势与局限性评估（FR-5）
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**:
  - 结构化优势：AI 理解精度提升、自动化验证增强、代码生成质量提升的具体分析
  - 可维护性优势：统一语法 vs 自由格式的长期维护成本对比
  - 生态优势：与 MyST 工具链互操作的可能性和限制
  - 学习曲线局限：开发者学习成本分析（5-10个常用directive的学习曲线评估）
  - 工具链依赖局限：脱离MyST生态后语法可移植性分析
  - 过度工程风险：directive类型过多导致写作负担加重的风险
  - 使用对比表格呈现优势/局限性及权衡
- **Acceptance Criteria Addressed**: [AC-5, AC-9]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 优势和局限性各≥3条
  - `human-judgement` TR-6.2: 每条有具体论据而非主观判断
  - `human-judgement` TR-6.3: 存在明确的权衡分析（不是单纯罗列优缺点）

## [x] Task 7: 撰写场景化建议章节（FR-6）
- **Priority**: medium
- **Depends On**: Task 2, Task 4
- **Description**:
  - 技能定义（SKILL.md）场景：推荐/可选/不推荐的语法元素清单
  - Web API 接口定义场景：endpoint 指令扩展建议
  - CLI 工具定义场景：参数表格 vs param directive 取舍
  - 工作流/协议文档场景：UI组件类directive适用性
  - 协作规范/治理文档场景：admonitions/include/toc适用性
  - 学习资料/Wiki场景：MyST完整语法适用度
  - 每个场景有具体示例代码（正确/错误用法对比）
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 覆盖≥5个场景
  - `human-judgement` TR-7.2: 每个场景有"推荐/可选/不推荐"三级分类
  - `human-judgement` TR-7.3: 包含≥3个正反例对比

## [x] Task 8: 撰写前瞻性洞察章节（FR-7）
- **Priority**: low
- **Depends On**: Task 1, Task 4
- **Description**:
  - MyST 生态演进趋势分析（基于官方文档、GitHub 仓库活跃度、版本发布节奏）
  - AI-native documentation 趋势下结构化标记语言的价值判断
  - MDI 作为 Markdown IDL 的长期演进路径预测
  - 跨 Agent 互操作场景下 MyST 作为标准化格式的潜力
  - 每个观点有论据支撑（官方路线图链接、行业趋势引用、技术类比）
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-8.1: ≥4个前瞻性观点
  - `human-judgement` TR-8.2: 每个观点有论据支撑（非纯主观推测）

## [x] Task 9: 创建Mermaid图表和可视化
- **Priority**: medium
- **Depends On**: Task 2, Task 4
- **Description**:
  - 创建核心概念适配性映射图（Mermaid flowchart/思维导图）
  - 创建实施路径决策树（Mermaid flowchart LR）
  - 创建 MyST→MDI Parser 集成架构图（Mermaid flowchart/组件图）
  - 创建语法对比表格（冒号围栏vs反引号围栏、directives vs 标题+表格）
  - 确保所有 Mermaid 语法正确
- **Acceptance Criteria Addressed**: [AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-9.1: ≥2张Mermaid图表语法正确
  - `human-judgement` TR-9.2: 图表清晰传达信息（非装饰性）

## [x] Task 10: 报告整合、格式规范与自审
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9
- **Description**:
  - 将各章节整合为完整报告文件，输出路径：d:\spaces\SpecWeave\docs\retrospective\reports\standards-tools\myst-to-agentspec-migration-analysis\report.md
  - 添加 TOML frontmatter（title/source/date/category/tags）
  - 添加目录导航和章节间交叉引用
  - 执行自审检查：
    * 占位符扫描（无TBD/TODO/未完成章节）
    * 内部一致性检查（各章节结论无矛盾）
    * 代码引用准确性检查（所有file:///链接路径正确）
    * Mermaid语法验证
    * 字数统计（≥6000字）
    * 客观性检查（无预设立场词汇，优势劣势均陈述）
  - 确保报告中文撰写、格式规范
- **Acceptance Criteria Addressed**: [AC-7, AC-9]
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在于指定路径
  - `programmatic` TR-10.2: TOML frontmatter正确（包含title/source/category/tags/date字段）
  - `programmatic` TR-10.3: 字数≥6000字
  - `human-judgement` TR-10.4: 无TBD/TODO占位符
  - `human-judgement` TR-10.5: 各章节结论逻辑自洽
- **Notes**: 报告目录若不存在需先创建
