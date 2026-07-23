---
version: "1.0"
---
# Protocol Buffers 版本演进知识库 - The Implementation Plan

## [x] Task 1: R阶段 - 事实采集与官方文档研究（七概念之R）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 通过网络搜索和官方文档（protobuf.dev、GitHub releases、Google Open Source Blog）系统采集 protobuf 各版本的客观事实数据
  - 采集维度：版本号/标识、发布年份、发布背景（blog/announcement）、语法特性列表、语言支持、重要改进点、已知问题
  - 采集的版本节点：Google内部版(proto1, 2001)、开源proto2(2008)、proto3 beta(2014-2015)、proto3 正式版(2016/3.0)、proto3 3.5(2017/未知字段恢复)、proto3 3.14(2020/新增特性)、proto3 3.15(2021/optional恢复)、Editions 2023、Editions 2024
  - 同时采集 caffe.proto 中 proto2 特性使用的统计事实（required数量、default数量、extensions使用、packed标注、枚举首值情况）
  - 输出：结构化事实列表（纯客观、无因果推断词）
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 事实列表中不出现"因为"、"导致"、"所以"、"错误"等因果判断词
  - `human-judgement` TR-1.2: 每个版本节点至少包含发布时间和3个以上核心特性描述
  - `human-judgement` TR-1.3: 信息来源标注了官方文档/blog/GitHub release等可溯源依据
- **Notes**: 使用 WebSearch 工具获取最新的官方信息；参考 caffe.proto 作为 proto2 实例

## [x] Task 2: I阶段 - 核心洞察分析（七概念之I）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 Task 1 采集的事实，提炼核心洞察，每条洞察包含四元组（陈述/证据/反常识/下次行动）
  - 洞察方向：
    1. protobuf 版本演进的设计哲学变迁（从显式控制→约定优先→feature原子化）
    2. 为什么 proto3 先移除后恢复部分特性（required/optional/presence的教训）
    3. Editions 出现的根本原因（proto2/proto3 二分法的困境）
    4. 字段 presence 作为版本间最核心语义鸿沟的延续性
  - 输出：≥3条核心洞察，每条含完整四元组
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `human-judgement` TR-2.1: 每条洞察包含陈述、证据（引用事实编号）、反常识点、下次行动四部分
  - `human-judgement` TR-2.2: 至少有1条洞察包含反直觉发现（非显而易见的结论）
  - `human-judgement` TR-2.3: 洞察揭示了版本变化背后的设计动机/原因，而非仅罗列差异
- **Notes**: 借鉴已完成的 caffe proto2/proto3 分析中的 I2（presence语义鸿沟）洞察，扩展到全版本范围

## [x] Task 3: E阶段 - 可复用模式萃取（七概念之E）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 从版本对比和选型决策中萃取可复用模式
  - 需要萃取的模式：
    1. "序列化 IDL 版本选型决策模型"（输入：场景特征→输出：版本推荐+理由）
    2. "IDL 版本迁移风险检查模式"（通用迁移检查清单框架）
    3. "API 演进的减法-回归辩证法"（先移除再恢复特性的模式识别）
  - 每个模式包含：触发场景、核心步骤、反模式、迁移验证（可迁移到非 protobuf 场景如 Thrift/JSON Schema/OpenAPI）
  - 输出：≥2个可跨场景复用的模式
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `human-judgement` TR-3.1: 每个模式包含触发场景、核心步骤、反模式、迁移验证四个要素
  - `human-judgement` TR-3.2: 至少1个模式能迁移到非 protobuf 场景验证（如JSON Schema draft版本选择、OpenAPI 2→3升级）
  - `human-judgement` TR-3.3: 选型决策模型覆盖至少6种典型场景
- **Notes**: 借鉴已有 proto2/proto3 分析中的"序列化IDL版本对比模式"，扩展为包含 Editions 的版本选型模型

## [x] Task 4: V阶段 - 对抗审查与质量校验（七概念之V）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 对 R/I/E 阶段产出进行多视角对抗审查
  - 审查视角：
    1. 魔鬼代言人：找反例、漏洞、事实错误（如"Editions真的统一了吗？"、"proto3的默认值语义是否真的更好？"）
    2. 新人视角：什么地方会让初学者困惑？
    3. 未来视角：如果 protobuf 推出 Editions 2025/2026，当前的分析框架是否仍然适用？
    4. 实用性视角：这些结论对实际项目选型有指导价值吗？反模式是否真实存在？
  - 基于审查意见修正事实/洞察/模式
  - 输出：审查记录（攻击点+回应+采纳/拒绝）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-4.1: 审查视角≥3个
  - `human-judgement` TR-4.2: 采纳修正≥2条
  - `human-judgement` TR-4.3: 最终事实/洞察/模式经修正后无明显漏洞
