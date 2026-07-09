---
id: "universal-prd-template"
title: "通用PRD模板"
type: "template"
source: "retrospective-analysis"
created_at: "2026-07-09"
completed_at: "2026-07-09"
status: "completed"
theme: "methodology-patterns"
version: "1.1"
archive_location: "docs/retrospective/patterns/methodology-patterns/spec-workflow/"
reference_spec: "frontmatter-specification,prd-structure-guide"
---

<!--
⚠️ 使用说明：
1. 复制本文件，重命名为 [项目id].md，id使用kebab-case英文命名
2. 修改frontmatter字段：id必填且全局唯一，status初始为candidate
3. 按章节填写内容，完成后删除所有<!-- -->注释提示
4. 编号规则：G/NG/NFR/TC/BC/D/A全局连续编号，FR/AC带追溯标记
-->

# {项目中文标题}

<!-- ===== 1. Overview ===== -->
## Overview

**Summary**: ≤50字，一句话说清做什么

**Purpose**: 说明为什么做，解决什么问题，带来什么价值，不涉及技术实现

**Target Users**: 具体目标用户群体，避免"所有用户"这类泛化表述

检查要点：[ ] 3秒能说清做什么 [ ] 三要素齐全 [ ] 无技术细节 [ ] 用户明确

---

<!-- ===== 2. Goals ===== -->
## Goals

3-8个可衡量目标，编号G1,G2...，动词+宾语+可衡量结果，避免"优化/提升"等模糊词，每个Goal映射至少一个AC

- G1: 建立100%外部引用自动验证机制，死链检测率100%
- G2:
- G3:
- G4:
- G5:

检查要点：[ ] 有可衡量指标 [ ] 编号清晰 [ ] 无模糊词 [ ] 3-8个 [ ] 含质量目标

---

<!-- ===== 3. Non-Goals ===== -->
## Non-Goals

明确不做什么+为什么，推迟事项说明未来重评估条件，编号NG1,NG2...

- NG1: 不实现自动事实核查——需领域知识，v2.0独立评估
- NG2:
- NG3:

检查要点：[ ] 每个说明"不做什么"+"为什么" [ ] 推迟项说明条件 [ ] 无"以后再说" [ ] 至少3条

---

<!-- ===== 4. Background & Context ===== -->
## Background & Context

回答"为什么是现在"，提供决策的时空坐标。以下子章节为推荐结构，可根据项目特点调整。

### 历史脉络
时间线形式说明前因后果，引用具体证据（文档/commit/日期）
- YYYY-MM-DD:

### 问题现状
描述当前存在的具体问题，用数据/事实支撑
1.
2.

### 关联项目
列出相关的父项目/子项目/依赖项目
-

检查要点：[ ] 说明"为什么是现在" [ ] 有历史脉络 [ ] 描述清问题 [ ] 提及关联项目

---

<!-- ===== 5. Functional Requirements ===== -->
## Functional Requirements

描述"系统应该做什么"而非"怎么做"，编号FR-1,FR-2...，标记[→Gx]追溯Goal，颗粒度1-3天工作量，子项用FR-1.1缩进

- FR-1 [→G1]: 系统应该能够自动检测Markdown文件中所有外部链接
  - FR-1.1: 支持HTTP/HTTPS协议
  - FR-1.2: 支持标准格式和裸链接
- FR-2 [→G1]:
- FR-3 [→G2]:
- FR-4 [→G3]:

检查要点：[ ] 用"系统应该能够..." [ ] 只描述做什么 [ ] 标记追溯 [ ] 颗粒度合适 [ ] 无技术实现

---

<!-- ===== 6. Non-Functional Requirements ===== -->
## Non-Functional Requirements

定义质量属性，每个必须量化，编号NFR-1,NFR-2...全局连续。按需增加分类（安全性/可用性/兼容性等）。

### 性能
- NFR-1 [→G4]: 单文件(<1000行)检查<5秒

### 可靠性
- NFR-2: 检测准确率>99%（误报<1%）

### 可维护性
- NFR-3: pep8规范，类型注解100%，单文件<500行

