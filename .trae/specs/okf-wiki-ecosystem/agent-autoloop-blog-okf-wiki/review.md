---
type: review
title: "Agent-Autoloop 知识包对抗审查记录"
status: "completed"
date: "2026-11-06"
---

# V 阶段：对抗审查记录

> **审查时点**：2026-11-06，E 阶段 14 个文件全部落盘之后。
> **审查方法**：四视角（事实溯源与口径 / 结构与导航 / 读者与教程可信度 / 合规与版权）+ 机械门禁。
> **V 门结论**：**通过** —— 共 9 条具体意见，**8 条采纳并落实修正**，1 条经论证不采纳并保留理由；机械门禁本束全绿，全库级剩余项均可归属到非本束因素。

## 一、四视角对抗审查

### 视角 A：事实溯源与口径（3 条，全部采纳）

| # | 审查意见 | 处置 | 落实证据 |
|---|---------|------|---------|
| A-1 | `concepts/00-project-overview.md` 初稿把同组 bundle 写成 `../pi-agent-harness/index.md`：从 `concepts/` 出发一层上溯会指向 `agent-autoloop/pi-agent-harness/`，是死链；同篇另有 `/references/...`、`/examples/...` 等绝对路径式引用，虽是文本但违反「无绝对路径残留」。追查发现根因在规格 `spec.md` NFR-4 原写「bundle 内链接用 bundle-relative `/` 路径」，与 V-5 门禁及同组惯例冲突。 | ✅ 采纳 | ① 重写该篇：兄弟 bundle 统一 `../../<bundle>/index.md`，跨层引用统一 `../references/...` 与 `../examples/...`；② 同步修正 `spec.md` NFR-4 为「一律用相对路径，禁止 `/` 开头与 `file:///`」并注明修正理由。最终自检：0 断链、0 绝对路径残留；四个互链目标经 Glob 确认真实存在。 |
| A-2 | `references/verification.md` 判定 bundle 为 `status: stable`（Skill 的 `stable`/`flagged` 二分），而同组既有 bundle 惯用 `verified`。根 index 若只写其中之一，会与核验报告或分组惯例自相矛盾。 | ✅ 采纳 | 根 index 取 `stable`，并在「信任与生命周期」显式注明：沿用 `blog-article-to-okf-wiki` 的 `stable`/`flagged` 二分、核心声明无失败未触发 `flagged`、语义等价于本组资讯包的 `verified`。 |
| A-3 | 官方 README 的外部事件规则示例本包未取得逐字 JSON；若仿写一份会变成「虚构官方配置」，而这是全包最不能出现的问题。 | ✅ 采纳 | `examples/02-rules-and-receipts.md` 只逐字引用官方给出的**定时规则** JSON，外部事件规则改为 `when.source`/`types`/`to`/`cwd`/`skill`/`parallel` 字段说明表，并标注「教程整理，非官方 JSON 原文；需逐字可用时直接复制官方示例」。 |

### 视角 B：结构与导航（2 条，全部采纳）

| # | 审查意见 | 处置 | 落实证据 |
|---|---------|------|---------|
| B-1 | 根 index 的 toctree 引用 `log` 但 `log.md` 尚未生成；`ai-agent/index.md` 的 toctree 未收录新束，导致本束 13 个文件在全库扫描中全部被判「未收录(不可达)」。 | ✅ 采纳 | 补齐 `log.md`，在 `ai-agent/index.md` toctree 末尾加 `agent-autoloop/index`。局部 `check-toctrees.py <bundle>` 通过：引用有效、全部内容可达。 |
| B-2 | 新增 1 束后，5 级索引 + README + doc 首页的计数投影面必须全部 +1，否则 `check-bundles-index.py` / `check-asset-baseline.py` 会拦截。 | ✅ 采纳 | 同步 `ai-agent` 61→62、`frameworks` ai-agent 61→62 及类合计 94→95、`jishu/ai` frameworks 94→95 及域合计 286→287、`jishu` 286→287、`bundles` 技术域 522→523 / ai 286→287 / 全库 712→713，另同步 `README.md` badge 与域表、`doc/index.md` 两处。`check-bundles-index.py` 五面一致全绿；资产门禁的 3 项「规模数字矛盾」清零。 |

### 视角 C：读者与教程可信度（2 条，1 采纳 / 1 不采纳）

| # | 审查意见 | 处置 | 落实证据 |
|---|---------|------|---------|
| C-1 | 根入口的「60 秒快速开始」代码块与三篇实战篇容易被读成「已验证可跑通」，而本包生成环境是 Windows、官方 Windows 版待定，且官方多处标注「未测 / 未逐个跑过」。 | ✅ 采纳 | 根入口标题标注「官方命令，未在本机实测」并在下方接合规提示；三篇实战篇文首统一加「可复现性声明」；根入口单列 8 项已知边界；`examples/index.md` 再声明一次。 |
| C-2 | 建议删掉整个 `examples/`、退回纯概念骨架，理由是「本机没实测就不该给可照做步骤」。 | ❌ 不采纳 | 骨架判定两问皆为「是」：官方给出 Node 24 版本约束、`try`→`answer 1 2`→`status` 输入输出序列、`sim/` 与 `benchmark` 复现命令，满足设 `examples/` 的判据。正确做法是保留操作层 + 显式标注「未在本机实测 / 官方未逐个跑过」，而不是删除知识层。该理由已记录，避免后续维护者误删。 |

### 视角 D：合规与版权（2 条，全部采纳）

