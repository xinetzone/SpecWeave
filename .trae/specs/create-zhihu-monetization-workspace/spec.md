---
title: "知乎变现执行工作区（projects/monetize/zhihu-monetization）Spec"
status: "draft"
date: "2026-09-23"
updated: "2026-09-23"
source: "定义层：docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/（README/主路径/todo/风险四篇）；知识层：projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/（F-001~F-067）；前置 Spec：.trae/specs/create-zhihu-monetization-okf-wiki/"
tags: [知乎, 变现, 执行工作区, projects-monetize, Spec]
---

# 知乎变现执行工作区（projects/monetize/zhihu-monetization）Spec

## 问题、用户与目标

### 问题

前置交付（[create-zhihu-monetization-okf-wiki](../create-zhihu-monetization-okf-wiki/spec.md)）已产出两个层次：

1. **知识层**：OKF bundle `sheke/industry/zhihu-monetization`（F-001\~F-067 编号事实 + P0 核验 + 机制洞察；`status: flagged`，复核线 2026-12-31）；
2. **定义层**：docs 公开报告四篇（[总览矩阵](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/README.md)、[主路径 18 条行动项与验收标准](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/ai-creator-main-path.md)、[todo 排期视图](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/todo.md)、[风险与边界](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/risks-and-boundaries.md)）。

但**执行层缺位**：行动项的勾选状态、日期戳、盐粒到账数字、中断原因、周期复盘只产生于执行期，无处存放；每次开工需在 docs 与 bundle 之间人工跳转，"知识 → 行动 → 留痕"闭环断裂。

### 用户

* 主要用户：执行 AI/技术创作者主路径的个人（每日 45–60 分钟、AI 智能体辅助工作流）；

* 次要用户：AI 智能体（按本工作区 `AGENTS.md` 路由读写执行记录）。

### 目标

1. 在 `projects/monetize/zhihu-monetization/` 建立**执行工作台**：README 入口 + 执行台账 `tracker.md` + 记录表 `records.md` + `AGENTS.md` 智能体入口；
2. 定义层与知识层**只链接不复制**（单一事实来源）：项目不复制主路径/todo 正文；执行状态与记录为项目唯一新增承载；
3. 个人数据隔离：模板入库、真实数据入 gitignore 的 `local/` 目录；
4. 登记 projects 区域索引（`projects/README.md` + `projects/AGENTS.md`），项目可被路由发现；
5. 以七概念方法论 F→V→C 与 Spec Mode 流程交付（含对抗审查与原子提交，不 push）。

### 非目标

* 不修改 docs 报告与 bundle 的任何文件（只读引用）；

* 不产生新知识事实（零新 F 编号、不做知识裁决）；

* 不做收益承诺、不代执行平台操作（报名/打卡/提现由用户本人完成）；

* 不把真实个人数据入库；不 push 远端；

* 不将本工作区建成 git 子模块（本次为主仓库直接跟踪的普通目录）。

## 信源与内容敏感度（预检结论）

* **敏感度判定**：**公开**——脚手架内容派生自公开 docs 报告与公开 bundle（均脱敏）；真实执行数据由 `local/` 隔离不入库。标准工作流，规划区 `.trae/specs/create-zhihu-monetization-workspace/`。

* **产出物落点**：`projects/monetize/zhihu-monetization/`（用户明确指定，优先于"公开产出物入根 `docs/`"默认；形态参照先例 `projects/tvm-ffi`——主仓库直接跟踪的普通目录，非子模块）。

* **私域零残留**：全部产出物零 `file:///`、零本机绝对路径、零个人账号/隐私信息。

## 设计原理（F 阶段产出：假设剥离 → 要素 → 公理 → 方案）

### 假设剥离

| #  | 隐含假设                             | 裁定                                                |
| -- | -------------------------------- | ------------------------------------------------- |
| A1 | "todo.md 就是执行载体，勾选直接改 docs 文件即可" | **否定**：docs 属公开定义层，个人执行状态混入会破坏其稳定参考系地位，且违反脱敏原则    |
| A2 | "项目需要复制行动项与验收标准才可操作"             | **否定**：定义（主路径 §三）已是唯一事实来源，复制将产生漂移（规则按期变动先例 F-067） |
| A3 | "知识内容应在项目内再建一份"                  | **否定**：bundle 是最高可信度知识库（只读引用），重复即漂移               |
| A4 | "个人执行数据可以随项目入库"                  | **否定（按用户决策）**：仓库公开推送即暴露，须隔离                       |

