# Microsoft Agent Framework OKF 知识包 — 任务清单

## [x] Task 1: 信源获取与事实登记
- 抓取 Build 2026 博文、Learn 文档中心 34 个页面、GitHub README 与 Releases。
- 产出 `facts.md`：F-001 ~ F-120，按主题分组，标注 S1/S2/S3。
- 验收：日期、GA 版本、包名、CodeAct 数据均有出处。

## [x] Task 2: 骨架与归属判定
- 判定落点 `jishu/ai/frameworks/microsoft-agent-framework/`。
- 操作可复现性两问皆“是”，设 `examples/`。
- 验收：`spec.md` 归属表与骨架段落完整。

## [x] Task 3: references 先行
- 写 `references/article-source.md`（F 编号双份登记）与 `references/verification.md`（P0 核验与勘误）。
- 验收：F 编号连续；勘误单列；单源声明明确。

## [x] Task 4: concepts 生成
- 写 10 篇概念文档，每篇 frontmatter 完整、引用 F 编号、含已知边界。
- 验收：无 F 之外数字；相对链接可达；术语一致。

## [x] Task 5: examples 生成
- 写 5 篇可演练示例（hello / tool+approval / harness+session / workflow+checkpoint / hosted+handoff）。
- 验收：命令、包名、代码与文档一致；标注“示例为最小化改写，非官方原文”。

## [x] Task 6: 索引接入与计数
- 更新 `frameworks/index.md`（导航行 + toctree + 计数）。
- 更新 `ai/index.md`、`jishu/index.md`、`bundles/index.md` 计数。
- 验收：toctree 条目数与目录数一致；三级计数同步。

## [x] Task 7: 对抗审查与机械门禁
- 四视角审查（溯源/结构/可用性/时效）。
- 执行 UTF-8、双份 F 编号、toctree、链接、计数、敏感路径检查。
- 产出 `review.md`；问题回改。

## [x] Task 8: 提交
- 子模块 `projects/awesome-okf-xs` 先提交；主仓库提交 spec。
- 验收：显式文件列表；不 push。
