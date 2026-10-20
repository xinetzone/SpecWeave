# OpenTUI OKF Wiki 教程 - Implementation Plan

> **方法论**：seven-concepts 知识沉淀（R→I→E→V→C），与 source-code-to-okf-wiki 阶段0 + R→I→E→V→C 对齐。按信源预检、事实、洞察、分批生成、导航、核验、交付顺序推进。

## Task 1: 固定信源并完成源码/文档范围盘点
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 确认 OpenTUI 工作树仍干净、HEAD 为 `f8f608e2b9a41685d613a1156708ff06c826c3ce`，远端为 `anomalyco/opentui`；记录精确 commit 链接及无精确 tag 的事实。
  - 对照 README、workspace/package manifests、公开导出入口、官方 docs 首页及 releases，建立包清单、主题清单和源码核心路径清单。
  - 将官方 docs 0.6.6 与固定源码 commit 的版本边界登记；不得把 `next` 内容当成已发布行为。
  - 复核 OKF 目标目录与共享导航最新状态；记录待更新索引范围，不覆盖无关改动。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-1.1: 信源分类、remote、commit、文档版本及本机状态均有可复核记录；evidence 为 Git 命令输出和官方页面。
  - `rule` TR-1.2: 包和主题清单可逐项映射到 workspace manifest、入口文件或官方文档；evidence 为清单及其来源路径。
- **Completion Evidence**: 固定 commit、remote、无精确匹配 tag 与文档 `0.6.6` 坐标已登记于 `references/source-code-snapshot.md`、`references/official-documentation.md`；七个 release package roots 按 `scripts/npm-publish.ts` 的 `RELEASE_PACKAGES` 条目计数并登记于 `references/package-surface.md`。

## Task 2: R 阶段采集编号事实
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 按 TypeScript 包层、Zig/native 层、示例与测试层分区阅读关键源码；覆盖公开 API 入口、renderer 生命周期、renderable 树、布局/绘制、输入输出、bindings 和 native ownership。
  - 阅读官方文档中与源码对应的 quickstart、Core concepts、bindings、testing、lifecycle、reference、native 等页面。
  - 在本 Spec 目录生成 `facts.md`；使用连续 F 编号、逐条标注固定源码相对路径或官方页面，事实只记录可验证声明。
  - 数量类事实以脚本/结构化解析统计，并写明计数口径；不以人工枚举作为唯一依据。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 每条事实含来源定位且不含动机推断；evidence 为逐条来源映射及事实文本检查。
  - `rule` TR-2.2: 每个公开包面和核心主题在 facts 中均有证据，数量事实附计数方法/口径；evidence 为覆盖矩阵和脚本输出。
- **Completion Evidence**: `facts.md` 已登记 F-001 至 F-035，覆盖包入口、Core、native 渲染、React/Solid、交互、生命周期和测试；七个 release package roots 的统计对象与脚本范围已明确。

## Task 3: I 阶段形成架构洞察与知识地图
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于 F 编号形成 3-5 个架构洞察，每项包含陈述、事实证据、反常识点与文档组织行动。
  - 在本 Spec 目录生成 `insights.md`，给出从快速入门到核心 API、运行时/原生机制的学习路径。
  - 为每篇计划中的 concept/example 指定标题、用途、对应 F 编号及来源。
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `rubric` TR-3.1: 洞察与学习地图质量；1 = 无事实引用或无可用顺序，3 = 覆盖主要主题但依赖关系/反常识不足，5 = 洞察均引用事实并能直接决定连贯的读者路径；threshold >= 4；evidence 为 `insights.md` 与 facts 对照。
- **Completion Evidence**: `insights.md` 已形成 5 项包含陈述、F 编号证据、反常识点和文档组织行动的洞察，并列出学习路径、文档映射及不超过 7 个文件的生成批次；实施后的示例清单已同步为 5 篇。

## Task 4: 先建 references 并生成第一批概念文档
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 先生成 references 中的源码固定坐标/源码结构、官方文档主题和 release version 登记。
  - 再按学习地图生成第一批 concepts；每批最多 7 个文件，文档引用明确的 F 编号。
  - concepts 可包括项目总览、快速开始、包生态与使用入口、renderable/renderer 基础；最终篇目以 R/I 证据和既有 bundle 结构为准。
  - 已生成 3 份 references 与 concepts 00–04；全部内容文档的 `sources` 均指向已登记信源。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: references 在所有引用它的概念文档之前存在；evidence 为文件时间/清单及 sources 解析。
  - `rule` TR-4.2: 每批 <=7 个文件，且每篇文档符合 OKF frontmatter 与来源归因规则；evidence 为批次清单和 frontmatter 检查。
