# 秒悟大使入驻指南 - The Implementation Plan (Decomposed and Prioritized Task List)

> 方法论：七概念知识沉淀链路（R→I→E）
> 质量门：G1（事实无因果词）→ G2（洞察四元组完整）→ G3（模式可迁移）

---

## [ ] Task 1: R阶段 - 事实采集与结构化整理
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 复盘采集钉钉文档和阿里云官网的全部事实信息
  - 按主题分类整理：基本介绍、入驻条件、权益体系、操作流程、活动信息、FAQ、风险规则
  - 纯客观描述，去除主观评价和因果推断词（"因为"、"所以"、"导致"等）
  - 交叉验证两个信息源，标记不一致或需要确认的地方
- **Acceptance Criteria Addressed**: [AC-1, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 所有关键数字（返佣10%、关联期90/365天、9.9元价格、8月1元券等）必须准确，与官方文档一致
  - `human-judgement` TR-1.2: 事实描述部分无主观评价、无因果推断词，纯客观陈述
  - `human-judgement` TR-1.3: 覆盖官方文档中的全部11个Q&A问题
  - `human-judgement` TR-1.4: 包含所有官方链接（云大使官网、承接页、报名链接等）
- **Notes**: G1质量门检查点，不通过不得进入I阶段

---

## [ ] Task 2: I阶段 - 洞察提炼（关键要点+风险点+实操建议）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 基于整理的事实，提炼入驻过程中的关键操作要点
  - 识别新手容易踩坑的风险点：
    - 关联用户必须"二次点击"（注册后登录状态下再次点击链接）
    - 自推自买无返佣
    - 前30天付款才能延长到365天关联期
    - 链接需要先测试再推广
  - 提炼实操建议：首单转化钩子（9.9元套餐）、客户查看路径、佣金结算规则等
  - 洞察四元组：现象描述 + 本质分析 + 影响评估 + 操作建议
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-6, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 至少识别5个关键操作要点或坑点
  - `human-judgement` TR-2.2: "二次点击关联"规则必须醒目标注，这是最高频的失败原因
  - `human-judgement` TR-2.3: 每个洞察点包含：是什么→为什么重要→怎么做/怎么避
  - `human-judgement` TR-2.4: 排位赛权重（新注册40%+新订阅60%）和奖励梯度清晰呈现
- **Notes**: G2质量门检查点，洞察四元组不完整不得进入E阶段

---

## [ ] Task 3: E阶段 - 萃取结构化入驻指南文档
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 按照标准指南结构撰写完整的Markdown文档：
    1. 文档开头：快速了解（这是什么、你能获得什么、谁适合加入）
    2. 入驻前准备：资质要求、材料准备
    3. 图文步骤：4步入驻流程（加入云大使→生成链接→获取资料→推广）
    4. 权益体系：基础权益+排位赛+8月限时权益（表格呈现）
    5. 避坑指南：红线规则、常见失败原因
    6. 自查Checklist：入驻前/中/后
    7. FAQ：11个官方问题+补充问题
    8. 链接汇总：所有关键URL
    9. 结尾：免责声明（以官方为准）
  - 关键信息用表格、加粗、引用块突出
  - 时效性信息标注时间范围
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-4, AC-5, AC-6, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 文档结构符合上述9个部分，逻辑流畅
  - `human-judgement` TR-3.2: 操作步骤是Step-by-Step的，新手可按图索骥
  - `human-judgement` TR-3.3: 至少3个关键信息用表格呈现（权益对比、排位赛奖励、FAQ）
  - `human-judgement` TR-3.4: Checklist分阶段（入驻前/中/后），可打印逐项打勾
  - `human-judgement` TR-3.5: 文档末尾有"详细规则以阿里云官方发布为准"的免责声明
  - `human-judgement` TR-3.6: 8月活动信息明确标注"2026年8月限定"
- **Notes**: G3质量门检查点，产出最终指南文档

---

## [ ] Task 4: 质量校验与最终完善
- **Priority**: medium
- **Depends On**: Task 3
- **Description**: 
  - 按G1-G3质量门逐项校验
  - 通读全文，检查语言流畅性、格式一致性
  - 验证所有链接格式正确
  - 检查Markdown层级（不超过4级）
  - 确认无遗漏的关键信息
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-4.1: G1通过：事实部分准确无主观推测
  - `human-judgement` TR-4.2: G2通过：关键要点和风险点都有操作建议
  - `human-judgement` TR-4.3: G3通过：指南结构清晰可复用
  - `human-judgement` TR-4.4: 无错别字、格式错误、死链
  - `human-judgement` TR-4.5: Markdown标题层级正确，无跳级
- **Notes**: 最终交付前的质量把关

---

## 交付物
- 主文档：`miaowu-ambassador-guide.md`（最终入驻指南）
- 位置：项目合适的文档目录（待确认）
