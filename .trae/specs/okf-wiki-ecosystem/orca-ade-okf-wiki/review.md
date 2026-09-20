---
status: "reviewed"
version: "1.0"
---

# 独立审查清单（review.md）

> 审查对象：`jishu/ai/orca-ade` bundle + spec 三件套。审查方式：**与非生成者视角独立复核**（V 阶段对抗审查）。
> 判定词：`rule`（硬规则，违反即阻断）/ `rubric`（质量评分项，可标注差距）。
> 审查日：2026-09-20。结论：**通过**，其中 G5 与 S7 按实际语境偏离字面表述并已注记（不构成阻断）。

## 一、事实溯源（rule）

| # | 检查项 | 判定 | 结果 |
|---|---|---|---|
| R1 | 正文所有数字/版本号/命令/组织名均可回溯到 `facts.md` 的 F 编号 | rule | ☑ F 引用密度：concepts 47/59/45 处、examples 57/77 处、references 138/83 处；抽查 `stablyai/orca/orca`（F-043/F-070）、v1.4.205（F-067）、66,453（F-061）、29/27/35（F-065/F-066）均命中 |
| R2 | 双份登记编号集合一致且连续（facts.md ↔ article-source.md），跳号有注记 | rule | ☑ 正则提取两侧均为 F-001~F-103，Compare-Object 集合相等，1..103 无缺号 |
| R3 | 作者观点与事实分层：F-006/F-019/F-028/F-051/F-055~F-057 在正文标注"作者观点" | rule | ☑ 正文"作者观点"标注共 11 处，覆盖全部 7 条 P2 观点 |
| R4 | 无独立出处的数字标注"仅博文单源"，未伪升级为"官方数据" | rule | ☑ 单源标注 10 处；F-101 第三方质疑与"README 未含采用数据"一并保留 |
| R5 | 未编造 facts.md 之外的任何 URL、版本号或引文 | rule | ☑ 抽查正文外链均可在 facts.md 找到同源登记（仓库 F-058、官网 F-069、App Store F-094、YC F-072、Homebrew tap F-070） |
| R6 | 引文为逐字引用（带引号处均核对过官方原文），意译处不加引号 | rubric | ☑ 官方文档引文以英文原文登记于 F-078~F-098，正文引号处与之一致；examples 顶部已声明"引号内容为官方文档原文措辞，非实测输出" |

## 二、勘误落实（rule）

| # | 检查项 | 判定 | 结果 |
|---|---|---|---|
| E1 | 博文域名硬错误（`onnorca.dev`）未在正文出现，统一为 `onorca.dev`，并标注源文口径 | rule | ☑ 10 处 `onnorca.dev` **逐处确认全部位于勘误/核验语境**（index 先读提示、log E-1、examples/00 坑位提醒、article-source 与 verification 核验记录）；运营性表述全部用 `onorca.dev` |
| E2 | "无需注册账号"以双口径呈现：桌面端 no account system / 移动端 Relay 需登录 | rule | ☑ index 先读提示第 2 条 + concepts/00 账号口径矛盾节 + verification E-2 |
| E3 | 星标数以"博文时点口径 + 核验日实测 + 第三方统计"三口径呈现 | rule | ☑ 6.7 万（发文时点）/ 66,453（核验日 GitHub API）/ 70.5K–71.4K（第三方）三口径并列 |
| E4 | "ADE" 全称标注为第三方外推，官方仅用缩写 | rule | ☑ concepts/00 与 index 已知边界均标注"全称无官方出处"（E-4） |
| E5 | 支持 Agent 数量呈现三处官方口径差异（29/27/35），不取单一数字 | rule | ☑ concepts/02 与 index 已知边界并列 README 29 / 官网 27 / docs 表 35 |
| E6 | Android 分发补充"无 Google Play 官方条目 + 版本号口径不一致" | rubric | ☑ concepts/00 与 examples/01 均补充 0.0.48 与 0.0.50 双版本口径 |
| E7 | 安装包形态按核验值呈现（macOS dmg / Windows exe / Linux AppImage） | rule | ☑ examples/00 按 F-068 列出 dmg / exe / AppImage（另注 .deb/.rpm） |

## 三、结构规范（rule）

| # | 检查项 | 判定 | 结果 |
|---|---|---|---|
| S1 | bundle 目录结构符合 OKF v0.2：index + log + concepts/ + examples/ + references/ | rule | ☑ 共 12 个文件，三层目录齐备 |
| S2 | 每个 `index.md` 均含 `{toctree}` 块（含根 index 与三个子目录 index） | rule | ☑ 4 个 index.md 均含 `{toctree}` 块 |
| S3 | 子目录 index toctree 收录本目录全部内容文件，条目按文件名排序 | rule | ☑ concepts 3 条 / examples 2 条 / references 2 条，与目录实际文件一一对应且有序 |
| S4 | frontmatter 十项齐备：okf_version/type/title/description/tags/generated/verified/status/stale_after/sources | rule | ☑ 8 个带 frontmatter 的文档全部齐备（**V 中补齐 verification.md 缺失的 `verified`**）；4 个 index.md 与 log.md 按本库既有约定不设 frontmatter |
| S5 | sources 同时含博文 URL 与核验权威 URL（GitHub/官网/Homebrew/YC） | rule | ☑ 根 index sources 含博文 + GitHub 仓库 + GitHub API + 官网 + Homebrew tap + YC + App Store 共 8 条 |
| S6 | 计数排除 `:` 指令行（`:hidden:` / `:maxdepth:`） | rule | ☑ 条目数为 3/2/2 与 4 个顶层条目，未计入指令行 |
| S7 | 相对路径引用：同 bundle 内 `/concepts/xx.md`，兄弟 bundle `../<name>/index.md` | rule | ⚠️ **按语境偏离**：本项字面写法仅在 bundle 根目录成立；`concepts/`、`examples/` 下的束间链接需多一层（`../../<name>/index.md`）。**V 中据此修复 concepts/02 三条层级错误**；束内引用沿用分组既有 `/concepts/...` 根绝对形式（同分组 704 处先例） |
| S8 | `file:///` 绝对路径零出现；家目录绝对路径零残留 | rule | ☑ 全束 0 命中（`C:\Users`、`/Users/`、`D:\spaces` 亦为 0） |