- **Completion Evidence**: 已创建 3 份 references 和 concepts 00–04；每篇概念文档的 `sources` 指向已存在的登记信源，源码引用固定到指定 commit。

## Task 5: 完成其余 concepts 与 examples
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 按批次补齐 layout/interaction/focus、testing/lifecycle、native rendering、framework bindings 及 R 阶段确认的其他核心主题。
  - 编写与概念对应的 Core、React、Solid 或原生边界示例；仅使用已核验 API，区分示例是否可独立运行及其前置条件。
  - 每批最多 7 个文件；对源码与官方文档口径不一致处保留版本标注和边界说明。
  - 已生成 concepts 05–09 与 5 份示例（Core、test renderer、React、Solid、native rendering 边界）；`insights.md` 已同步实际示例清单。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-5.1: examples 的 imports、API 和配置与固定源码/官方文档一致；evidence 为逐符号源码验证记录。
  - `rubric` TR-5.2: 教程覆盖质量；1 = 多项核心主题缺失，3 = 主要路径覆盖但存在显著缺口，5 = 公开包面和核心机制均有事实支撑、示例可核验且版本边界清楚；threshold >= 4；evidence 为覆盖矩阵和独立复核记录。
- **Completion Evidence**: 已生成 concepts 05–09 和 5 篇示例（Core、test renderer、React、Solid、native 渲染观测边界）；示例 API 与固定源码或官方文档对照，版本边界说明保留。

## Task 6: 最后生成 bundle 索引并挂载父级导航
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 内容文档定稿后最后生成 `concepts/index.md`、`examples/index.md`、`references/index.md`、bundle 根 `index.md` 与 `log.md`。
  - 更新 `jishu/terminal/index.md`、必要的 `jishu/index.md` 及 `doc/bundles/index.md`；先重读最新文件，只做 OpenTUI 所需的追加与计数更正。
  - 保持 bundle 内链接采用 `/` 开头路径；每个 index 同时包含读者导航与完整 `{toctree}`。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-6.1: 新 bundle 从父级导航可达，所有目录索引覆盖本目录内容，且未改写 Textualize 或其他在途 bundle；evidence 为导航 diff 与 BFS gate。
  - `rule` TR-6.2: 总束数/分组数/技术域数按官方 gate 口径与目录树一致；evidence 为 `invoke gates.bundles` 输出。
- **Completion Evidence**: 已创建 `concepts/`、`examples/`、`references/` 索引、bundle 根 `index.md` 与 `log.md`；终端组 toctree 已挂入 OpenTUI，总索引更新为 652 束、jishu 482 束、terminal 2 束。`invoke gates.toctrees` 仅报告并行在途 `jishu/iac/sst` 下 12 项不可达/缺索引；`invoke gates.bundles` 未报告上述束数漂移，只报告该未登记 iac 组及其组数差异，未修改该在途目录。

## Task 7: 执行内容级、结构级与构建质量自验
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 逐项核对事实到源码/API，检查代码块、包清单、版本说明、数量口径和负向声明。
  - 检查 frontmatter、sources 目标、bundle 内交叉链接、文件命名、索引清单和父级导航。
  - 在 awesome-okf-xs 环境运行 `invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8`；在可用时运行文档构建或本次文件的定向构建。
  - 修复本次发现的问题并复跑相应验证；对既有门禁红项只确认是否命中本次变更，不修无关内容。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 所有可行动内容问题关闭；evidence 为修复 diff 和复测记录。
  - `rule` TR-7.2: 本次变更相关质量门通过或经证据确认零命中；evidence 为命令输出。
