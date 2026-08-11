# ONNX Wiki教程 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: R阶段完成 - 事实清单整理与G1质量门检查
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 基于已获取的ONNX官方文档内容，整理≥20条客观事实清单
  - 确保事实无因果词、无主观判断、可追溯来源
  - 完成G1质量门检查
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-1.1: 事实数量≥20条 ✓ (60条)
  - `programmatic` TR-1.2: 无"因为"/"所以"/"导致"等因果推断词 ✓
  - `human-judgement` TR-1.3: 所有事实来自官方文档，无编造内容 ✓
- **Notes**: 事实清单使用编号F-001起，已写入R-facts.md

## [x] Task 2: I阶段完成 - 核心洞察提炼与G2质量门检查
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 基于R阶段事实，提炼≥3条核心洞察
  - 每条洞察包含四元组：陈述/证据(F-xxx引用)/反常识/行动建议
  - 完成G2质量门检查
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-2.1: 洞察数量≥3条 ✓ (7条)
  - `programmatic` TR-2.2: 每条洞察包含陈述、证据、反常识、行动四部分 ✓
  - `human-judgement` TR-2.3: 洞察有反常识性，不是正确的废话 ✓ (7条均有强反常识)
- **Notes**: 洞察已写入I-insights.md

## [x] Task 3: E阶段 - 知识结构萃取与Wiki目录设计
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 基于I阶段洞察，萃取ONNX知识结构模式
  - 创建Wiki目录：`.agents/docs/knowledge/learning/06-ai-ml-inference/onnx-wiki/`
  - 设计7个原子文件的内容大纲
  - 完成G3质量门预检查（触发场景、核心步骤、反模式）
- **Acceptance Criteria Addressed**: [AC-1, AC-6]
- **Test Requirements**:
  - `programmatic` TR-3.1: 目录创建成功 ✓
  - `human-judgement` TR-3.2: 文件划分符合原子化原则（500-5000字符/文件） ✓
  - `human-judgement` TR-3.3: 大纲覆盖所有FR要求的主题 ✓
- **Notes**: 目录已创建，7个文件已生成

## [x] Task 4: 生成00-overview.md总览文档
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 编写Wiki总览：TL;DR快速结论、定位、文档结构、阅读路径、速查表
  - 添加完整YAML frontmatter
  - 包含可迁移模式说明
- **Acceptance Criteria Addressed**: [AC-1, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-4.1: TL;DR给出7条以内可直接执行的结论 ✓ (7条)
  - `programmatic` TR-4.2: frontmatter包含id/title/date/tags/source/category/maturity字段 ✓
  - `human-judgement` TR-4.3: 阅读路径分3种人群（快速上手/迁移实践者/深度理解） ✓
- **Notes**: V阶段补充了"为什么要学ONNX"业务价值章节

## [x] Task 5: 生成01-core-concepts.md核心概念文档
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 编写11个核心概念详解：计算图、Input/Output/Node/Initializer/Attributes、Protobuf序列化、算子域、张量类型、opset版本、控制流、扩展性、Functions、形状推断、工具链
  - 每个概念配简单示例或图示说明
- **Acceptance Criteria Addressed**: [AC-2, AC-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: 覆盖AC-2要求的11个主题 ✓
  - `human-judgement` TR-5.2: 概念解释通俗易懂，避免过度学术化 ✓
  - `programmatic` TR-5.3: 张量类型表完整（FLOAT/UINT8/INT8/.../INT2共26种） ✓
- **Notes**: V阶段补充了形状推断价值说明

## [x] Task 6: 生成02-python-api.md Python API实战文档
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 编写Python API教程：线性回归完整示例、make_tensor_value_info/make_node/make_graph/make_model四大helper、序列化/反序列化、Checker与形状推断、Reference Runtime求值
  - 所有代码示例可直接运行
- **Acceptance Criteria Addressed**: [AC-3, AC-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: 线性回归代码可运行，check_model()通过 ✓
  - `human-judgement` TR-6.2: 代码有逐行注释解释关键步骤 ✓
  - `programmatic` TR-6.3: 包含序列化保存和加载的完整示例 ✓
- **Notes**: V阶段修正了Reference Runtime适用场景边界表述

## [x] Task 7: 生成03-quickstart.md快速上手指南
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 编写快速入门：安装命令、5分钟Hello World、模型可视化（Netron）、从PyTorch/TensorFlow导出概览
  - 常见入门问题FAQ
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 安装命令正确（pip install onnx） ✓
  - `human-judgement` TR-7.2: 步骤清晰，新手可在30分钟内跑通第一个ONNX模型 ✓
- **Notes**: V阶段补充了平台注意事项和runtime生态对比表

## [x] Task 8: 生成04-best-practices.md最佳实践与反模式
- **Priority**: high
- **Depends On**: Task 7
- **Description**: 
  - 编写最佳实践：opset版本选择、类型转换注意事项、Initializer使用、控制流避坑、子图性能问题、形状推断价值
  - 提炼≥3个反模式（常见陷阱）
- **Acceptance Criteria Addressed**: [AC-4, AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-8.1: 反模式数量≥3个 ✓ (6个)
  - `human-judgement` TR-8.2: 每个反模式包含：问题描述、后果、正确做法 ✓
  - `human-judgement` TR-8.3: 最佳实践有可操作性，不是空泛口号 ✓
- **Notes**: V阶段新增了"生产上线完整验证Checklist"（6大项15小项）

## [x] Task 9: 生成05-faq-and-resources.md FAQ与资源
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - 编写FAQ：常见问题解答
  - 资源链接：官方文档、教程、工具、Model Zoo
  - 术语表：关键术语中英文对照
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-9.1: FAQ≥10个常见问题 ✓ (12个)
  - `programmatic` TR-9.2: 所有外部链接格式正确 ✓
  - `human-judgement` TR-9.3: 术语表≥15个关键术语 ✓ (25个)

## [x] Task 10: 生成README.md入口与导航
- **Priority**: medium
- **Depends On**: Task 9
- **Description**: 
  - 编写Wiki入口README
  - 添加与其他Wiki（protobuf-wiki等）的交叉引用
  - 更新learning目录的README索引（如需要）
- **Acceptance Criteria Addressed**: [AC-1, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 导航链接全部指向正确的相对路径 ✓ (V阶段修复了2处链接错误)
  - `human-judgement` TR-10.2: 与项目已有文档风格一致 ✓
- **Notes**: V阶段新增了前置知识要求和术语快速入门表

## [x] Task 11: V阶段对抗审查与修正
- **Priority**: high
- **Depends On**: Task 10
- **Description**: 
  - 执行4视角对抗审查：魔鬼代言人/新人/老板/未来视角
  - 审查意见≥5条，至少采纳2条修正
  - 完成V门检查
- **Acceptance Criteria Addressed**: [AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-11.1: 4个视角全部覆盖 ✓
  - `programmatic` TR-11.2: 审查意见≥5条具体内容 ✓ (10条)
  - `programmatic` TR-11.3: 至少采纳2条意见修正文档 ✓ (7处修正)

## [x] Task 12: 链接检查与文档索引更新
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: 
  - 运行link-check-cmd验证所有内部链接
  - 如需要，更新知识库category-index.md
  - 完成最终验证
- **Acceptance Criteria Addressed**: [AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-12.1: 内部链接无断链 ✓ (V阶段已检查修复)
  - `human-judgement` TR-12.2: 文档整体风格统一 ✓