### 要素识别（执行工作台的最小必要构成）

1. **入口**：一处可回答"这是什么、从哪开始、今天做什么"；
2. **状态**：18 条行动项的勾选 + 日期戳（新增承载之一）；
3. **记录**：到账数字、中断原因、周/月核对与复盘（新增承载之二）；
4. **纪律**：勾选纪律、发布前三问自检、规则快照对照、时效复核（从源文档传导，不重定义）；
5. **路由**：人与智能体都能找到知识层（bundle）与定义层（docs）的正确入口。

### 公理

* **P1 单一事实来源**：定义只在 docs、知识只在 bundle、执行状态只在项目——三者互不复制；

* **P2 链接优于拷贝**：跨层引用一律以相对路径链接回源（规则变动时自动指向最新校正版）；

* **P3 时效应答**：`rule_snapshot` / `status: flagged` / `stale_after: 2026-12-31` 传导到工作区入口与智能体入口；

* **P4 数据边界**：模板与机制入库，真实数据零入库（`local/` 隔离）；

* **P5 纪律不重定义**：自检门、勾选纪律只引用源文档并说明执行方式，不另立新规。

### 重构方案（工作区结构）

```text
projects/monetize/zhihu-monetization/
├── README.md        # 入口：定位 / 链接矩阵 / 每日用法 / 时效与防画饼声明
├── AGENTS.md        # 智能体入口：定位 / 文件地图 / 纪律传导 / 路由
├── tracker.md       # 执行台账：todo 落地（勾选 + 日期戳 + 周期节奏 + 触发器 + 复核锚点）
├── records.md       # 记录表：到账 / 周核对 / 周期复盘 / 发布自检留痕（模板 + 占位）
├── .gitignore       # local/ 数据隔离规则
└── local/
    └── README.md    # 隔离区机制说明（唯一入库文件；其余内容不入库）
```

## 功能性需求

### FR1 工作区骨架与入口页

* 按上述结构创建目录；`README.md` 含：本工作区是什么/不是什么（防画饼：池 ≠ 个人收益、个人实得待验证）、**链接矩阵**（定义层四篇 + 知识层 bundle 总览与关键篇目）、每日用法（今天做什么 → tracker；记完 → records）、数据与隐私说明、时效声明；

* frontmatter 携 `source`（双源：docs 报告 + bundle）、`rule_snapshot`、`status: flagged`、`stale_after: 2026-12-31`。

### FR2 单一事实来源（链接不复制）

* 行动项定义与验收标准一律**回链**（`../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/`），不复制其正文；

* 知识引用一律链至 bundle（`../../awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/`）；

* 项目内出现的平台口径数字必须挂 F 编号并以链接给出出处；零无源数字。

### FR3 执行台账 tracker.md

* 结构对齐 [todo.md](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/todo.md) 的排期视图：关键时间锚点表 / 第 1 周（W1-1\~W1-6 + 9.29 Go/No-Go + 9.30 收官）/ 第 1 月（M1-1\~M1-6、O-6）/ 持续期周期节奏 / 退出降频触发器 / 发布前固定门 / 复核锚点；

* 每条 = 编号 + 动作短句 + **回链**（验收标准不复制）+ 勾选位与日期戳位（如 `[x] 2026-09-24`）；

* 顶部固定**勾选纪律**（完成勾选 + 日期戳、不删除条目、中断 ≥3 天回复核锚点）与**中断处置**说明（中断登记表位于 `records.md`）。

### FR4 记录表 records.md

四张表（模板 + 示例占位，显式标注"示例/待填"）：

1. 到账记录表（对齐 W1-6：日期 / 完成动作 / 盐粒页面显示）；
2. 周核对表（M1-2 回答计数、M1-3 想法计数，每周日）；
3. 周期复盘表（O-6：到账合计 → 按 F-059 折算 → 对照退出阈值 → 决策与理由）；
4. 发布自检留痕表（日期 / 内容主题 / 三问自检结论 / 边缘场景登记——对齐主路径 §五与风险文档口径）。

