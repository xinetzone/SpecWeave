# 跨文化第一性原理比较研究 - The Implementation Plan

## [ ] Task 0: 对抗性审查标准与"反向语义漂移"防御机制制定
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 复用v1.0对抗性审查协议（来源分级/可信度评分/五维验证/偏差识别）
  - 建立"反向语义漂移"防御机制：防止以西方概念框架生硬套用东方思想
  - 制定古文引用验证标准：关键原文至少比对2个权威注译本
  - 制定学派立场标注规范：标注不同学派对同一概念的不同解读
  - 建立跨文化认知偏差检查清单：西方中心/东方主义/文化挪用/概念误植
  - 设计来源验证日志模板（复用v1.0模板，增加古文注译本比对字段）
  - 输出：00-cross-cultural-review-protocol.md
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-0.1: "反向语义漂移"检查清单包含至少5个防御检查点
  - `programmatic` TR-0.2: 古文引用验证标准明确权威注译本选择规则
  - `human-judgment` TR-0.3: 防御机制具体可操作，不是抽象原则声明
- **Notes**: 本任务是所有资料搜集工作的前置依赖，v1.0对抗性审查经验的跨文化适配

## [ ] Task 1: 道家哲学核心概念系统整理
- **Priority**: high
- **Depends On**: Task 0
- **Description**: 
  - 搜集老子《道德经》中"道"作为宇宙本原的原始论述（至少5章）
  - 搜集"德""自然""无为""朴"等核心概念的古文原文与权威注译
  - 搜集庄子对"道"的展开论述（《逍遥游》《齐物论》等篇）
  - 整理道家"根本性推理"的方法论特征（反名言、反人为、回归自然）
  - 分析道家思维与西方第一性原理的异同
  - 对抗性审查：古文原文比对王弼注、陈鼓应注译等至少2个权威版本
  - 输出：01-daoism-core-concepts.md
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 覆盖"道""德""自然""无为"四个核心概念
  - `programmatic` TR-1.2: 每个概念引用《道德经》至少3章原文
  - `programmatic` TR-1.3: 引用至少2个权威注译本
  - `human-judgment` TR-1.4: 区分老子与庄子在概念使用上的差异

## [ ] Task 2: 儒家思想核心概念系统整理
- **Priority**: high
- **Depends On**: Task 0
- **Description**: 
  - 搜集《大学》"格物致知"全文及朱熹、王阳明注解
  - 搜集"本""末""体""用"等核心概念的古文原文
  - 搜集《中庸》"诚"的概念及"天命之谓性"的根本性命题
  - 整理朱熹"即物穷理"与王阳明"致良知"的根本性推理方法差异
  - 分析儒家思维与西方第一性原理的异同
  - 对抗性审查：古文原文比对权威注译本，标注学派差异
  - 输出：02-confucianism-core-concepts.md
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 覆盖"本""体""用""格物致知"四个核心概念
  - `programmatic` TR-2.2: 引用《大学》《中庸》关键原文
  - `programmatic` TR-2.3: 覆盖朱熹与王阳明的主要观点差异
  - `human-judgment` TR-2.4: 不陷入学派之争，客观呈现差异

## [ ] Task 3: 墨家方法论核心概念系统整理
- **Priority**: high
- **Depends On**: Task 0
- **Description**: 
  - 搜集《墨子》中"三表法"的完整原文与解释
  - 搜集"类""故""理"等墨家逻辑范畴的古文原文
  - 分析"三表法"与第一性原理"可验证性"原则的结构性对应
  - 整理墨家"兼爱""非攻"等主张中的根本性推理方式
  - 分析墨家方法论与西方第一性原理的异同
  - 对抗性审查：古文原文比对权威注译本
  - 输出：03-mohism-core-concepts.md
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 覆盖"三表法""类""故""理"四个核心概念
  - `programmatic` TR-3.2: 引用《墨子》关键原文
  - `human-judgment` TR-3.3: 包含与"可验证性"原则的对应分析

