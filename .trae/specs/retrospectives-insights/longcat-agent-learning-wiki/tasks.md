# LongCat-2.0 Agent 能力实测 Wiki Tasks

## L1 内容提取
- [x] 使用 defuddle 提取原始微信公众号网页
- [x] 验证提取质量，去噪（导航、广告、评论区等已去除）
- [x] 保存干净内容为 clean-source.md（临时文件，不提交）

## L2 内容分析
- [x] 通读并标记核心观点（实测结论、架构特点、效率数据）
- [x] 识别关键概念：MoE架构、稀疏注意力、loop engineering、Agent原生
- [x] 梳理逻辑结构：背景→概念→配置→实战→效率→方法论
- [x] 验证内容完整性：确认所有实操步骤、配置参数、截图信息均已提取

## L3 结构设计
- [x] 完成 spec.md（含 DoD 完成定义）
- [x] **原子化决策**：按4项判断标准评估，已确认"需要拆分"（spec.md 中已记录）
- [x] 设计章节结构（9个章节，基于8章节标准结构扩展）
- [x] 拆分内容到各章节
- [x] 完成 checklist.md（含子代理验收5点检查）
- [x] 在 tasks.md 中预置原子化步骤（L5阶段）

## L4 文档生成（首次提交：内容创作提交）
- [x] 创建 wiki 目录 `docs/knowledge/learning/longcat-agent-learning-wiki/`
- [x] 创建所有9个章节文件并添加 YAML frontmatter
  - [x] 00-overview.md（概述与学习目标）
  - [x] 01-core-concepts.md（LongCat-2.0核心概念）
  - [x] 02-claude-code-integration.md（Claude Code接入指南）
  - [x] 03-bi-dashboard-demo.md（BI数据看板实战）
  - [x] 04-token-efficiency.md（Token效率对比）
  - [x] 05-loop-engineering.md（Loop Engineering方法论）
  - [x] 06-summary.md（总结）
  - [x] 07-faq.md（FAQ）
  - [x] 08-resources.md（资源链接）
- [x] 填充各章节内容（引用原文信息，进行结构化整理）
- [x] 添加内部链接和导航表（00-overview.md 中）
- [x] **子代理产出验收**：按5点检查清单逐项验证 frontmatter 格式
- [x] 运行文件名规范检查：`python .agents/scripts/check-filename-convention.py`（系统文件权限问题，与本次变更无关）
- [x] 原子提交1（commit: docs(knowledge): 创建LongCat-2.0 Agent能力实测Wiki教程）

## L5 原子化拆分（第二次提交：结构重构提交）
- [x] 创建索引页 `longcat-agent-learning-wiki.md`（含导航表格，无深度内容）
- [x] 确认 `longcat-agent-learning-wiki/` 目录下所有原子文件内容完整
- [x] 为每个原子文件添加正确 frontmatter 和 source 溯源
- [x] 创建配套 TOML 元数据文件（9个原子文件 + 1个索引页的 .toml）
- [x] 运行文件名规范检查验证
- [x] 原子提交2（commit: docs(knowledge): 原子化拆分LongCat-2.0 Wiki教程）

## L6 收尾验证
- [x] 运行 fix-x-toml-ref.py 自动修复 x-toml-ref 路径并创建缺失 TOML 文件：`python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/longcat-agent-learning-wiki/ --write --create-toml`
- [x] 运行 check-links.py 验证所有链接有效
- [x] 运行 check-filename-convention.py 验证文件名规范（系统文件权限问题，与本次变更无关）
- [x] 更新 `docs/knowledge/README.md` 知识库索引
- [x] 更新 `docs/knowledge/learning/README.md`（如存在）
- [x] 确认工作区无无关文件混入

# Task Dependencies
- L2 依赖 L1 完成
- L3 依赖 L2 完成
- L4 依赖 L3 完成
- L5 依赖 L4 完成
- L6 依赖 L5 完成
- L4 中所有章节文件创建可并行执行
- L5 中 TOML 文件创建可并行执行