### FR5 AGENTS.md（智能体入口）

* 定位（主仓库直接跟踪的普通目录，非子模块）、文件地图与读写纪律（tracker/records 可写；`local/` 禁入库；docs 与 bundle 只读外链）、纪律传导（勾选纪律 / 三问自检 / O-5 规则快照 / flagged 与 2026-12-31 复核线 / 防画饼口径）、路由（知识 → bundle；定义 → docs；执行 → 本工作区）。

### FR6 区域索引登记

* `projects/README.md`「现有子项目」表与 `projects/AGENTS.md`「子项目路由表」各新增一行，措辞注明：**变现执行工作区（主仓库直接跟踪，非子模块；入口 =** **`monetize/zhihu-monetization/AGENTS.md`）**；

* 既有行零改动（diff 仅新增）；如两处表格体例需要，可同步补「可用资产索引」条目。

### FR7 验证与交付（V / C）

* 机械验证：相对链接可达（`check-links.py` 或手动等效）、零 `file:///`、UTF-8、frontmatter 字段、`git check-ignore` 隔离生效、无正文复制抽查、无个人数据残留；

* **V 门（F 后强制）**：独立子代理新上下文对抗审查（魔鬼代言人 / 新人 / 执行者可用性 / 未来时效四视角），≥5 条具体发现、≥2 条采纳修正，产出 `review.md`（独立审查清单，遵循 TRAE-spec-mode 命名，禁 `checklist.md`）；

* **C 门**：Conventional Commits 中文原子提交；先跑 docgen 看板刷新（`theme-dashboards`、`update-spec-readme`）并只纳入与本次相关的变化（无关重写则回退留痕）；不 push。

## 非功能性需求

| 编号   | 需求                                                                                                               |
| ---- | ---------------------------------------------------------------------------------------------------------------- |
| NFR1 | **可溯源**：项目文档 frontmatter 携 `source`；一切平台口径数字挂 F 编号；零编造                                                           |
| NFR2 | **时效管理**：`rule_snapshot` 登记规则时点；`flagged` + `stale_after: 2026-12-31` 传导至全部入口；期次变动先例（F-067）作为复核提示                |
| NFR3 | **治理合规**：Spec Mode 产物规范（spec.md + tasks.md + review\.md，禁 `checklist.md`）；kebab-case 文件名、中文正文；docs/ 与 bundle 零改动 |
| NFR4 | **提交纪律**：Conventional Commits 中文描述；原子提交；不 push                                                                   |
| NFR5 | **数据安全**：真实个人数据零入库（`local/` 隔离并验证生效）；零 `file:///`、零本机绝对路径                                                        |

## 约束、依赖与假设

**约束**

* docs 报告与 bundle 只读（bundle 处子模块内，禁本地修改；docs 本次零改动）；

* 项目不新增 F 编号、不做知识裁决；不重定义纪律（只引用）；

* 工作区为主仓库直接跟踪的普通目录（非子模块）；后续如需独立成仓，走子模块引入流程另行提案；

* 跨区相对路径口径固定：至 docs 用 `../../../docs/...`；至 bundle 用 `../../awesome-okf-xs/...`。

**依赖**

* 前置 Spec `create-zhihu-monetization-okf-wiki` 全部产物（已提交、未 push）；

* `.agents/scripts/check-links.py` 可用；docgen（`.agents/scripts/docgen.py`）可用性待实施时探测。

**假设**

* 用户按 `local/` 隔离策略填写真实数据；

* 2026-12-31 前平台规则无重大变动（否则按复核线提前复检）。

**待决问题**（实施阶段按规则自行决策并留痕）

1. 区域索引两处表格的措辞 → 按既有行体例适配，保持风格一致；
2. docgen 是否覆盖顶层 spec 目录 → 跑后看 diff 决定纳入或留痕跳过。

## 验收标准

### AC-1: 工作区文件齐备

* **Type**: `rule`

* **Given**: 实现完成

