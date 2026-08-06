# 百度 Unlimited-OCR Wiki 教程生成 - 实现计划

## [x] Task 1: 创建 wiki 目录与概述页（00-overview.md）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建目录 `docs/knowledge/learning/baidu-unlimited-ocr-wiki/`
  - 生成 00-overview.md，包含：一句话摘要、背景与痛点、项目简介、核心特性一览表、目标受众表、章节导航表（9章）、阅读路径建议（快速体验/深度理解/全栈3条路径）、Mermaid架构图（R-SWA非对称注意力核心设计）、前置知识、下一章链接
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-00-overview
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在，00-overview.md 文件存在
  - `programmatic` TR-1.2: frontmatter包含id/title/source/date/category/tags六个字段
  - `human-judgement` TR-1.3: 章节导航表列出9个章节（00-08），标题与后续计划一致
  - `human-judgement` TR-1.4: Mermaid图展示R-SWA核心设计（参考侧全可见+输出侧滑窗+KV cache FIFO），语法正确
  - `human-judgement` TR-1.5: 阅读路径包含至少2条（快速体验、深度理解），章节编号合理
- **Notes**: Mermaid图参考headroom wiki的风格，用subgraph分区展示参考侧/输出侧/KV cache的结构差异

## [x] Task 2: 生成核心架构章节（01-core-architecture.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 生成 01-core-architecture.md，详解三大核心技术：R-SWA机制（抄书类比、非对称注意力、软遗忘）、DeepEncoder视觉编码器（16倍压缩、一次性编码、不参与状态转移）、固定大小KV cache队列（FIFO、128窗口、参考/输出双区对比表）
  - 包含R-SWA vs 标准注意力的对比表、参考侧/输出侧四维对比表
  - 可包含补充Mermaid图展示注意力机制差异
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-01-core-architecture
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在，frontmatter字段完整
  - `human-judgement` TR-2.2: R-SWA原理清晰，"人抄书"类比保留，非对称注意力设计描述准确
  - `human-judgement` TR-2.3: DeepEncoder的16倍压缩（1024→256 token）和一次性编码特性描述准确
  - `programmatic` TR-2.4: 参考侧/输出侧对比表包含注意力可见性、KV cache行为、内存占用、信息特性四行
  - `human-judgement` TR-2.5: 章节末尾有上一章(00)和下一章(02)链接
- **Notes**: 这是技术核心章节，务必确保R-SWA的"软遗忘"概念解释准确——不是遗忘参考信息，而是有选择地遗忘早期输出历史

## [x] Task 3: 生成性能数据章节（02-performance-data.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 生成 02-performance-data.md，包含三部分：OmniDocBench基准测试对比表（Unlimited-OCR/DeepSeek-OCR/Qwen3-VL/Gemini-2.5Pro）、长文档表现数据表（20页/40+页编辑距离、Distinct-35）、推理效率对比表（TPS 7847 vs 5822，+35%）
  - 关键反差解读：500M vs 235B的参数效率分析
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-02-performance-data
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在，frontmatter字段完整
  - `programmatic` TR-3.2: 基准测试表中Unlimited-OCR v1.5=93.23%、v1.6=93.92%，Qwen3-VL=89.15%，DeepSeek-OCR=87.01%
  - `programmatic` TR-3.3: TPS数据准确：Unlimited-OCR=7847，DeepSeek-OCR=5822，差距+35%
  - `programmatic` TR-3.4: 长文档数据准确：20页编辑距离0.057，40+页<0.11，Distinct-35=97%
  - `human-judgement` TR-3.5: 对500M反超235B的反差有明确解读段落
  - `human-judgement` TR-3.6: 章节末尾有上一章(01)和下一章(03)链接

## [x] Task 4: 生成快速上手指南（03-quick-start.md）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 生成 03-quick-start.md，包含：通用前置处理（PDF→PyMuPDF转图片DPI=300流程图）、Transformers方式（依赖安装pip install torch transformers pymupdf、适用场景）、SGLang方式（服务启动命令、OpenAI-compatible API特性）、两种方式对比表（7个维度）
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-03-quick-start
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在，frontmatter字段完整
  - `programmatic` TR-4.2: SGLang启动命令准确：`python -m sglang.launch_server --model-path baidu/Unlimited-OCR --port 30000`
  - `programmatic` TR-4.3: Transformers依赖列表准确：torch, transformers, pymupdf
  - `human-judgement` TR-4.4: 两种方式对比表包含定位、部署复杂度、依赖、API、流式输出、并发、吞吐量、适用阶段等维度
  - `human-judgement` TR-4.5: 有明确的方式选择建议
  - `human-judgement` TR-4.6: 章节末尾有上一章(02)和下一章(04)链接

## [x] Task 5: 生成局限性与风险章节（04-limitations-risks.md）
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 生成 04-limitations-risks.md，包含：5项局限性详表（模式支持/上下文长度/输入格式/硬件依赖/开源协议，含严重程度和影响范围）、项目成熟度评估（技术/工程/生态/生产就绪四维度）、适用场景建议（5星评级制）
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-04-limitations-risks
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在，frontmatter字段完整
  - `human-judgement` TR-5.2: 5项局限性完整，每项有具体内容、严重程度、影响范围
  - `human-judgement` TR-5.3: GPU硬件依赖和开源协议风险标记为"高"严重程度
  - `human-judgement` TR-5.4: 适用场景建议包含星级评分（5星到❌）
  - `human-judgement` TR-5.5: 章节末尾有上一章(03)和下一章(05)链接
