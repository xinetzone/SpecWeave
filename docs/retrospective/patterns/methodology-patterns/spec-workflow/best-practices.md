---
id: "best-practices"
title: "Spec编写最佳实践与避坑指南"
source: "retrospective-analysis"
created_at: "2026-07-09"
status: "completed"
theme: "methodology-patterns"
version: "1.0"
archive_location: "docs/retrospective/patterns/methodology-patterns/spec-workflow/"
parent_spec: "universal-prd-template-extraction"
reference_spec: "prd-structure-guide,format-selection-guide"
---

# Spec编写最佳实践与避坑指南

## 概述

本指南汇总Spec编写过程中的常见陷阱（附正反示例）、质量自检清单，并整合已验证的方法论模式，帮助写出高质量、可执行、可验证的规格文档。

**关联模式引用**：
- [spec-nine-section-narrative](../product-growth/spec-nine-section-narrative.md)：九节叙事弧，产品定义完整性
- [spec-reference-validation](./spec-reference-validation-pattern.md)：引用验证模式，避免无效引用
- [spec-triple-sync](../governance-strategy/spec-triple-sync.md)：规范三同步，确保规范落地
- [bidirectional-navigation-links](../document-architecture/bidirectional-navigation-links.md)：双向导航，原子文档可读性
- [prd-structure-guide.md](./prd-structure-guide.md)：PRD十节结构规范
- [format-selection-guide.md](./format-selection-guide.md)：PRD/Change格式选择

---

## 常见陷阱与正反示例（8个核心+4个补充）

### 陷阱1：Goals用模糊词汇，不可衡量

**反例**：
```markdown
## Goals
- 优化用户体验
- 提升系统性能
- 做好引用管理
```

**问题**："优化"、"提升"、"做好"都是主观感受，无法判断是否完成。

**正例**：
```markdown
## Goals
- G1: 建立100%外部引用自动验证机制，死链检测率100%
- G2: 单文件(<1000行)链接检查<5秒，全量100文件<30秒
- G3: 引用格式统一支持3种风格，转换准确率100%
```

**修正原则**：每个Goal必须包含"动词+宾语+可量化指标"，问自己："怎么算做完了？"

---

### 陷阱2：FR描述"怎么做"而非"做什么"

**反例**：
```markdown
## Functional Requirements
- FR-1: 用Python写爬虫，使用requests库，数据存SQLite
- FR-2: 前端用React+Ant Design，表格展示结果
```

**问题**：过早绑定技术实现，限制了实现方案的选择空间，且不是需求而是设计。

**正例**：
```markdown
## Functional Requirements
- FR-1 [→G1]: 系统应该能够自动检测Markdown文件中所有外部链接
- FR-2 [→G1]: 系统应该能够验证链接可访问性，区分死链/活链/重定向
- FR-3 [→G3]: 系统应该能够统一格式化引用为指定风格
```

**修正原则**：使用"系统应该能够..."句式，只描述外部可观察的行为，不涉及内部实现。

---

### 陷阱3：Non-Goals缺失或模糊

**反例**：
```markdown
## Non-Goals
- 不做没用的功能
- 暂时不考虑其他需求
- 以后再说
```

**问题**：没有明确边界，范围必然蔓延，"不做什么"比"做什么"更重要。

**正例**：
```markdown
## Non-Goals
- NG1: 不实现自动事实核查（仅验证来源存在性）——需领域知识，v2.0独立评估
- NG2: 不支持书籍/视频等非网页引用——v1.0聚焦网页/论文，待非网页引用>20%时纳入
- NG3: 不做IDE实时检查插件——v1.0先做CLI，收集1个月数据再决策
```

**修正原则**：每个Non-Goal必须说明"不做什么"+"为什么不做"+"未来什么条件下可以考虑做"。

---

### 陷阱4：AC写"用户满意/没有Bug"，不可证伪

**反例**：
```markdown
## Acceptance Criteria
- AC-1: 功能正常
- AC-2: 用户满意
- AC-3: 没有bug
```

**问题**：这些是美好愿望，不是验收标准。开发说"我觉得功能正常"，测试说"我觉得有bug"，永远吵不清。

**正例**：
```markdown
## Acceptance Criteria
- AC-1 [→FR-1→G1] [Programmatic]:
  Given: 含10个链接的测试文件；When: 运行检测脚本；Then: 10个链接全识别无遗漏
  Verification: `python scripts/check-links.py --test` 通过率100%
- AC-3 [→FR-3→G2] [Human-Judgment]:
  Given: 10个不同域名来源；When: 运行自动评级；Then: 与专家判断一致性≥90%
  Verification: 2名维护者独立审核记录准确率
```

**修正原则**：Given（前置条件）→ When（操作）→ Then（可观察结果），必须能明确回答"过还是不过"。

---

### 陷阱5：Assumptions写美好愿望，不是可验证命题

**反例**：
```markdown
## Assumptions
- 用户会喜欢这个功能
- 一切都会顺利
- 网络应该没问题
```

**问题**：这些是期待，不是假设。假设是"我们认为X是真的，如果不对会有Y影响"。

