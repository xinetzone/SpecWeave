---
id: "minitap-ai-wiki-update-tasks"
title: "Minitap.ai官网学习与wiki更新 - 实施计划"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/minitap-ai-wiki-update/tasks.toml"
date: "2026-07-07"
---
# Minitap.ai官网系统学习与wiki更新 - The Implementation Plan

## [x] Task 1: 补充获取官网关键子页面内容
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 获取benchmark页面详细内容（https://www.minitap.ai/benchmark）
  - 如有必要获取博客页面关键文章内容
  - 补充提取主站中可能被遗漏的细节（定价、集成说明等）
  - 整理所有提取的信息，按主题分类
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 检查是否覆盖官网所有关键板块（产品、功能、技术、客户、定价、博客等）
  - `human-judgement` TR-1.2: 信息按主题分类整理，便于后续wiki撰写
- **Notes**: 使用defuddle工具提取页面，优先保证主站内容完整性

## [x] Task 2: 创建minitap-official-wiki.md完整wiki文档
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在docs/knowledge/learning/03-agent-platforms-tools/目录下创建minitap-official-wiki.md
  - 遵循现有wiki格式，添加标准frontmatter
  - 撰写完整目录导航
  - 按章节组织内容：产品概述、核心功能、技术优势、集成生态、支持平台、客户案例、成本数据、最新动态、媒体报道、FAQ、资源链接
  - 使用表格呈现对比数据（如QA方式对比、成本对比等）
  - 添加关键信息来源链接
  - 添加与mobile-use、复盘报告、模式库的交叉引用
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-4, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 检查frontmatter完整性（title/category/source/date/tags/summary）
  - `human-judgement` TR-2.2: 检查目录导航与章节对应关系
  - `human-judgement` TR-2.3: 验证所有关键数据与官网一致
  - `human-judgement` TR-2.4: 检查交叉引用链接有效性
  - `human-judgement` TR-2.5: 检查文件命名符合kebab-case规范
- **Notes**: 参考anthropic-agent-roadmap-wiki.md的12章节结构

## [x] Task 3: 更新mobile-use-deep-learning-analysis.md补充商业产品视角
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 读取现有mobile-use-deep-learning-analysis.md文档
  - 在适当位置（建议在文档末尾或新增章节）添加Minitap商业产品介绍
  - 说明mobile-use开源项目与Minitap商业产品minitest的关系
  - 添加minitap-official-wiki.md的交叉引用
  - 补充官网技术指标链接（AndroidWorld benchmark、论文链接等）
- **Acceptance Criteria Addressed**: [AC-3, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 新增内容不破坏原有文档结构
  - `human-judgement` TR-3.2: 清晰说明开源项目与商业产品关系
  - `human-judgement` TR-3.3: 交叉引用链接正确
- **Notes**: 更新要温和，不要大幅修改原有技术分析内容

## [x] Task 4: 验证与收尾
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 检查新wiki文档格式一致性
  - 验证所有链接（内部和外部）格式正确
  - 更新learning目录索引（如需要）
  - 执行文件名规范检查
  - 完成checklist中所有验证项
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-4.1: 运行文件名规范检查脚本，确认新文件命名合法
  - `human-judgement` TR-4.2: 整体审阅文档质量，确保专业、准确、完整
- **Notes**: 使用python .agents/scripts/check-filename-convention.py进行检查
