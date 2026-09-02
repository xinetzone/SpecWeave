---
type: V-Review-Report
title: "tcm 域视觉资产 V 阶段对抗审查报告（17 Mermaid + 8 配图）"
created: 2026-09-02
reviewer: V 阶段独立对抗审查（黑盒验证）
target: projects/awesome-okf-xs/doc/bundles/yixue/tcm/
source: ".trae/specs/standards-tools/add-tcm-bundle-visual-assets/{spec.md,visual-plan.md,checklist.md}"
verdict: 全部通过（视觉资产本体）；3 项 C 阶段收尾待施工方补齐
---

# tcm 域视觉资产 — V 阶段独立对抗审查报告

## 总结论

**视觉资产本体：全部通过（PASS）。** 17 张 Mermaid 与 8 张配图在数量、配额、六规则合规、事实一致性、边界合规、Sphinx 构建、质量门、产物落盘八个维度全部验证通过，未发现 P0/P1 问题。

**流程收尾：3 项 P2 待办**（不影响资产本体验收）：CP-21 changelog v1.2.0 条目、CP-22 五束 log.md 登记、CP-24 看板状态更新均未实施，属施工方 C 阶段收尾动作。另记录 1 项域外观察（yishu/vocal 并行会话的既有构建告警，与本次改动无关）。

---

## A. 程序化合规扫描

### A1 Mermaid 块清点与六规则合规 — PASS

