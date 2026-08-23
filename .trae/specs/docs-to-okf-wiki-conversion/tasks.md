# docs/ 全量转换为 OKF v0.2 Wiki 教程 - 实施计划

> **方法论链路**：R（事实采集）→ I（架构洞察）→ E（批量生成，分9批）→ V（独立验证）→ C（模式沉淀）
>
> **批次限制**：每批最多 7 个 Bundle（遵循 source-code-to-okf-wiki Skill 安全清单），每批完成后必须通过验证再推进下一批。

---

## [x] Task 1: R 阶段 — 全量事实采集与文件清单验证

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 遍历 `d:\AI\docs\` 全部子目录，提取每个 Markdown 文件的精确事实清单：
    - 文件相对路径、文件大小、行数
    - 是否已有 YAML frontmatter
    - 现有 frontmatter 字段列表（id/title/date/category/tags/source/maturity 等）
    - 文件中的内部链接数量和目标
    - 是否包含 Sphinx 特有语法（toctree/ref/note 等）
  - 所有事实编号 F-xxx，写入 `.trae/specs/docs-to-okf-wiki-conversion/supporting-analysis/facts.md`
  - G1 质量门：事实中不出现"用于"/"目的是"/"设计为"等推断词，纯客观描述
- **Acceptance Criteria Addressed**: AC-7（文件计数完整）
- **Test Requirements**:
  - `programmatic` TR-1.1：事实清单覆盖 docs/ 下全部 280 个 .md 文件，文件计数与 `Get-ChildItem -Recurse -Filter *.md` 结果一致
  - `programmatic` TR-1.2：每个文件的事实条目包含 path、has_frontmatter、frontmatter_fields、internal_links_count 四个字段
  - `programmatic` TR-1.3：事实清单中无推断性表述（Grep 检查"用于"、"目的是"、"设计为"等关键词出现在事实描述中为 0）
- **Notes**：此任务为后续所有转换提供事实基础，必须在 Task 2 之前完成

---

## [x] Task 2: I 阶段 — Bundle 映射与类型分配方案设计

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单，为每个文件确定：
    - 所属 Bundle（31 个 Bundle 之一）
    - OKF `type` 字段值（Tutorial/Concept/Reference/Pattern/Report/Example）
    - 在 Bundle 内的目标路径（concepts/、examples/、references/ 或根目录）
    - `description` 字段内容（30-80 字，从正文提取或生成）
  - 解决 spec.md 中的 Open Questions Q1-Q5，做出明确决策
  - 设计链接转换映射表：每个旧路径 → 新路径
  - 产出 `.trae/specs/docs-to-okf-wiki-conversion/supporting-analysis/bundle-mapping.md`
  - G2 质量门：每个映射条目含陈述（分配结果）、证据（文件内容特征）、反常识（注意事项）、行动（具体操作）
- **Acceptance Criteria Addressed**: AC-9（类型映射合理）
- **Test Requirements**:
  - `programmatic` TR-2.1：全部 280 个文件均有明确的 Bundle 归属和 type 分配，无遗漏
  - `programmatic` TR-2.2：31 个 Bundle 每个均有 index.md 和 log.md 的生成计划
  - `human-judgement` TR-2.3：type 分配经人工审查合理——教程章节为 Tutorial/Concept，复盘报告为 Report，模式为 Pattern，参考为 Reference
  - `programmatic` TR-2.4：链接转换映射表覆盖所有内部链接，无悬空映射
- **Notes**：此任务的输出是 E 阶段所有批次的操作蓝图

---

## [x] Task 3: E 阶段 — 试点批次（3 个 Wiki Bundle）

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 转换 3 个结构完整的 Wiki 作为试点，验证转换流程和模板：
    1. `python314-stdlib-wiki`（18 文件，有 frontmatter，结构标准）
    2. `deepseek-harness-wiki`（17 文件，有 source 字段，结构标准）
    3. `github-cli-wiki`（9 文件，有 RETROSPECTIVE.md，结构标准）
  - 每个 Bundle 执行以下操作：
    - 创建 `concepts/` 子目录
    - 将 `NN-topic.md` 文件移入 `concepts/`
    - 将 `00-overview.md` 内容转为根 `index.md`（添加 `okf_version: "0.2"` frontmatter）
    - 将 `seven-concepts-report.md`、`RETROSPECTIVE.md` 等非教程文件移入 `references/`
    - 为每个 Concept 文件补全 OKF frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）
    - 将现有 `source` 字段转为 OKF `sources` 格式
    - 修正内部链接为 Bundle 绝对路径（`/concepts/NN-topic.md`）
    - 创建 `concepts/index.md`（无 frontmatter）
    - 创建 `references/index.md`（无 frontmatter，如存在 references/）
    - 创建 `log.md`（含初始化条目）
  - G3 质量门：references/ 先于 concepts/ 生成，分批≤7，index 最后写
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-3.1：3 个 Bundle 目录结构合规（根 index.md 含 okf_version，concepts/ 存在且含 index.md）
  - `programmatic` TR-3.2：所有 Concept 文件 frontmatter 包含 type/title/description/generated/verified/status 字段
  - `programmatic` TR-3.3：所有内部链接以 `/` 开头且目标文件存在（无断链）
  - `programmatic` TR-3.4：concepts/index.md 和 references/index.md 无 frontmatter
  - `programmatic` TR-3.5：正文内容与原始文件一致（排除 frontmatter 和链接路径变更）
  - `human-judgement` TR-3.6：description 字段 30-80 字，准确反映文档内容
- **Notes**：试点批次完成后暂停，审查转换质量，确认模板无误后再推进后续批次

---

## [x] Task 4: E 阶段 — 批次 2（4 个 Wiki Bundle）

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 转换以下 4 个 Wiki Bundle：
    1. `agency-agents-wiki`（12 文件）
    2. `cordis-spatiotemporal-composability-wiki`（14 文件，含 seven-concepts-report.md）
    3. `okf-kit-wiki`（13 文件，含 seven-concepts-report.md）
    4. `open-code-review-wiki`（11 文件）
  - 转换操作同 Task 3 标准流程
  - 注意：cordis 和 okf-kit 的 seven-concepts-report.md 移入 references/
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-4.1：4 个 Bundle 结构合规，文件数与映射表一致
  - `programmatic` TR-4.2：所有 frontmatter 字段完整
  - `programmatic` TR-4.3：内部链接路径正确且无断链
  - `programmatic` TR-4.4：正文内容保真
- **Notes**：沿用 Task 3 验证通过的模板

---

## [x] Task 5: E 阶段 — 批次 3（4 个 Wiki Bundle）

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 转换以下 4 个 Wiki Bundle：
    1. `agent-runtime-protocol-wiki`（14 文件，含 HTML 交互文件保持原位）
    2. `ai-engineering-four-milestones-wiki`（8 文件）
    3. `baidu-unlimited-ocr-wiki`（9 文件）
    4. `book-to-skill-wiki`（10 文件）
  - 转换操作同 Task 3 标准流程
  - 注意：agent-runtime-protocol-wiki 中的 `interactive-selection-matrix.html` 保持原位不移动
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1：4 个 Bundle 结构合规
  - `programmatic` TR-5.2：HTML 文件保持原位未被移动
  - `programmatic` TR-5.3：所有 frontmatter 字段完整
  - `programmatic` TR-5.4：内部链接无断链
  - `programmatic` TR-5.5：正文内容保真

---

## [x] Task 6: E 阶段 — 批次 4（3 个 Wiki Bundle）

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 转换以下 3 个 Wiki Bundle：
    1. `headroom-context-compression-wiki`（11 文件）
    2. `minit2i-minimalist-t2i-wiki`（8 文件）
    3. `python314-cpython-wiki`（17 文件，含多个辅助文件：Python314-Learning-Path.md、learning-path.md、python314-cheatsheet.html、seven-concepts-report.md）
  - 转换操作同 Task 3 标准流程
  - 注意：python314-cpython-wiki 中的 HTML 文件保持原位；Python314-Learning-Path.md 和 learning-path.md 归入 concepts/；seven-concepts-report.md 归入 references/
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1：3 个 Bundle 结构合规
  - `programmatic` TR-6.2：HTML 文件保持原位
  - `programmatic` TR-6.3：所有 frontmatter 字段完整
  - `programmatic` TR-6.4：内部链接无断链
  - `programmatic` TR-6.5：正文内容保真

---

## [x] Task 7: E 阶段 — 批次 5（5 个微信文章分析 Bundle）

- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 转换以下 5 个分析报告 Bundle：
    1. `analyze-wechat-article-ai-switch-governance`（4 文件：analysis-report.md、article-content.md、insight-extraction-report.md、seven-concepts-report.md）
    2. `analyze-wechat-article-causal-ai`（3 文件：analysis-report.md、article-content.md、seven-concepts-report.md）
    3. `analyze-wechat-article-mainecoon`（11 文件，含多个分析草稿和 wiki 文件）
    4. `analyze-wechat-article-quantdinger`（3 文件：analysis-report.md、article-content.md、seven-concepts-report.md）
    5. `analyze-wechat-article-rqndd`（1 文件：analysis-report.md）
  - type 映射：article-content.md → Reference（原文信源），analysis-report.md → Report，insight-extraction-report.md → Report，seven-concepts-report.md → Reference（方法论记录），wiki 文件 → Tutorial
  - article-content.md 移入 references/ 作为信源登记
  - 创建 concepts/ 存放分析报告
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-7.1：5 个 Bundle 结构合规
  - `programmatic` TR-7.2：article-content.md 位于 references/ 且 type 为 Reference
  - `programmatic` TR-7.3：analysis-report.md 位于 concepts/ 且 type 为 Report
  - `programmatic` TR-7.4：frontmatter 完整、链接无断链、内容保真

---

## [x] Task 8: E 阶段 — 批次 6（5 个其他知识主题 Bundle）

- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 转换以下 5 个知识主题 Bundle：
    1. `codewhale`（9 文件，含嵌套结构 general/domain/、tech/、topics/，需在 concepts/ 下保留子目录结构）
    2. `three-ai-tools-learning-wiki`（2 文件：article-content.md、seven-concepts-report.md）
    3. `ai-engineering`（3 文件：README.md、karpathy-llm-wiki-analysis-20260707.md、loop-engineering-knowledge-base.md）
    4. `atomic-emergence`（1 md 文件 + 1 html，html 保持原位）
    5. `deep-learning-atomic-design`（3 文件）
  - codewhale 的嵌套目录结构在 concepts/ 下保留（concepts/general/domain/、concepts/tech/、concepts/topics/）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-8.1：5 个 Bundle 结构合规
  - `programmatic` TR-8.2：codewhale 的 concepts/ 下保留 general/domain、tech、topics 子目录
  - `programmatic` TR-8.3：HTML 文件保持原位
  - `programmatic` TR-8.4：frontmatter 完整、链接无断链、内容保真

---

## [x] Task 9: E 阶段 — 批次 7（4 个项目文档 Bundle）

- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 转换以下 4 个项目文档 Bundle：
    1. `specweave-tech-docs`（源：`tech/`，10 文件：intro.md、quickstart.md、features.md、contributing.md、changelog.md、four-layer-logging-pattern.md、release-onnx-*.md 等）
    2. `general-knowledge`（源：`general/`，2 文件：README.md、index.md）
    3. `design-topics`（源：`topics/`，2 文件：README.md、index.md）
    4. `refactor-notes`（源：`refactor/`，1 文件：refactor-concurrent-safety-checker-20260812.md）
  - tech/ 中的文件大部分无 frontmatter，需从头补全
  - 注意：tech/ 下的 README.md 和 index.md 处理为 Bundle 根 index.md
  - four-layer-logging-pattern.md 的 type 为 Pattern
  - release-onnx-*.md 的 type 为 Reference
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-9.1：4 个 Bundle 结构合规
  - `programmatic` TR-9.2：tech/ 下原来无 frontmatter 的文件均已补全
  - `programmatic` TR-9.3：four-layer-logging-pattern.md 的 type 为 Pattern
  - `programmatic` TR-9.4：frontmatter 完整、链接无断链、内容保真

---

## [x] Task 10: E 阶段 — 批次 8（3 个复盘内容 Bundle）

- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 转换以下 3 个复盘内容 Bundle：
    1. `methodology-patterns`（源：`retrospective/patterns/methodology-patterns/`，16 个模式文件 + README.md，所有文件 type 为 Pattern）
    2. `retrospective-reports`（源：`retrospective/reports/`，递归包含 adversarial-review/、competitive-analysis/、knowledge/、milestone/ 共约 28 文件，type 为 Report，在 concepts/ 下保留子目录结构）
    3. `retrospective-root`（源：`retrospective/index.md`，1 文件，作为 Bundle 根索引）
  - 模式文件需检查是否已有 TOML frontmatter（项目规范中 Pattern 文件使用 TOML frontmatter），如有则在 TOML 后追加 YAML frontmatter 或转换为 YAML（保留 TOML 中的字段作为扩展字段）
  - 复盘报告子目录结构在 concepts/ 下保留
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-10.1：3 个 Bundle 结构合规
  - `programmatic` TR-10.2：methodology-patterns 中所有文件 type 为 Pattern
  - `programmatic` TR-10.3：retrospective-reports 的 concepts/ 下保留 adversarial-review、competitive-analysis、knowledge、milestone 子目录
  - `programmatic` TR-10.4：TOML frontmatter 中的字段被保留（作为 YAML 扩展字段或双 frontmatter）
  - `programmatic` TR-10.5：frontmatter 完整、链接无断链、内容保真
- **Notes**：Pattern 文件可能使用 TOML frontmatter（`+++` 包裹），需特殊处理——OKF 规范要求 YAML frontmatter（`---` 包裹），转换时需将 TOML 字段映射为 YAML 格式

---

## [x] Task 11: E 阶段 — 批次 9（根级导航与散文件处理）

- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 处理根级导航文件和散文件：
    1. 更新 `docs/index.md`：添加 `okf_version: "0.2"` frontmatter，更新链接路径指向各 Bundle
    2. 更新 `docs/knowledge/index.md`：更新链接路径
    3. 更新 `docs/knowledge/learning/03-agent-platforms-tools/README.md`：更新为该组 Wiki Bundle 的导航索引
    4. 处理 `knowledge/learning/` 下的散文件：
       - `okf-topic-index.md`：保留为知识库级索引（type: Reference）
       - `ai-engineering-four-milestones-wiki.md`：检查是否与 `ai-engineering-four-milestones-wiki/` Bundle 重复，如重复则归入该 Bundle 的 references/
       - `anthropic-financial-services-wiki.md`：创建独立小 Bundle 或归入最近的相关 Bundle
       - `octo-platform-wiki.md`：同上
       - `three-ai-tools-wiki.md`：检查是否与 `three-ai-tools-learning-wiki/` Bundle 重复
  - 更新 docs/README.md 与 index.md 保持同步
  - 注意：根级 index.md 是整个文档站的入口，也是最大范围的 OKF Bundle 根索引
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-11.1：docs/index.md 包含 okf_version: "0.2" frontmatter
  - `programmatic` TR-11.2：所有根级导航文件中的内部链接指向正确的新路径
  - `programmatic` TR-11.3：5 个散文件均有明确归属，无悬空文件
  - `human-judgement` TR-11.4：根级 index.md 的导航结构清晰，覆盖所有 Bundle 入口

---

## [x] Task 12: V 阶段 — 全量结构与 Frontmatter 验证

- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 独立验证（不参与转换的子代理执行）：
    - 遍历 docs/ 下全部 .md 文件，验证：
      - 每个非 index.md/log.md 文件有 YAML frontmatter
      - 每个 frontmatter 包含非空 type 字段
      - type 值属于允许集合（Tutorial/Concept/Reference/Pattern/Report/Example）
      - 每个 frontmatter 包含 title/description/tags/generated/verified/status
      - generated.at 和 verified.at 为合法 ISO 8601 格式
      - 子目录 index.md 无 frontmatter
      - Bundle 根 index.md 含 okf_version: "0.2"
      - log.md 使用 ISO 8601 日期标题
    - 输出验证报告到 `.trae/specs/docs-to-okf-wiki-conversion/supporting-analysis/verification-report.md`
    - 发现的问题逐一修复
  - G4 质量门：无虚构内容（本次为文档转换，不涉及 API 虚构，但需检查 description 是否与正文一致）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-8
- **Test Requirements**:
  - `programmatic` TR-12.1：280+ 个文件全部通过 frontmatter 验证，0 个缺失 type
  - `programmatic` TR-12.2：所有子目录 index.md 无 frontmatter
  - `programmatic` TR-12.3：所有 Bundle 根 index.md 含 okf_version
  - `programmatic` TR-12.4：所有 log.md 日期格式合规
  - `programmatic` TR-12.5：验证报告中记录的问题全部修复

---

## [x] Task 13: V 阶段 — 全量链接验证

- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 遍历 docs/ 下全部 .md 文件中的 Markdown 链接：
    - Bundle 内部链接（`/` 开头）：验证目标文件存在
    - 相对路径链接（非 `http`、非 `/` 开头）：检查是否需要转换为 Bundle 绝对路径
    - 外部 URL（`http://`、`https://`）：记录但不验证可达性
    - 图片链接：验证目标文件存在
    - Sphinx `{ref}` 指令：记录为已知不转换项
  - 使用 link-check Skill 或自定义脚本执行
  - 输出断链报告并修复
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-13.1：Bundle 内部链接（`/` 开头）100% 指向存在的文件，断链数为 0
  - `programmatic` TR-13.2：无遗漏的相对路径内部链接（所有同 Bundle 内文件间链接已转为 `/` 开头）
  - `programmatic` TR-13.3：图片链接目标文件存在
  - `programmatic` TR-13.4：断链报告中记录的问题全部修复或标注为已知容忍项

