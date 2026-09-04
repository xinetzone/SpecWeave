# GraphQL OKF Wiki 教程 - 实施计划（分解与优先级任务清单）

> 方法论：source-code-to-okf-wiki 五阶段（R→I→E→V→C）+ seven-concepts-cmd 知识沉淀场景（R→I→E 链路）
> 目标路径：`projects/awesome-okf-xs/bundles/graphql/graphql/`

---

## [x] Task 1: R 阶段——GraphQL 规范文档事实采集（Section 1-4）

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 通读 `external/libs/GraphQL/graphql-spec/spec/` 下 Section 1（Overview）、Section 2（Language）、Section 3（Type System）、Section 4（Introspection）
  - 提取可验证事实：设计原则列表、语法产生式规则、类型系统分类（Scalar/Object/Interface/Union/Enum/Input Object/Directive）、内省查询字段（__schema/__type/__typename）
  - 每条事实编号 F-001 起，记录所属章节和关键术语
  - 写入 `bundles/graphql/graphql/spec/facts.md`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-1.1: 事实清单覆盖 Section 1-4 的所有主要小节，无遗漏核心定义
  - `human-judgement` TR-1.2: 每条事实无"用于"/"目的是"/"设计为"等推断词，只陈述"规范里写了什么"
  - `programmatic` TR-1.3: 每条事实包含信源定位（章节名称或文件路径）
- **Notes**: 规范文档是 Markdown 格式，事实来源标注为"Section X -- Y"而非代码行号

## [x] Task 2: R 阶段——GraphQL 规范文档事实采集（Section 5-7 + Appendix）

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 通读 Section 5（Validation）、Section 6（Execution）、Section 7（Response）以及 Appendix C（Grammar Summary）
  - 提取验证规则类别、执行引擎流程（Execute→ExecuteSelectionSet→ExecuteField→CompleteValue）、响应格式（data/errors/extensions）、错误对象结构
  - 继续编号 F-xxx，追加到 `spec/facts.md`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-2.1: 事实清单覆盖验证规则的主要类别和执行引擎的核心阶段
  - `human-judgement` TR-2.2: 响应格式事实包含 data/errors/extensions 三个顶级键的规范定义
  - `programmatic` TR-2.3: 事实编号连续无重复
- **Notes**: Section 6 Execution 是规范最长的章节，重点关注字段解析、错误传播、结果合并算法

## [x] Task 3: R 阶段——AI WG MCP 源码事实采集

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 通读 `external/libs/GraphQL/ai-wg/mcp/` 下的 server.py、schema_indexer.py、schema.graphql、test_graphql_server/server.py
  - 阅读 `external/libs/GraphQL/ai-wg/rfcs/semantic-introspection.md`
  - 提取 Python 源码事实：类名、方法签名、参数、数据流、MCP 工具定义；提取 RFC 核心提议
  - 追加编号事实到 `spec/facts.md`
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 所有引用的 Python 类名/方法名可在源码文件中通过 Grep 验证存在
  - `human-judgement` TR-3.2: MCP 服务器暴露的工具列表完整且与 server.py 中的注册一致
  - `human-judgement` TR-3.3: semantic-introspection RFC 的核心动机和提议被准确概括
- **Notes**: 这是唯一有传统源码的子模块，V 阶段需对 Python API 做 Grep 级验证

## [x] Task 4: R 阶段——官网生态信息采集

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 抓取 graphql.org 首页、learn/introduction、community/tools-and-libraries（Python client/server）、resources/backend、resources/frontend、ai/ 页面内容
  - 提取 Python 客户端库列表（名称、简介、URL）、Python 服务端库列表（名称、简介、URL）、AI 专题关键信息
  - 追加编号事实到 `spec/facts.md`
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `human-judgement` TR-4.1: Python 客户端和服务端库列表与官网页面一致
  - `programmatic` TR-4.2: 每个库条目包含名称和可访问的 URL
- **Notes**: 使用浏览器工具或 WebFetch 抓取页面；若网络不可达则基于已知信息标注"待网络验证"

