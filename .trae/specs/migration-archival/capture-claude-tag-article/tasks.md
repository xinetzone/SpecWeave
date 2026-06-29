# Tasks

- [x] Task 1: 编写 `docs/knowledge/learning/claude-tag-article.md` 知识条目
  - [x] SubTask 1.1: 编写文件头元数据（原文标题、来源 URL、公众号、作者、发布日期）
  - [x] SubTask 1.2: 编写「文章概述」章节（一段话概括主题思想）
  - [x] SubTask 1.3: 编写「核心观点」章节（产品定位、LLM 三次变革论断、与传统 AI 助手差异、四大能力、统一入口判断）
  - [x] SubTask 1.4: 编写「关键概念与术语」章节（Claude Tag、Ambient Mode、共享上下文、持续记忆、异步执行、Claude 身份、Opus 4.8、Fable 5 等条目释义）
  - [x] SubTask 1.5: 编写「重要数据」章节（65% 代码占比、Opus 4.8 限定、Slack 部署、Beta 开放、扩展计划等量化与事实信息）
  - [x] SubTask 1.6: 编写「结构框架」章节（按原文四个小节概括：升级概览、先进团队协作、实际部署、社区反响）
  - [x] SubTask 1.7: 编写「与 SpecWeave 的关联」章节（多智能体协作、组织知识沉淀、Agent 工作流的对照参考）
  - [x] SubTask 1.8: 附「参考链接」章节（原文链接、Anthropic 官方博客、TechCrunch、Reuters）
- [x] Task 2: 重新生成知识库索引
  - [x] SubTask 2.1: 运行 `python scripts/generate_index.py` 重新生成 `docs/knowledge/README.md`
  - [x] SubTask 2.2: 验证索引中 learning 分类包含新条目，标签索引含相关标签

# Task Dependencies

- Task 2 依赖 Task 1（必须先创建知识条目文件，索引脚本才能扫描到）
