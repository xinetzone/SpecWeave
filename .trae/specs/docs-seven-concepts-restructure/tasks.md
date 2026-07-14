# Tasks — docs/ 七概念重构实施步骤

> 基于 spec.md 的 I→F→A→C 链路，按依赖顺序编排实施任务。
> 原则：先建目录骨架 → 再迁移内容 → 后修复引用 → 最后验证。

---

## 阶段0：准备工作（无文件变更）

- [x] Task 0: 创建目录骨架与备份策略
  - [x] SubTask 0.1: 在 `docs/` 下创建子目录结构：`insights/product-layer/`、`insights/architecture-layer/`、`insights/philosophy-layer/`、`insights/meta-layer/`、`reviews/retrospectives/`、`reviews/analysis/`、`reviews/history/`
  - [x] SubTask 0.2: 记录当前所有文件路径与引用关系快照（用于后续引用修复的对照基准）
  - [x] SubTask 0.3: 确认 `.trae/specs/docs-seven-concepts-restructure/` 下的 spec.md 已获用户批准

---

## 阶段1：insights/ 原子化拆分（核心变更，优先执行）

- [x] Task 1: 拆分 `insights-01-30.md` → product-layer + architecture-layer
  - [x] SubTask 1.1: 将洞察 1-15（产品层）提取至 `insights/product-layer/2026-06-17-insights-01-15.md`，保留文件头部声明并更新编号范围
  - [x] SubTask 1.2: 将洞察 16-30（架构层）提取至 `insights/architecture-layer/2026-06-17-insights-16-30.md`，保留文件头部声明并更新编号范围
  - [x] SubTask 1.3: 删除原 `insights/2026-06-17-insights-01-30.md`
  - 验证标准：两个新文件各约 350-380 行，洞察编号连续无遗漏，文件头部编号范围正确（实际：351 + 379 行）

- [x] Task 2: 拆分 `insights-31-53.md` → philosophy-layer（5个文件，洞察50移至元层）
  - [x] SubTask 2.1: 将洞察 31-40（玄同/恒德/家庭场景）提取至 `insights/philosophy-layer/2026-06-17-insights-31-40.md`
  - [x] SubTask 2.2: 将洞察 41-48（守柔处下/冲突场景/实践架构）提取至 `insights/philosophy-layer/2026-06-17-insights-41-48.md`
  - [x] SubTask 2.3: 将洞察 49（虚静内观操作手册）提取至 `insights/philosophy-layer/2026-06-17-insights-49.md`（独立文件，体道四法之首）
  - [x] SubTask 2.4: 将洞察 51-52（自然无为+生活实践操作手册）提取至 `insights/philosophy-layer/2026-06-17-insights-51-52.md`（两法互补，合并为一文件）
  - [x] SubTask 2.5: 将洞察 53（每日一问习惯引擎）提取至 `insights/philosophy-layer/2026-06-17-insights-53.md`（独立文件，产品核心引擎）
  - [x] SubTask 2.6: 洞察 50（报名帖前台视图元洞察）因元层性质移至 meta-layer，与洞察54-58合并
  - [x] SubTask 2.7: 删除原 `insights/2026-06-17-insights-31-53.md`
  - 验证标准：五个新文件行数分别为 297/248/404/452/157 行，洞察编号 31-53 连续无遗漏（洞察50移至元层）

- [x] Task 3: 拆分 `insights-54-68.md` → meta-layer（4个文件，含洞察50）
  - [x] SubTask 3.1: 将洞察 50（前台视图）+ 54-58（元认知/UX法则/熵增/元分析）提取至 `insights/meta-layer/2026-06-17-insights-50-54-58.md`（文件已重命名以包含洞察50）
  - [x] SubTask 3.2: 将洞察 59-62（开发者/探索者困境/版权合规/竞争格局）提取至 `insights/meta-layer/2026-06-17-insights-59-62.md`
  - [x] SubTask 3.2b: 将洞察 63-65（定位解缚/反效率工具/解缚决策法）提取至 `insights/meta-layer/2026-06-17-insights-63-65.md`
  - [x] SubTask 3.3: 将洞察 66-68（柔弱不争/留存/睡前静心）提取至 `insights/meta-layer/2026-06-17-insights-66-68.md`
  - [x] SubTask 3.4: 删除原 `insights/2026-06-17-insights-54-68.md` 和中间产物 `insights-59-65.md`
  - 验证标准：四个新文件行数分别为 538/466/579/379 行，洞察编号 50/54-68 连续无遗漏