## [x] Task 5: I 阶段——架构洞察与知识地图设计

- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**:
  - 基于全部 F-xxx 事实，提炼 3-5 个核心架构洞察（四元组：陈述/证据/反常识/行动）
  - 设计知识地图：概念文档分三组（入门篇/核心篇/高级篇），确定文件编号和标题
  - 确定每个概念文档覆盖哪些 F-xxx 事实
  - 确定 examples/ 和 references/ 文件清单
  - 写入 `spec/insights.md`
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-5.1: 3-5 个洞察每个都有四元组（陈述/证据引用 F-xxx/反常识/行动指导）
  - `human-judgement` TR-5.2: 知识地图有明确的学习路径顺序（00→NN），文档间依赖关系清晰
  - `human-judgement` TR-5.3: 每个计划中的概念文档都映射了至少 3 条相关事实
- **Notes**: G2 质量门；洞察指导 E 阶段的文档组织结构

## [x] Task 6: E 阶段——创建 Bundle 目录结构与 references/ 信源文件

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 创建 `bundles/graphql/graphql/` 及子目录 `concepts/`、`examples/`、`references/`
  - **信源先行**：生成 references/ 下所有信源登记文件，每个文件对应一个或多个规范章节/源码文件
  - 预期信源文件（约 7-9 个）：
    - `spec-overview.md`（Section 1）
    - `spec-language.md`（Section 2）
    - `spec-type-system.md`（Section 3）
    - `spec-introspection.md`（Section 4）
    - `spec-validation.md`（Section 5）
    - `spec-execution.md`（Section 6）
    - `spec-response.md`（Section 7）
    - `ai-wg-mcp.md`（MCP 源码 + RFC）
    - `python-ecosystem.md`（官网工具库列表）
- **Acceptance Criteria Addressed**: AC-3, AC-9
- **Test Requirements**:
  - `programmatic` TR-6.1: references/ 目录存在且包含所有计划的信源文件
  - `human-judgement` TR-6.2: 每个信源文件有 `type: reference` frontmatter 和 `sources` 字段
  - `human-judgement` TR-6.3: 信源文件准确登记对应章节的关键事实和术语
- **Notes**: references/ 必须在 concepts/ 之前生成（信源先行原则）；每批≤7文件，可分两批

## [x] Task 7: E 阶段——生成 concepts/ 入门篇概念文档（批次 1）

- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 按知识地图生成入门篇概念文档（约 4-5 个），每批≤7：
    - `00-overview.md` — GraphQL 概述、设计原则、与 REST 的对比
    - `01-query-language.md` — 查询语言基础（query/mutation/subscription、字段、参数、别名、片段、变量）
    - `02-schema-basics.md` — Schema 基础（type/Query/Mutation/字段定义/标量类型）
    - `03-first-schema.md` — 第一个 Schema 设计（类型定义、Resolver 概念）
  - 每个文档包含完整 frontmatter（type: concept, title, description, sources 指向 references/）
  - 开头概述，## 分节，结尾"## 相关概念"
- **Acceptance Criteria Addressed**: AC-4, AC-7, AC-9
- **Test Requirements**:
  - `programmatic` TR-7.1: 每个文件有 `type: concept` frontmatter，sources 指向已存在的 references/ 文件
  - `human-judgement` TR-7.2: 内容与 facts.md 中对应事实一致，无虚构的类型/字段/指令
  - `programmatic` TR-7.3: 交叉链接使用 `/concepts/xx.md` 或 `/references/xx.md` 格式，无 `../`
  - `human-judgement` TR-7.4: 文档结尾有"## 相关概念"章节
- **Notes**: GraphQL 代码块标注 `graphql`，响应示例标注 `json`

## [x] Task 8: E 阶段——生成 concepts/ 核心篇概念文档（批次 2）

- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 生成核心篇概念文档（约 4-5 个）：
    - `04-type-system.md` — 完整类型系统（Scalar/Object/Interface/Union/Enum/Input Object/List/NonNull）
    - `05-directives.md` — 指令系统（@skip/@include/@deprecated、自定义指令）
    - `06-validation.md` — 验证规则（字段选择、参数、片段、指令验证等）
    - `07-execution.md` — 执行引擎（解析管线、字段完成、错误传播、Mutation 顺序）
    - `08-introspection.md` — 内省系统（__schema/__type/__typename、内省查询）
- **Acceptance Criteria Addressed**: AC-4, AC-9
- **Test Requirements**:
  - `programmatic` TR-8.1: frontmatter 完整，sources 指向 references/ 中对应信源
  - `human-judgement` TR-8.2: 类型系统覆盖规范定义的全部 8 种类型 + List/NonNull 包装类型
  - `human-judgement` TR-8.3: 执行引擎章节描述的阶段顺序与 Section 6 规范一致
  - `programmatic` TR-8.4: 交叉链接格式正确
- **Notes**: 这是知识密度最高的一批，特别是类型系统和执行引擎

## [x] Task 9: E 阶段——生成 concepts/ 高级篇概念文档（批次 3）

- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 生成高级篇概念文档（约 3-4 个）：
    - `09-response-format.md` — 响应格式（data/errors/extensions、错误对象、路径）
    - `10-python-ecosystem.md` — Python 生态全景（客户端库对比、服务端库对比、选型指南）
    - `11-graphql-and-ai.md` — GraphQL + AI（MCP 服务器架构、Schema 索引器、语义内省 RFC、AI WG 方向）
  - 视洞察决定是否增加 `12-best-practices.md`（最佳实践/反模式）
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-9
- **Test Requirements**:
  - `human-judgement` TR-9.1: Python 生态章节中库名称和描述与官网列表一致
  - `programmatic` TR-9.2: MCP 服务器描述中的类名/方法名可在 server.py 中 Grep 验证
  - `human-judgement` TR-9.3: 语义内省 RFC 描述准确反映文档核心提议
  - `programmatic` TR-9.4: 所有文档 frontmatter 和交叉链接合规
- **Notes**: Python 生态基于官网信息，不深入每个库源码；MCP 部分需要源码级准确

## [x] Task 10: E 阶段——生成 examples/ 示例文档

- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 生成示例文档（约 4-5 个）：
    - `first-query.md` — 第一个 GraphQL 查询（含 Schema、query、响应、变量、别名、片段）
    - `schema-design.md` — Schema 设计实战（类型定义、关系建模、接口/联合、分页）
    - `python-client.md` — Python 客户端实战（gql 库：查询、变更、订阅、错误处理）
    - `python-server.md` — Python 服务端实战（Strawberry/Ariadne 选型 + 完整可运行示例）
  - 每个示例文档 frontmatter type: example，包含完整可运行代码
- **Acceptance Criteria Addressed**: AC-7, AC-9
- **Test Requirements**:
  - `human-judgement` TR-10.1: 每个示例包含完整代码（非零散片段），可独立理解
  - `human-judgement` TR-10.2: GraphQL 示例语法符合规范（可通过对照语法产生式核验）
  - `human-judgement` TR-10.3: Python 示例的 import 语句和 API 调用与 facts.md 中库信息一致
  - `programmatic` TR-10.4: frontmatter 和交叉链接合规
- **Notes**: 代码块标注正确语言；Python 示例基于稳定版 API

## [x] Task 11: E 阶段——生成各级 index.md 和 log.md

- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - **最后生成**各级 index.md（Index 最后写原则）：
    - `concepts/index.md` — 列出所有概念文档，按编号排序，无 frontmatter
    - `examples/index.md` — 列出所有示例文档，无 frontmatter
    - `references/index.md` — 列出所有信源文件，无 frontmatter
    - `index.md`（bundle 根）— 含 `okf_version: "0.2"` frontmatter，完整知识地图导航
  - 生成 `log.md` 记录创建日期和内容概要
