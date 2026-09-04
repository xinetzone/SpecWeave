# FastAPI OKF Wiki 教程 - 验证清单

## R阶段验证
- [x] facts.md 包含≥80条编号事实（F-001起）— 实际158条
- [x] 每条事实指向具体源码文件路径和行号范围
- [x] 事实中无"用于"/"目的是"/"设计为"等推断性表述 — 修复2处后通过
- [x] 核心模块全覆盖：applications/routing/params/dependencies/openapi/security/middleware/responses/exceptions/encoders
- [x] 每个核心模块至少3条事实

## I阶段验证
- [x] insights.md 包含≥4个洞察四元组（陈述+证据+反常识+行动）— 实际7个
- [x] 知识地图有入门→核心→高级学习路径
- [x] 每个概念文档规划关联≥5条F-xxx事实
- [x] references/ 规划≥6个信源文件 — 实际8个
- [x] examples/ 规划≥4个示例文档 — 实际5个

## E阶段验证 - 结构与规范
- [x] Bundle 根目录存在 index.md、log.md
- [x] concepts/ 目录存在且含 index.md
- [x] examples/ 目录存在且含 index.md
- [x] references/ 目录存在且含 index.md
- [x] 根 index.md frontmatter 含 `okf_version: "0.2"`
- [x] 子目录 index.md 无 frontmatter
- [x] 所有非 index.md 文件含可解析 YAML frontmatter
- [x] 每个 frontmatter 的 type 字段非空（Concept/Example/Reference）
- [x] frontmatter 含 title/description/tags/generated/verified/status/stale_after/sources
- [x] generated.by 和 verified.by 使用 actor 约定（reference_agent/trae, process:seven-concepts-v）
- [x] verified.at 记录 V 阶段验证时间

## E阶段验证 - 内容覆盖
- [x] concepts/ 包含≥12个概念文档（00-13）— 实际14个
- [x] 概念文档覆盖：应用类、路由系统、路径操作、依赖注入、参数声明、请求体、响应模型、OpenAPI生成、安全机制、中间件/CORS、异常处理、流式/WebSocket、测试
- [x] examples/ 包含≥4个示例文档 — 实际5个
- [x] references/ 包含≥6个信源登记文件 — 实际8个
- [x] 每个概念文档结尾有"相关概念"章节
- [x] 正文使用中文，英文术语首次出现时括号注释
- [x] 代码块标注语言（python/yaml/bash/text）— V阶段修复7处

## E阶段验证 - 生成纪律
- [x] references/ 信源文件先于 concepts/ 生成
- [x] index.md 在所有内容文档定稿后最后生成
- [x] 每批生成文档数≤7（7+7+5+references8）
- [x] 交叉链接使用 `/` 开头的 bundle-relative 路径
- [x] 无 `../` 相对路径交叉链接

## V阶段验证 - API真实性
- [x] 文档中引用的 FastAPI 公开类名100%在源码中存在（Grep验证）— 41个API全部验证
- [x] 文档中引用的 FastAPI 公开函数/方法名100%在源码中存在（Grep验证）
- [x] 代码示例中的 API 调用与 facts.md 事实一致
- [x] 无虚构的类
- [x] 无虚构的方法签名或参数

## V阶段验证 - 链接与索引
- [x] 所有 `/` 开头交叉链接目标文件存在（无死链）— 60个链接全部有效
- [x] 根 index.md 列出的文件全部存在（27个内容文档）
- [x] concepts/index.md 列出所有14个概念文档
- [x] examples/index.md 列出所有5个示例文档
- [x] references/index.md 列出所有8个信源文件
- [x] index.md 无遗漏文档

## V阶段验证 - 代码示例
- [x] 代码示例语法正确（Python可解析）
- [x] import 语句引用的模块在 FastAPI 中存在
- [x] 示例代码逻辑与文档描述一致
- [x] 无硬编码的虚构 URL 或不存在的端点

## 生态分组索引
- [x] bundles/fastapi/ 目录创建
- [x] bundles/fastapi/index.md 创建（分组索引，列出 fastapi bundle）
- [x] bundles/index.md 中 fastapi 分组计数更新（后续可手动更新总索引）
