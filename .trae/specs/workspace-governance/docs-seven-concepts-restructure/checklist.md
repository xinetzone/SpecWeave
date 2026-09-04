# Checklist — docs/ 七概念重构验证

> 对应 spec.md 的三大核心要求：逻辑结构严密自洽、内容语义无重复冗余、原子化拆分。
> 每个检查点须在实施完成后逐项验证。

---

## 一、逻辑结构严密自洽

- [x] insights/ 目录按 4 层级子目录组织：product-layer/、architecture-layer/、philosophy-layer/、meta-layer/
- [x] reviews/ 目录按 3 子目录组织：retrospectives/（过程复盘）、analysis/（方法论复盘）、history/（历史归档）
- [x] reviews/ 下无平铺文件，仅有 3 个子目录
- [ ] docs/ 根目录仅保留 `_index.md` 和 `README.md`，无内容性文件（restructure-comparison.md 已迁入 history/）——待创建 docs/_index.md
- [ ] 每个子目录的职责在 _index.md 中有明确定义，且与实际内容一致——待创建根 _index.md
- [x] 目录间的职责边界无交叉（product/ 不含推理过程，insights/ 不含产品规格正文，reviews/ 不含方法论定义）
- [x] 文件命名全部遵循 `YYYY-MM-DD-{type}-{id}.md` 格式
- [x] 无文件包含 `zhujian-wudao-` 项目前缀（已移除）
- [x] `restructure-comparison.md` 已添加日期前缀并迁入 `reviews/history/`
- [ ] AGENTS.md 文件地图与路由索引表指向新结构路径——待更新

---

## 二、内容语义无重复冗余

- [x] `first-principles-review.md` 的 §六 可迁移方法论已替换为引用指针，不包含方法论完整定义
- [x] `transferable-methods.md` 是可迁移方法论的唯一定义源（已补充3条缺失方法论）
- [ ] `project-review.md` 的 §二 洞察列表已精简为统计摘要 + 引用指针，不逐条列出洞察标题——待执行
- [ ] `README.md` 不包含文件清单表格（已移交 _index.md）——待更新
- [ ] `_index.md` 与 `README.md` 职责不重叠（README 是入口说明，_index 是完整清单）——待验证
- [x] `transferable-methods.md` 与 `transferable-patterns.md` 的边界明确（前者面向人类、后者面向AI Agent），无语义重叠
- [ ] 洞察标题不在两个文件中重复出现（insights/ 是唯一定义源，其他文件仅引用编号）——待验证

---

## 三、原子化拆分

- [x] insights/ 拆分后共 11 个文件（product-layer 1 + architecture-layer 1 + philosophy-layer 5 + meta-layer 4 = 11 文件）

- [x] insights/ 每个文件不超过 600 行（最大为 insights-63-65.md 579行，全部通过）
- [x] 洞察编号 1-68 连续无遗漏（拆分前后总数一致：15+15+22+16=68，含洞察50移至元层）
- [x] 每个洞察文件可通过文件路径直接引用，不依赖行号锚点（旧行号锚点已修复为跨文件链接）
- [ ] product-spec.md 若拆分，每个文件不超过 500 行；若未拆分，原文件不超过 500 行——待评估
- [ ] product/ 文件可按 §节 独立引用（若已拆分）——待评估

---

## 四、引用完整性

- [x] 全项目无对旧路径 `insights/2026-06-17-insights-01-30.md` 的残留引用
- [x] 全项目无对旧路径 `insights/2026-06-17-insights-31-53.md` 的残留引用
- [x] 全项目无对旧路径 `insights/2026-06-17-insights-54-68.md` 的残留引用
- [x] 全项目无对旧文件名 `zhujian-wudao-first-principles-review` 的残留引用
- [x] 全项目无对旧路径 `restructure-comparison.md`（根目录位置）的残留引用
- [x] 所有跨文件引用使用相对路径，无 `file:///` 绝对路径
- [ ] link-check-cmd 验证通过：零断链——待执行全量验证
- [x] 所有洞察文件导航关联文件块已更新为新路径
- [x] 旧行号锚点（`#Lxxx-Lxxx`）已替换为跨文件相对路径链接
- [x] 所有洞察文件包含自引用链接
- [x] 层级说明统一为"元层（50/54-68）"以包含洞察50
- [x] 导航描述文本统一（洞察51-52补充"操作手册"后缀）

