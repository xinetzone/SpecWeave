---
version: 1.0
id: create-seven-concepts-deeptutor-wiki-tutorial-checklist
title: 七概念理论与DeepTutor实践案例Wiki教程 - 验证检查清单
---

# 七概念理论与DeepTutor实践案例Wiki教程 - 验证检查清单

## 理论准确性检查
- [ ] 七概念7个核心概念（R/I/E/C/A/F/V）均有清晰定义
- [ ] 每个概念包含一句话公理、4个基础要素、层级归属说明
- [ ] 七概念理论表述与现有方法论文档（seven-concepts-quick-reference.md等）一致
- [ ] 五层层级模型（感知/认知/验证/执行/沉淀）描述准确
- [ ] 概念组合工作流（R→I→E、A→V→C、F→V→I等）描述准确

## DeepTutor事实准确性检查
- [ ] Chat模式描述准确：六种模式共享一个Agent引擎
- [ ] Partners模块描述准确：可接入本地Claude Code/Codex，支持分支续聊、Mattermost
- [ ] My Agents模块描述准确：自定义Agent独立空间、Persona/知识库/技能隔离
- [ ] Co-Writer模块描述准确：多文档协同写作、智能编辑、TTS、Markdown导出
- [ ] Book模块描述准确：活书编译器、笔记/对话编译HTML、章节对话提问
- [ ] Knowledge Center描述准确：四引擎RAG（LlamaIndex/PageIndex/GraphRAG/LightRAG）、Obsidian链接、版本管理
- [ ] Learning Space描述准确：技能市场、EduHub导入、Mastery Path掌握练习仪表盘
- [ ] Memory模块描述准确：L1原始对话/L2摘要/L3综合提炼、Memory Graph溯源、v1.4.6升至顶级导航
- [ ] Settings模块描述准确：模型/嵌入/TTS/搜索/端口统一配置、多LLM提供商、本地模型支持
- [ ] PyPI安装命令准确：`pip install -U deeptutor` → `deeptutor init` → `deeptutor start`
- [ ] Docker命令准确：`ghcr.io/hkuds/deeptutor:latest`、端口3782、卷挂载deeptutor-data
- [ ] Docker本地模型配置说明准确：`--add-host=host.docker.internal:host-gateway`
- [ ] CLI-only模式命令提及：`deeptutor chat`、`deeptutor kb create`、`deeptutor memory show`
- [ ] 端口信息准确：前端3782、后端8001
- [ ] 优缺点评价与原文一致：迭代快文档慢、RAG引擎选择无官方推荐、embedding配置不友好等

## 引文与术语检查
- [ ] 所有>块引用可在DeepTutor原文中定位
- [ ] 所有引文标注了来源位置（CLN规则）
- [ ] 关键术语表（glossary）已建立，包含≥20个DeepTutor术语+7个方法论术语
- [ ] 术语使用与术语表一致，无近义词替换导致的概念漂移
- [ ] 无虚构概念/功能/数据/数字（原文未提及的内容未加入）
- [ ] 案例归属正确：DeepTutor是港大数据科学实验室项目、GitHub 25k Star等信息准确

## 融合分析质量检查
- [ ] 每个七概念都有对应的DeepTutor实践案例分析
- [ ] 案例分析有"哪里体现→为什么（机制M）→带来什么好处（结果B）"三层结构
- [ ] 分析有深度，不是简单贴标签（如Memory三层↔R三阶段的对应关系）
- [ ] 组合工作流分析至少覆盖3种核心组合
- [ ] 无"理论是理论、案例是案例"的两张皮问题

## 文档结构与原子化检查
- [ ] 采用原子化文档结构，每个主题独立文件
- [ ] 所有单文件≤500行
- [ ] 有主README.md作为导航入口，包含目录导航表和阅读路径
- [ ] 文件命名遵循kebab-case规范
- [ ] 目录结构逻辑清晰：理论→案例→分析→学习路径

## 学习路径与练习检查
- [ ] 有明确的阅读路径（入门→进阶→实战）
- [ ] 至少包含1个可动手操作的实践练习
- [ ] 练习有明确的目标、步骤、验收标准/评分rubric
- [ ] 有自学质量检查清单
- [ ] 有延伸阅读索引（七概念完整文档+DeepTutor GitHub链接）

## 文档规范合规检查
- [ ] 所有Markdown文件有完整YAML frontmatter（id/title/source/version/date等）
- [ ] 无`file:///`绝对路径引用
- [ ] 所有交叉引用使用相对路径
- [ ] Changelog章节用`<!-- changelog -->`标记包裹
- [ ] 链接有效性检查通过（check-links.py无断链）
- [ ] 遵循项目Markdown风格（无多余注释、无emoji滥用除非用户要求）

## 独立事实核查V检查
- [ ] 独立核查由未参与编写的新子代理执行
- [ ] 核查覆盖6个维度：引文真实性、术语一致性、案例归属、章节标注准确性、虚构概念检测、理论准确性
- [ ] 核查发现的所有问题已修复
- [ ] 核查报告有具体问题定位（文件+行号）

## 最终收尾检查
- [ ] 教程存放在docs/下正确目录
- [ ] 相关导航索引已更新（如需要）
- [ ] 整体通读流畅，无明显逻辑断裂
- [ ] 无敏感信息泄露
- [ ] 内容为公开内容，适合存入公共docs/区域
