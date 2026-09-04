# LongCat-2.0 Agent 能力实测 Wiki Quality Checklist

## 格式规范
- [x] frontmatter 使用 YAML（---）格式，字段完整
- [x] id/title/source/x-toml-ref 字段正确
- [x] 链接使用相对路径，无死链（check-links.py 验证通过）
- [x] 文件名符合 kebab-case 规范，纯英文无中文
- [x] 文件编号正确（00-, 01-, ..., 08-）

## 内容质量
- [x] 核心观点完整保留，无重大遗漏（MoE架构、国产算力、实测结果、效率对比）
- [x] 关键概念解释清晰（MoE、稀疏注意力、loop engineering、Agent原生）
- [x] 章节逻辑连贯，从概念→配置→实战→效率→方法论自然递进
- [x] 代码/命令示例可验证（Claude Code 配置 JSON、API 调用方式）
- [x] 有明确的学习路径（新手→中级→进阶）
- [x] 局限性/注意事项如实说明，不夸大

## 结构完整性
- [x] 包含9个章节（8章节标准结构 + 新增 loop engineering 方法论章节）
- [x] **原子化决策已明确**：spec.md 中记录了"需要拆分"的决策及4项判断依据
- [x] 索引页有完整导航表
- [x] 原子文件结构正确（9个原子文件，数字前缀 00-08）
- [x] FAQ 覆盖常见疑问（8个Q&A）
- [x] 资源链接有效且相关（LongCat平台、原文、官方文档）

## 子代理产出验收5点检查（强制！）
- [x] frontmatter 分隔符正确：使用 `---`（YAML），不是 `+++`（TOML）
- [x] x-toml-ref 存在且路径正确：指向 `.meta/toml/` 镜像路径，相对层级 4 层 `../../../../`
- [x] 标题层级从 h1 开始：文件第一行是 `# 标题`，无跳级
- [x] 文件名合规：kebab-case、纯英文、数字前缀正确（两位数字 00-08）
- [x] source 溯源字段存在：派生产物标注原始来源 URL

## 元数据
- [x] tags 分类准确（longcat, agent, claude-code, moe, loop-engineering, ai-coding, meituan）
- [x] date 字段正确（2026-07-04）
- [x] status 标记正确（draft）
- [x] x-toml-ref 路径正确（4层 `../` 到达项目根目录）

## 内容专项检查
- [x] 01-core-concepts.md：MoE 架构、稀疏注意力、1.6T参数、国产算力训练四项核心概念均覆盖
- [x] 02-claude-code-integration.md：API Key 获取、环境变量配置（含完整 JSON）、模型切换步骤完整
- [x] 03-bi-dashboard-demo.md：需求描述→任务拆解→项目结构→开发过程→报错修复→最终成果，完整流程
- [x] 04-token-efficiency.md：LongCat-2.0（15万）vs Codex+GPT-5.5（22万）对比数据，缓存机制说明
- [x] 05-loop-engineering.md：概念定义、与传统编程对比、在本次实测中的体现
- [x] 08-resources.md：原文链接、LongCat 平台链接、API文档链接、相关 wiki 链接

## 关联更新
- [x] `docs/knowledge/README.md` 知识库索引已更新
- [x] `docs/knowledge/learning/` 目录结构正确
- [x] 本主题 README.md（retrospectives-insights/）已登记新 spec（通过长期看板自动扫描机制）