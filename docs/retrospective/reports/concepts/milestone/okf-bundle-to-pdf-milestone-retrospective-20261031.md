---
id: okf-bundle-to-pdf-milestone-retrospective-20261031
title: OKF bundle → 带目录 PDF 导出流水线里程碑复盘报告（2026-10-31）
date: 2026-10-31
type: retrospective
source: 七概念方法论 R→I→E→V→A→C（场景1·里程碑复盘 + 场景4·知识沉淀，standard）
category: milestone
maturity: L1
tags: [方法论, 七概念, 里程碑复盘, OKF, PDF, Pandoc, Mermaid, Playwright, CDP, 产物断言]
---

# OKF bundle → 带目录 PDF 导出流水线里程碑复盘报告

> **周期**：2026-10-31 交付（PDF 导出 → 目录追问 → 目录补全）→ 同日复盘 | **方法**：七概念 R→I→E→V→A→C（场景1 里程碑复盘，depth=standard；含场景4 知识沉淀的 V 门）| **对象**：`laozi-culture-ecosystem` OKF bundle（HEAD `f0dfa2caf`）的 PDF 导出链路 | **数据**：PDF 结构实测（pypdf）+ 文件规模实测 + 工具版本实测

---

## 一、事实（R · 复盘 · 纯客观，无判断词）

### 1.1 任务与产出

| 编号 | 事实 | 证据 |
|------|------|------|
| F-01 | 用户第一条指令为「`.../laozi-culture-ecosystem` 帮我转为 pdf」 | 会话记录 |
| F-02 | 用户第二条指令为「为何没有目录」 | 会话记录 |
| F-03 | 用户在选项应答中选择「书签大纲 + 目录页（推荐）」（两种形式叠加） | AskUserQuestion 应答 |
| F-04 | 用户第三条指令为「Use Skill: seven-concepts-cmd 里程碑复盘+萃取可复盘skill」 | 会话记录 |
| F-05 | 用户在选项应答中选择萃取目标「OKF bundle → 带目录 PDF（推荐）」、落盘范围「全量落盘 + 原子提交（推荐）」 | AskUserQuestion 应答 |

### 1.2 bundle 规模（磁盘实测）

| 编号 | 事实 | 证据 |
|------|------|------|
| F-06 | bundle 路径为 `projects/awesome-okf-xs/doc/bundles/guoxue/laozi/laozi-culture-ecosystem`（位于 git submodule 内） | LS 实测 |
| F-07 | bundle 内含 `.md` 文件 23 个 | LS 实测 |
| F-08 | 23 个文件中 `index.md` 计 4 个：根 `index.md`、`concepts/index.md`、`examples/index.md`、`references/index.md` | LS 实测 |
| F-09 | 非 index 的正文 `.md` 计 19 个：`facts.md`、`insights.md`、`log.md` + `concepts/00`–`concepts/09`（10）+ `examples/01`–`examples/04`（4）+ `references/01`、`references/02`（2） | LS 实测 |
| F-10 | 非 index 正文合计 **124461 字符** | 字符计数实测 |
| F-11 | Mermaid 代码块 **12 个**，分布于 **12 个文件**（一文件一块） | 围栏扫描实测 |

### 1.3 PDF 规格（pypdf 实测）

| 编号 | 事实 | 证据 |
|------|------|------|
| F-12 | 产物路径为 `dist/laozi-culture-ecosystem.pdf` | 文件实测 |
| F-13 | 文件大小 **3357333 字节**（3.20 MB） | `os.path.getsize` |
| F-14 | 页数 **188** | `pypdf.PdfReader.pages` |
| F-15 | 书签大纲条目合计 **264** | `pypdf` outline 递归计数 |
| F-16 | outline 顶层列表长度 **40**（= 20 个顶层书签 + 20 个子列表），即顶层书签 **20 个** | `len(reader.outline)` |
| F-17 | 链接注释（`/Annots`）合计 **335** | 逐页 `pg.get('/Annots')` 计数 |
| F-18 | 第 1 页文本首行为「目 录」，其后为「快速导航」「快速开始」「知识包」 | 首页文本抽取 |