| # | 审查意见 | 处置 | 落实证据 |
|---|---------|------|---------|
| D-1 | 「一切皆插件」是博文作者对 DSH 设计思想的概括，官方 README 无此短语；若加引号当作 DSH 官方定位，属于引文误植。官方限定语（「整机断电没有单独测过」「我们还没有逐个跑过」）若在转述中被缩写为结论，同样构成失真。 | ✅ 采纳 | 全包按转述处理，`concepts/00` 与 `references/verification.md`「引文逐字核对表」双重标注；四机制篇与插件篇保留官方限定语原措辞；正文只做原创教程 + 事实转述 + 短语级引用，不逐字转录博文全文。 |
| D-2 | 官方「用量与合规说明」（高频自动化建议 API Key、订阅额度主要为人工交互设计、对外服务请用 API Key）博文完全未提；若按博文写定时巡检教程，会误导读者用订阅账号跑 cron。 | ✅ 采纳 | 落四处：`examples/01` 第 0 节动手前合规前置、`concepts/03` 第七节、`examples/03` 收尾检查清单、根入口「60 秒快速开始」下方提示；`references/verification.md` 第 10 项专列。 |

**统计**：9 条具体意见 → 8 条采纳并落实、1 条经论证不采纳（≥5 条且采纳 ≥2 条，V 门满足）。

## 二、机械门禁结果

| 检查项 | 命令 / 方式 | 结果 |
|--------|------------|------|
| 双份 F 编号集合比对 | 正则比对 `facts.md` ↔ `references/article-source.md` | ✅ 68 / 68 / 68 三者相等，F-001~F-068 连续无跳号；bundle 正文引用 0 越界 |
| UTF-8（本束） | `python scripts/check-utf8.py <bundle>` | ✅ 14 个文件均为有效 UTF-8 |
| UTF-8（全库） | `python scripts/check-utf8.py` | ✅ 12900 个文件通过 |
| 总索引五面一致 | `python scripts/check-bundles-index.py` | ✅ 9 域 / 64 组 / 713 束，frontmatter / 计数行 / 节标题 / 分组表 / toctree 全一致 |
| toctree（本束） | `python scripts/check-toctrees.py <bundle>` | ✅ 引用有效、全部内容文档可达 |
| toctree（全库） | `python scripts/check-toctrees.py` | ⚠️ 剩 10 处，全部指向 `sheke/industry/ai-comic-drama-opc-transition`（并行会话 WIP，缺 `index.md`）；**本束 0 问题** |
| 章节锚点（本束） | `python scripts/check-section-anchors.py <bundle>` | ✅ 扫描 14 文件，全部锚点可解析 |
| 章节锚点（全库） | 同上无参数 | ⚠️ 存量 6500+ 处既有噪声（多为纯中文标题跨文档锚点、`/concepts/...` 绝对路径），与本束无关 |
| 资产基线 | `python scripts/check-asset-baseline.py` | ✅ 3 项「规模数字矛盾」已清零；⚠️ 剩 1 项「行尾归一失效」（见第三节） |
| 相对链接 / 绝对路径 | 自建正则遍历 14 文件 | ✅ 0 断链、0 绝对路径残留、0 `file:///` |
| toctree 条目逐文件 | 自建解析 | ✅ 13 条目全部解析到真实 `.md` |
| frontmatter | 自建解析 | ✅ 10 个非保留文件全部含 `type`；`okf_version` 仅出现在 bundle 根 `index.md`；`index.md` / `log.md` 保留文件名无 frontmatter |

## 三、工具链限制与既有噪声归属（不得谎报）

1. **`invoke gates.*` 未运行**：`invoke --list` 在子项目目录失败，报 `PackageNotFoundError: No package metadata was found for invocations`（`tasks/__init__.py` → `tasks/docs.py` 导入 `invocations` 时包元数据缺失）。这是环境依赖问题，不是本束文件问题。
   → **等效验证**：直接执行 `scripts/check-utf8.py`、`check-bundles-index.py`、`check-toctrees.py`、`check-section-anchors.py`、`check-asset-baseline.py`（这些即 gates 底层实现，仅依赖 stdlib），结果见上表。**本报告不声称 `invoke gates.toctrees` / `gates.bundles` 通过**。
2. **资产门禁剩余 1 项**：`[行尾归一失效] 工作区归一后字节与 HEAD 残差超过容差`（残差随工作区未提交内容增长而浮动：本束交付前复跑为 `+190733`，早前一次为 `+177802`，差异来自另一并行会话持续写入 WIP 目录，故此处不写死单一数值）。脚本自身处置建议为「请先提交或 stash 工作区变更再复跑」。当前工作区含本束新增/修改文件**以及另一并行会话正在写入的 `ai-comic-drama-opc-transition/` 目录**；用户未要求 commit，且他束 WIP 不得代提交，故保留该项并如实登记，不以任何方式掩盖。
3. **`git status` 中 `?? doc/bundles/sheke/industry/ai-comic-drama-opc-transition/`** 为其他会话产物，本任务未读取、未修改、未代写其 `index.md`。全库 `check-toctrees` 的 10 处剩余问题均归属该目录；`check-section-anchors` 的存量噪声为仓库历史状态，与本束无关。

## 四、V 门结论

- **V 门通过**：对抗审查 9 条 / 采纳 8 条，机械门禁在本束范围全绿。
- **`status: stable` 维持**：10 大项 P0 核验 5 ✅ / 5 ⚠️ / 0 ❌，核心声明无失败，未触发 `flagged`。
- **交付边界**：教程示例未在本机实测；性能数字为作者单环境自测；整机断电未单独测过；Windows 版待定；插件支持范围分三档；`deliver-review` 仅博文单源——已在根入口 8 项已知边界与 `references/verification.md` 中登记。
- **复核计划（stale_after 2026-12-31 前）**：Windows 版进度（issue #17）、项目版本与 Release、性能数字与测试环境、插件实测范围、`deliver-review` 是否进入官方配置手册。
