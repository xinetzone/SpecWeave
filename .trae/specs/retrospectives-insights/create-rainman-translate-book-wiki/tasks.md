# Rainman Translate Book Wiki 教程 Tasks

## L1 内容提取
- [x] 使用 defuddle 提取原始网页内容
- [x] 验证提取质量，去除噪音（导航、广告、评论区）
- [x] 保存干净文本作为参考

## L2 内容分析
- [x] 通读网页内容，标记核心观点（3-5 条）
- [x] 识别关键概念：并行子代理翻译、术语表锁定（glossary.json）、相邻上下文、断点续传（run_state.json/manifest.json）、多格式输出流水线
- [x] 梳理逻辑结构：项目介绍 → 工作原理 → 5 大功能详解 → 安装部署 → 使用流程 → 评价与局限性
- [x] 验证内容完整性，确认无遗漏关键信息

## L3 结构设计
- [x] 完成 spec.md（含 DoD 完成定义）
- [x] **原子化决策**：内容预计约 300+ 行，章节独立性高（各功能可单独阅读），决定采用原子化拆分（索引页 + 目录 + 数字前缀原子文件）
- [x] 设计 8 章节原子文件结构：
  - 00-overview.md（概述与学习目标）
  - 01-core-concepts.md（核心功能：并行翻译/术语表/相邻上下文/断点续传/多格式输出）
  - 02-installation.md（安装部署：Claude Code CLI/Calibre/Pandoc/Python/Skill）
  - 03-usage.md（使用流程：翻译一本书/指定封面/修改术语表重译）
  - 04-limitations.md（局限性与注意事项）
  - 05-summary.md（总结与回顾）
  - 06-faq.md（常见问题 FAQ）
  - 07-resources.md（资源链接）
- [x] 拆分内容到各章节
- [x] 完成 checklist.md（含子代理验收 5 点检查）

## L4 文档生成（首次提交：内容创作提交）
- [x] 创建 wiki 目录 `docs/knowledge/learning/rainman-translate-book-wiki/`
- [x] 创建索引页 `rainman-translate-book-wiki.md`（含导航表格，无深度内容）
- [x] 创建所有 8 个原子文件并添加 YAML frontmatter
- [x] 填充各章节内容
- [x] 添加内部链接和导航表
- [x] **子代理产出验收**：按 5 点检查清单逐项验证 frontmatter 格式
- [x] 创建配套 TOML 元数据文件（.meta/toml/ 镜像路径）
- [x] 运行 fix-x-toml-ref.py 自动修复 x-toml-ref 路径
- [x] 运行文件名规范检查：`python .agents/scripts/check-filename-convention.py`
- [x] 更新知识库索引 docs/knowledge/README.md
- [ ] 原子提交（commit: docs(knowledge): 创建 Rainman Translate Book Wiki 教程）

## L5 收尾验证
- [x] 运行 fix-x-toml-ref.py 确保所有 x-toml-ref 路径正确
- [x] 运行 check-links.py 验证所有内部链接有效
- [x] 运行 check-filename-convention.py 验证文件名规范
- [x] 确认工作区无无关文件混入

# Task Dependencies
- L4 文档生成 依赖 L3 结构设计完成
- L5 收尾验证 依赖 L4 文档生成完成
- L1/L2/L3 可串行推进