# MiniT2I Wiki教程生成 - 验证检查清单

## 目录结构
- [ ] Wiki目录 `docs/knowledge/learning/minit2i-minimalist-t2i-wiki/` 已创建
- [ ] 8个章节文件全部存在（00-07，两位数字编号）
- [ ] 文件名符合规范（00-overview.md, 01-design-philosophy.md, 02-three-subtractions.md, 03-mm-jit-architecture.md, 04-experiments-performance.md, 05-limitations-open-problems.md, 06-paradigm-shift-insights.md, 07-summary-faq-resources.md）

## Frontmatter格式
- [ ] 每个文件都有TOML frontmatter（---包裹）
- [ ] frontmatter包含id字段（唯一标识，如minit2i-wiki-00-overview）
- [ ] frontmatter包含title字段（中文标题）
- [ ] frontmatter包含source字段（原始分析来源路径）
- [ ] frontmatter包含date字段（2026-08-03）
- [ ] frontmatter包含category字段（"learning"）
- [ ] frontmatter包含tags字段（相关标签数组）

## 00-overview.md内容
- [ ] 包含背景介绍（文生图领域现状、MiniT2I发布背景）
- [ ] 包含核心主题说明（极简主义、减法哲学、范式转移）
- [ ] 包含学习目标（至少5条，明确学完能做什么）
- [ ] 包含前置知识说明
- [ ] 包含完整章节导航表（8章，含链接和内容概要）
- [ ] 包含阅读路径建议（初学者/进阶/研究者路径）
- [ ] 包含至少1个Mermaid图表（技术路线概览图）
- [ ] 文件末尾有导航链接（下一章→）

## 01-design-philosophy.md内容
- [ ] "每一步都做减法"核心理念阐述清晰
- [ ] 四大原则完整：质疑默认前提、减法即加法、如无必要勿增实体、基线先于优化
- [ ] 每个原则有解释和示例
- [ ] 减法哲学量化成果汇总表（至少5项减法，含去掉什么/获得什么）
- [ ] 文件末尾有导航链接（←返回概述 | 下一章→）

## 02-three-subtractions.md内容
- [ ] 减法一：无VAE像素空间直出（去掉什么/为什么能去掉/收益/证据/技术背景）
- [ ] 减法二：无AdaLN朴素Transformer（去掉什么/为什么能去掉/收益/证据/关键洞察）
- [ ] 减法三：无私有数据两阶段训练（两阶段方案表格、消融结论）
- [ ] GFLOPs数据准确：1379→570，降低58.7%
- [ ] 两阶段训练数据准确：CC12M 250K步预训练 + ~12万张40K步微调
- [ ] 包含1个Mermaid技术路线对比图
- [ ] 文件末尾有导航链接（←上一章 | 下一章→）

## 03-mm-jit-architecture.md内容
- [ ] MM-DiT vs MM-JiT 8维度对比表完整
- [ ] 核心设计一：两层文本适配器（动机/实现/考量/本质）
- [ ] 核心设计二：删除AdaLN分支（删除组件/删除依据）
- [ ] 关键洞察"噪声图像携带时间步信息"解释清晰（含公式）
- [ ] 架构简化量化收益表准确：12→17层（+41.7%），FID 18.7→13.7（-26.7%）
- [ ] 包含1个Mermaid MM-JiT架构图
- [ ] 文件末尾有导航链接（←上一章 | 下一章→）

## 04-experiments-performance.md内容
- [ ] 模型规格与参数配置表
- [ ] 计算量对比表（GFLOPs）
- [ ] GenEval数据准确：B/16为0.87
- [ ] DPG-Bench数据准确：B/16为84.2
- [ ] PRISM-Bench数据准确：文字渲染30.6 vs SD3 50.9，命名实体60.3 vs 66.3
- [ ] 训练成本准确：B/32在8张H100约3天
- [ ] 消融实验结论（AdaLN消融、VAE消融）
- [ ] 与SD3-Medium综合对比表（至少10个维度）
- [ ] 文件末尾有导航链接（←上一章 | 下一章→）

## 05-limitations-open-problems.md内容
- [ ] patch伪影：现象/原因/解决方向/定位，梯度高17-22%数据准确
- [ ] CFG副作用：现象/原因/解决方向/定位
- [ ] 分辨率天花板：token增长表（512→1024→2048→4K）、现象/原因/解决方向/定位
- [ ] 数据瓶颈：现象/原因/解决方向/定位
- [ ] 局限性总结评估表（严重程度/性质/是否本质/可解决性）
- [ ] 科学态度分析（诚实承认局限的价值）
- [ ] 文件末尾有导航链接（←上一章 | 下一章→）

## 06-paradigm-shift-insights.md内容
- [ ] 五个范式转移洞察完整：堆料→提纯、研究门槛降低（AlexNet时刻）、LLM范式迁移、减法哲学、何恺明团队风格传承
- [ ] 堆料vs提纯对比表
- [ ] 何恺明团队三件代表作对比表（ResNet/MAE/MiniT2I）
- [ ] 对AI研究者建议（选题/执行/心态，至少10条）
- [ ] 对工程师实践启示（至少5条）
- [ ] 领域影响预判（短期/中期/长期）
- [ ] 文件末尾有导航链接（←上一章 | 下一章→）

## 07-summary-faq-resources.md内容
- [ ] 10条关键要点总结完整
- [ ] FAQ常见问题（至少8个问题及解答）
- [ ] 参考资料：原文资源、评测基准、训练数据集
- [ ] 关键术语表（至少10个术语：VAE/AdaLN/MM-JiT/MM-DiT/FID/GFLOPs/CFG/Flow Matching/FID/GenEval/DPG-Bench等）
- [ ] 文件末尾有导航链接（←返回上一章）

## 整体质量
- [ ] 所有技术数据点100%准确（抽查10个关键数据）
- [ ] Mermaid图表总数≥3个
- [ ] 按顺序阅读8章，认知路径"背景→哲学→技术→架构→数据→局限→洞察→总结"逻辑递进自然
- [ ] 使用表格呈现对比数据，避免大段纯文字
- [ ] 语言通俗易懂，适合学习者阅读，前置知识明确
- [ ] 核心技术内容无遗漏（三大减法、两个架构设计、四个局限、五个洞察、方法论建议）
