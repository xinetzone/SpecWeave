# GraphQL Wiki 教程验证清单

## 目录结构与文件完整性
- [x] graphql-wiki/ 目录已创建在 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/` 下
- [x] 包含 README.md 导航入口文件
- [x] 包含 00-overview.md 总览章节
- [x] 包含 01-core-concepts.md 核心概念章节
- [x] 包含 02-queries.md 查询语言章节
- [x] 包含 03-schema-types.md 类型系统章节
- [x] 包含 04-validation-execution.md 验证与执行章节
- [x] 包含 05-client-basics.md 客户端基础章节
- [x] 包含 06-server-concepts.md 服务端概念章节
- [x] 包含 07-python-ecosystem.md Python 生态章节
- [x] 包含 08-best-practices.md 最佳实践章节
- [x] 包含 11-glossary.md 术语表章节
- [x] 章节总数 ≥ 8 个（不含 README，实际 10 个章节）

## 文档格式规范
- [x] 所有 Markdown 文件包含有效的 YAML frontmatter
- [x] frontmatter 中包含 source 字段，值为 `spec:create-graphql-wiki-tutorial`
- [x] 文件名符合 kebab-case + 数字前缀命名规范（NN-xxx.md）
- [x] 无中文文件名
- [x] 所有交叉引用使用相对路径
- [x] 无 `file:///` 绝对路径引用
- [x] 锚点链接使用 ASCII 格式（显式 `<a id="..."></a>`）

## 内容质量检查
- [x] 教程内容覆盖 GraphQL 核心概念、查询、类型系统、执行、客户端、服务端、Python 工具、最佳实践
- [x] 查询/Schema 相关章节包含 GraphQL 代码示例
- [x] Python 章节包含可运行的 Python 代码片段（Strawberry+FastAPI、gql 客户端）
- [x] 专业术语首次出现有一句话通俗解释
- [x] 术语表包含 ≥15 条核心术语（实际 26 条）
- [x] 每条术语有 plain language 解释
- [x] 内容语言为标准现代汉语书面语
- [x] 无网络流行语、俚语或不规范表达

## 导航与关联
- [x] README.md 包含完整的文档索引表（在 README_INDEX_START/END 标记之间）
- [x] README.md 包含相关资源链接（返回上级、文档首页等）
- [x] 父目录 README 已添加 graphql-wiki 入口链接
- [x] 术语表包含项目内相关 Wiki 的交叉引用（IDL、API/ABI 等）
- [x] 外部引用链接为官方文档 URL，可正常访问

## 收尾验证
- [x] 文件名规范检查脚本通过
- [x] 链接有效性检查通过（无断链）
- [x] 每个章节单文件 ≤ 800 行（原子化）
- [x] 内容与现有 Wiki（ffi-wiki、protobuf-wiki）结构风格一致