- **Notes**: 重点审查事实准确性（发布时间、特性描述是否与官方一致）

## [x] Task 5: 创建 protobuf-wiki 目录与 01-version-timeline.md（版本时间线）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建目录 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/protobuf-wiki/`
  - 基于 R 阶段验证后的事实，编写版本时间线文档 01-version-timeline.md
  - 文档结构：
    - 简介
    - 版本演进总时间轴图（文本表格/ASCII）
    - 各版本详细说明（Google内部版→proto2→proto3各里程碑→Editions 2023/2024）
    - 每个版本包含：版本标识、时间、背景、核心特性、重要改进、局限/已知问题、线格式兼容性说明
  - 添加 YAML frontmatter（id、title、date、tags、source、maturity）
  - 添加章末导航（上一章/返回目录/下一章）
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `human-judgement` TR-5.1: 覆盖≥6个主要版本节点
  - `human-judgement` TR-5.2: 每个版本有发布时间、背景、≥3个核心特性
  - `programmatic` TR-5.3: 文件创建在正确路径，有完整 YAML frontmatter
- **Notes**: 内容来自经 V 阶段验证的 R 阶段事实数据

## [x] Task 6: 编写 02-version-comparison.md（三版对比矩阵）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 编写 proto2/proto3/Editions 三版本多维度对比矩阵文档 02-version-comparison.md
  - 对比维度（≥12个）：
    - 语法声明、字段修饰符（required/optional/repeated/singular）
    - 字段 presence 追踪、默认值规则
    - 枚举规则（闭合/开放、首值约束）
    - 扩展机制（extensions/Any/feature）
    - 内置类型支持（Any/Struct/Value等well-known types）
    - JSON映射规范、map类型、oneof、group支持
    - 未知字段处理、packed编码默认行为
    - 线格式兼容性
  - 每个维度用表格对比，标注兼容性影响级别
  - 增加"语法迁移示例"小节：同一个 message 在三个版本中的写法对比
  - 添加 YAML frontmatter 和章末导航
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `human-judgement` TR-6.1: 对比维度≥12个
  - `human-judgement` TR-6.2: 每个维度有三列（proto2/proto3/Editions）和兼容性标注
  - `human-judgement` TR-6.3: 包含≥3个代码示例（同一message在三版中的写法）
- **Notes**: 借鉴 caffe-architecture-wiki/04 中的对比表，扩展增加 Editions 列

## [x] Task 7: 编写 03-feature-evolution.md（关键功能演进史）
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 编写核心功能演进历程文档 03-feature-evolution.md
  - 覆盖≥6个核心功能的演进故事：
    1. 字段 Presence（显式追踪→默认不追踪→feature开关）
    2. 枚举类型（闭合→开放→闭合可选）
    3. 扩展机制（extensions→Any→feature+Any）
    4. 默认值语义（自定义→类型默认→feature控制）
    5. Packed 编码（显式声明→默认packed→feature控制）
    6. 未知字段（保留→丢弃→恢复→feature控制）
  - 每个功能包含：proto1/proto2中的行为→proto3中的变化→变化原因→Editions中的处理→迁移影响
  - 融入 I 阶段的核心洞察（设计哲学变迁、减法-回归辩证法）
  - 添加 YAML frontmatter 和章末导航
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `human-judgement` TR-7.1: 覆盖≥6个核心功能
  - `human-judgement` TR-7.2: 每个功能演进包含"为什么变"的解释，而非仅"变了什么"
  - `human-judgement` TR-7.3: 功能演进有清晰的版本脉络（proto2→proto3→Editions）
- **Notes**: 这是文档中最有洞察深度的章节，体现七概念分析价值

## [x] Task 8: 编写 04-selection-guide.md（选型决策指南）
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 编写版本选型决策指南 04-selection-guide.md
  - 内容结构：
    - 选型决策树（ASCII 或文本描述）
    - 场景-版本匹配矩阵（≥6种典型场景）
    - E阶段萃取的"序列化IDL版本选型决策模型"模式
    - 常见误区与反模式
    - Editions 推荐策略（什么情况下直接用 Editions）
  - 典型场景覆盖：
    1. 新建 gRPC 微服务
    2. 配置 DSL/配置文件（如 Caffe）
    3. 持久化存储格式
    4. 跨团队公开 API
    5. 遗留 proto2 系统维护
    6. 多语言项目
  - 添加 YAML frontmatter 和章末导航
