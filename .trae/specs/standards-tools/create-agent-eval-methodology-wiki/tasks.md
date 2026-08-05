# Agent评测体系化建设方法论 Wiki教程与知乎文章 - The Implementation Plan

## [x] Task 1: 目录结构与创作准备

## [x] Task 2: R阶段 - 资料梳理与事实清单构建（G1质量门）

## [x] Task 3: F阶段 - 第一性原理本质思考（V门前置准备）
- **Priority**: high
- **Depends On**: [Task 2]
- **Description**:
  - 问题界定：Agent评测的本质问题是什么？（不是"跑个分"而是"质量闭环"）
  - 假设剥离：列出行业关于Agent评测的10+默认假设，逐条质疑
  - 要素识别：拆解评测体系到不可再分的基础单元（测试用例、评分标准、执行器、分析器、迭代回路）
  - 公理提炼：提炼Agent评测体系的5+条不证自明的公理
  - 从公理自下而上重构评测体系框架
  - 记录框架搭建阶段的思考过程：为什么选六大模块？为什么是八阶段？决策依据是什么？
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-4, NFR-2]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 公理列表自洽独立，无循环论证
  - `human-judgement` TR-3.2: 框架设计从公理推导而来，不是经验拼凑
  - `programmatic` TR-3.3: 创作过程记录中包含框架设计的决策依据、备选方案对比、最终选择理由
  - `human-judgement` TR-3.4: 识别并挑战了≥5个行业常见默认假设（如"评测分数越高=产品越好"）
- **Notes**: F之后必须做V对抗审查，不能跳过

## [x] Task 4: I阶段 - 核心洞察提炼（G2质量门）
- **Priority**: high
- **Depends On**: [Task 3]
- **Description**:
  - 从事实清单和公理推导中提炼3-5条核心洞察
  - 每条洞察必须包含四元组：陈述+证据（引用F-xxx事实编号）+反常识点+行动建议
  - 洞察维度独立不重叠：至少覆盖方法论层、实施层、避坑层
  - 确保洞察有反常识性，不是"评测很重要"这类正确的废话
  - G2质量门检查：四元组完整、证据可追溯、有反常识、行动具体
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-4.1: 核心洞察3-5条，每条包含陈述/证据/反常识/行动四元组
  - `programmatic` TR-4.2: 每条洞察的证据引用R阶段事实编号，可追溯
  - `human-judgement` TR-4.3: 洞察有反常识价值，挑战了默认认知
  - `human-judgement` TR-4.4: 行动建议具体可执行，不是空泛口号
- **Notes**: 洞察是wiki的灵魂，直接决定内容深度

## [x] Task 5: E阶段 - Wiki教程主体内容撰写（模块1-3）
- **Priority**: high
- **Depends On**: [Task 4]
- **Description**:
  - 模块1：方法论概述（定义、价值、成熟度模型0-5级、4个常见误区）
  - 模块2：核心框架对比（6大框架深度对比表+选型决策树）
  - 模块3：关键指标体系（四维80+指标详解，含定义/测量方法/参考阈值）
  - 每个模块独立成文件，原子化组织
  - 边写边记录内容撰写阶段的思考：如何平衡深度与可读性？如何组织复杂信息？遇到哪些表达困难？如何解决？
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, NFR-3]
- **Test Requirements**:
  - `programmatic` TR-5.1: 模块1包含成熟度模型（0-5级）、≥4个常见误区
  - `programmatic` TR-5.2: 模块2包含6个框架的对比表格（≥8个对比维度）和选型决策树
  - `programmatic` TR-5.3: 模块3覆盖四个维度，关键指标≥50个，每个指标有定义/测量/阈值
  - `human-judgement` TR-5.4: 内容组织清晰，逻辑连贯，专业术语有解释
  - `programmatic` TR-5.5: 创作过程记录同步更新
- **Notes**: 先写骨架再填肉，用表格和决策树降低理解成本

## [x] Task 6: E阶段 - Wiki教程主体内容撰写（模块4-6）
- **Priority**: high
- **Depends On**: [Task 5]
- **Description**:
  - 模块4：八阶段实施步骤（每阶段输入/输出/工具/验收/坑点，0-8周落地清单）
  - 模块5：8个行业案例分析（每个案例：背景/做法/成果/经验教训/可复用要点）
  - 模块6：常见问题解答（FAQ≥20条，覆盖选型/实施/踩坑三类）
  - 添加引用来源、参考文献、延伸阅读
  - 继续记录内容撰写阶段的思考和挑战
- **Acceptance Criteria Addressed**: [AC-1, AC-4, AC-5, AC-6, NFR-3]
- **Test Requirements**:
  - `programmatic` TR-6.1: 模块4包含完整八阶段，每阶段有输入/输出/工具/验收标准/常见坑
  - `programmatic` TR-6.2: 模块4包含0-8周落地清单，按周分解任务
  - `programmatic` TR-6.3: 模块5包含8个案例，每个案例5要素完整（背景/做法/成果/教训/要点）
  - `programmatic` TR-6.4: 模块6 FAQ≥20条，分类组织
  - `human-judgement` TR-6.5: 实施步骤"看完能直接照着做"，案例真实可信不编造
  - `programmatic` TR-6.6: 所有引用来源标注清晰
- **Notes**: 实施步骤是wiki最有价值的部分，要写得像操作手册

## [x] Task 7: 创作过程记录文档完善与G3质量门
- **Priority**: high
- **Depends On**: [Task 6]
- **Description**:
  - 整合四个阶段（资料收集/框架搭建/内容撰写/审核修订）的过程记录
  - 萃取"技术wiki创作方法论"可复用模式
  - 模式必须包含：触发场景、核心步骤、反模式（≥3个）、检验标准、跨场景迁移示例
  - G3质量门检查：模式可迁移、有反模式、有检验标准