## 四、读者可用性（rubric）

| # | 检查项 | 判定 | 结果 |
|---|---|---|---|
| U1 | index.md 提供"本文概要 + 文档结构 + 主题关联 + 已知边界"四段，读者可 30 秒定位 | rubric | ☑ 四段齐备，另加"三条先读提示"置顶 |
| U2 | examples 顶部显著标注"命令源自官方文档核验、非博文实测、未真机执行" | rule | ☑ examples/index.md 顶部引用块 + 两个正文文档各自复述 |
| U3 | concepts 首篇回答"这是什么/谁做的/凭什么信"，符合事实层定位 | rubric | ☑ 00 篇含一句话定位、厂商 YC W22/MIT、星标与版本三方数字 |
| U4 | 与同分组 bundle（echobird / loopx / codex-agent-workflow-practices）的差异与分工有明说 | rubric | ☑ concepts/02 逐条对比分工；index 主题关联段另加 todesk-ai / planning-with-files / context-optimization |
| U5 | 每篇文档含 Mermaid 或表格等结构化呈现（非纯段落） | rubric | ☑ 全部内容文档含表格（最少 7 行）；concepts/00、concepts/01、examples/01 另含 Mermaid |

## 五、时效边界（rule）

| # | 检查项 | 判定 | 结果 |
|---|---|---|---|
| T1 | `stale_after` 已设定且与该产品周级迭代节奏匹配（建议 2026-11-30） | rule | ☑ 全束统一 `stale_after: "2026-11-30"` |
| T2 | index.md 顶部有时效提示块（版本 v1.4.205、星标变动、官方口径不一） | rule | ☑ "三条先读提示"第 3 条含版本、星标、stale_after |
| T3 | 已知边界段承认"未真机实测""官方文档自相矛盾项未获澄清""星标时点快照不可还原" | rule | ☑ 已知边界 9 条含全部三项，并补建仓/YC 时序、FAQ 未取到、App Store 主体对应关系等未覆盖项 |

## 六、机械门禁（rule）

| # | 检查项 | 判定 | 结果 |
|---|---|---|---|
| G1 | UTF-8 严格 roundtrip 全部新增/修改 .md 通过 | rule | ☑ `scripts/check-utf8.py` 通过：10434 个文件均为有效 UTF-8 |
| G2 | 三级 toctree 条目逐一 Test-Path 存在 | rule | ☑ `scripts/check-toctrees.py` 本束 12 文件零问题（脚本另报 4 处属他会话 WIP `jishu/ai/jev`，未代为修改） |
| G3 | `jishu/ai/index.md` 束数 = toctree 条目数 = 实际 bundle 目录数 | rule | ☑ 导航表加 1 行、toctree 加 1 条，与目录树一致（总索引脚本递归口径对账通过） |
| G4 | `bundles/index.md` total_bundles / jishu / ai 三处计数与目录树一致 | rule | ☑ 556→557、423→424（节标题 + mermaid 节点）、204→205；`check-bundles-index.py` 报"9 域 / 59 组 / 557 束 五面一致" |
| G5 | grep 全库无 `onnorca.dev` 残留 | rule | ⚠️ **按语境偏离**：字面不成立——全库仍有 10 处 `onnorca.dev`，但**逐处确认全部位于勘误/核验语境**（E1 要求"标注源文口径"本身就需要该字符串），运营性表述零残留，博文硬错误未被照搬 |
| G6 | 若未执行 `invoke gates.*`，已在 log.md 注明采用手动等效验证（禁止谎报通过） | rule | ☑ 未走 invoke 通道，log.md 已注明"直接运行仓库 stdlib 脚本"并列出三项脚本与结果 |

## 七、提交规范（rule）

| # | 检查项 | 判定 | 结果 |
|---|---|---|---|
| C1 | 子模块先提交，主仓库后提交 spec，最后更新子模块指针 | rule | ☑ 子模块 `projects/awesome-okf-xs` 先提交 bundle 12 文件 + `jishu/ai/index.md` + `bundles/index.md`；主仓库随后提交 spec 四文件并携带子模块指针更新 |
| C2 | 提交经 `git-commit-utf8.py` 且显式列出全部文件（未传目录参数） | rule | ☑ 两次提交均使用 `python .agents\scripts\git-commit-utf8.py` 并显式列全文件路径 |
| C3 | Conventional Commits 格式、中文主体；未 push | rule | ☑ `docs(okf-wiki): ...` / `docs(okf-wiki-ecosystem): ...`，中文主体；未执行 push |