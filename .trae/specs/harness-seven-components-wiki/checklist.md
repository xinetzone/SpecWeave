# Harness业务运行底座七组件Wiki教程 - Verification Checklist

## 结构完整性检查
- [ ] 目录 `docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/` 已创建
- [ ] 文件总数在12-15个之间（00-overview ~ 13-quick-reference + README）
- [ ] 00-overview.md 存在且包含背景、学习目标、导航表、术语表
- [ ] 01-core-concepts.md 存在且包含Harness核心定义与七大组件概览
- [ ] 02-model-gateway.md 存在（模型网关）
- [ ] 03-tool-registry.md 存在（工具注册表）
- [ ] 04-knowledge-base.md 存在（知识库引擎）
- [ ] 05-memory-system.md 存在（记忆系统）
- [ ] 06-policy-engine.md 存在（策略引擎）
- [ ] 07-observability.md 存在（可观测性）
- [ ] 08-configuration.md 存在（配置管理）
- [ ] 09-practice-guide.md 存在（实践指南）
- [ ] 10-case-study.md 存在（案例分析）
- [ ] 11-faq.md 存在（常见问题）
- [ ] 12-resources.md 存在（资源链接）
- [ ] 13-quick-reference.md 存在（速查手册）
- [ ] README.md 存在且包含索引表、学习路径、相关资源

## YAML Frontmatter 规范检查
- [ ] 每个.md文件都包含YAML frontmatter（---包裹）
- [ ] 每个frontmatter包含id字段
- [ ] 每个frontmatter包含title字段
- [ ] 每个frontmatter包含date字段
- [ ] 每个frontmatter包含category字段（值为"learning"）
- [ ] 00-overview.md包含source字段标注原文URL
- [ ] 无空frontmatter或缺失必要字段

## 内容准确性检查
- [ ] Harness定义准确："AI Agent的业务运行底座"
- [ ] 核心论点准确："大模型解决智能问题，Harness解决交付问题"
- [ ] 七大组件名称完整准确：模型网关、工具注册表、知识库引擎、记忆系统、策略引擎、可观测性、配置管理
- [ ] 每个组件章节包含：定义、核心职责、生活场景类比、文章Agent应用、设计原则
- [ ] 家庭聚餐类比与七大组件映射关系正确
- [ ] 文章Agent三类模型路由准确（选题→强模型、材料→长上下文、格式→便宜模型）
- [ ] 知识库三类内容准确（历史文章、案例纪要、观点框架）
- [ ] 记忆系统短期/长期区分准确
- [ ] 策略引擎三条关键策略准确（选题策略、内容安全、质量标准）
- [ ] 可观测性数据指标和Badcase闭环流程准确
- [ ] 配置管理三层区分（红线/长期偏好/任务配置）准确
- [ ] "知识库是你的判断力缓存"核心洞见保留
- [ ] "不是让Agent更会写，而是让Agent不乱写"核心洞见保留
- [ ] 内容忠实于原文，无篡改核心论点或添加无依据内容

## Mermaid 图表检查
- [ ] 组件架构总览图（00-overview.md中）存在且语法正确
- [ ] 组件协作流程图（01-core-concepts.md中）存在且语法正确
- [ ] 模型网关路由决策图（02-model-gateway.md中）存在且语法正确
- [ ] 记忆分层图（05-memory-system.md中）存在且语法正确
- [ ] 策略引擎边界约束图（06-policy-engine.md中）存在且语法正确
- [ ] 可观测性闭环图（07-observability.md中）存在且语法正确
- [ ] 配置管理层次图（08-configuration.md中）存在且语法正确
- [ ] Mermaid图表总数≥7张
- [ ] 所有Mermaid代码块使用```mermaid标记
- [ ] 无Mermaid语法错误（节点名无特殊字符、箭头方向正确）

## 实践指南与案例检查
- [ ] 实践指南包含产品经理视角和开发者视角
- [ ] 从零构建Harness的五步法步骤清晰
- [ ] 实施优先级排序表存在且合理
- [ ] 最小可行Harness（MVH）清单存在
- [ ] 组件选型决策表存在
- [ ] 案例分析包含家庭聚餐完整映射表
- [ ] 文章Agent逐组件深度分析存在
- [ ] 有无Harness对比表存在
- [ ] 传统PM vs AI PM对比论述存在

## FAQ检查
- [ ] FAQ总数≥12个
- [ ] 概念混淆类≥4个（知识库vs记忆、工具vs策略、Harness vs Prompt、配置vs记忆）
- [ ] 实施难点类≥4个（MVH构成、策略设计、模型vs Harness、知识库内容）
- [ ] 边界判断类≥2个（不需要完整Harness场景、Badcase落地）
- [ ] 知识关联类≥2个（与harness-engineering-wiki区别、与四代范式对应）

## 交叉引用与链接检查
- [ ] 12-resources.md中包含harness-engineering-wiki正确相对路径链接
- [ ] 12-resources.md中包含four-engineering-concepts-wiki.md正确链接
- [ ] 12-resources.md中包含harness-loop-engineering-article-analysis.md正确链接
- [ ] 文件间内部互引使用相对路径
- [ ] 上级目录README.md已更新，包含新wiki条目
- [ ] 无file:///绝对路径
- [ ] 无断链（运行链接检查脚本通过）

## README与导航检查
- [ ] README使用README_INDEX_START/END标记包裹索引表
- [ ] README包含至少3条学习路径（产品经理/开发者/进阶）
- [ ] README文档索引表完整列出所有章节文件
- [ ] 上级目录README的子Wiki索引表新增条目准确
- [ ] 上级目录README的快速导航场景分组新增条目准确

## 速查手册检查
- [ ] 13-quick-reference.md包含七组件公理速查卡表格
- [ ] 速查卡包含：组件名/一句话公理/核心职责/生活类比/文章Agent应用/设计原则
- [ ] 包含核心论点速记
- [ ] 包含MVH检查清单
- [ ] 包含Badcase闭环速查

## 代码规范检查
- [ ] 无ASCII字符画替代Mermaid图表
- [ ] Markdown语法使用MyST兼容格式
- [ ] 术语首次出现附英文原文
- [ ] 全文使用中文撰写
- [ ] 无多余注释或无关内容
- [ ] 层级标题使用正确（# → ## → ###）