**正例**：
```markdown
## Assumptions
- A1: 公开网络可获取足够高质量资料——若不成立，调整评级标准或申请数据库权限
- A2: 大多数网站支持HEAD/正常响应GET——若不成立，为特定站实现自定义检查
- A3: 执行环境有稳定网络——若离线，提供缓存/离线模式
```

**修正原则**：每个假设必须是可证伪的命题，并且必须写清楚"如果不成立怎么办"。

---

### 陷阱6：Constraints写"无"，不承认现实边界

**反例**：
```markdown
## Constraints
- 无
- 没有什么限制，我们什么都能做
```

**问题**：所有项目都有约束（时间、预算、技术栈、依赖、合规...），不写不等于不存在，只是把风险藏起来。

**正例**：
```markdown
## Constraints
### Technical
- TC1: 不能访问付费学术数据库——无机构订阅，零预算
- TC2: 仅支持Python 3.10+——利用类型注解新特性
### Business
- BC1: 不存储受版权保护全文——仅存元数据和链接，规避法律风险
### Dependencies
- D1 [已就绪]: first-principles项目提供对抗性审查经验
- D3 [待完成]: 可信度评级域名名单需人工整理初始版本
```

**修正原则**：诚实面对现实约束，区分硬约束/软约束，标注依赖的就绪状态，不遗漏合规/预算限制。

---

### 陷阱7：Spec中引用文件但不验证存在性

**反例**：
```markdown
## Impact
- 关联模块：self-cognition.md, validation-utils.py
- 参考文档：some-other-spec.md
```

**问题**：写完Spec就以为这些文件存在，到实施时才发现`self-cognition.md`实际叫`self-insight.md`，返工。

**正例**：
```markdown
## Impact
- 关联模块：self-insight.md（✅已验证存在）, validation-utils.py（需新建）
- 参考文档：first-principles-comprehensive-research（✅已验证存在）
```

**修正原则**：遵循[spec-reference-validation](./spec-reference-validation-pattern.md)模式，写完Spec后用Glob验证所有引用路径的存在性。

---

### 陷阱8：Open Questions只列问题，不记录决策过程

**反例**：
```markdown
## Open Questions
- 还有些问题没想清楚
- 以后再说
- IDE插件做不做？
```

**问题**：过一周连自己都忘了当时怎么想的、为什么这么决策，spec变成静态合同而非活的决策日志。

**正例**：
```markdown
## Open Questions
- [x] Q1: 是否支持书籍/视频等非网页引用？
  分析: 验证机制不同复杂度高；决策: v1.0仅支持网页/论文；
  理由: 当前90%引用是此类，先解决主要问题；重评估: 非网页引用>20%时
- [ ] Q3: 是否提供IDE插件实时检查？
  阻塞点: 需调研使用场景——CI检查还是编写时检查？
  计划: v1.0先做CLI，收集1个月数据再决策
```

**修正原则**：每个问题必须记录：问题→分析→决策→理由，已解决[x]，未解决[ ]说明阻塞点和计划。

---

### 陷阱9（补充）：Background一句话，没有历史脉络

**反例**：`因为领导要求所以做。`

**正例**：
```markdown
## Background
- 2026-Q2: vibe-coding-prompts发现30%外链1个月后失效
- 2026-07-02: first-principles项目验证了对抗性审查价值
- 2026-07-08: 复盘发现跨项目引用规范不统一
```

---

### 陷阱10（补充）：NFR没有量化指标

**反例**：`- 系统要快 - 代码要好 - 要稳定`

**正例**：
```markdown
### 性能
- NFR-1: 单文件(<1000行)检查<5秒
- NFR-2: 网络错误重试3次不崩溃
### 可维护性
- NFR-7: pep8规范，类型注解100%
- NFR-9: kebab-case命名，单文件<500行
```

---

### 陷阱11（补充）：FR/AC没有追溯标记，形成孤岛

**反例**：FR和AC独立编号，看不出哪个AC对应哪个FR，哪个FR支撑哪个Goal。

**正例**：
- FR: `FR-1 [→G1]: 系统应该能够自动检测链接`
- AC: `AC-1 [→FR-1→G1] [Programmatic]: Given...When...Then...`

---

### 陷阱12（补充）：写完新规范不做三同步，成为死文档

**反例**：创建了新规范文档，但不在任何入口链接，不迁移存量文件，几个月后没人记得有这个规范。

**正例**：遵循[spec-triple-sync](../governance-strategy/spec-triple-sync.md)：
1. 总览规范中添加引用
2. 导航/规则目录添加入口
3. 迁移至少1批存量文件作为示范

---

## 质量自检清单（15项）

写完Spec后，对照以下清单逐一检查：

### 完整性检查（5项）

- [ ] **检查1**：PRD十节/Change六节核心章节齐全，无缺失
- [ ] **检查2**：YAML frontmatter必填字段（id/title/source/created_at/status/theme/version）已填写
- [ ] **检查3**：每个Goal至少对应一个FR，每个FR至少对应一个AC
- [ ] **检查4**：Constraints和Assumptions章节不是空的，也不是写"无"
- [ ] **检查5**：Non-Goals至少列出3条明确不做的事项

