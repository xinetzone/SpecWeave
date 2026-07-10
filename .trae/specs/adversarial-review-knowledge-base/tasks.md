---
id: adversarial-review-knowledge-base-tasks
title: 对抗性审查知识库 - 实施计划
version: "1.0"
created_at: "2026-07-10"
status: completed
---

# 对抗性审查知识库 - The Implementation Plan

## [x] Task 1: 目录初始化与格式规范准备
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建目录 `d:\AI\docs\knowledge\learning\02-agent-engineering-methodology\adversarial-review-wiki\`
  - 读取现有知识库的2-3个典型文件（00-overview.md模板、README.md索引格式）确认实际格式规范
  - 复制并适配frontmatter模板和可信度标记标准
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录创建成功，路径正确
  - `human-judgment` TR-1.2: 格式规范确认完毕，与现有知识库保持一致
- **Notes**: 遵循"格式一致性优先原则"——以现有同类文档实际做法为权威标准，而非仅凭规范描述

## [x] Task 2: 核心概念与哲学起源文档
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 00-overview.md：知识库概览、可信度评级说明、阅读路径、文件索引
  - 创建 01-core-concepts.md：核心概念定义、相关概念辨析、两大应用分支介绍
  - 创建 02-philosophy-origins.md：思想源头追溯（怀疑主义→证伪主义→同行评审→红队演练→认知偏差研究）
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 3个文件创建成功，文件名符合kebab-case规范，包含正确frontmatter
  - `human-judgment` TR-2.2: 00-overview.md包含至少3条分层次阅读路径（入门/进阶/专家）
  - `human-judgment` TR-2.3: 01-core-concepts.md清晰区分对抗性审查与代码审查/红队/审计等概念
  - `human-judgment` TR-2.4: 单个文件不超过500行
- **Notes**: 先完成00-overview.md框架，确定文件编号和主题边界，再写具体内容

## [x] Task 3: 方法论框架文档
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 03-methodology-framework.md：系统阐述两大场景方法论
    - 知识研究场景：七模块完整协议（阶段0-6）
    - AI协作/代码场景：多Agent对抗模式（四大攻击者角色、执行流程、Prompt标准形式）
  - 整合项目内已有模式文档内容（adversarial-review-protocol.md和adversarial-review-prompt-pattern.md）
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件创建成功，格式正确
  - `human-judgment` TR-3.2: 两大应用场景方法论均完整覆盖，逻辑清晰
  - `human-judgment` TR-3.3: 项目内已有实践经验被正确整合，没有遗漏核心要点
  - `human-judgment` TR-3.4: 单个文件不超过500行（如超过则拆分）
- **Notes**: 这是知识库的核心文档，需投入最多精力确保质量

## [x] Task 4: 认知偏差防御与检查清单工具
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 04-cognitive-biases-defense.md：审查场景高频认知偏差（确认偏差/权威偏差/锚定效应/群体思维/幸存者偏差/事后归因等），含识别特征、审查中表现、防御措施、检查项。与第一性原理知识库做交叉引用，补充审查场景特有偏差
  - 创建 05-checklists-templates.md：可直接复用的工具集合
    - 知识研究五维验证检查清单
    - 代码对抗审查四大攻击者检查清单
    - 来源可信度评分表
    - 异常标记模板
    - 验证日志模板
    - 多Agent对抗Prompt标准模板
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 2个文件创建成功，格式正确
  - `human-judgment` TR-4.2: 检查清单和模板可直接复用（读者可复制使用）
  - `human-judgment` TR-4.3: 与第一性原理认知偏差部分的交叉引用正确，无重复内容
  - `human-judgment` TR-4.4: Prompt模板包含四大攻击者角色的标准形式
- **Notes**: 05文件是实用性最强的文档，确保工具可操作、可直接使用

## [x] Task 5: 行业标准与开源工具文档
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 创建 06-industry-standards.md：整合外部权威标准（OWASP代码审查指南/LLM Top 10、NIST AI RMF、MITRE ATLAS、EU AI Act），标注核心要点与适用场景
  - 创建 07-open-source-tools.md：开源工具链指南（Garak/PyRIT/Promptfoo/Inspect AI/DeepTeam/Purple Llama），包含对比矩阵、选型指南、快速上手、CI/CD集成建议
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 2个文件创建成功，格式正确
  - `human-judgment` TR-5.2: 行业标准部分标注可信度分级，核心要点提炼准确
  - `human-judgment` TR-5.3: 工具对比矩阵包含至少6个工具，覆盖上手难度/多轮攻击/CI集成/学习曲线/最佳场景维度
  - `human-judgment` TR-5.4: 外部链接格式正确，无断链
- **Notes**: 所有外部标准和工具均需标注来源和可信度评级

## [x] Task 6: 实战案例与学术资源文档
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 创建 08-practice-cases.md：实战案例集
    - 本项目AIHOT案例（OOM死循环/未来时间污染/HTML清洗炸弹）
    - 金融公司LLM泄露案例
    - 卡兹克对抗式全局审查方法
    - OpenAI强化学习红队Agent实践
    - 每案例：问题→对抗方法→发现→经验教训
  - 创建 09-academic-resources.md：经筛选的学术资源与权威书籍（Tversky & Kahneman、Nickerson确认偏差综述、NVIDIA PLOS One研究、代码审查心理学论文等），按可信度分级
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 2个文件创建成功，格式正确
  - `human-judgment` TR-6.2: 案例结构统一（问题→方法→发现→教训），数据可追溯
  - `human-judgment` TR-6.3: 学术资源标注完整出处和可信度评级
  - `human-judgment` TR-6.4: 单个文件不超过500行

## [x] Task 7: 术语表与资源索引文档
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**:
  - 创建 11-glossary.md：核心术语表，中英文对照、精确定义、交叉引用
  - 创建 12-resources.md：延伸阅读与外部资源链接，按主题分类
  - 创建 13-quick-reference.md：快速参考速查表（核心流程、检查清单、工具命令、Prompt模板极简版）
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `programmatic` TR-7.1: 3个文件创建成功，格式正确
  - `human-judgment` TR-7.2: 术语表覆盖知识库中所有专业术语，定义准确
  - `human-judgment` TR-7.3: 速查表内容精炼，可打印使用（1-2页A4纸规模）
- **Notes**: 这三个文档可在核心内容完成后补充，在最后阶段统一完善

## [x] Task 8: 来源验证档案（自举验证）
- **Priority**: high
- **Depends On**: Task 2-7（所有内容文档完成后）
- **Description**:
  - 创建 10-source-validation-log.md：完整的来源验证档案
    - 五维验证执行记录
    - 来源类型统计（一级/二级/三级）
    - 可信度分布统计（🟢A/🔵B/🟡C/🔴D）
    - 关键事实交叉验证记录（≥2个独立来源）
    - 认知偏差识别记录（构建过程中识别和防御的偏差）
    - 异常标记汇总
    - 排除资料记录（为什么某些资源未被采用）
  - 这是"用对抗性审查方法构建对抗性审查知识库"的自举验证核心
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件创建成功，格式正确
  - `human-judgment` TR-8.2: 包含明确的统计数据，一级来源≥70%、🟢A级≥60%、🔴D级=0%
  - `human-judgment` TR-8.3: 所有关键事实有交叉验证记录，验证过程可审计
  - `human-judgment` TR-8.4: 完整记录构建过程中识别到的认知偏差及防御措施
- **Notes**: 这是质量门禁文档——统计数据不达标则需要回溯补充/修正内容

## [x] Task 9: 索引文件与交叉引用完善
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 创建README.md目录索引（遵循现有自动生成格式）
  - 完善所有文档间的交叉引用链接
  - 添加与第一性原理知识库、相关模式文件的双向引用
  - 更新上级目录 `02-agent-engineering-methodology/README.md`，将新知识库加入索引
- **Acceptance Criteria Addressed**: AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-9.1: README.md创建成功，格式符合现有规范
  - `programmatic` TR-9.2: 运行链接检查脚本，确保无断链
  - `human-judgment` TR-9.3: 所有内部交叉引用正确，双向链接有效
  - `programmatic` TR-9.4: 上级目录README已更新，包含新知识库索引
- **Notes**: 链接检查是重要质量门禁，必须确保所有链接可达

## [x] Task 10: 最终质量验证与收尾
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 运行文件名规范检查脚本
  - 运行链接检查脚本
  - 通读所有文档，检查格式一致性、逻辑连贯性
  - 验证所有可信度标记和异常标记使用正确
  - 更新00-overview.md中的最终统计数据
  - 确认自举验证（知识库构建过程本身作为对抗性审查案例）成立
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8（全部验收标准）
- **Test Requirements**:
  - `programmatic` TR-10.1: `python .agents/scripts/check-filename-convention.py` 通过
  - `programmatic` TR-10.2: 链接检查脚本无错误
  - `human-judgment` TR-10.3: 所有文档通读检查完成，格式一致，逻辑连贯
  - `human-judgment` TR-10.4: 可信度标记使用规范统一，没有错标漏标
  - `human-judgment` TR-10.5: 00-overview.md中的统计数据与10-source-validation-log.md一致
- **Notes**: 这是最终验收步骤，所有检查必须通过才能标记完成
