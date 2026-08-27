# GraphQL OKF Wiki 教程 - 验证清单

## R 阶段：事实采集

- [ ] C1: `spec/facts.md` 存在且包含编号事实 F-001 起连续编号
- [ ] C2: 事实覆盖 GraphQL 规范 Section 1（Overview）的全部设计原则
- [ ] C3: 事实覆盖 Section 2（Language）的核心语法产生式（操作、选择集、字段、参数、片段、变量）
- [ ] C4: 事实覆盖 Section 3（Type System）的全部类型种类（Scalar/Object/Interface/Union/Enum/Input Object/List/NonNull）
- [ ] C5: 事实覆盖 Section 4（Introspection）的 __schema、__type、__typename 内省字段
- [ ] C6: 事实覆盖 Section 5（Validation）的主要验证规则类别
- [ ] C7: 事实覆盖 Section 6（Execution）的执行阶段（ExecuteSelectionSet→ExecuteField→CompleteValue）
- [ ] C8: 事实覆盖 Section 7（Response）的 data/errors/extensions 结构
- [ ] C9: 事实包含 AI WG MCP server.py 中的类名、方法签名和 MCP 工具定义
- [ ] C10: 事实包含 schema_indexer.py 的核心功能描述
- [ ] C11: 事实包含 semantic-introspection.md RFC 的核心提议
- [ ] C12: 事实包含官网 Python 客户端库和服务端库列表
- [ ] C13: G1 质量门——事实中无"用于"/"目的是"/"设计为"等推断性表述
- [ ] C14: 每条事实包含信源定位（章节名称、文件路径或 URL）

## I 阶段：架构洞察

- [ ] C15: `spec/insights.md` 存在且包含 3-5 个核心洞察
- [ ] C16: 每个洞察包含四元组：陈述、证据（引用 F-xxx 编号）、反常识、行动
- [ ] C17: 知识地图将概念文档分为入门/核心/高级三组
- [ ] C18: 每个计划的概念文档映射了至少 3 条相关事实编号
- [ ] C19: 文档编号形成连续学习路径（00→NN）
- [ ] C20: G2 质量门——洞察四元组完整，知识地图有明确学习路径

## E 阶段：文档生成（信源先行）

- [ ] C21: `bundles/graphql/graphql/` 目录存在，包含 concepts/、examples/、references/ 子目录
- [ ] C22: references/ 信源文件在 concepts/ 内容文件之前生成（信源先行原则）
- [ ] C23: references/ 包含覆盖 Section 1-7 的信源文件（约 7 个）
- [ ] C24: references/ 包含 AI WG MCP 信源文件
- [ ] C25: references/ 包含 Python 生态信源文件
- [ ] C26: 每批生成文档数 ≤ 7（分批生成原则）

## E 阶段：概念文档

- [ ] C27: concepts/ 包含 00-overview.md（GraphQL 概述与设计原则）
- [ ] C28: concepts/ 包含查询语言基础文档（操作/选择集/字段/参数/别名/片段/变量）
- [ ] C29: concepts/ 包含 Schema 基础文档
- [ ] C30: concepts/ 包含完整类型系统文档（覆盖全部类型种类）
- [ ] C31: concepts/ 包含指令系统文档（@skip/@include/@deprecated + 自定义指令）
- [ ] C32: concepts/ 包含验证规则文档
- [ ] C33: concepts/ 包含执行引擎文档
- [ ] C34: concepts/ 包含内省系统文档
- [ ] C35: concepts/ 包含响应格式文档
- [ ] C36: concepts/ 包含 Python 生态文档（客户端+服务端库选型）
- [ ] C37: concepts/ 包含 GraphQL + AI 文档（MCP/语义内省）
- [ ] C38: 每个概念文档 500-5000 字
- [ ] C39: 每个概念文档使用 ## 二级标题分节，不使用 # 一级标题
- [ ] C40: 每个概念文档结尾有"## 相关概念"章节

## E 阶段：示例文档

- [ ] C41: examples/ 包含第一个 GraphQL 查询示例
- [ ] C42: examples/ 包含 Schema 设计实战示例
- [ ] C43: examples/ 包含 Python 客户端示例
- [ ] C44: examples/ 包含 Python 服务端示例
- [ ] C45: 每个示例包含完整可运行代码（非零散片段）
- [ ] C46: GraphQL 代码块标注 `graphql`，Python 代码块标注 `python`，JSON 标注 `json`

## E 阶段：Index 与 Log

- [ ] C47: index.md（bundle 根）在所有内容文档之后生成（Index 最后写原则）
- [ ] C48: 根 index.md frontmatter 包含 `okf_version: "0.2"`
- [ ] C49: 根 index.md 包含完整知识地图导航（分组列出 concepts/examples/references）
- [ ] C50: concepts/index.md 存在且无 frontmatter
- [ ] C51: examples/index.md 存在且无 frontmatter
- [ ] C52: references/index.md 存在且无 frontmatter
- [ ] C53: 每个子目录 index.md 列出该目录下所有 .md 文件
- [ ] C54: log.md 存在且记录创建日期

## Frontmatter 合规

- [ ] C55: 每个非 index .md 文件包含 `type` 字段（concept/example/reference）
- [ ] C56: 每个内容文档包含 `title` 字段
- [ ] C57: 每个内容文档包含 `description` 字段
- [ ] C58: 每个内容文档包含 `sources` 字段，指向已存在的 references/ 文件或源码路径
- [ ] C59: type 字段值小写（concept/example/reference）

## 交叉链接

- [ ] C60: 所有内部交叉链接使用 `/` 开头的 bundle-relative 路径（如 `/concepts/04-type-system.md`）
- [ ] C61: 无 `../` 相对路径风格的交叉链接
- [ ] C62: 所有交叉链接的目标文件实际存在（无断裂链接）

## V 阶段：事实核验（G4 质量门）

- [ ] C63: 文档中引用的所有 GraphQL 内建标量类型（String/Int/Float/Boolean/ID）与规范一致
- [ ] C64: 文档中引用的所有内建指令（@skip/@include/@deprecated）与规范一致
- [ ] C65: 文档中引用的内省类型和字段（__Schema/__Type/__Field/__TypeKind/__Directive等）与 Section 4 一致
- [ ] C66: MCP 文档中的 Python 类名/方法名/工具名可在 ai-wg/mcp/ 源码中 Grep 验证存在
- [ ] C67: Python 生态文档中的库名称与官网 tools-and-libraries 页面一致
- [ ] C68: 无虚构的 GraphQL 类型、字段、指令或 API
- [ ] C69: 代码示例中的 GraphQL 语法符合 Appendix C Grammar Summary
- [ ] C70: 检查报告中无未修复的 🔴 级别（虚构内容）问题

## 中文与术语

- [ ] C71: 正文使用中文撰写
- [ ] C72: 英文技术术语首次出现时有括号注释（如"内省（Introspection）"）
- [ ] C73: 文件名使用 kebab-case 英文命名

## 安全与边界

- [ ] C74: 未修改 external/libs/GraphQL/ 下的任何文件
- [ ] C75: 未修改 projects/awesome-okf-xs/ 中除 bundles/graphql/ 外的其他文件
- [ ] C76: 未修改 projects/awesome-okf-xs/bundles/index.md 总索引（除非用户要求）