### 1.4 工具链（版本实测）

| 编号 | 事实 | 证据 |
|------|------|------|
| F-19 | `pandoc 3.8` 可用 | `pandoc --version` |
| F-20 | `playwright 1.60.0` 已安装 | `playwright --version` |
| F-21 | `playwright install chromium` 下载进度停在 0% | 终端输出 |
| F-22 | 改用 `p.chromium.launch(headless=True, channel="msedge")` 后打印成功（复用系统 Edge） | 运行日志 |
| F-23 | `page.pdf(outline=True)` 调用被接受且不抛异常，产物 PDF 不含 `/Outlines` | pypdf 结构检查 |
| F-24 | 改用 CDP `Page.printToPDF` 并设 `generateDocumentOutline: True` 后，264 条大纲落地 | pypdf 结构检查 |
| F-25 | CDP 路径参数以英寸为单位：`paperWidth 8.27`、`paperHeight 11.69`、四边 `margin 0.7874` | 脚本常量 |
| F-26 | `h2` 未注入 `id` 时，页内目录条目点击不跳转 | 浏览器实测 |
| F-27 | 为 `h1`/`h2` 注入 `{#doc-<slug>}`、`{#doc-<slug>-hN}` 后跳转生效 | 浏览器实测 |
| F-28 | 本次核验改用程序化断言（`pypdf` 抽文本/outline/Annots + `pypdfium2` 墨迹分析），未依赖读图 | 核验脚本 |

### 1.5 仓库状态与资产盘点（实测）

| 编号 | 事实 | 证据 |
|------|------|------|
| F-29 | 主仓 HEAD 为 `f0dfa2caf docs(specs): 新增老子文化生态圈知识包规格并前移 awesome-okf-xs 子模块指针` | `git log` |
| F-30 | 子模块 `projects/awesome-okf-xs` 近期提交含 `2a718b44 docs(bundles): 新增老子文化生态圈 OKF 知识包` | 子模块 `git log` |
| F-31 | 仓库脚本 `.agents/scripts/export-md-to-pdf.py` 存在，支持单文件 MD→PDF，参数含 `--css/--wait-ms/--keep-html/--no-mermaid`，不含 bundle 合并与目录能力 | 源文件实测 |
| F-32 | `.agents/skills/` 下既有完整 Skill 47 个、命令集门面 11 个，其中无任何「bundle → 带目录 PDF」Skill | README 与 registry 实测 |
| F-33 | 最近邻 Skill 为 `markdown-first-deliverable-drafting`，覆盖「对话方案→Markdown→单文件 PDF/Word」，不含 bundle 合并、子 index 剔除、链接降级、h1/h2 锚点注入、Pandoc `--toc`、CDP 书签大纲 | SKILL.md 实测 |
| F-34 | `dist/` 被根 `.gitignore` 忽略，PDF 不入库 | `.gitignore` 实测 |
| F-35 | 本次中间脚本（bundle 合并脚本、CSS 附加样式、Edge 导出脚本等）位于系统临时目录，会话结束前已被删除 | 临时目录实测 |

### 1.6 口径偏差记录

| 编号 | 事实 | 证据 |
|------|------|------|
| F-36 | 早期会话摘要记载「20 篇 / 117706 字符」，磁盘实测为「19 篇非 index 正文 / 124461 字符 / 共 23 个 `.md`（含 4 个 index）」 | 摘要文本 vs 磁盘实测 |

> **为什么单列一节记录口径偏差？** R 阶段的质量门（G1 第七项）要求「关键数据完整无遗漏」。若沿用摘要里的旧数字，后续所有「规模」「覆盖率」断言都建立在错误基数上；此偏差在本次已按磁盘实测修正，故显式留痕以便复现。

---

## 二、洞察（I · 3 条四元组）

### I-01 「选项被接受」不等于「选项生效」——静默吞参比报错更危险