- **Completion Evidence**:
  - Bundle 内容范围为 10 篇 concepts、5 篇 examples、3 份 references；facts F-001–F-035、5 项架构洞察及固定源码坐标已逐项对照。关键 API、React/Solid 入口、renderer 生命周期和 test renderer 示例均在固定源码中核验。
  - 定向链接检查扫描 23 篇 Markdown：136 条本地引用有效，33 个唯一外部 URL 可达；frontmatter 路径有效。信源稳定性审计覆盖 23 篇文件，临时、不存在、锚点越界及环境绑定路径均为 0。
  - `invoke gates.toctrees` 通过：全部 index 引用有效、内容文档均可达。
  - `invoke gates.bundles` 通过：9 域 / 63 组 / 654 束，frontmatter、计数行、节标题、分组表和 toctree 五面一致。共享总索引计数含并行 IAC 增量；OpenTUI 对应 terminal 分组为 2 束。
  - `invoke gates.utf8` 通过：11,922 个文件均为有效 UTF-8。
  - 已执行两轮全站 HTML 构建：一轮以 269 条全站 warning 触发 warning-as-error 失败；另一轮最终 exit 0，构建成功但有 329 条全站 warning。两轮为不同构建，不合并计数；独立 Review 检查警告上下文未发现 OpenTUI 专属命中。
  - 本任务未修改 OpenTUI 源码或 Textualize bundle；无 OpenTUI 内容级、结构级或可行动构建问题遗留。

## Task 8: 完成 C 阶段交付核对
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 核对 bundle 与主仓 Spec 文件清单、git status/diff，确保没有纳入任何不相关或用户在途文件。
  - 整理事实采集、洞察、生成、质量门与未能运行项目的证据摘要。
  - 不创建 Git commit；仅在用户明确提出提交请求后另行执行提交工作流。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: 交付清单仅含本任务文件且与目标路径一致；evidence 为两仓库 status/diff。
  - `rule` TR-8.2: 汇总已通过门禁、独立 Review 后续结论及剩余限制；evidence 为验证记录。
- **Notes**:
  - 子项目工作树含 OpenCode、Xerj、IAC/SST 等并行 WIP；仅审计本任务的 OpenTUI bundle、terminal 导航和 Spec 文件。
  - `doc/bundles/index.md` 是共享文件，当前 diff 同时包含并行 IAC/SST 增量；保留原状，只核对官方 bundles gate 的整体一致性。
  - 不创建 Git commit；实施队列清空后已由全新上下文完成只读独立 Review，结果为 `pass`，记录见 `review.md`。
- **Completion Evidence**:
  - 根仓状态仅显示 awesome-okf-xs 子模块为 dirty、daoapps 子模块及其 Spec 为他项变更、本任务 Spec 目录未跟踪；没有暂存或提交本任务文件。
  - 子项目状态确认本任务资产为新建的 `jishu/terminal/opentui/` bundle、`jishu/terminal/index.md` OpenTUI 导航行，以及共享 `doc/bundles/index.md` 中的计数/terminal 条目。共享总索引中的 IAC/SST 增量和 OpenCode、Xerj、IAC 其他文件均为并行 WIP，未纳入或改写。
  - 交付清单为 bundle 23 个 Markdown 文件及 Spec 的 `spec.md`、`tasks.md`、`facts.md`、`insights.md`；无 Textualize bundle 改动。
  - 相关 tracked diff 的 `git diff --check` 无输出；三项项目门禁通过。独立 Review R1 已在队列清空后完成，结果与证据记录于 `review.md`。
  - 独立 Review R1 检查 AC-1–AC-7 与 TR-1.1–TR-8.2：CP-R1–CP-R4 全部通过，CP-U1 为 5/5；无可行动发现或 P0–P2 问题。唯一 P3 advisory 为全站成功构建仍有 329 条 warnings，审查者检查的警告上下文未发现 OpenTUI 命中。示例 API 做了静态核验，未逐条执行。

## Task Dependencies
- Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8
- 全部实施任务完成后才进入 Spec Mode Review；`review.md` 仅在 Review 阶段创建。

## Quality Gates
- **G0**：信源坐标不可变、文档版本边界明确、公开包/主题清单有依据。
- **G1**：事实无推断、逐条可溯源、数量事实有脚本口径。
- **G2**：洞察四元组完整，知识地图和篇目均映射 F 编号。
- **G3**：OKF 文档引用稳定信源、分批 <=7、索引最后生成。
- **G4/V**：独立源码符号核验、链接/frontmatter/toctree/计数/build 复验；独立 Review 依据 spec.md 与证据给出 pass/fail/blocked。