### 可验证性检查（4项）

- [ ] **检查6**：所有Goals都包含可量化指标，没有"优化/提升/做好"等模糊词
- [ ] **检查7**：所有NFR都有量化标准（时间/准确率/覆盖率等）
- [ ] **检查8**：所有AC都采用Given/When/Then格式，可明确判断通过/不通过
- [ ] **检查9**：Programmatic类型的AC指明了验证脚本或命令

### 边界清晰度检查（3项）

- [ ] **检查10**：每个Non-Goal都说明"不做什么"+"为什么"+"未来条件"
- [ ] **检查11**：FR只描述"做什么"（系统应该能够...），不描述"怎么做"（技术实现）
- [ ] **检查12**：推迟的功能明确说明重评估条件，没有"以后再说"

### 追溯与引用检查（3项）

- [ ] **检查13**：FR标记`[→Gx]`追溯到Goal，AC标记`[→FR-x→Gx]`完整追溯链
- [ ] **检查14**：所有引用的文件/文档路径都经过存在性验证（遵循spec-reference-validation）
- [ ] **检查15**：Open Questions记录了分析/决策/理由，不只是问题列表

---

## Spec写作流程最佳实践

### 写作顺序建议

不要从第一节开始顺序写，推荐顺序：

1. **先填YAML Frontmatter**：确定id/title/status，明确这是什么
2. **写Goals + Non-Goals**：这是最关键的章节，定义了成功和边界
3. **写Overview**：最后写Overview，因为你已经知道全貌了，才能3秒说清
4. **写Background**：补充历史脉络和问题现状
5. **分解FR + NFR**：从Goals分解出功能和质量要求
6. **写Constraints + Assumptions**：承认现实边界，把隐含假设显式化
7. **写AC**：最花时间但最有价值，把每个FR变成可证伪的验收条件
8. **写Open Questions**：记录决策过程，包括被否决的选项
9. **追溯标记检查**：补全所有`[→Gx]`标记，检查没有孤岛
10. **引用验证**：用Glob检查所有引用路径存在（spec-reference-validation）
11. **质量自检**：对照15项清单逐一检查

---

### 格式选择建议

开始写作前，先用[format-selection-guide.md](./format-selection-guide.md)的决策树判断用PRD Spec还是Change Spec：

- 全新项目/大重构（>70%变更）→ PRD Spec（十节）
- 小迭代/增量变更（<30%）→ Change Spec（六节）
- 不确定时看：基线存在吗？读者需要完整上下文吗？

---

### 产品思考完整性建议

对于产品类Spec，参考[spec-nine-section-narrative](../product-growth/spec-nine-section-narrative.md)的九节叙事弧，问自己九个问题：

1. **产品定位**：为什么存在？解决谁的什么问题？
2. **核心功能**：做什么？不做什么？
3. **交互设计**：用户怎么用？核心流程是什么？
4. **内容体系**：用什么支撑？数据从哪来？
5. **用户留存**：用户为什么回来？
6. **合规边界**：什么不能做？法律/伦理风险？
7. **商业模式**：如何生存？成本/收益？
8. **技术架构**：如何实现？关键技术选型？
9. **社会价值**：为什么值得做？意义是什么？

不需要每节都写很长，但九个问题都要想过。纯内部工具可简化6/7，但1/2不可跳过。

---

### 文档架构建议

当Spec原子化为多个文件时，遵循[bidirectional-navigation-links](../document-architecture/bidirectional-navigation-links.md)：

- 每个章节文件末尾放置三链路导航：⬅️上一章 | 📑返回目录 | ➡️下一章
- "返回目录"是强制必需的，防止读者迷路
- 首章不写上一章，末章不写下一章
- 导航统一放在文件末尾，不要放在开头

---

### 规范落地建议

当你创建新的Spec规范/模板/模式时，遵循[spec-triple-sync](../governance-strategy/spec-triple-sync.md)：

1. **同步1**：在顶层开发规范总览中添加引用，说明适用场景
2. **同步2**：在规则/导航目录中添加入口，提供场景化导航
3. **同步3**：迁移至少1批存量文件作为示范，证明规范可执行

三个同步缺一不可，否则规范就是死文档。

---

## 颗粒度建议

| Spec类型 | 推荐篇幅 | FR数量 | 典型工作量 |
|----------|----------|--------|-----------|
| 小修复/小优化 | 50-100行 | 1-3个 | 0.5-1天 |
| 单一功能 | 100-200行 | 3-8个 | 1-3天 |
| 完整功能模块 | 200-400行 | 8-15个 | 3-10天 |
| 新项目/大版本 | 400-500行 | 15-30个 | 2-4周 |

**超过500行**：考虑拆分，可能你把多个项目塞到一个Spec里了。

**少于50行**：考虑是不是不需要写Spec，直接改就行（但要确认没有影响其他模块）。

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0 | 2026-07-09 | 初始版本，包含12个常见陷阱、15项自检清单、6个模式引用 |