- **Acceptance Criteria Addressed**: AC-9, AC-11
- **Test Requirements**:
  - `programmatic` TR-11.1: 根 index.md 包含 `okf_version: "0.2"` in frontmatter
  - `programmatic` TR-11.2: 子目录 index.md 不含 frontmatter
  - `programmatic` TR-11.3: 每个 index.md 列出的文件都实际存在，无遗漏无多余
  - `human-judgement` TR-11.4: 根 index.md 的知识地图描述清晰，分组合理
- **Notes**: 这是 E 阶段最后一步，确保 index 与实际文件 100% 一致

## [x] Task 12: V 阶段——结构与格式审查

- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 目录结构完整性检查（concepts/examples/references/spec 各目录和文件）
  - Frontmatter 检查：每个非 index .md 文件有 type 字段，根 index 有 okf_version
  - 交叉链接检查：所有 `/` 开头链接的目标文件存在，无 `../` 风格链接
  - Index 完整性检查：列出的文件均存在，存在的文件均被列出
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-12.1: 无断裂链接（Glob/Grep 验证）
  - `programmatic` TR-12.2: 每个内容文档有非空 type 字段
  - `programmatic` TR-12.3: 无 `../` 相对路径交叉链接
- **Notes**: 此阶段可委派给独立 subagent 做黑盒验证

## [x] Task 13: V 阶段——事实溯源与虚构内容检测

- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 对文档中出现的每个 GraphQL 内建类型名（String/Int/Boolean/ID/Float/Object/Interface/Union/Enum/InputObject）、指令名（@skip/@include/@deprecated）、内省字段（__schema/__type/__typename）对照 facts.md 核验
  - 对 MCP 相关文档中的 Python 类名/方法名/工具名，在 `ai-wg/mcp/` 源码中 Grep 验证存在性
  - 对 Python 生态文档中的库名称，与官网页面和 facts.md 交叉核验
  - 检查代码示例中的 GraphQL 语法是否符合 Appendix C Grammar Summary
  - 输出检查报告，按严重程度分类（🔴虚构/🟡不准确/🟢格式），逐一修复
- **Acceptance Criteria Addressed**: AC-8, AC-6
- **Test Requirements**:
  - `programmatic` TR-13.1: MCP Python API 100% Grep 验证通过
  - `human-judgement` TR-13.2: 所有 GraphQL 内建类型/指令/内省字段与规范一致
  - `human-judgement` TR-13.3: 检查报告中无未修复的 🔴 级别问题
- **Notes**: G4 质量门——最关键检查；发现>1个虚构API时需全面复查

## [x] Task 14: V 阶段——代码示例审查与最终修复

- **Priority**: medium
- **Depends On**: Task 13
- **Description**:
  - 审查 examples/ 中所有代码示例的完整性和正确性
  - GraphQL 示例：查询语法、Schema 定义语法、响应 JSON 结构
  - Python 示例：import 语句、类实例化、方法调用签名
  - 修复 TR-13 中发现的所有问题
  - 修复后重新运行结构检查确认无回归
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `human-judgement` TR-14.1: 所有代码示例语法正确
  - `programmatic` TR-14.2: 修复后结构检查无新增断裂链接或格式问题
- **Notes**: 修复时只改必要内容，不做额外重构

## [x] Task 15: C 阶段——模式沉淀与流程复盘

- **Priority**: low
- **Depends On**: Task 14
- **Description**:
  - 回顾 R/I/E/V 各阶段的顺利点和问题点
  - 记录本次"规范文档型"源码（非传统编程语言源码）的 OKF Wiki 生成经验
  - 若发现新的反模式或改进点，记录为经验（不强制入库 patterns/，因本次主要在子项目内操作）
- **Acceptance Criteria Addressed**: N/A（过程改进任务）
- **Test Requirements**:
  - `human-judgement` TR-15.1: 记录至少 3 条本次实践的经验教训
- **Notes**: C 阶段在本项目中为轻量复盘，不强制更新主仓库 patterns/ 目录
