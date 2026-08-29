# docs/ 到 docs/knowledge/ 迁移验证清单

> 状态：全部验证通过（2026-08-23）。任务 1-23 已完成，count_wikis.py 输出 151 与 CATEGORIES.md 统计一致。

## 文件迁移完整性

- [x] 13 个完全缺失的 Wiki 文件夹全部迁移至目标分类目录
- [x] agency-agents-wiki（12 个文件）完整迁移
- [x] cordis-spatiotemporal-composability-wiki（14 个文件）完整迁移
- [x] deepseek-harness-wiki（17 个文件）完整迁移
- [x] okf-kit-wiki（12 个文件）完整迁移
- [x] baidu-unlimited-ocr-wiki（6 个缺失文件）补全
- [x] book-to-skill-wiki（8 个缺失文件）补全
- [x] github-cli-wiki（7 个缺失文件）补全
- [x] minit2i-minimalist-t2i-wiki（6 个缺失文件）补全
- [x] python314-cpython-wiki（14 个缺失文件 + html）补全
- [x] python314-stdlib-wiki（17 个缺失文件）补全
- [x] three-ai-tools-learning-wiki（1 个缺失文件）补全
- [x] open-code-review-wiki 缺失章节（8 个文件）补全
- [x] agent-runtime-protocol-wiki 从单文件扩展为原子化文件夹
- [x] ai-engineering-four-milestones-wiki（6 个缺失文件）补全
- [x] 5 个微信文章分析文件夹全部迁移
- [x] ai-engineering/ 下 2 个知识文件迁移
- [x] algorithmic-art/atomic-emergence/ 2 个文件迁移
- [x] engineering/deep-learning-atomic-design/ 3 个文件迁移
- [x] 15 个方法论模式文件迁移至 retrospective/patterns/
- [x] 18 个复盘报告文件迁移至 retrospective/
- [x] tech/ 下 4 个散落文件迁移
- [x] refactor/ 下 1 个文件迁移
- [x] 3 个 HTML 附属文件迁移至对应 Wiki 目录

## Frontmatter 格式合规

- [x] 所有原子化 Wiki 章节文件 frontmatter 恰好包含 4 个字段（id/title/source/x-toml-ref）
- [x] 无多余字段（version/type/description/category/status/author/summary/date/tags 等不在章节 YAML 中）
- [x] id 命名遵循 `{wiki-name}-{chapter-id}` 约定
- [x] source 字段指向原始 URL 或父文件路径
- [x] x-toml-ref 路径层级计算正确

## TOML 元数据

- [x] 每个原子化 Wiki 文件都有对应的 .meta/toml/ 镜像路径 TOML 文件
- [x] TOML 文件包含 category 字段
- [x] TOML 文件包含 date 字段
- [x] TOML 文件包含 tags 数组
- [x] TOML 文件包含 status 字段
- [x] fix-x-toml-ref.py 验证全部通过

## 链接完整性

- [x] check-links.py 对全部迁移文件零断链（本次会话 5 个 Wiki 目录 323 个本地引用全部有效）
- [x] Wiki 内部章节间相对路径正确（考虑目录深度变化）
- [x] 跨 Wiki 交叉引用路径已更新
- [x] 指向 docs/ 的旧路径引用已更新为 .agents/docs/ 路径
- [x] HTML 文件中的资源引用（如有）路径正确

## 文件命名

- [x] check-filename-convention.py 全部通过
- [x] 所有文件名使用 kebab-case
- [x] 所有文件名纯英文，无中文字符
- [x] 章节编号使用 NN-topic.md 两位数字前缀
- [x] 文件夹命名符合 kebab-case 规范

## README.md 索引

- [x] 每个迁移的 Wiki 文件夹都有 README.md
- [x] README.md 包含文档索引表
- [x] README.md 包含阅读路径建议
- [x] 自动生成的 README 使用标记区域规范
- [x] README.md 中的链接全部有效

## 分类合理性

- [x] 每个 Wiki 的目标分类符合 CATEGORIES.md 主题边界
- [x] 无 Wiki 跨主题重复放置
- [x] 厂商产品 Wiki 归入 07-vendor-product-learning/ 对应子目录
- [x] 协议接口类 Wiki 归入 01-agent-protocols-interfaces/
- [x] 工程方法论类 Wiki 归入 02-agent-engineering-methodology/
- [x] 平台工具类 Wiki 归入 03-agent-platforms-tools/
- [x] 多模态内容类 Wiki 归入 05-ai-multimodal-content/
- [x] 商业趋势类 Wiki 归入 06-business-trends-analysis/
- [x] 系统基础设施类 Wiki 归入 08-systems-infrastructure/
- [x] 通用基础知识类 Wiki 归入 10-foundational-knowledge/

## 索引更新

- [x] CATEGORIES.md 中对应主题 Wiki 清单已追加（含 baidu-ocr-wiki 新增、agent-runtime-protocol-wiki 类型更新）
- [x] CATEGORIES.md 统计数字已更新（count_wikis.py 输出 151，与统计一致）
- [x] learning/README.md 已更新（如需要）
- [x] category-index.md 已更新
- [x] knowledge/README.md 总条目数已更新
- [x] knowledge/README.md 最近更新列表已更新

## 已有内容保护

- [x] 目标目录中已有文件未被覆盖或损坏
- [x] 已有 1288 条目全部保持完整
- [x] 已有分类体系和编号结构未被破坏
- [x] 已有交叉引用未因迁移而断裂

## 非迁移项确认

- [x] Sphinx/Jupyter Book 构建配置文件（conf.py、_config.toml）未迁移
- [x] requirements.txt、tasks.py 未迁移
- [x] _static/ 目录下 CSS/PNG 主题资源未迁移
- [x] docs/index.md（Sphinx 首页）未迁移