## [ ] Task 4: 佛教因明学核心概念系统整理
- **Priority**: high
- **Depends On**: Task 0
- **Description**: 
  - 搜集"现量""比量"的认知二分法原文与解释
  - 搜集"宗·因·喻"三支作法的推理结构原文
  - 搜集陈那《因明正理门论》中的逻辑规则
  - 分析因明学与西方逻辑学/第一性原理推理的异同
  - 对抗性审查：古文原文比对权威注译本
  - 输出：04-buddhist-logic-core-concepts.md
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 覆盖"现量""比量""宗因喻"三个核心概念
  - `programmatic` TR-4.2: 引用陈那《因明正理门论》关键原文
  - `human-judgment` TR-4.3: 包含与西方逻辑学的对比分析

## [ ] Task 5: 跨文化四维比较框架建立
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**: 
  - 建立四维比较框架：概念定义→核心特征→哲学功能→应用场景
  - 对四个体系逐一进行四维分析
  - 建立跨体系比较矩阵（至少20个比较维度）
  - 标注共性维度与差异维度
  - 输出：05-cross-cultural-comparison-framework.md
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 四维比较框架覆盖所有四个体系
  - `programmatic` TR-5.2: 比较矩阵包含至少20个比较维度
  - `human-judgment` TR-5.3: 共性维度与差异维度明确标注

## [ ] Task 6: 与v1.0西方第一性原理的对比分析
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 共性识别：找出各体系与西方第一性原理的共通原则（至少5条）
  - 差异分析：找出各体系独特的方法论贡献（至少5条）
  - 互补关系：分析不同体系在哪些维度上可以互补（至少3组）
  - 统一框架：提炼跨文化第一性原理思维的共性框架
  - 输出：06-comparison-with-western-first-principles.md
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 共性识别至少5条
  - `programmatic` TR-6.2: 差异分析至少5条
  - `programmatic` TR-6.3: 互补关系至少3组
  - `human-judgment` TR-6.4: 统一框架具有可操作性

## [ ] Task 7: 方法论提炼与可操作框架
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 提炼跨文化第一性原理思维的统一操作步骤
  - 标注各步骤在不同文化体系中的实现方式
  - 建立跨文化第一性原理思维工具/检查清单
  - 识别跨文化应用中的常见误区
  - 输出：07-cross-cultural-methodology-framework.md
- **Acceptance Criteria Addressed**: G7
- **Test Requirements**:
  - `human-judgment` TR-7.1: 统一操作步骤可直接用于指导实践
  - `human-judgment` TR-7.2: 检查清单覆盖跨文化应用的关键风险点

## [ ] Task 8: 知识档案整合与索引建立
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**: 
  - 建立知识档案README索引（导航入口+阅读路径）
  - 建立跨文化概念对照总表（西方第一性原理↔中方概念映射）
  - 建立术语统一表（防止中英文概念混用）
  - 建立时间线（各体系关键哲学家与著作年表）
  - 建立来源验证日志（汇总所有资料的审查记录）
  - 输出：README.md + 08-concept-mapping-table.md + 09-terminology-alignment.md + 10-timeline.md + 11-source-validation-log.md
  - 归档至 `docs/knowledge/learning/first-principles/chinese-philosophy-parallels/`
- **Acceptance Criteria Addressed**: AC-7, AC-9
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有文件名符合kebab-case规范
  - `programmatic` TR-8.2: 一级来源占比不低于70%
  - `programmatic` TR-8.3: 单文件不超过500行
  - `human-judgment` TR-8.4: README索引导航清晰，阅读路径合理

## [ ] Task 9: 复盘与洞察萃取
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - 执行标准化复盘四步流程（事实收集→过程分析→洞察提取→报告生成）
  - 萃取跨文化比较研究的方法论洞察
  - 评估"反向语义漂移"防御机制的有效性
  - 沉淀可复用模式（如适用）
  - 更新第一性原理指令集（如适用，增加跨文化视角执行指引）
  - 输出：复盘报告（四文件结构）+ 洞察原子卡片
- **Acceptance Criteria Addressed**: 项目闭环
- **Test Requirements**:
  - `human-judgment` TR-9.1: 复盘报告符合复盘规范
  - `human-judgment` TR-9.2: "反向语义漂移"防御机制有效性得到评估