- **陈述**：`page.pdf(outline=True)` 调用返回成功、不抛异常，但产物 PDF 结构中不存在 `/Outlines`；换成 CDP `Page.printToPDF(generateDocumentOutline=True)` 后 264 条大纲才落地。API「接受参数」与「参数生效」是两件事。
- **证据**：F-23、F-24（同一次打印任务，唯一变量为调用通道；结构差异由 pypdf 直接读出）。
- **反常识**：直觉以「函数没报错」推断「功能已生效」；实测形态是「参数被静默丢弃」，没有任何错误码可依据。
- **行动**：任何「选项开关」类能力，验收断言必须落在**产物结构**上（如 outline/Annots 计数），禁止以「调用未抛异常」判定通过。

### I-02 「运行时通道」与「二进制来源」是两件事——依赖缺失不必终止任务

- **陈述**：Chromium 下载停在 0% 时，改用 `channel="msedge"` 复用系统已装 Edge，整条渲染链路继续跑通。
- **证据**：F-21、F-22。
- **反常识**：默认心智是「Playwright 必须先 `install chromium`」；实际上 Playwright 是驱动层，浏览器二进制可来自系统既有安装（Windows 自带 Edge）。
- **行动**：转换/渲染链设计为「可替换运行时通道」，把外部下载依赖降级为可选；下载类阻塞不作为任务终止条件。

### I-03 目录是两层结构，页内目录与书签大纲互补且各有前置条件

- **陈述**：页内目录（Pandoc `--toc`）依赖标题锚点存在；书签大纲（`/Outlines`）依赖打印通道支持；两者不能互相替代。`h2` 缺 `id` 时页内目录条目点击无效。
- **证据**：F-17、F-18、F-26、F-27、F-24。
- **反常识**：常见假设是「加了 `--toc` 就有目录」「有目录就够了」；实测是「页内目录需要锚点前置」「阅读器侧边栏需要 `/Outlines`」两套独立前置。
- **行动**：目录交付默认双层（页内 TOC + 书签大纲）；把 h1/h2 锚点注入固化为导出前置步骤，而非可选美化。

---

## 三、萃取（E · 可复用模式）

### 3.1 模式：**双层目录导出法**

| 项 | 内容 |
|----|------|
| 模式 ID | `okf-bundle-dual-toc-export` |
| 模式名 | 双层目录导出法（7 字） |
| 成熟度 | L1（单案例，待第二次验证升级） |
| 适用域 | 多文档集合 → 单文件长文档交付（PDF/EPUB）；不限于 OKF bundle |

**触发条件（三者同时成立）**

1. 输入是**多篇 Markdown**（目录树形态，含分层索引文件），需要合并为单一可阅读产物；
2. 产物需要**可导航**（跨文档跳转 + 阅读器侧边栏）；
3. 内容含**需运行时渲染**的资源（Mermaid / KaTeX / 图表），或运行环境缺少默认渲染依赖。

**核心步骤（7 步，顺序不可颠倒）**

| 步 | 动作 | 关键约束 |
|----|------|---------|
| 1 | 枚举 bundle 文件清单，剔除**嵌套 `index.md`**（保留根 index 作前言）| 禁止凭记忆构造清单；先递归枚举再核对 |
| 2 | 相对链接**降级**为纯文本（合并后跨文件相对路径失效）| 降级而非删除，保留可读标题 |
| 3 | 为每个文件注入**文档分节锚点**：`h1` → `{#doc-<slug>}`，`h2` → `{#doc-<slug>-hN}` | 锚点注入必须跳过代码围栏内的 `#` |
| 4 | Pandoc 合并转换，开启 `--toc --toc-depth=2` 生成**页内目录** | `--toc` 生效前提是第 3 步锚点已存在 |
| 5 | 浏览器端渲染运行时资源（Mermaid CDN → SVG），等待「所有 `.mermaid` 均含 `svg`」 | 等待条件必须可判定，禁止固定睡眠兜底 |
| 6 | 打印 PDF 时走 **CDP `Page.printToPDF` + `generateDocumentOutline: True`** 生成**书签大纲** | 参数单位为英寸；路径参数与 `format` 混用会冲突 |
| 7 | **程序化验收**：断言页数 / outline 条目 / Annots 计数 / 首页含「目录」 | 禁止以「命令退出码 0」替代结构断言 |

