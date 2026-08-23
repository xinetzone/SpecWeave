# docs/ 到 .agents/docs/knowledge/ OKF Wiki 教程迁移 - 实施计划

## 任务分组策略

按内容类型和依赖关系分为 6 个批次：
- **批次 A**：独立完整 Wiki（高优先级，无依赖）
- **批次 B**：需要合并/扩展的 Wiki（依赖批次 A 验证格式标准）
- **批次 C**：微信文章分析系列（可并行）
- **批次 D**：非 Wiki 知识文件（ai-engineering、engineering、algorithmic-art）
- **批次 E**：复盘报告与模式文件（目标目录不同）
- **批次 F**：索引更新与收尾验证

---

## [x] Task 1: 迁移 agency-agents-wiki ✅ 2026-08-22

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将 `docs/knowledge/learning/03-agent-platforms-tools/agency-agents-wiki/` 全部 12 个文件迁移至 `.agents/docs/knowledge/learning/03-agent-platforms-tools/agency-agents-wiki/`
  - 标准化 frontmatter 为原子化 Wiki 4 字段格式
  - 创建配套 TOML 元数据文件
  - 生成 README.md 索引
  - 修复内部章节链接路径
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: 目标目录存在全部 12 个 .md 文件
  - `programmatic` TR-1.2: 每个文件 frontmatter 恰好包含 id/title/source/x-toml-ref
  - `programmatic` TR-1.3: check-links.py 对该目录零断链
  - `programmatic` TR-1.4: check-filename-convention.py 全部通过
  - `programmatic` TR-1.5: 每个 x-toml-ref 指向的 TOML 文件存在
- **Notes**: 首个迁移任务，建立格式标准模板供后续 Wiki 参考

## [x] Task 2: 迁移 cordis-spatiotemporal-composability-wiki ✅ 2026-08-22

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/` 全部 14 个文件迁移至 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/cordis-wiki/`
  - 标准化 frontmatter、创建 TOML、生成 README、修复链接
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 目标目录存在全部 14 个 .md 文件
  - `programmatic` TR-2.2: frontmatter 格式合规
  - `programmatic` TR-2.3: check-links.py 零断链
  - `programmatic` TR-2.4: TOML 文件全部存在

## [x] Task 3: 迁移 deepseek-harness-wiki ✅ 2026-08-22

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/03-agent-platforms-tools/deepseek-harness-wiki/` 全部 17 个文件迁移至 `.agents/docs/knowledge/learning/07-vendor-product-learning/deepseek/deepseek-harness-wiki/`
  - 标准化 frontmatter、创建 TOML、生成 README、修复链接
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1: 目标目录存在全部 17 个 .md 文件
  - `programmatic` TR-3.2: frontmatter 格式合规
  - `programmatic` TR-3.3: check-links.py 零断链
  - `programmatic` TR-3.4: TOML 文件全部存在

## [x] Task 4: 迁移 okf-kit-wiki ✅ 2026-08-22

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/` 全部 12 个文件迁移至 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/okf-kit-wiki/`
  - 标准化 frontmatter、创建 TOML、生成 README、修复链接
  - 注意与已有 okf-wiki 目录的交叉引用
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 目标目录存在全部 12 个 .md 文件
  - `programmatic` TR-4.2: frontmatter 格式合规
  - `programmatic` TR-4.3: check-links.py 零断链（含跨 wiki 链接）
  - `programmatic` TR-4.4: TOML 文件全部存在

## [/] Task 5: 迁移 baidu-unlimited-ocr-wiki

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/baidu-unlimited-ocr-wiki/` 全部 9 个文件迁移至 `.agents/docs/knowledge/learning/07-vendor-product-learning/baidu/baidu-ocr-wiki/`
  - 仅 6 个文件需迁移（00-overview、01-core-architecture、03-quick-start 已存在同名文件，需对比确认是否为同一内容）
  - 标准化格式
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 缺失文件已补充
  - `programmatic` TR-5.2: frontmatter 格式合规
  - `programmatic` TR-5.3: check-links.py 零断链

## [/] Task 6: 迁移 book-to-skill-wiki

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/book-to-skill-wiki/` 全部 10 个文件迁移至 `.agents/docs/knowledge/learning/02-agent-engineering-methodology/02-prompt-coding/book-to-skill-wiki/`
  - 8 个文件需迁移（00-overview、01-core-architecture 已存在同名文件）
  - 标准化格式
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 缺失文件已补充
  - `programmatic` TR-6.2: frontmatter 格式合规
  - `programmatic` TR-6.3: check-links.py 零断链

## [/] Task 7: 迁移 github-cli-wiki

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/github-cli-wiki/` 全部 9 个文件迁移至 `.agents/docs/knowledge/learning/08-systems-infrastructure/github-cli-wiki/`
  - 7 个文件需迁移（00-overview、01-installation 已存在同名文件）
  - RETROSPECTIVE.md 归入复盘目录或作为 wiki 附录
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 目标目录存在全部文件
  - `programmatic` TR-7.2: frontmatter 格式合规
  - `programmatic` TR-7.3: check-links.py 零断链