- **数量**：tcm 域 `.md` 中 ```mermaid 块共 **17 个**（与 visual-plan.md M1–M17 一一对应）；waijing/concepts/01 原有 ASCII 时间线代码块非 mermaid，未误计。
- **合规扫描**：独立脚本（`.temp/tcm-mermaid-scan.py`，17 块逐块机检）结果：
  - 块内无空行、无字面 `\n` ✅
  - 中文/特殊字符标签全部双引号包裹，无 `X[中文` 裸标签形态 ✅
  - 无 `数字. ` / `- ` 列表触发格式 ✅
  - 换行均为 `<br/>` ✅
  - subgraph `ID ["标题"]` 与 `end` 配对正确 ✅
  - 边标签均为 `-->|"…"|` 形态；timeline 事件引号成对、事件内无 ASCII 双引号 ✅
- **构建侧佐证**：Sphinx 构建对 17 块零告警（见 C2），产物中 17 个 `<pre class="mermaid">` 节点分布与计划完全一致（见 C3）。

### A2 图片引用清点 — PASS

- Markdown 中 `/_static/bundles/yixue/tcm/...jpg` 引用共 **8 处**，全部 `.jpg`（无 .png 死链）。
- 8 个目标文件在 `doc/_static/bundles/yixue/tcm/` 下全部真实存在（Glob 核对），单张 333KB–555KB，均 <2MB。
- 构建产物侧二次佐证：8 张 jpg 均被 Sphinx 复制进 `_images/`，字节大小与源文件逐一相同（见 C3）。

### A3 配额 — PASS

- `references/` 目录：零 mermaid 块、零图片引用 ✅
- 单文件视觉资产（mermaid+图片）≤2：最高为 `tcm-overview/concepts/01-four-classics-guide.md`（M2+M3=2），无超标 ✅
- 分布统计（与清单一致）：

| 束 | Mermaid | 配图（束内） |
|---|---|---|
| 域级 index | — | I1（1） |
| tcm-overview | M1–M4（4） | I2 束封面、I7 章节图（2） |
| nanjing | M5–M7（3） | I3（1） |
| shanghan-zabinglun | M8–M11（4） | I4（1） |
| shennong-bencaojing | M12–M14（3） | I5（1） |
| waijing-weiyan | M15–M17（3） | I6 束封面、I8 章节图（2） |
| **合计** | **17** | **8** |

### A4 变更范围 — PASS

`git status --short`（cwd=projects/awesome-okf-xs）核对：
- 修改：tcm 域 24 个 `.md`（域 index + 5 束 index + 18 个 concepts/examples），diff 为**纯插入**，无正文删除/改写；
- 新增：8 个 jpg（`doc/_static/bundles/yixue/tcm/` 下）；
- **无** `references/`、`log.md`、`changelog.md`、`conf.py`、其他束/域文件改动；
- 审查期间构建产物写入子模块 `_build/`，经 `git check-ignore` 确认已被 gitignore，不污染变更集。

---

## B. 事实对抗抽查

### B1–B6 六大风险点 — 全部 PASS

| 编号 | 图 | 核对结论 |
|---|---|---|
| B1 | M15（waijing/concepts/01） | 成书系年作"约1689年前后"且含"无定论"语义；块内**无 1697/1698** ✅ |
| B2 | M13（bencaojing/concepts/02） | 理论数 120/120/125=365 与实计 146/114/103=363 分属两节点、虚线连接、"不作弥合"；"佐使"用字正确 ✅ |
| B3 | M9（shanghan/concepts/02） | 四版本年代 1599 / 1144 / 1060·1937 / 1934·1939 与正文对照表逐字一致；四系并列；无"真本/祖本/善本"裁决性措辞（仅保留"不作单一真本裁决"否定性声明）✅ |
| B4 | M5（nanjing/concepts/01） | 六部难次 22+7+18+14+7+13=81 验算正确；"共三卷（一说五卷）"两说并存 ✅ |
| B5 | M17（waijing/concepts/06） | 命门三章篇号 36/37/39（**第38篇未入图**）；SUWEN 节点含"原指心"、边标签含"翻转" ✅ |
| B6 | M10（shanghan/concepts/03） | 条数 178/84/10/8/45/56 + 霍乱10 + 劳复7，合计 398 验算正确；提纲条号 1/180/263/273/281/326 与正文一致 ✅ |

### B7 其余 11 图抽查 — PASS

M1–M4、M6–M8、M11、M12、M14、M16 各抽 2–3 个关键事实（人名/年代/数字/书名）与同束正文比对：注家谱系（吕广/杨玄操/滑寿/徐大椿）、四辑本（卢复/孙星衍/顾观光/森立之）、金匮 25 篇存目、9卷81篇结构、颠倒顺逆等要点均可在正文定位依据，无正文无据内容、无数字不符、无武断裁决。诸说并列处（难经成书五说、伤寒四版本、本草四辑本、外经真伪两派）图表均保持并列。

### B8 边界审查 — PASS

- 8 张配图均为意象类（书案古籍/山水/草木写意/卷轴/溪流），无文字、无人物、无人体/经络/穴位/脏腑/舌脉/药草鉴真元素；
- 风格统一（水墨淡彩、暖纸色基调），横向构图；
- alt 文本与周边文字无医学诊断暗示；git diff 纯插入证明各束既有免责声明未被触碰或削弱。

---

## C. Sphinx 全量构建

### C1 构建方式探测 — PASS

- 构建命令：`invoke build` ≡ `sphinx-build -E -b html doc _build/html`（tasks/docs.py + tasks/__init__.py：source=`doc`、target=`_build/html`）。
- `doc/conf.py`：`myst_parser` + `myst_fence_as_directive = ["mermaid"]` 将 ```mermaid 栅栏映射为 sphinxcontrib-mermaid 指令；mermaid 11.4.1 CDN 运行时 JS 渲染，零构建期渲染依赖。
- 环境实测：Sphinx 8.2.3 / myst-parser 5.1.0 / sphinxcontrib-mermaid 8.2.3 均可用。

### C2 构建执行 — PASS（tcm 域零错误零告警）

- **全量 reading 阶段**：7504 个源文件 100% 读取完成（内容/语法类告警均在此阶段暴露）。严格过滤 `: WARNING: / : ERROR:` 后全库仅 2 条，**均不在 tcm 域**：
  - `doc/bundles/yishu/vocal/meitong-yanyin-pedagogy/index.md:3: WARNING: Document headings start at H2, not H1 [myst.header]`
  - 同文件 `:1: ERROR: Document or section may not begin with a transition. [docutils]`
  - （并行会话声乐束文件，属既有/他方问题，与本次 tcm 改动无关，见问题清单 P2-4）
- **tcm 定向构建**：91 个 tcm 页面子集构建 `build succeeded, 3 warnings`——2 条即上述 yishu/vocal 告警（reading 期全库扫描所致），1 条为子集构建特有的 search index 不完整提示（非内容问题）；**tcm 域页面 0 错误、0 告警**。
- 说明（环境限制，不影响结论）：全站点 HTML writing 阶段（7504 页，本机预计约 5 小时）两次被任务宿主生命周期中断，未在会话内跑完全程；但内容告警只在 reading 阶段产生（已 100% 完成），tcm 全部页面已通过子集构建完整写出并通过产物核查（C3）。RTD/CI 侧会做完整全量构建，建议作为最终例行确认。

### C3 构建产物抽查 — PASS

- tcm HTML 页面 **91 个**全部写出；
- `class="mermaid"` 节点共 **17 个**，分布与 M1–M17 计划逐文件一致（含 `01-four-classics-guide.html` 2 个）；抽查 M13 产物，`<pre class="mermaid">` 内 flowchart 源码完整嵌入（引号/`<br/>` 正确转义），mermaid 11.4.1 ESM 引导脚本正常注入；
- `<img>` 标签共 **8 个**，落在 8 个计划页面（域 index、5 束 index、tcm-overview/concepts/02、waijing/concepts/05）；8 张 jpg 均复制进 `_images/` 且字节大小与源文件一致（333,686–554,801 字节），无断链。

### 质量门（补充 CP-19）— PASS

- `check-utf8.py`：7518 个文件均为有效 UTF-8 ✅
- `check-toctrees.py`：全部 index.md 引用有效，所有内容文档可达 ✅
- `check-bundles-index.py`：9 域 / 44 组 / 389 束，frontmatter、计数行、节标题、分组表、toctree 五面一致 ✅（本次未新增束/文档，计数不变）

---

## 问题清单

| 级别 | 编号 | 问题 | 建议 |
|---|---|---|---|
| P0 | — | 无 | — |
| P1 | — | 无 | — |
| P2 | P2-1 | CP-21/FR-6：`tcm/changelog.md` 尚未新增 v1.2.0 视觉资产条目（git status 无该文件改动） | 施工方 C 阶段补登（含 17 Mermaid + 8 配图实际数量与验证证据） |
| P2 | P2-2 | CP-22/FR-6：5 束 `log.md` 未登记 2026-09-02 视觉资产变更 | 施工方 C 阶段逐束补登 |
| P2 | P2-3 | CP-24：standards-tools 主题看板未更新本 spec 完成状态 | 收尾时更新看板 |
| P2 | P2-4 | 域外观察：`yishu/vocal/meitong-yanyin-pedagogy/index.md` 存在 1 WARNING（H2 起首）+1 ERROR（文档以 transition 起首，疑首行 `---` 被误判），为并行会话声乐束文件 | 转交该会话修复；与 tcm 改动无关，不阻塞本次验收 |

---

## checklist.md 24 检查点勾选建议

| 检查点 | 建议 | 依据 |
|---|---|---|
| CP-1 清单产出且数量在区间、路径真实 | ✅ | 17 Mermaid（区间 12–18）+ 8 配图（区间 6–10），A1/A2 |
| CP-2 无 references/存目页资产、单页≤2 | ✅ | A3 |
| CP-3 图表事实均有正文依据、诸说并列 | ✅ | B1–B7 |
| CP-4 配图 prompt 风格约束与意象题材 | ✅ | B8（产物侧验证：8 图均水墨淡彩暖纸、无文字无人体、横向） |
| CP-5 配图落盘路径与 kebab-case 命名 | ✅ | A2 |
| CP-6 单张≤2MB、PNG/JPG、横向 | ✅ | A2（333–555KB，jpg） |
| CP-7 逐张目检无禁用元素 | ✅ | B8 |
| CP-8 风格统一 | ✅ | B8 |
| CP-9 Mermaid 12–18、每束 2–4、栅栏内嵌 | ✅ | A1/A3（每束 3–4） |
| CP-10 六规则合规 | ✅ | A1 机检 + C2 构建零告警 |
| CP-11 引用格式与路径一一对应 | ✅ | A2/C3 |
| CP-12 图前引导/图后说明、frontmatter/toctree 未破坏 | ✅ | 抽查无孤立堆放；三门全绿 |
| CP-13 正文事实表述未改动 | ✅ | A4 diff 纯插入 |
| CP-14 逐张事实核对 | ✅ | B1–B7 |
| CP-15 诸说并列 | ✅ | B3/B7（难经五说、伤寒四版本、本草四辑本、外经真伪两派） |
| CP-16 无诊疗暗示、免责声明完好 | ✅ | B8 |
| CP-17 P0/P1 清零 | ✅ | 本报告问题清单无 P0/P1 |
| CP-18 构建成功零新增告警 | ✅ | C2（tcm 0 告警） |
| CP-19 三门全绿、计数不变 | ✅ | 质量门三节 |
| CP-20 产物图片可访问无断链 | ✅ | C3 |
| CP-21 changelog v1.2.0 | ❌ 待补 | P2-1 |
| CP-22 五束 log.md 登记 | ❌ 待补 | P2-2 |
| CP-23 变更集限域、未自动 commit | ✅ | A4（变更集纯净；未提交符合 spec Non-Goals） |
| CP-24 看板登记并更新状态 | ❌ 待补 | P2-3 |

**勾选汇总**：21 项 ✅ / 3 项 ❌（均为 C 阶段收尾待办，非资产质量问题）。