---

## [x] Task 14: V 阶段 — 内容保真验证

- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 对每个转换后的文件，通过 Git diff 验证：
    - 正文部分（frontmatter 之后的内容）除链接路径变更外，无文字增删改
    - frontmatter 中的原有字段（id、date、category、tags、source、maturity 等）均被保留
    - 代码块内容完全一致
    - 表格内容完全一致
  - 使用 Git 的暂存区差异或提交前 diff 进行验证
  - 对发现的内容差异逐一核查并修复
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-14.1：正文 diff 中仅允许出现链接路径变更（`XX.md` → `/concepts/XX.md`），无其他文字变更
  - `programmatic` TR-14.2：原有 frontmatter 字段 100% 保留（可能有格式变化但字段值不变）
  - `programmatic` TR-14.3：代码块和表格内容字节级一致
  - `human-judgement` TR-14.4：抽样 10% 文件人工复核正文内容完整性

---

## [x] Task 15: C 阶段 — 模式萃取与经验沉淀

- **Priority**: medium
- **Depends On**: Task 14
- **Description**:
  - 回顾整个转换流程：
    - 记录顺利点和问题点
    - 萃取"批量文档→OKF Bundle 转换"可复用模式
    - 更新 source-code-to-okf-wiki Skill 的 L2 模式文档，补充"非源码文档转换"场景
    - 沉淀反模式（如 TOML frontmatter 处理、散文件归属决策、Sphinx 语法兼容等）
  - G5 质量门：模式含触发场景、核心步骤、反模式≥5、迁移验证
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-15.1：模式文档包含触发条件、核心步骤、反模式（≥5个）
  - `programmatic` TR-15.2：模式文档入库到 `docs/retrospective/patterns/` 正确目录
  - `human-judgement` TR-15.3：模式可迁移——另一个人按模式文档可独立完成类似转换