- **Acceptance Criteria Addressed**: [AC-6, AC-10]
- **Test Requirements**:
  - `programmatic` TR-7.1: 创作过程记录完整覆盖四阶段，每个阶段有思考/决策/挑战/解决方案
  - `programmatic` TR-7.2: 萃取的wiki创作模式包含触发/步骤/反模式（≥3个）/检验/迁移五要素
  - `human-judgement` TR-7.3: 过程记录真实不做作，不是事后编的"完美流程"
  - `human-judgement` TR-7.4: 萃取的模式确实可复用，不是针对本次任务的定制
- **Notes**: 反模式比正确做法更有价值，一定要写真实踩过的坑

## [x] Task 8: V阶段 - 四视角对抗审查与内容修订
- **Priority**: high
- **Depends On**: [Task 7]
- **Description**:
  - 🔴魔鬼代言人视角：挑刺，找反例，质疑因果关系，找幸存者偏差
  - 🟢新人视角：找看不懂的术语，找"然后呢"不知道下一步的地方，要求Hello World示例
  - 🟠老板视角：问ROI，问企业能不能用，问风险，问什么时候见效
  - 🔵未来视角：问这会不会过时，问二阶效应，问缺失的拼图
  - 汇总审查意见（≥10条），按P0-P3分级
  - 至少采纳3条意见对wiki内容进行实质性修订
  - 记录审核修订阶段的挑战：如何平衡不同视角的冲突意见？如何取舍？
  - V门检查：四视角覆盖、意见≥10条、采纳≥3条、有修订记录
- **Acceptance Criteria Addressed**: [AC-8, NFR-2, NFR-4]
- **Test Requirements**:
  - `programmatic` TR-8.1: 四视角审查意见≥10条，每条有具体攻击点，不是客套话
  - `programmatic` TR-8.2: 至少采纳3条意见进行修订，有修订前后对比记录
  - `human-judgement` TR-8.3: 审查意见有深度，不是表面挑错
  - `programmatic` TR-8.4: 创作过程记录补充审核修订阶段内容
- **Notes**: 表演式审查是自欺欺人，必须真找问题、真修改

## [x] Task 9: 知乎文章撰写
- **Priority**: medium
- **Depends On**: [Task 8]
- **Description**:
  - 知乎文章定位：专业科普，面向技术从业者和产品经理
  - 文章结构：开头用痛点引入→生动案例讲清楚为什么需要评测→核心框架通俗讲解→实施路线简化版→创作经验分享→结尾总结
  - 语言风格：避免过多学术术语，用生活化类比，加入1-2个有趣的行业故事
  - 篇幅控制：5000-8000字
  - 包含wiki创作经验与心得章节，真诚分享创作过程中的真实感受
- **Acceptance Criteria Addressed**: [AC-7, NFR-4]
- **Test Requirements**:
  - `programmatic` TR-9.1: 字数5000-8000字
  - `human-judgement` TR-9.2: 非AI专业读者能看懂80%以上内容，语言生动不枯燥
  - `human-judgement` TR-9.3: 有具体案例和故事，不是干巴巴的知识罗列
  - `human-judgement` TR-9.4: 创作经验分享真实真诚，有可借鉴的内容
- **Notes**: 知乎文章和wiki是不同的产品——wiki是手册，知乎文章是"说服+启发"

## [x] Task 10: A阶段 - 原子化拆分、格式合规与链接修复
- **Priority**: medium
- **Depends On**: [Task 9]
- **Description**:
  - 检查文件大小，对超过5000字符的文件进行合理原子化拆分
  - 统一所有文件的YAML frontmatter格式（id/title/date/tags/source等字段）
  - 添加/更新所有交叉引用，使用相对路径
  - 运行链接检查脚本，修复断链
  - 检查文件名kebab-case规范，无中文
  - 检查markdown表格格式
  - 补充完善创作过程记录的审核修订阶段
- **Acceptance Criteria Addressed**: [AC-9, NFR-6]
- **Test Requirements**:
  - `programmatic` TR-10.1: 所有文件名kebab-case，无中文、无空格
  - `programmatic` TR-10.2: 所有文件有完整YAML frontmatter，字段齐全
  - `programmatic` TR-10.3: 运行link-check脚本无断链
  - `programmatic` TR-10.4: 每个文件500-5000字符，语义完整不碎片化
  - `programmatic` TR-10.5: markdown表格格式正确，无语法错误
- **Notes**: 使用finalize-atomization脚本辅助断链修复

## [x] Task 11: 最终质量检查与G4质量门
- **Priority**: high
- **Depends On**: [Task 10]
- **Description**:
  - 通读所有内容，检查逻辑一致性和衔接
  - 运行ci-check基础检查（链接、格式、命名规范）
  - 验证所有AC验收标准：逐项核对checklist
  - G4质量门检查：产出单一职责（wiki/创作记录/知乎文章三者边界清晰）、可独立验证、可交付
  - 更新相关索引文件（如knowledge目录README）
- **Acceptance Criteria Addressed**: [AC-1到AC-10全部]
- **Test Requirements**:
  - `programmatic` TR-11.1: ci-check基础检查通过
  - `programmatic` TR-11.2: checklist.md所有检查项打勾完成
  - `human-judgement` TR-11.3: 通读无明显逻辑矛盾、无错别字、无格式错误
  - `human-judgement` TR-11.4: wiki/创作记录/知乎文章三者定位清晰不混淆
- **Notes**: G4是交付前最后一道关，不能为了赶工放水