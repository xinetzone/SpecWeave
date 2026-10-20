# 「教与学」全面调研 → OKF Wiki 教程 Implementation Plan

> 目标 bundle：`projects/awesome-okf-xs/doc/bundles/zhexue/methodology/teaching-and-learning/`
> 依赖关系：Task 1 先行，内容文档（2-6）可部分并行，Task 7 依赖全部内容文档，Task 8 依赖 7，Task 9-10 依赖 8。

## Task 1: 创建 bundle 目录结构与子目录索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `zhexue/methodology/teaching-and-learning/` 目录树：`concepts/`、`examples/`、`references/`
  - 创建 `concepts/index.md`、`examples/index.md`、`references/index.md`（各含 `type: concepts-index` / `examples-index` / `references-index` frontmatter 与 `{toctree}` 占位，内容文档落盘后同步填充条目）
- **Acceptance Criteria Addressed**: AC-1, AC-9
- **Test Requirements**:
  - `rule` TR-1.1: 目录树创建后 `Test-Path` 三个子目录与三个子索引全部为 True
  - `rule` TR-1.2: 每个子索引 frontmatter 含非空 `type` 字段

## Task 2: 概念文档 00-02（教、学、学习理论谱系）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `00-what-is-teaching.md`：教的定义谱系（共同活动论/教学即教学生学/学重于教）+ 教的第一性命题
  - `01-what-is-learning.md`：学的定义谱系（经典三要素定义/建构主义/关系中的自我改变）
  - `02-learning-theory-spectrum.md`：行为主义→认知主义→建构主义→社会文化理论→深度学习的谱系表与演变逻辑
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-2.1: 三篇均含 OKF v0.2 frontmatter（`type: concept` 及 title/name/sources）
  - `rule` TR-2.2: 每篇至少 2 个 sources 条目或脚注指向 references/ 信源
  - `rubric` TR-2.3: 定义谱系完整性；scale 1-5；1=单一定义，3=两谱系并置，5=中西/古今定义谱系并置且有演变脉络；threshold >= 4

## Task 3: 概念文档 03-05（教学法、循证学习策略、教与学关系）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `03-teaching-methods.md`：教学法流派（讲授/苏格拉底/建构主义三法/项目式/探究式/翻转课堂）对照表与适用边界
  - `04-evidence-based-learning.md`：学习科学循证策略（检索练习/间隔/交错/样例/主动学习/认知负荷）
  - `05-teaching-learning-relationship.md`：区别（无教可学/有教未必学）→ 联系（教以学为归宿/学以教为加速器）→ 教学相长（《学记》原文+费曼机制）
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 三篇均含 frontmatter 且《学记》引文标注篇目出处
  - `rule` TR-3.2: 05 篇含"教学相长非自动发生"的反例/边界论述（对抗审查要求）
  - `rubric` TR-3.3: 教学法对照清晰度；scale 1-5；1=罗列名称，3=有对照维度，5=有对照表且每法标注适用边界与失效条件；threshold >= 4

## Task 4: 概念文档 06-08（本质、真需求、AI 时代）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `06-first-principles-essence.md`：第一性原理三重命题（学的不可代理性、教的条件创设性、输出驱动输入的合流）及其互相咬合
  - `07-real-needs-and-goals.md`：学习者真需求（SDT 自主/胜任/归属）、教与学脱节与评估错位、真目标（教是为了不教/学会学习）
  - `08-ai-era-transformation.md`：知识通胀/认知外包/流畅陷阱、能力转向（提问/反思/价值判断）、AI 作为"学生"与"脚手架"
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 三篇均含 frontmatter；AI 时代"观点类"内容标注"观点/一方称"属性
  - `rule` TR-4.2: 06 篇含三重命题且相互引用关系明确（不可代理→条件创设→输出合流）
  - `rubric` TR-4.3: 本质洞察深度；scale 1-5；1=仅罗列定义，3=单一命题，5=三重命题咬合且含对抗审查边界；threshold >= 4

## Task 5: 实操层 examples/（3 篇）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - `01-teaching-method-selection.md`：教学法选型对照表（目标×学习者×场景→方法+失效条件）
  - `02-learning-strategy-playbook.md`：学习策略实操手册（检索练习/间隔重复/费曼讲解执行步骤）
  - `03-teaching-and-learning-self-check.md`：教者/学者双向自查清单
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-5.1: 三篇均含可执行步骤或清单结构（非纯论述）
  - `rule` TR-5.2: 每篇含"何时用/何时不用"边界说明

## Task 6: 信源层 references/（4 篇）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - `01-chinese-pedagogy-sources.md`：中国教学论信源（《学记》原文/教育部引例/孔子/叶圣陶/谢维和）
  - `02-western-philosophy-sources.md`：杜威/卢梭/教育本质论信源
  - `03-learning-science-sources.md`：NTU/Manchester/北师大/浙大等学习科学信源
  - `04-ai-era-sources.md`：郭毅可/张雨东/中国教科院/教育部行动计划（标注观点属性）
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-6.1: 四篇均含 sources 条目（resource URL + title + 性质标注）
  - `rule` TR-6.2: 04 篇每条观点标注"观点/一方称"或"官方文件"属性

## Task 7: bundle 根 index.md 与 log.md
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, 3, 4, 5, 6
- **Description**:
  - `index.md`：frontmatter（`okf_version: "0.2"` + `type: bundle-index` + bundle_path/bundle_name/created_at/total_concepts/total_references），toctree 覆盖全部内容文档，含核心概念表与关键洞察
  - `log.md`：更新历史（YYYY-MM-DD 倒序）
- **Acceptance Criteria Addressed**: AC-1, AC-9
- **Test Requirements**:
  - `rule` TR-7.1: index.md toctree 列出 concepts/、examples/、references/ 全部 .md（含子索引）
  - `rule` TR-7.2: index.md frontmatter 含 `okf_version: "0.2"` 与 `type: bundle-index`

## Task 8: 更新三级索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - `zhexue/methodology/index.md`：total_bundles 3→4、toctree 追加 `teaching-and-learning/index`、知识包列表表加行
  - `zhexue/index.md`：methodology 行束数与域说明同步
  - `bundles/index.md`：total_bundles 650→651、mermaid zhexue 7→8、哲学域节 7→8、methodology 行束数 3→4
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-8.1: 三处文件计数分别变为 4 / 8（zhexue 域）/ 651，与目录树实际一致
  - `rule` TR-8.2: 三处导航表均含 teaching-and-learning 新束条目

## Task 9: 运行质量门验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 在 awesome-okf-xs 运行 `invoke gates.toctrees` 与 `invoke gates.bundles`
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-9.1: gates.toctrees 退出码 0 且无本束断链告警
  - `rule` TR-9.2: gates.bundles 退出码 0（总计数五面对账一致）

## Task 10: Sphinx 构建验证
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 运行 `invoke build`（或 `sphinx-build -b dummy -E doc _build/dummy`）验证构建通过且无本束引入的 ERROR
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-10.1: 构建退出码 0，日志无本束文件相关 ERROR
