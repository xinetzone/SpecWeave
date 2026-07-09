---
version: "1.0"
source: "https://mp.weixin.qq.com/s/YirJ8-6_TZuFe9cLepFNSg?from=industrynews&amp;color_scheme=light#rd"
---

# Fable 5 成本优化技巧深度分析 - Product Requirement Document

## Overview
- **Summary**: 对微信公众号文章《天才程序员体验卡+5！》进行系统性学习和深度分析，提取Anthropic Fable 5模型按量计费后的成本优化方法论，以原子化文档形式整理到知识库中，包含3个社区开源方案和2个官方优化技巧的完整知识体系。
- **Purpose**: 记录Fable 5从订阅制转向按量计费后的行业应对策略，沉淀Token经济学、多模型协作、知识蒸馏等AI工程化最佳实践，为后续高成本模型使用提供可复用的成本优化参考。
- **Target Users**: AI Agent开发者、Claude Code用户、大模型应用工程师、关注LLM成本优化的技术人员。

## Goals
- 系统性梳理文章中提到的5大成本优化方法（3个开源方案+2个官方技巧）
- 以原子化文档形式组织知识，每个知识点独立成篇，便于检索和复用
- 提取核心工程洞察：Token价差利用、模型分层协作、知识沉淀传承、缓存机制优化
- 建立完整的wiki结构，包含概览、核心技巧、开源项目、官方机制、选型决策、资源索引
- 所有文档携带source溯源字段，保持知识可追溯性

## Non-Goals (Out of Scope)
- 不实际部署或测试文章中提到的开源项目（pxpipe、技能蒸馏、包工头模式）
- 不进行成本测算和性能基准测试
- 不扩展到其他模型（如GPT-5.6、Gemini等）的成本优化
- 不开发新的成本优化工具或脚本
- 不进行价格预测或商业分析

## Background &amp; Context
- Anthropic于2026年7月宣布Fable 5使用权延长至7月12日，之后转为按量计费
- Fable 5定价：输入$10/百万token，输出$50/百万token，是Opus 4.8的两倍
- 开发者社区迅速响应，GitHub涌现多个成本优化开源项目
- 官方提供Prompt Cache（缓存命中省90%）和Batch API（批量接口半价）两种机制
- 项目已有成熟的学习知识库结构（docs/knowledge/learning/），采用原子化wiki模式组织内容

## Functional Requirements
- **FR-1**: 创建原始文章内容存档，保留完整markdown格式和图片引用
- **FR-2**: 建立wiki目录结构，包含00-overview到07-resources的完整章节
- **FR-3**: 记录技能蒸馏方案（fable-5-train-opus-skills-after-it-retires）的完整方法论
- **FR-4**: 记录pxpipe文字转图片方案的原理、效果、局限性
- **FR-5**: 记录包工头模式（fable-token-saving-skills-orchestrator）的分层协作思路
- **FR-6**: 深入解析缓存经济学机制（TTL、命中刷新、冷启动成本、续命策略）
- **FR-7**: 记录批量接口（Batch API）的使用场景和价格优势
- **FR-8**: 提供场景化选型决策矩阵，帮助用户根据任务类型选择合适方案
- **FR-9**: 汇总所有相关开源项目地址和参考资源
- **FR-10**: 更新learning目录README，添加新wiki入口
- **FR-11**: 每个原子化文档携带正确的YAML frontmatter，包含source字段溯源

## Non-Functional Requirements
- **NFR-1**: 文档遵循原子化单一职责原则，每个文件聚焦一个独立知识点
- **NFR-2**: 所有内部引用使用相对路径，不使用file://绝对路径
- **NFR-3**: 文档命名遵循kebab-case规范，序号前缀保持一致
- **NFR-4**: Changelog章节使用&lt;!-- changelog --&gt;标记包裹
- **NFR-5**: 提交遵循Conventional Commits规范，每个提交对应一个原子化知识点
- **NFR-6**: 知识内容准确还原原文，不添加未经验证的推测性内容

## Constraints
- **Technical**: 遵循现有docs/knowledge/learning/目录的wiki组织结构，使用myst-parser兼容的Markdown格式
- **Business**: 知识库面向内部学习使用，内容需注明来源
- **Dependencies**: 依赖现有generate-readme.py脚本进行索引更新，依赖check-links.py进行链接验证

## Assumptions
- 用户已了解Claude Code和Fable 5的基本概念
- docs/knowledge/learning/03-agent-platforms-tools/是存放此类工具技巧的合适位置
- 现有wiki模板结构（00-overview到07-resources）适用于本主题
- 原始文章内容已通过defuddle成功提取，质量满足分析需求

## Acceptance Criteria

### AC-1: 原始内容存档完整
- **Given**: 已提取微信文章markdown内容
- **When**: 创建article-content.md存档文件
- **Then**: 文件包含完整文章内容、标题、来源URL、提取时间，格式正确
- **Verification**: `programmatic`
- **Notes**: 保留图片引用链接

### AC-2: Wiki目录结构规范
- **Given**: 确定在03-agent-platforms-tools下创建fable5-cost-optimization-wiki
- **When**: 创建wiki目录和所有章节文件
- **Then**: 目录包含00-overview.md到07-resources.md共8个核心文件+README.md，命名规范
- **Verification**: `programmatic`

### AC-3: 三个开源方案记录完整
- **Given**: 文章中提到的fable-5-train-opus-skills、pxpipe、fable-token-saving-skills-orchestrator
- **When**: 编写对应章节文档
- **Then**: 每个方案包含项目地址、核心原理、使用方法、优缺点、适用场景
- **Verification**: `human-judgment`

### AC-4: 官方优化机制解析深入
- **Given**: 缓存经济学和批量接口两个官方技巧
- **When**: 编写对应章节文档
- **Then**: 清晰说明缓存TTL、价格机制、续命策略；批量接口适用场景、价格、与缓存叠加效果
- **Verification**: `human-judgment`

### AC-5: 选型决策矩阵实用
- **Given**: 不同场景的成本优化需求
- **When**: 编写选型决策章节
- **Then**: 提供清晰的if-then决策逻辑，覆盖长上下文、重复任务、混合任务等典型场景
- **Verification**: `human-judgment`

### AC-6: 溯源与索引正确
- **Given**: 所有文档编写完成
- **When**: 添加frontmatter和更新索引
- **Then**: 每个文件携带正确的source字段，README已更新，无断链
- **Verification**: `programmatic`
- **Notes**: 运行check-links.py验证

### AC-7: 原子化提交规范
- **Given**: 所有知识点文档准备就绪
- **When**: 执行git原子化提交
- **Then**: 每个提交对应单一职责，commit message符合Conventional Commits，工作区干净
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要补充与现有Token优化相关wiki（如headroom-context-compression、longcat-agent）的交叉引用？
- [ ] 是否需要在文档中标注"方案有效性待验证"提示（因为未实际测试开源项目）？