---

## 阶段1.5：导航与一致性修复（阶段1拆分后立即执行）

- [x] Task 3.5: 全量导航链接修复
  - [x] SubTask 3.5.1: 更新所有洞察文件的导航关联文件块，指向新拆分的文件路径
  - [x] SubTask 3.5.2: 修复旧行号锚点引用（`#Lxxx-Lxxx`），替换为跨文件相对路径链接
  - [x] SubTask 3.5.3: 为 product-layer 和 architecture-layer 文件添加自引用链接
  - [x] SubTask 3.5.4: 统一层级说明为"元层（50/54-68）"以包含洞察50
  - [x] SubTask 3.5.5: 统一导航描述文本，为洞察51-52补充"操作手册"后缀

- [x] Task 3.6: 命名与标题一致性检查
  - [x] SubTask 3.6.1: 检查 meta 层文件 insights-50-54-58.md 的文件名、标题、导航自引用一致
  - [x] SubTask 3.6.2: 检查其他 meta 层文件（59-62、63-65、66-68）遵循命名和标题一致性规范
  - [x] SubTask 3.6.3: 检查 philosophy 层和其他层级文件标题格式一致

---

## 阶段2：reviews/ 重组（依赖阶段0目录骨架）

- [x] Task 4: 迁移 reviews/ 现有文件至子目录
  - [x] SubTask 4.1: 将 `reviews/2026-06-17-project-review.md` 移至 `reviews/retrospectives/2026-06-17-project-review.md`
  - [x] SubTask 4.2: 将 `reviews/2026-06-17-registration-review.md` 移至 `reviews/retrospectives/2026-06-17-registration-review.md`
  - [x] SubTask 4.3: 将 `reviews/2026-07-14-zhujian-wudao-first-principles-review.md` 重命名并移至 `reviews/analysis/2026-07-14-first-principles-review.md`（移除 `zhujian-wudao-` 前缀）
  - 验证标准：reviews/ 下仅 3 个子目录（retrospectives/、analysis/、history/），无平铺文件

- [x] Task 5: 迁移 `restructure-comparison.md` 至历史归档
  - [x] SubTask 5.1: 将 `docs/restructure-comparison.md` 重命名并移至 `docs/reviews/history/2026-06-26-restructure-comparison.md`
  - 验证标准：docs/ 根目录无 `restructure-comparison.md`，history/ 下有带日期前缀的文件

---

## 阶段3：内容去重（依赖阶段1、2完成）

- [x] Task 6: first-principles-review.md 去重
  - [x] SubTask 6.1: 读取 `reviews/analysis/2026-07-14-first-principles-review.md` 的 §六 可迁移方法论（6条）
  - [x] SubTask 6.2: 对比 `knowledge-transfer/2026-06-17-transferable-methods.md`，确认哪些方法论已在后者中定义
  - [x] SubTask 6.3: 将 §六 正文替换为引用指针表（`方法论名 → 见 transferable-methods.md 第N章`），保留方法论"发现"论述（为什么这些方法论有价值）
  - [x] SubTask 6.4: 若 transferable-methods.md 中缺失某条方法论（经对比发现），将其完整定义补充至 transferable-methods.md
  - 验证标准：first-principles-review.md 不再包含方法论完整定义，仅保留引用指针；transferable-methods.md 是方法论的唯一定义源

- [ ] Task 7: project-review.md 洞察列表精简
  - [ ] SubTask 7.1: 读取 `reviews/retrospectives/2026-06-17-project-review.md` 的 §二 68条洞察完整列表
  - [ ] SubTask 7.2: 将 §二 替换为统计摘要（总数 68 + 分层分布：产品层15/架构层15/哲学层22/元层16）+ 引用指针（`→ 见 insights/ 各层级文件目录`）
  - 验证标准：project-review.md 不再逐条列出洞察标题，仅保留统计摘要