- **Acceptance Criteria Addressed**: AC-4, AC-6, AC-7
- **Test Requirements**:
  - `human-judgement` TR-8.1: 决策树可执行（输入场景特征能得出明确推荐）
  - `human-judgement` TR-8.2: 场景矩阵覆盖≥6种场景
  - `human-judgement` TR-8.3: 包含≥3个反模式/常见误区
- **Notes**: 以 caffe.proto 作为"配置DSL选proto2"的验证案例

## [x] Task 9: 编写 05-migration-guide.md（迁移路径与风险清单）
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 编写迁移指南 05-migration-guide.md
  - 内容结构：
    - proto2→proto3 迁移：逐项检查清单（required/default/extensions/packed/enum/group/presence）
    - proto2→proto3 渐进式迁移策略（利用线格式兼容性分阶段迁移）
    - proto2/proto3→Editions 迁移：Prototiller 工具介绍、feature 映射表
    - 线格式兼容性边界详细说明（什么能互解析、什么不能）
    - 以 caffe.proto 为实例的迁移成本评估（统计有多少处需要修改）
  - 添加 YAML frontmatter 和章末导航
- **Acceptance Criteria Addressed**: AC-5, AC-7
- **Test Requirements**:
  - `human-judgement` TR-9.1: 迁移检查清单≥8个检查项
  - `programmatic` TR-9.2: 以 caffe.proto 为实例验证，能识别出其使用的所有 proto2 独有特性
  - `human-judgement` TR-9.3: 包含渐进式迁移策略（非一刀切方案）
  - `human-judgement` TR-9.4: 线格式兼容性说明清晰标注兼容/不兼容边界
- **Notes**: 对照 caffe.proto 实际文件验证检查清单的完备性

## [x] Task 10: 编写 00-overview.md 总览与导航
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 编写总览文档 00-overview.md
  - 内容结构：
    - protobuf 简介与本wiki定位
    - 文档结构图与阅读路径建议（快速查阅/版本选型/迁移评估/深度学习四种路径）
    - 版本演进速查表（一页纸版本对比要点）
    - 与其他 wiki 的关系（idl-wiki基础、caffe-architecture-wiki实例）
    - 章末导航（指向01）
  - 添加 YAML frontmatter
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-10.1: 提供≥3种不同阅读路径（快速入门/深度研读/迁移查阅）
  - `human-judgement` TR-10.2: 速查表能在1分钟内回答"我应该用哪个版本"
- **Notes**: 00-overview 是读者进入 wiki 的第一个文档

## [x] Task 11: 创建 README.md 索引并更新交叉引用
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 创建 README.md（遵循项目自动索引格式，含 README_INDEX_START/END 标记）
  - 建立与 idl-wiki 的交叉引用：在 idl-wiki 相关章节添加"深度阅读：protobuf-wiki"链接
  - 建立与 caffe-architecture-wiki 的交叉引用：在 protobuf-wiki 中引用 caffe proto2/proto3 分析
  - 确保所有章末导航链接正确
  - 参考项目现有 wiki 的 README 风格
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-11.1: README.md 包含所有 6 个文档（00-05）的索引条目
  - `programmatic` TR-11.2: idl-wiki/04-major-idl-specs.md 中添加了指向 protobuf-wiki 的交叉引用
  - `human-judgement` TR-11.3: 所有章末导航链接（上一章/返回/下一章）指向正确文件
- **Notes**: 交叉引用更新应最小化对 idl-wiki 的修改（仅添加链接，不改内容）

## [x] Task 12: 链接检查与最终验证
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 运行 `python .agents/scripts/check-links.py --path ".agents/docs/knowledge/learning/01-agent-protocols-interfaces/protobuf-wiki"` 验证所有链接
  - 同时检查被修改的 idl-wiki 文件链接
  - 检查所有文档的 frontmatter 完整性
  - 检查文档编号连续性（00-05）
  - 修复任何发现的断链
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-12.1: check-links.py 报告无断链（允许目录链接警告）
  - `human-judgement` TR-12.2: 所有 6 个文档（00-05）+ README 均存在且编号连续
  - `human-judgement` TR-12.3: 所有文件有完整 YAML frontmatter（id、title、date、tags 字段）
- **Notes**: 这是最终质量门禁，必须通过才能标记完成
