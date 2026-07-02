---
version: 1.0
---

# MyST Directives/Roles 在 Agent Spec 中可迁移性技术评估 - Verification Checklist

## 研究准备验证
- [ ] MDI Parser 中 directives 相关代码已精读（_DIRECTIVE_RE、_parse_directive_content、_extract_interfaces_from_directives、_ADMONITION_TYPES 等）
- [ ] mdit-py-plugins colon_fence 插件可用性已调研（版本、API、已知问题）
- [ ] 现有 Spec/SKILL 文档的语法模式统计已完成（表格/代码块/提示块使用频率）
- [ ] LLM 对 MyST 语法理解的相关证据已收集

## 核心概念适配性分析验证
- [ ] 映射矩阵覆盖≥6个MyST核心概念（Directives、Roles、Fences、Options、Arguments、Nesting、Frontmatter）
- [ ] ≥10个内置Directive的适配性评估已完成
- [ ] ≥8个常见Role的适配性评估已完成
- [ ] 两种围栏（`:::`/`` ``` ``）的三维度适用性对比已完成
- [ ] 每个概念有"高度适配/部分适配/不适配"评级及具体理由
- [ ] 适配性映射包含代码/语法示例

## 技术挑战分析验证
- [ ] ≥5个关键技术挑战已识别
- [ ] 每个挑战包含：问题描述、影响范围、复杂度评级（低/中/高）、潜在解决方向
- [ ] 解析器扩展挑战有具体技术方案分析（基于markdown-it-py插件机制）
- [ ] 降级显示分析包含GitHub/IDE/普通阅读器的实测或合理推断
- [ ] AI理解挑战有训练数据分布或实际经验支撑
- [ ] 向后兼容挑战有影响文件数的量化评估

## 实施路径方案验证
- [ ] 方案一（保守）描述完整（变更、依赖、性能、兼容、风险）
- [ ] 方案二（平衡/推荐）描述完整
- [ ] 方案三（激进）描述完整
- [ ] 有明确的推荐方案及推荐理由
- [ ] Mermaid决策树语法正确且可渲染
- [ ] 每个方案的变更清单具体到文件/模块级别

## 架构兼容性验证
- [ ] mdit-py-plugins生态分析包含具体版本号和API信息
- [ ] 三类Profile（Skill/WebApi/CliTool）各有≥2个具体Directive/Role建议
- [ ] 代码生成器增强点有具体技术描述
- [ ] 验证器增强点有具体技术描述
- [ ] 与现有共享库（frontmatter.py等）的集成点已分析

## 优势与局限性验证
- [ ] 优势≥3条且每条有具体论据
- [ ] 局限性≥3条且每条有具体论据
- [ ] 存在明确的权衡分析（非单纯罗列）
- [ ] 过度工程风险有具体防范建议
- [ ] 学习曲线评估有量化参考（如"5-10个directive"）

## 场景化建议验证
- [ ] 覆盖≥5个Agent开发典型场景
- [ ] 每个场景有"推荐/可选/不推荐"三级分类
- [ ] 包含≥3个正反例代码对比
- [ ] 技能定义场景建议明确
- [ ] Web API/CLI场景建议有具体directive推荐
- [ ] 学习资料/Wiki场景建议充分（考虑当前已使用TOML frontmatter的事实）

## 前瞻性洞察验证
- [ ] ≥4个前瞻性观点
- [ ] 每个观点有论据支撑（官方链接、趋势数据、技术类比）
- [ ] MyST生态演进分析引用了官方路线图或版本发布信息
- [ ] MDI长期演进预测有逻辑自洽的推理链条

## 报告格式规范验证
- [ ] 报告文件位于正确路径：docs/retrospective/reports/standards-tools/myst-to-agentspec-migration-analysis/report.md
- [ ] 使用TOML frontmatter（+++包裹），包含title/source/date/category/tags字段
- [ ] 有目录导航和章节间交叉引用
- [ ] ≥2张Mermaid图表且语法正确
- [ ] 使用表格做对比分析
- [ ] 全文中文撰写
- [ ] 总字数≥6000字
- [ ] 无TBD/TODO等占位符
- [ ] 各章节结论逻辑自洽无矛盾
- [ ] 代码引用使用file:///绝对路径格式
- [ ] 无预设立场词汇（"显然"、"毫无疑问"等）
- [ ] 对既有"不引入完整myst-parser"决策进行了评估但未轻率否定