---

## 阶段4：product-spec.md 拆分评估（可选，依赖阶段0）

- [ ] Task 8: 评估并执行 product-spec.md 拆分
  - [ ] SubTask 8.1: 统计 `product/2026-06-17-product-spec.md` 实际行数
  - [ ] SubTask 8.2: 若超过 500 行，按 §一-§三 / §四-§五 / §六-§九 拆分为 3 文件；否则保持原文件
  - [ ] SubTask 8.3: 若拆分，更新文件内部交叉引用（§五.2引用洞察53等 → 指向新insights路径）
  - 验证标准：product/ 下每个文件不超过 500 行（若拆分）或保持原文件（若不拆分）

---

## 阶段5：索引与导航更新（依赖阶段1-4完成）

- [x] Task 9: 创建 `_index.md` 目录索引
  - [x] SubTask 9.1: 在 `docs/insights/_index.md` 和 `docs/reviews/_index.md` 中建立子目录索引
  - [ ] SubTask 9.2: 在 `docs/_index.md` 中建立完整目录树（反映阶段1-4后的新结构）
  - [ ] SubTask 9.3: 建立文件清单表格（文件名/用途/行数/简介）
  - [ ] SubTask 9.4: 建立快速查找表（需求场景 → 对应文件路径）
  - [ ] SubTask 9.5: 声明各子目录的职责边界（从 spec.md §二.4 复制职责定义表）
  - 验证标准：_index.md 完整反映新结构，可作为导航入口

- [ ] Task 10: 更新 README.md
  - [ ] SubTask 10.1: 移除 README.md 中的文件清单表格和快速查找表（移交 _index.md）
  - [ ] SubTask 10.2: 更新目录结构树为新结构
  - [x] SubTask 10.3: 在 README.md 顶部添加 `→ 完整索引见 [_index.md](_index.md)`
  - [ ] SubTask 10.4: 更新"重组说明"为第二次重组记录
  - 验证标准：README.md 不再包含文件清单表格，指向 _index.md

- [ ] Task 11: 更新 AGENTS.md 路由表
  - [ ] SubTask 11.1: 更新 `apps/zhujian-wudao/AGENTS.md` 文件地图中的 docs/ 路径
  - [ ] SubTask 11.2: 更新路由索引表中 insights 的文件路径（3文件 → 10文件的层级目录）
  - [ ] SubTask 11.3: 更新路由索引表中 reviews 的文件路径（含子目录）
  - 验证标准：AGENTS.md 路由表中所有路径指向新结构

---

## 阶段6：引用修复（依赖阶段1-5完成，可并行执行）

- [x] Task 12: 全项目引用修复（阶段1.5已完成insights内部导航修复）
  - [x] SubTask 12.1: 搜索全项目对旧 insights 路径的引用（`insights/2026-06-17-insights-01-30.md` 等 3 个旧路径），替换为新路径
  - [x] SubTask 12.2: 搜索全项目对旧 reviews 路径的引用，替换为新路径（含子目录）
  - [x] SubTask 12.3: 搜索全项目对 `restructure-comparison.md` 的引用，替换为新路径
  - [x] SubTask 12.4: 搜索全项目对 `first-principles-review.md` 旧文件名的引用，替换为新文件名
  - [ ] SubTask 12.5: 检查 product-spec.md 内部交叉引用（§5.2/§5.3/§4.1 等引用洞察的路径），更新为新路径
  - 验证标准：全项目无断链，所有引用指向有效文件路径

---

## 阶段7：验证与收尾（依赖阶段1-6完成）

- [ ] Task 13: 链接有效性验证
  - [ ] SubTask 13.1: 运行 link-check-cmd Skill 检查所有内部链接
  - [ ] SubTask 13.2: 修复发现的任何断链
  - 验证标准：零断链