检查要点：[ ] 有量化指标 [ ] 编号清晰 [ ] 覆盖关键维度 [ ] 含工程规范 [ ] 无模糊表述

---

<!-- ===== 7. Constraints ===== -->
## Constraints

每个约束说明"是什么"+"为什么"，Technical/Business/Dependencies分类编号，依赖标注[已就绪]/[待完成]

### Technical
- TC1: 仅支持Python 3.10+——利用类型注解新特性

### Business
- BC1: 零预算，不购买付费内容/API

### Dependencies
- D1 [已就绪]: first-principles项目提供对抗性审查经验
- D2 [待完成]:

检查要点：[ ] 分类清晰 [ ] 说明"是什么"+"为什么" [ ] 依赖标注状态 [ ] 含法律/预算约束

---

<!-- ===== 8. Assumptions ===== -->
## Assumptions

把隐含假设显式化，编号A1,A2...，每个说明"假设什么是真的"+"——若不成立，应对措施"，3-8个

- A1: 公开网络可获取足够高质量资料——若不成立，调整评级标准或申请数据库权限
- A2:
- A3:

检查要点：[ ] 是可验证命题 [ ] 说明不成立影响 [ ] 列显而易见假设 [ ] 3-8个 [ ] 无美好愿望

---

<!-- ===== 9. Acceptance Criteria ===== -->
## Acceptance Criteria

Given(前置)→When(操作)→Then(结果)格式，分小节书写更清晰，编号AC-1,AC-2...，标注[Programmatic]/[Human-Judgment]，标记追溯链[→FR-x→Gx]

- AC-1 [→FR-1→G1] [Programmatic]:
  - Given: 含10个链接的测试文件
  - When: 运行检测脚本
  - Then: 10个链接全识别无遗漏
  - Verification: `python scripts/check.py --test` 通过率100%

- AC-2 [→FR-2→G1] [Human-Judgment]:
  - Given:
  - When:
  - Then:
  - Verification: 2名维护者独立审核记录准确率

检查要点：[ ] 有Given/When/Then分节 [ ] 标注验证方式 [ ] 标记追溯链 [ ] Programmatic指明脚本 [ ] Human-Judgment有标准 [ ] 每个FR有对应AC

---

<!-- ===== 10. Open Questions ===== -->
## Open Questions

记录决策过程，已解答[x]未解答[ ]。统一字段：问题/分析/决策&理由/后续计划

- [x] Q1: 是否支持书籍/视频等非网页引用？
  - 分析: 验证机制不同复杂度高
  - 决策&理由: v1.0仅支持网页/论文——当前90%引用是此类，先解决主要问题
  - 后续计划: 非网页引用>20%时重评估

- [ ] Q2: 是否提供IDE插件实时检查？
  - 分析: 需调研使用场景——CI检查还是编写时检查？
  - 阻塞点: 使用场景不明确
  - 后续计划: v1.0先做CLI，收集1个月数据再决策

检查要点：[ ] 已解答含分析/决策/理由 [ ] 未解答说明阻塞点 [ ] 记录被否决选项 [ ] 推迟项说明重评估条件

---

<!-- ===== 可选章节（按需启用，删除注释）=====
## Requirements Traceability Matrix
| Goal | Functional Requirements | Acceptance Criteria |
|------|-------------------------|---------------------|
| G1 | FR-1, FR-2 | AC-1, AC-2 |

## Risks & Mitigation
| 风险来源 | 风险描述 | 可能性 | 影响 | 缓解策略 | 触发条件 |
|----------|----------|--------|------|----------|----------|
| A1 | | 中 | 高 | | |

## Timeline & Milestones
| 里程碑 | 预计日期 | 交付物 | 验收标准 |
|--------|----------|--------|----------|
| M1 | | | |
-->

---

<!-- ===== 11. 版本历史（必填收尾）===== -->
## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 0.1 | YYYY-MM-DD | 初始Spec框架 |
| 1.0 | YYYY-MM-DD | Spec评审通过，正式立项 |