**反模式（≥3 条）**

| 编号 | 反模式 | 后果 |
|------|--------|------|
| AP-1 | 以「调用未报错」判定目录已生成 | 静默吞参，交付物缺 `/Outlines` 而自查全绿 |
| AP-2 | 只做页内目录，或只做书签大纲 | 缺一即「跨文档跳不动」或「侧边栏无导航」 |
| AP-3 | 先合并后补锚点，或跳过锚点直接 `--toc` | 页内目录条目全部不可点击 |
| AP-4 | 依赖下载（浏览器二进制/字体）阻塞时直接判任务失败 | 存在系统既有通道（如 Edge）时属可绕过的伪阻塞 |
| AP-5 | 凭会话摘要中的旧数字（篇数/字符数）做规模断言 | 基数错误，覆盖率/完整性结论失真 |

**迁移验证（≥1 个跨领域）**

- 同域：任意 OKF bundle、Sphinx 多页导出、技术手册合集（结构同型，直接复用 7 步）。
- 跨域：**法律/合规卷宗汇编**、**课程讲义合集**、**API 文档离线包**——共同结构均为「多文件 + 分层索引 + 需运行时渲染 + 需双层导航」，7 步逐条对应；差异仅在运行时资源的渲染器替换。

### 3.2 Skill 产物

模式落地为 Skill `okf-bundle-to-pdf`（`.agents/skills/okf-bundle-to-pdf/`），把 7 步固化为 `scripts/build_bundle_pdf.py`，并按仓库规范完成四处登记（详见 §五 A-1/A-2）。

**边界划清**（避免与最近邻重叠）：

| Skill | 覆盖 | 不覆盖 |
|-------|------|--------|
| `markdown-first-deliverable-drafting` | 对话方案 → Markdown 草稿 → 确认门 → 单文件 PDF/Word | bundle 合并、子 index 剔除、锚点注入、双层目录 |
| `okf-bundle-to-pdf`（本 Skill） | 多文档 bundle → 单文件**双层目录** PDF | 内容创作、草稿确认门、Word/DOCX 输出 |

---

## 四、对抗审查（V · 4 视角）

| 视角 | 攻击意见 | 处置 |
|------|---------|------|
| 魔鬼代言人 | V-1：所谓「新模式」不过是 Pandoc + Playwright 的常规用法拼接，不构成可迁移模式 | **部分采纳**：降级为 L1（单案例），并写死升级门槛（第二次非同 bundle 验证）；保留模式成立的核心判据——「双层目录各有独立前置条件」是可迁移约束而非操作技巧 |
| 魔鬼代言人 | V-2：`outline=True` 失效可能只是本次 Playwright/Edge 组合的偶然，写进 Skill 会过时 | **采纳**：SKILL.md 中该条以「实测环境（playwright 1.60.0 + msedge）」标注适用边界，并要求 CDP 路径为默认、`page.pdf` 路径为可选降级 |
| 新人 | V-3：新人不清楚「子 index 剔除」的判定标准 | **采纳**：模式步骤 1 明确「剔除嵌套 `index.md`、保留根 `index.md`」，并在 Skill 输入参数中提供显式排除开关 |
| 新人 | V-4：7 步里第 5 步「等待条件」写得抽象，新人会写 `sleep` | **采纳**：Skill 固化为可判定断言（所有 `.mermaid` 均含 `svg`），禁止固定睡眠 |
| 老板 | V-5：这份复盘对业务有什么可度量收益 | **部分采纳**：报告补入 A-3（下次同类导出目标：从「先出无目录版再返工」改为「一次产出带双层目录的版本」），收益可度量为「返工轮次 1 → 0」 |
| 老板 | V-6：投入做 Skill 是否值得，直接用仓库既有 `export-md-to-pdf.py` 不就够了 | **采纳**：§1.5 F-31/F-33 明确既有脚本不含 bundle 合并与目录，属真实能力缺口；Skill 复用既有脚本的第 1/4/5 步实现思路，不重复造轮子 |
| 未来 | V-7：环境变更（Playwright 升级、CDN 变更）会让 Skill 静默失效 | **采纳**：Skill 增加程序化验收步骤（第 7 步）与 §11 错误码，使环境漂移在验收期暴露而非交付后 |
| 未来 | V-8：`dist/` 被 gitignore，PDF 不入库，Skill 的可复现性只依赖输入 bundle | **部分采纳**：报告 F-34 已记录；Skill 增加「输入 bundle 必须存在于受版本控制的位置」的前置检查，产物不入库不影响复现 |