- [x] Task 14: 结构一致性验证
  - [x] SubTask 14.1: 验证 insights/ 11 个文件的洞察编号 1-68 连续无遗漏（含洞察50移至元层）
  - [x] SubTask 14.2: 验证所有文件遵循 `YYYY-MM-DD-{type}-{id}.md` 命名格式
  - [x] SubTask 14.3: 验证无文件超过 600 行（原子化阈值）——全部通过（最大579行）
  - [x] SubTask 14.4: 验证 reviews/ 下仅 3 个子目录，无平铺文件
  - 验证标准：四项验证全部通过

- [ ] Task 15: 内容语义去重验证
  - [x] SubTask 15.1: 验证 first-principles-review.md 不包含 transferable-methods.md 中已定义的方法论正文
  - [ ] SubTask 15.2: 验证 project-review.md 不包含 insights/ 中已存在的洞察标题逐条列表
  - [ ] SubTask 15.3: 验证 README.md 与 _index.md 职责不重叠（README 是入口说明，_index 是文件清单）
  - 验证标准：三项去重验证全部通过

- [ ] Task 16: 原子提交
  - [ ] SubTask 16.1: 按 atomic-commit-cmd 规范，将重构变更拆分为多个原子提交（建议按阶段拆分提交）
  - [ ] SubTask 16.2: 提交信息格式：`refactor(docs): {阶段名}——{简述}`
  - 验证标准：每个提交单一职责，提交信息遵循 Conventional Commits

---

## 阶段8：后续优化（可选）

- [x] Task 17: 拆分 insights-59-65.md（1020行 → insights-59-62.md + insights-63-65.md）
  - 验证标准：拆分后每个文件 ≤ 600 行，洞察编号连续无遗漏（已完成：466行 + 579行）

- [ ] Task 18: 修复所有残留引用并完成最终验证
  - 包括 product-spec.md 内部引用、AGENTS.md 路由表、docs/_index.md 创建、README.md 更新等

---

# Task Dependencies

- Task 0（目录骨架）→ 所有后续任务
- Task 1, 2, 3（insights 拆分）→ Task 3.5/3.6（导航修复）→ Task 12（引用修复）、Task 14（验证）
- Task 4, 5（reviews 重组）→ Task 12（引用修复）
- Task 6, 7（内容去重）依赖 Task 3, 4 完成
- Task 8（product 拆分）独立，可与 Task 1-5 并行
- Task 9, 10, 11（索引更新）依赖 Task 1-8 全部完成
- Task 12（引用修复）依赖 Task 1-11 全部完成
- Task 13, 14, 15（验证）依赖 Task 12 完成
- Task 16（原子提交）依赖 Task 13-15 验证通过
- Task 17（59-65拆分）可在 Task 3 完成后随时执行
- Task 18（最终收尾）依赖所有任务完成

# 可并行任务组

- **并行组A**（阶段1）：Task 1 + Task 2 + Task 3（三个 insights 文件独立拆分）
- **并行组B**（阶段2-3）：Task 4 + Task 5 + Task 8（reviews 迁移、history 归档、product 评估，互不依赖）
- **并行组C**（阶段6）：Task 12 的 SubTask 12.1-12.5 可并行搜索不同路径模式

# 当前进度总结

- ✅ **已完成**：阶段0（目录骨架）、阶段1（insights拆分，含方案C调整：哲学层5文件、洞察50移至元层；insights-59-65二次拆分为59-62和63-65）、阶段1.5（导航链接修复+一致性检查）、阶段2（reviews重组）、Task 6（first-principles-review去重）、insights/_index.md 和 reviews/_index.md 创建、insights原子化全部完成（11文件，全部≤600行）
- ⏳ **待完成**：Task 7（project-review精简）、Task 8（product-spec评估拆分）、Task 9根_index.md、Task 10（README更新）、Task 11（AGENTS.md路由）、Task 12.5（product-spec内部引用）、Task 13（链接验证）、Task 15.2-15.3（去重验证）、Task 16（原子提交）
- 📌 **待优化**：无P0待办，insights原子化已全部完成
