# Tasks

- [x] Task 0: G0 信源稳定性预检：记录 12 个仓库的 commit hash/分支/盘点日期到 `<spec-dir>/source-versions.md`；确认信源路径无临时段；任务期间冻结信源（禁止 git pull）。
- [x] Task 1: R 阶段 - 事实采集（深度仓库）：
  - [x] 1.1 rich：阅读 `rich/rich/` 核心模块（console/segment/style/text/table/markdown/progress/live/layout/panel/box/measure/protocol），提取 F-xxx 事实 → `facts-rich.md`（89 条）
  - [x] 1.2 textual：阅读 `textual/src/textual/` 核心（app/widget/screen/dom/reactive/events/message/binding/worker + css/ + widgets/ 抽样 + drivers/），提取事实 → `facts-textual.md`（115 条）
- [x] Task 2: R 阶段 - 事实采集（中度仓库，可并行委派）：
  - [x] 2.1 frogmouth（app 架构 + Markdown 渲染管线）→ `facts-frogmouth.md`（并入 facts-satellites-1.md，22 条）
  - [x] 2.2 toolong / trogon / rich-cli → `facts-satellites-1.md`（24+30+24 条）
  - [x] 2.3 textual-dev / textual-serve / textual-web → `facts-satellites-2.md`（18+20+20 条）
- [x] Task 3: R 阶段 - 事实采集（轻度仓库）：.github / textual-demo / textual-key-recorder 概览事实并入 `facts-ecosystem.md`（15 条）
- [x] Task 4: I 阶段 - 架构洞察与知识地图：基于全部 facts 提炼 3-5 个洞察四元组（陈述/证据/反常识/行动）+ 分组学习路径（入门→rich 核心→textual 核心→卫星工具→生态总览），产出 `insights.md`（5 洞察 + 27 概念 + 8 示例 + 覆盖度核对）；确定每篇概念文档覆盖的 F-xxx 编号
- [x] Task 5: E 阶段 - 创建 Bundle 骨架 + references/ 信源先行：`projects/Textualize/{index.md,log.md,concepts/,examples/,references/}`；先生成 12 个 `references/<repo>.md`（含 commit hash）+ `references/index.md`
- [ ] Task 6: E 阶段 - concepts/ 分批生成（每批≤7文件，按学习路径，可并行委派）：
  - [ ] 6.1 批次A：生态总览 + rich 入门（00-05）
  - [ ] 6.2 批次B：rich 核心概念（06-12）
  - [ ] 6.3 批次C：textual 核心概念（13-19）
  - [ ] 6.4 批次D：卫星工具概念（20-26，每仓库 1-2 篇）
- [ ] Task 7: E 阶段 - examples/ 生成：rich 渲染示例 + textual 应用示例 + 卫星工具用法示例（每批≤7）
- [ ] Task 8: E 阶段 - index 收尾：最后生成 `concepts/index.md`、`examples/index.md`、根 `index.md`（含 okf_version + toctree）、`log.md`；所有 index 必含 `{toctree}` 块
- [ ] Task 9: V 阶段 - 独立验证：
  - [ ] 9.1 Grep 级 API 真实性验证（每篇文档引用的类名/方法名在信源中命中）
  - [ ] 9.2 计数断言验证（"X个/Y份"陈述经 Glob/Grep 独立计数）
  - [ ] 9.3 frontmatter 完整性 + 链接检查（`/` 开头 bundle-relative）+ toctree 完整性
  - [ ] 9.4 运行 `check-source-path-stability.py` audit；输出验证报告，逐一修复
- [ ] Task 10: C 阶段 - 模式沉淀：回顾流程顺利点/问题点，补充反模式，记录到 `<spec-dir>/retrospective.md`（不强制入库，除非用户要求）

# Task Dependencies

- Task 1-3 依赖 Task 0（信源固定后才可采集事实）
- Task 4 依赖 Task 1-3（洞察基于全部事实）
- Task 5 依赖 Task 0（references 需要 commit hash）；可与 Task 4 并行
- Task 6-7 依赖 Task 4-5（知识地图 + 信源先行）
- Task 8 依赖 Task 6-7（index 最后写）
- Task 9 依赖 Task 8
- Task 10 依赖 Task 9
- Task 1.1/1.2、Task 2.1-2.3、Task 6.1-6.4 内部可并行委派子代理