**采纳统计**：8 条意见，完全采纳 6 条、部分采纳 2 条、否决 0 条（满足 V 门「意见 ≥5 条、至少采纳 2 条、4 视角全覆盖」）。

---

## 五、行动项（A · 原子化）

| 编号 | 行动项 | 交付物 | 验收标准 | 状态 |
|------|--------|--------|---------|------|
| A-1 | 新建 Skill `okf-bundle-to-pdf` | `.agents/skills/okf-bundle-to-pdf/SKILL.md` + `scripts/build_bundle_pdf.py` | `check-skill-quality.py --path` → 100/100、退出码 0 | 本报告同批完成 |
| A-2 | 四处登记新 Skill | README 表行与计数 47→48 / `capability-registry/02-skills.md` 表行与计数 47→48 / `CHANGELOG.md` 新条目 / `.meta/toml/.agents/skills/okf-bundle-to-pdf/SKILL.toml` 五字段镜像 | `check-links.py --paths ... --check-frontmatter-paths` → 本次引入 0 断链 | 本报告同批完成 |
| A-3 | 下次同类导出改走 Skill 主路径 | Skill 方案一 | 产出物**首次即含**页内目录 + 书签大纲，返工轮次 1 → 0 | 待下次同类任务验证 |
| A-4 | 模式 L1 → L2 升级门槛 | 本模式二次验证案例 | 第二个**非同 bundle** 案例复用 7 步并记录差异 | 待触发 |
| A-5 | 环境边界复测 | Skill §11 错误码表 | Playwright 升版或 CDN 变更后复跑验收，记录是否需更新默认通道 | 待触发 |

---

## 六、质量门记录

| 门 | 判据 | 结论 |
|----|------|------|
| G1（事实） | 事实 ≥20 条、无因果推断词、同族口径一致 | **通过**：F-01–F-36 共 36 条；口径偏差已在 F-36 显式修正 |
| G2（洞察） | 每条含 陈述 / 证据 / 反常识 / 行动 四元组 | **通过**：I-01–I-03 四元组完整 |
| G3（萃取） | 模式名 4–8 字、含触发条件 + 核心步骤 + ≥3 反模式 + ≥1 跨领域迁移 | **通过**：模式名 7 字、7 步、5 条反模式、2 类迁移验证 |
| G4（行动） | 行动项单一职责、可独立验证、有验收标准 | **通过**：A-1–A-5 各含交付物与验收标准 |
| V 门 | 4 视角全覆盖、意见 ≥5 条、至少采纳 2 条 | **通过**：8 条意见、4 视角、采纳 6 条 |

---

## 附：本次链路与产出的边界（据实记录）

- 本报告与 Skill 为**新增**产出，未修改 bundle 内任何文档、未修改既有两个 Skill（含最近邻）。
- PDF 产物位于 `dist/`（被 `.gitignore` 忽略），未入库、未移动。
- 中间脚本（bundle 合并、CSS 附加、Edge 导出等）位于系统临时目录，会话结束前已删除，未入库。
- 子模块 `projects/awesome-okf-xs` 内的 bundle 指针与内容在本次会话前已由 `2a718b44` / `f0dfa2caf` 提交；本报告不触碰子模块。