## [x] Task 8: 迁移 minit2i-minimalist-t2i-wiki ✅ 2026-08-22

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/minit2i-minimalist-t2i-wiki/` 全部 8 个文件迁移至 `.agents/docs/knowledge/learning/05-ai-multimodal-content/minit2i-wiki/`
  - 6 个文件需迁移（00-overview、01-design-philosophy 已存在同名文件）
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 目标目录存在全部文件
  - `programmatic` TR-8.2: frontmatter 格式合规

## [x] Task 9: 迁移 python314-cpython-wiki ✅ 2026-08-22

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/python314-cpython-wiki/` 全部 17 个 md + 1 个 html 迁移至 `.agents/docs/knowledge/learning/10-foundational-knowledge/python314-cpython-wiki/`
  - 14 个文件需迁移（00-overview、11-faq-troubleshooting 已存在同名文件）
  - python314-cheatsheet.html 作为附属资源保留
  - Python314-Learning-Path.md 和 learning-path.md 内容可能重复，需对比合并
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-9.1: 目标目录存在全部文件（含 html）
  - `programmatic` TR-9.2: frontmatter 格式合规
  - `programmatic` TR-9.3: check-links.py 零断链

## [x] Task 10: 迁移 python314-stdlib-wiki ✅ 2026-08-22

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 `docs/knowledge/learning/python314-stdlib-wiki/` 全部 18 个文件迁移至 `.agents/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/`
  - 17 个文件需迁移（仅 00-overview 已存在同名文件）
  - 包含 okf-optimization 和 mystx-optimization 系列报告
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-10.1: 目标目录存在全部 18 个文件
  - `programmatic` TR-10.2: frontmatter 格式合规
  - `programmatic` TR-10.3: check-links.py 零断链

## [x] Task 11: 补全 open-code-review-wiki 缺失章节 ✅ 2026-08-22

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 目标已有 `.agents/docs/knowledge/learning/03-agent-platforms-tools/03-code-devtools/open-code-review-wiki/` 但仅有 09-faq.md 和 README.md
  - 从源目录补充 8 个缺失章节文件（01-installation 至 08-integrations、10-summary-resources）
  - 注意目标路径比源多了一层 `03-code-devtools/`，需调整链接
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-11.1: 目标目录包含完整 11 个章节文件
  - `programmatic` TR-11.2: 章节编号连续无缺号
  - `programmatic` TR-11.3: 链接路径适配新目录深度

