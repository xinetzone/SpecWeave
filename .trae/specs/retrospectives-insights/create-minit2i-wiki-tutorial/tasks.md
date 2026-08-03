# MiniT2I极简文生图模型Wiki教程生成 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建Wiki目录并生成00-overview.md
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建目录 `docs/knowledge/learning/minit2i-minimalist-t2i-wiki/`
  - 生成00-overview.md：概述与学习目标，包含背景、核心主题、学习目标（5条）、前置知识、章节导航表、阅读路径建议、Mermaid技术路线概览图
  - 包含正确的TOML frontmatter
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-5]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录`docs/knowledge/learning/minit2i-minimalist-t2i-wiki/`存在 ✅
  - `programmatic` TR-1.2: 00-overview.md文件存在且包含TOML frontmatter（id/title/source/date/category/tags字段） ✅
  - `human-judgement` TR-1.3: 章节导航表包含8个章节的完整链接（00-07） ✅
  - `human-judgement` TR-1.4: 包含至少1个Mermaid图表 ✅
- **Notes**: 参考github-cli-wiki/00-overview.md和ai-engineering-four-milestones-wiki/00-overview.md的格式

## [x] Task 2: 生成01-design-philosophy.md（核心设计哲学）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 基于core-arguments.md和最终报告第3、8.4节内容
  - 包含"每一步都做减法"的核心理念
  - 四大原则：质疑默认前提、减法即加法、如无必要勿增实体、基线先于优化
  - 减法哲学量化成果汇总表
  - 章节导航链接
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在且包含TOML frontmatter ✅
  - `human-judgement` TR-2.2: 四大减法原则阐述清晰，每个原则有说明 ✅
  - `human-judgement` TR-2.3: 包含减法操作量化成果表（至少5项减法） ✅
  - `programmatic` TR-2.4: 文件末尾有导航链接（←返回概述 | 下一章→） ✅

## [x] Task 3: 生成02-three-subtractions.md（技术路线三大减法）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 基于core-arguments.md和最终报告第4节
  - 减法一：无VAE——像素空间直出（理由、收益、证据、技术背景）
  - 减法二：无AdaLN——回归朴素Transformer（理由、收益、证据、关键洞察）
  - 减法三：无私有数据/RL——全公开数据两阶段训练（两阶段方案细节、消融结论）
  - Mermaid技术路线对比图（传统vs MiniT2I）