- **Notes**: 本章体现客观中立，不过度美化项目

## [x] Task 6: 生成架构创新启示章节（05-architecture-insights.md）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 生成 05-architecture-insights.md，包含三部分深度洞察：归纳偏置的力量（任务定制架构vs通用参数堆砌）、"软遗忘"的哲学启示（哪些该记哪些该忘、信息分区→差异化记忆策略框架）、视觉token不参与状态转移的关键洞见（静态参考信息vs动态生成状态处理方式对比表）
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-05-architecture-insights
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在，frontmatter字段完整
  - `human-judgement` TR-6.2: 归纳偏置部分清晰解释了"机制创新>参数堆砌"的核心论点
  - `human-judgement` TR-6.3: 软遗忘哲学包含"该记住的永不遗忘/该遗忘的主动遗忘"两维度
  - `programmatic` TR-6.4: 静态/动态信息对比表包含信息类型、生命周期、变化特性、处理方式四列
  - `human-judgement` TR-6.5: 章节末尾有上一章(04)和下一章(06)链接

## [x] Task 7: 生成可迁移模式章节（06-transferable-patterns.md）
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 生成 06-transferable-patterns.md，包含：MoE+稀疏激活的效率哲学（3B总/500M激活的知识容量与推理成本解耦）、专用模型与通用大模型分化共存表（5维度对比）、"继续训练4000步"的创新路径、R-SWA可迁移性分析表（OCR/代码生成/客服/摘要/创作5场景适配度与改造点）
  - 代码生成场景和客服对话场景给出具体改造方向
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-06-transferable-patterns
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在，frontmatter字段完整
  - `programmatic` TR-7.2: MoE参数准确：总参数3B，激活500M
  - `programmatic` TR-7.3: 训练步数准确：约4000步基于DeepSeek-OCR继续训练
  - `human-judgement` TR-7.4: R-SWA迁移表包含5个场景，OCR为5星、开放域创作为2星
  - `human-judgement` TR-7.5: 代码生成场景有具体改造方向（多粒度参考、动态窗口、锚点保留）
  - `human-judgement` TR-7.6: 章节末尾有上一章(05)和下一章(07)链接
- **Notes**: 本章是"E（萃取）"阶段的核心产出，提炼可复用模式

## [x] Task 8: 生成SpecWeave启示章节（07-specweave-implications.md）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 生成 07-specweave-implications.md，包含两条可行动启示：
    - 启示1：规范前置+对话滑窗的上下文管理中间件（System/Anchor/History三区设计、预期收益4点）
    - 启示2：文档编码器+按需检索的长文档处理机制（预处理阶段、执行阶段、规范路由表、预期收益4点）
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-07-specweave-implications
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在，frontmatter字段完整
  - `human-judgement` TR-8.2: 启示1包含System/Anchor/History三区结构的清晰描述
  - `human-judgement` TR-8.3: 启示2包含预处理（拆分/摘要/索引/符号表）和执行（入口加载/按需检索/临时参考）两阶段
  - `human-judgement` TR-8.4: 两条启示都有明确的预期收益列表
  - `human-judgement` TR-8.5: 章节末尾有上一章(06)和下一章(08)链接

## [x] Task 9: 生成总结与FAQ章节（08-summary-faq.md）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 生成 08-summary-faq.md，包含：核心要点回顾（一句话总结+3-5个关键takeaway）、关键信息速查表（与原报告附录一致，类别+关键信息）、常见问题FAQ（5-8个问题，如"R-SWA和普通滑动窗口注意力有什么区别？""为什么不用线性注意力？""CPU能跑吗？""商用需要注意什么？"等）、延伸阅读建议
  - TOML frontmatter: id=baidu-unlimited-ocr-wiki-08-summary-faq
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在，frontmatter字段完整
  - `programmatic` TR-9.2: 速查表关键数据准确（93.23%、500M、7847 TPS、GitHub地址等）
  - `human-judgement` TR-9.3: FAQ包含至少5个有价值的问题，答案准确
  - `human-judgement` TR-9.4: 作为最后一章，只有上一章(07)链接，无下一章链接
  - `human-judgement` TR-9.5: 一句话总结准确概括项目核心价值
- **Notes**: 这是wiki的收尾章节，确保读者能快速回顾核心内容

## [x] Task 10: 整体一致性验证
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 验证所有9个文件的frontmatter一致性（date、source、category、tags统一）
  - 验证章节导航表（00-overview）与实际文件完全对应
  - 验证所有前后章节链接正确（无断链）
  - 验证所有数值数据与原报告一致
  - 运行文件名规范检查
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: 9个文件全部存在
  - `programmatic` TR-10.2: 所有文件名符合NN-kebab-case.md规范
  - `programmatic` TR-10.3: 所有frontmatter的date字段为"2026-08-03"，category为"learning"
  - `human-judgement` TR-10.4: 通读检查内容无遗漏、无重复、无数据矛盾
  - `human-judgement` TR-10.5: 确认原报告所有核心章节内容均被覆盖