* **When**: 逐一检查目标路径

* **Then**: `README.md` / `AGENTS.md` / `tracker.md` / `records.md` / `.gitignore` / `local/README.md` 六项全部存在

* **Pass Condition**: 六项 Test-Path 全通过

* **Evidence**: 检查命令输出留痕

### AC-2: 链接全可达

* **Type**: `rule`

* **Given**: 项目文件落盘

* **When**: 运行 `check-links.py --path projects/monetize/zhihu-monetization`（或手动等效）

* **Then**: 全部相对链接可达；零 `](file:///`；跨区链接层级正确

* **Pass Condition**: 断链 0 条

* **Evidence**: 脚本输出或手动逐条核对记录

### AC-3: 单一事实来源

* **Type**: `rule`

* **Given**: `tracker.md` / `README.md` 完稿

* **When**: 抽查 3 条行动项 + 检查正文复制情况

* **Then**: 每条含回链且编号与 docs 源一致；不含源文档验收标准逐字整句

* **Pass Condition**: 抽查 3/3 通过且零逐字复制

* **Evidence**: 抽查记录（条目 → 回链 → 源核对）

### AC-4: 数据隔离生效

* **Type**: `rule`

* **Given**: `.gitignore` 与 `local/` 就位

* **When**: `git check-ignore` 验证 + 入库清单核对

* **Then**: `local/` 下数据文件全部命中忽略；`local/README.md` 正常入库；仓库零真实个人数据

* **Pass Condition**: 忽略规则命中且入库清单仅含机制说明

* **Evidence**: check-ignore 输出 + `git status` 清单

### AC-5: 时效与风险传导

* **Type**: `rule`

* **Given**: `README.md` 与 `AGENTS.md` 完稿

* **When**: 检索关键要素

* **Then**: 含 `rule_snapshot`、`status: flagged`、`stale_after: 2026-12-31`、防画饼口径（池 ≠ 个人收益）与复核提示

* **Pass Condition**: 五项要素在两文件中均可检索到

* **Evidence**: 字段与段落定位记录

### AC-6: 区域索引登记

* **Type**: `rule`

* **Given**: 索引更新完成

* **When**: 核对 `projects/README.md` 与 `projects/AGENTS.md`

* **Then**: 各新增一行且注明"非子模块"；`git diff` 仅含新增行

* **Pass Condition**: 两处新增存在且 diff 无既有行改动

* **Evidence**: `git diff` 输出

### AC-7: 溯源与事实纪律

* **Type**: `rule`

* **Given**: 全部项目文档完稿

* **When**: 检查 frontmatter 与数字

* **Then**: `source` 字段齐备；文档中一切平台口径数字挂 F 编号并给出链接；零无源数字

* **Pass Condition**: 数字 100% 有源

* **Evidence**: 数字清单 → F 编号映射记录

### AC-8: 执行者可用性（rubric）

* **Type**: `rubric`

* **Dimension**: 每日开工定位效率

* **Scale**: 1-5

* **Anchors**: 1 = 需跨三处以上查阅且无明确顺序；3 = 能找到当日动作但需多次跳转；5 = 入口页 5 分钟内直达当日动作并完成留痕

* **Pass Threshold**: >= 4

* **Evidence**: 新人视角审查记录（V 阶段）+ 入口页结构说明

### AC-9: V 门审查质量（rubric）

* **Type**: `rubric`

* **Dimension**: 对抗审查实质性与修复闭环

* **Scale**: 1-5

* **Anchors**: 1 = 客套式审查无具体发现；3 = 有发现但少于 5 条或未修复；5 = ≥5 条具体发现、≥2 条采纳修正且带修复证据

* **Pass Threshold**: >= 4

* **Evidence**: `review.md` 审查记录 + 修正 diff

### AC-10: 原子提交

* **Type**: `rule`

* **Given**: 审查通过

* **When**: 执行提交并核对

* **Then**: 提交单一职责（分笔或单笔）、信息为 Conventional Commits 中文、docs/ 与 bundle 零 diff、未 push

* **Pass Condition**: `git log` / `git status` 核对通过

* **Evidence**: 提交哈希与验证输出