- **Acceptance Criteria Addressed**: [AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在且包含TOML frontmatter ✅
  - `programmatic` TR-3.2: GFLOPs数据准确：1379→570，降低58.7% ✅
  - `programmatic` TR-3.3: 两阶段训练数据准确：CC12M 250K步预训练 + ~12万张40K步微调 ✅
  - `human-judgement` TR-3.4: 三个减法每个都包含"去掉了什么/为什么能去掉/收益/证据"四要素 ✅
  - `human-judgement` TR-3.5: 包含1个Mermaid对比图 ✅

## [x] Task 4: 生成03-mm-jit-architecture.md（MM-JiT架构深度解析）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 基于mm-jit-architecture.md和最终报告第5节
  - MM-DiT vs MM-JiT 8维度对比表
  - 核心设计一：两层文本适配器（动机、实现、考量、本质）
  - 核心设计二：删除AdaLN分支（删除的组件、删除依据）
  - 关键洞察："被噪声污染的图像本身携带时间步信息"（理论基础、传统反思、验证意义）
  - 架构简化量化收益表（12→17层、FID 18.7→13.7等）
  - Mermaid MM-JiT架构图
- **Acceptance Criteria Addressed**: [AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在且包含TOML frontmatter ✅
  - `programmatic` TR-4.2: 架构简化数据准确：层数12→17（+41.7%），FID 18.7→13.7（-26.7%） ✅
  - `human-judgement` TR-4.3: 噪声图像携带时间步信息的理论解释清晰（含公式说明） ✅
  - `human-judgement` TR-4.4: MM-DiT vs MM-JiT对比表包含至少8个维度 ✅
  - `human-judgement` TR-4.5: 包含1个Mermaid架构图 ✅

## [x] Task 5: 生成04-experiments-performance.md（实验结果与性能分析）
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 基于experiment-data.md和最终报告第6节
  - 模型规格与参数配置表
  - 计算量对比表
  - GenEval/DPG-Bench/PRISM-Bench评测结果
  - 训练成本数据（8张H100约3天）
  - 消融实验核心结论（AdaLN消融、VAE消融）
  - 与SD3-Medium综合对比表
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在且包含TOML frontmatter ✅
  - `programmatic` TR-5.2: 关键评测数据准确：GenEval 0.87、DPG-Bench 84.2（B/16） ✅
  - `programmatic` TR-5.3: PRISM-Bench数据准确：文字渲染30.6 vs SD3 50.9，命名实体60.3 vs 66.3 ✅
  - `programmatic` TR-5.4: 训练成本准确：B/32在8张H100约3天 ✅
  - `human-judgement` TR-5.5: 与SD3综合对比表包含至少10个维度 ✅

## [x] Task 6: 生成05-limitations-open-problems.md（局限性与开放问题）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 基于limitations.md和最终报告第7节
  - 四个局限性逐一分析：patch伪影（梯度高17-22%）、CFG副作用、分辨率天花板（token增长表）、数据瓶颈
  - 每个局限包含：现象描述、原因分析、潜在解决方向、问题定位
  - 局限性总结评估表（严重程度/问题性质/是否本质问题/可解决性）
  - 科学态度分析：诚实承认局限的价值
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在且包含TOML frontmatter ✅
  - `programmatic` TR-6.2: patch伪影数据准确：边界梯度高17-22% ✅
  - `human-judgement` TR-6.3: 四个局限每个都包含现象/原因/解决方向/定位四部分 ✅
  - `human-judgement` TR-6.4: 包含局限性总结评估表 ✅
  - `human-judgement` TR-6.5: 包含科学态度价值分析 ✅

## [x] Task 7: 生成06-paradigm-shift-insights.md（范式转移与方法论启示）
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 基于paradigm-insights.md、methodology-insights.md和最终报告第8、9节
  - 洞察一：从"堆料"到"提纯"的范式转移（对比表）
  - 洞察二：文生图研究门槛降低（AlexNet时刻类比）
  - 洞察三：LLM训练范式向文生图迁移
  - 洞察四：系统设计的减法哲学
  - 洞察五：何恺明团队"返璞归真"研究风格传承（ResNet/MAE/MiniT2I对比表）
  - 对AI研究者的建议（选题/执行/心态）
  - 对工程师的实践启示
  - 领域影响预判（短期/中期/长期）
- **Acceptance Criteria Addressed**: [AC-4, AC-6]
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在且包含TOML frontmatter ✅
  - `human-judgement` TR-7.2: 五个范式转移洞察阐述清晰 ✅
  - `human-judgement` TR-7.3: 何恺明团队三件代表作对比表完整（ResNet/MAE/MiniT2I） ✅
  - `human-judgement` TR-7.4: 对研究者建议≥10条，对工程师建议≥5条 ✅
  - `human-judgement` TR-7.5: 包含短/中/长期影响预判 ✅

## [x] Task 8: 生成07-summary-faq-resources.md（总结、FAQ与资源）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 10条关键要点总结
  - 常见问题FAQ（至少8个问题）
  - 参考资料（原文资源、评测基准、数据集、关键术语表）
  - 章节导航（返回概述）
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在且包含TOML frontmatter ✅
  - `human-judgement` TR-8.2: 10条关键要点总结完整 ✅
  - `human-judgement` TR-8.3: FAQ包含至少8个常见问题及解答 ✅（实际包含8个Q&A）
  - `human-judgement` TR-8.4: 术语表包含至少10个关键术语（VAE/AdaLN/MM-JiT/FID/CFG等） ✅（实际包含14个术语）
  - `programmatic` TR-8.5: 文件末尾有导航链接（←返回上一章） ✅

## [x] Task 9: 质量验证与格式检查
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 验证所有8个文件存在
  - 抽查关键数据准确性（对照原报告）
  - 检查所有导航链接正确
  - 检查Mermaid图表数量≥3个
  - 检查frontmatter格式统一
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-5]
- **Test Requirements**:
  - `programmatic` TR-9.1: 8个Markdown文件全部存在（00-07） ✅
  - `programmatic` TR-9.2: 所有文件都有TOML frontmatter ✅
  - `human-judgement` TR-9.3: 抽查10个关键数据点全部准确 ✅（抽查60+数据点全部准确）
  - `programmatic` TR-9.4: Mermaid图表总数≥3个 ✅（实际3个）
  - `human-judgement` TR-9.5: 按顺序阅读章节，逻辑递进自然 ✅（由浅入深：概述→哲学→技术减法→架构→实验→局限→洞察→总结）