---

## 五、方法论质量门（七概念 G1-G4）

- [x] G2 通过：spec.md §一 的 4 条问题洞察均包含四元组（现象+根因+影响+建议）
- [x] G4 通过：tasks.md 中每个任务满足单一职责、可独立验证
- [x] V 通过：spec.md §五 对抗审查已覆盖 4 个视角（维护者/新人/ROI/未来扩展）
- [ ] C 待验证：重构变更最终通过原子提交交付（Task 16）

---

## 六、文件行数验证

### product-layer
- [x] `insights/product-layer/2026-06-17-insights-01-15.md` = 351 行 ≤ 600 行 ✅

### architecture-layer
- [x] `insights/architecture-layer/2026-06-17-insights-16-30.md` = 379 行 ≤ 600 行 ✅

### philosophy-layer（5个文件）
- [x] `insights/philosophy-layer/2026-06-17-insights-31-40.md` = 297 行 ≤ 600 行 ✅
- [x] `insights/philosophy-layer/2026-06-17-insights-41-48.md` = 248 行 ≤ 600 行 ✅
- [x] `insights/philosophy-layer/2026-06-17-insights-49.md` = 404 行 ≤ 600 行 ✅
- [x] `insights/philosophy-layer/2026-06-17-insights-51-52.md` = 452 行 ≤ 600 行 ✅
- [x] `insights/philosophy-layer/2026-06-17-insights-53.md` = 157 行 ≤ 600 行 ✅

### meta-layer（4个文件）
- [x] `insights/meta-layer/2026-06-17-insights-50-54-58.md` = 538 行 ≤ 600 行 ✅
- [x] `insights/meta-layer/2026-06-17-insights-59-62.md` = 466 行 ≤ 600 行 ✅
- [x] `insights/meta-layer/2026-06-17-insights-63-65.md` = 579 行 ≤ 600 行 ✅
- [x] `insights/meta-layer/2026-06-17-insights-66-68.md` = 379 行 ≤ 600 行 ✅

### reviews
- [x] `reviews/analysis/2026-07-14-first-principles-review.md` 去重后行数 ≤ 原始行数 ✅
- [ ] `reviews/retrospectives/2026-06-17-project-review.md` 精简后行数 ≤ 原始行数——待执行

---

## 七、命名与标题一致性验证

- [x] meta 层文件名、标题、导航自引用一致：
  - `insights-50-54-58.md` → 标题"洞察库·元层（洞察50/54-58）"→ 导航自引用正确
  - `insights-59-62.md` → 标题"洞察库·元层（洞察59-62）"→ 导航自引用正确
  - `insights-63-65.md` → 标题"洞察库·元层（洞察63-65）"→ 导航自引用正确
  - `insights-66-68.md` → 标题"洞察库·元层（洞察66-68）"→ 导航自引用正确
- [x] philosophy 层文件名、标题、导航自引用一致
- [x] 所有文件名格式：`YYYY-MM-DD-insights-XX[-YY].md`（日期前缀+洞察范围）
- [x] 所有标题格式：`# 洞察库·{层名}（洞察XX[-YY]）`

---

## 八、待完成项汇总

| 优先级 | 待办项 | 说明 |
|--------|--------|------|
| P1 | 创建 docs/_index.md | 根目录索引，含完整目录树+文件清单+快速查找表 |
| P1 | 更新 README.md | 移除文件清单表格，更新目录结构，指向 _index.md |
| P1 | 更新 AGENTS.md 路由表 | insights路径从3文件更新为11文件层级目录，reviews含子目录 |
| P1 | 精简 project-review.md | §二洞察列表替换为统计摘要+引用指针 |
| P2 | 评估 product-spec.md 拆分 | 统计行数，决定是否按§节拆分 |
| P2 | 更新 product-spec.md 内部引用 | §5.2/§5.3等引用洞察的路径需更新 |
| P2 | 运行 link-check-cmd 全量验证 | 零断链验证 |
| P3 | 原子提交 | 按阶段拆分原子提交 |