## [ ] Task 12: 扩展 agent-runtime-protocol-wiki 为原子化 Wiki

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 目标当前为单文件 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md`
  - 源为完整文件夹含 12 个章节文件，需创建 `agent-runtime-protocol-wiki/` 目录
  - 将单文件内容与源文件夹章节合并，避免内容丢失
  - 原单文件可保留为入口概览或重定向
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-12.1: 目标目录存在且包含全部章节文件
  - `programmatic` TR-12.2: 原单文件内容已整合，无信息丢失
  - `human-judgement` TR-12.3: 单文件到原子化的转换逻辑合理

## [/] Task 13: 迁移 ai-engineering-four-milestones-wiki

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 将文件夹 8 个文件迁移至 `.agents/docs/knowledge/learning/02-agent-engineering-methodology/01-paradigms/ai-engineering-four-milestones-wiki/`
  - 00-overview 和 05-loop-engineering 已存在，需对比合并
  - 根级 `ai-engineering-four-milestones-wiki.md` 单文件版本需处理（可能是旧版概览）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `programmatic` TR-13.1: 目标目录完整
  - `programmatic` TR-13.2: 无内容重复或丢失

## [x] Task 14: 迁移 three-ai-tools-learning-wiki ✅ 2026-08-22

- **Priority**: low
- **Depends On**: Task 1
- **Description**:
  - 将 2 个文件迁移至 `.agents/docs/knowledge/learning/06-business-trends-analysis/three-ai-tools-wiki/`
  - article-content.md 已存在，仅需迁移 seven-concepts-report.md
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-14.1: 文件存在于目标位置

## [x] Task 15: 迁移微信文章分析系列（5 个文件夹）✅ 2026-08-22

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - ai-switch-governance → `learning/06-business-trends-analysis/ai-switch-governance/`
  - causal-ai → `learning/05-ai-multimodal-content/causal-ai/`
  - mainecoon → `learning/05-ai-multimodal-content/mainecoon-wiki/`
  - quantdinger → `learning/03-agent-platforms-tools/quantdinger/`
  - rqndd → `learning/06-business-trends-analysis/rqndd/`
  - 这些文件夹包含 analysis-report.md、article-content.md、seven-concepts-report.md 等过程文件
  - 评估是否全部保留或仅保留 wiki 成品文件
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-15.1: 5 个文件夹均已迁移至对应分类
  - `human-judgement` TR-15.2: 过程文件保留决策合理

## [x] Task 16: 迁移非 Wiki 知识文件 ✅ 2026-08-22

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - `knowledge/ai-engineering/*.md`（2 个）→ `learning/02-agent-engineering-methodology/`
  - `knowledge/algorithmic-art/atomic-emergence/`（2 个，含 html）→ `learning/05-ai-multimodal-content/atomic-emergence/`
  - `knowledge/engineering/deep-learning-atomic-design/`（3 个）→ `learning/02-agent-engineering-methodology/`
  - `knowledge/learning/okf-topic-index.md` → 合并到已有 OKF 主题索引
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-16.1: 所有文件已迁移至目标位置
  - `programmatic` TR-16.2: frontmatter 格式合规

## [/] Task 17: 迁移复盘模式文件

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将 `docs/retrospective/patterns/methodology-patterns/` 下 15 个 .md 文件迁移至 `.agents/docs/retrospective/patterns/methodology-patterns/`
  - 检查目标目录是否已有同名文件，避免覆盖
  - 这些是方法论模式文件，非 Wiki 教程，使用模式文件的 frontmatter 格式
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-17.1: 15 个文件存在于目标目录
  - `programmatic` TR-17.2: 无已有文件被覆盖

## [ ] Task 18: 迁移复盘报告文件

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将 `docs/retrospective/reports/` 下 18 个报告文件迁移至 `.agents/docs/retrospective/` 对应子目录：
    - adversarial-review/ → `archives/` 或 reports/adversarial-review/
    - competitive-analysis/ → `archives/` 或 reports/competitive-analysis/
    - knowledge/ → `archives/` 或 reports/knowledge/
    - milestone/ → 根级或 archives/milestone/
  - 检查目标目录已有同名报告，避免重复
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-18.1: 所有报告文件已迁移
  - `programmatic` TR-18.2: 无已有文件被覆盖

## [ ] Task 19: 迁移 tech/refactor 散落文件

- **Priority**: low
- **Depends On**: None
- **Description**:
  - `docs/tech/contributing.md` → 评估是否已存在于 `.agents/docs/`
  - `docs/tech/four-layer-logging-pattern.md` → `.agents/docs/knowledge/best-practices/`
  - `docs/tech/release-onnx-*.md`（2 个）→ `.agents/docs/knowledge/tech/`
  - `docs/refactor/refactor-concurrent-safety-checker-20260812.md` → `.agents/docs/knowledge/best-practices/`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-19.1: 文件已迁移至合适位置

## [ ] Task 20: 更新分类索引和统计

- **Priority**: high
- **Depends On**: Task 1-19
- **Description**:
  - 更新 `learning/CATEGORIES.md`：在对应主题的 Wiki 清单表格中追加新增 Wiki，更新统计数字
  - 更新 `learning/README.md`：如有需要
  - 更新 `category-index.md`：重新生成或手动追加
  - 更新 `.agents/docs/knowledge/README.md`：更新总条目数和最近更新
  - 运行 `generate-readme.py` 为所有新迁移的 Wiki 文件夹生成/更新 README.md
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-20.1: CATEGORIES.md 中每个新增 Wiki 已列出
  - `programmatic` TR-20.2: 统计数字与实际文件数一致
  - `programmatic` TR-20.3: 所有新 Wiki 文件夹有 README.md

## [ ] Task 21: 全量链接与格式验证

- **Priority**: high
- **Depends On**: Task 20
- **Description**:
  - 运行 `fix-x-toml-ref.py` 批量修复和验证所有 x-toml-ref 路径
  - 运行 `check-links.py` 全量验证内部链接
  - 运行 `check-filename-convention.py` 验证文件名
  - 修复发现的所有问题
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-21.1: check-links.py 零错误
  - `programmatic` TR-21.2: check-filename-convention.py 零错误
  - `programmatic` TR-21.3: 所有 x-toml-ref 路径有效且 TOML 存在

## [ ] Task 22: 迁移结果人工审核

- **Priority**: medium
- **Depends On**: Task 21
- **Description**:
  - 按 spec.md 附录的分类映射表逐项核对
  - 检查分类合理性（AC-9）
  - 抽查 frontmatter 格式一致性
  - 确认无内容丢失
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `human-judgement` TR-22.1: 分类映射表逐项审核通过
  - `human-judgement` TR-22.2: 抽查 5 个 Wiki 的 frontmatter 格式
  - `human-judgement` TR-22.3: 确认无内容丢失或重复
