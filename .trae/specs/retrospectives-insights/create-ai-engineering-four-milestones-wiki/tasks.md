# AI工程四个路标 Wiki教程 Tasks

## L1 内容提取（已完成）
- [x] 使用defuddle提取原始网页（已在analyze-wechat-article-eeb14任务中完成）
- [x] 验证提取质量，内容完整无截断
- [x] 文章内容已用于深度分析（双层结构报告已完成）

## L2 内容分析（已完成）
- [x] 通读并标记核心观点（7个主要观点已梳理）
- [x] 识别关键概念（10个概念/术语已识别）
- [x] 梳理逻辑结构（四站递进+层层包含已明确）
- [x] 验证内容完整性（28个检查点全通过）
- [x] 深度洞察分析（3项行业趋势+4项市场动态+4个认知模型）

## L3 结构设计（已完成）
- [x] 完成spec.md（含原子化决策：需要拆分）
- [x] 原子化决策：4项判断标准均满足，选择"需要拆分"
- [x] 设计章节结构（8章节：00-overview到07-summary-faq-resources）
- [x] 完成checklist.md（含子代理验收5点检查）

## L4 文档生成
- [ ] Task 1: 创建wiki目录 `docs/knowledge/learning/ai-engineering-four-milestones-wiki/`
- [ ] Task 2: 创建索引页 `ai-engineering-four-milestones-wiki.md`（导航表+学习目标，<100行）
- [ ] Task 3: 创建00-overview.md（背景、核心主题、学习目标、前置知识、文档导航）
- [ ] Task 4: 创建01-bottleneck-migration.md（瓶颈外移模型、四站递进、层层包含）
- [ ] Task 5: 创建02-prompt-engineering.md（模型预测本质、提示词配方、瓶颈：怎么说）
- [ ] Task 6: 创建03-context-engineering.md（上下文窗口、context rot、渐进式披露）
- [ ] Task 7: 创建04-harness-engineering.md（Hashimoto定义、复利效应、Agent=模型+Harness）
- [ ] Task 8: 创建05-loop-engineering.md（回合制→循环制、三人点响、瓶颈：你自己）
- [ ] Task 9: 创建06-insights-patterns.md（行业趋势、市场动态、4个认知模型、Harness方法论）
- [ ] Task 10: 创建07-summary-faq-resources.md（核心要点、FAQ、资源链接）
- [ ] Task 11: 更新 `docs/knowledge/README.md` 知识库索引
- [ ] Task 12: 子代理产出验收（9点检查清单）

## L5 原子化配套
- [ ] Task 13: 运行 `python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/ai-engineering-four-milestones-wiki/ --write --create-toml`
- [ ] Task 14: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/ai-engineering-four-milestones-wiki/`
- [ ] Task 15: 运行 `python .agents/scripts/check-filename-convention.py`

## L6 收尾验证
- [ ] Task 16: 确认所有frontmatter使用YAML（---）格式
- [ ] Task 17: 确认原子化wiki frontmatter仅含4字段（id/title/source/x-toml-ref）
- [ ] Task 18: 确认索引页<100行，仅含导航+学习目标
- [ ] Task 19: 确认工作区无无关文件混入

# Task Dependencies
- Task 1（创建目录）→ 无依赖，首先执行
- Task 2-10（创建各章节文件）→ 依赖 Task 1，可并行委派子智能体
- Task 11（更新索引）→ 依赖 Task 2-10 完成
- Task 12（验收）→ 依赖 Task 2-10 完成
- Task 13-15（自动化验证）→ 依赖 Task 12 验收通过
- Task 16-19（收尾）→ 依赖 Task 13-15 通过

# Parallelizable Work
- Task 2-10（9个文件的创建）可并行委派子智能体，或整体委托单个子智能体（参考"深度依赖链任务整体委托模式"）
