---
type: checklist
title: 手势×声乐教学 OKF 教程束 - 验证清单
session: sc-20260902-gesture-vocal-wiki
chain: F→R→I→E→V→C
---

# 手势辅助声乐教学教程束 - 验证清单

> 用法：每个检查点由独立子智能体（black-box）核验；`programmatic` 点以命令/脚本输出为准，`human-judgment` 点以评审 rubric 为准。全部勾选方可结项。

## A. 结构与门控（对应 AC-1/AC-2/AC-8/AC-11）

- [ ] CP-01：新束目录 `doc/bundles/yishu/vocal/gesture-vocal-pedagogy/` 存在，含 `concepts/`、`examples/`、`references/` 三个 marker 子目录，被 check-bundles-index 识别为 1 束。
- [ ] CP-02：束内 .md 清单齐备——束根 index.md、facts.md、insights.md、log.md、concepts/index.md + 8 篇（00-07）、examples/index.md + 3 篇（01-03）、references/index.md + 2 篇（01-02），共 20 个 .md。
- [ ] CP-03：束根 toctree 含 6 条目（concepts/index、examples/index、references/index、facts、insights、log）；子目录 index 的 toctree 覆盖其全部子文件；`invoke gates.toctrees` 无 broken link、无 orphan。
- [ ] CP-04：`conda run --no-capture-output -n py314 invoke gates.all`（cwd=projects/awesome-okf-xs）退出码 0，utf8/toctrees/bundles 三门全绿，计数五面对账无差异。
- [ ] CP-05：定向 Sphinx dummy 构建（新束全部 .md + vocal/index.md + yishu/index.md + bundles/index.md）退出码 0、0 ERROR（含无 Malformed YAML）；构建后 `.temp/dummy` 已清理。
- [ ] CP-06：全束 .md 为 UTF-8 无 BOM；frontmatter 均可被 `yaml.safe_load` 解析且 `type` 字段齐备；双引号标量内无 ASCII 双引号（中文引号用全角“”）。
- [ ] CP-07：仅束根 index.md 含 `okf_version: "0.2"`，其余文件无该字段；frontmatter generated/verified actor 约定对齐姊妹束（`agent:seven-concepts-cmd` / `process:seven-concepts-v`）。

## B. 事实与信源层（对应 AC-3/AC-11，Task 1/7）

- [x] CP-08：facts.md 以 GV-01 起编号，条目 ≥25（实测 33 条 GV-01~GV-33）；纯客观陈述，扫描无"因为/导致/所以/由于"等因果推断词（实测零命中）。
- [x] CP-09：每条 GV 事实含至少 1 个 http(s) 信源 URL；双源条目占比 ≥80%（实测 31/33=93.9%），其余 2 条显式标注（单源待核）。
- [x] CP-10：七唱名手型+空间高度描述与 ≥2 个权威信源（Kodály 协会/音乐教育教材/权威百科）逐项一致；Sarah Glover、Curwen、Kodály、Dalcroze、金铁霖生卒年与著作年份无硬错误（V 阶段逐项对表，信源冲突裁决留痕于 log.md：Glover 1786 说、手势定型 1870 说、OAKE 1975 说）。
- [x] CP-11：references 两篇（01-core-books-methods、02-science-embodied）登记三大体系著作/机构/课标与具身认知实证文献；V 阶段抽检 URL 可访问且内容相符。

## C. 概念与实践内容（对应 AC-4/AC-5/AC-10，Task 3/4/5）

- [x] CP-12：concepts 8 篇齐备且与 FR-4 清单一一对应（00 入门地图、01 原理、02 柯尔文、03 声乐课堂手势、04 指挥、05 体态律动、06 教学序列、07 反模式）。
- [x] CP-13：03 篇五类声乐手势每个含"动作要领→针对问题→使用时机→常见错误"四要素；与姊妹束 meitong-yanyin-pedagogy 的交叉链接 ≥3 处且路径有效（实测跨束链接 11 处，脚本核验闭合）。
- [x] CP-14：04 篇 2/3/4 拍图式方向序列与经典指挥教材一致（2 拍下-上、3 拍下-外-上、4 拍下-里-外-上）；起拍/收拍/双手分工成篇。
- [x] CP-15：07 篇反模式 ≥10 条（实测 12 条），每条"表现→为什么错→正确做法"齐备且具体可辨认；与姊妹束纠错篇无矛盾。
- [x] CP-16：examples 3 篇均含分步流程 + 时间/频次剂量 + 可观察自检标准（照文可执行无歧义步骤占比 ≥90%，无"多练习/注意音准"类空话）；示例 02 与姊妹束每日练声清单剂量/顺序不矛盾且链接有效。
- [x] CP-17：新手可懂性——零基础读者照 02 篇表格能做出 do/mi/sol 三手势并说出高度差异；术语首次出现均有解释（00 篇术语地图 + 02 篇唱名 si=ti 说明）。
- [x] CP-18：安全提示就位——束根含嗓音安全 blockquote（疼痛/嘶哑即停就医、不替代面授）；07 篇含手势使用安全（不替代听觉训练、器质性问题就医、儿童动作幅度）。

## D. 洞察与留痕（对应 FR-3/FR-8，AC-7）

- [x] CP-19：insights.md 含 ≥4 条四元组洞察（实测 5 条，引用 24 个 GV 编号经脚本交叉校验全部存在），覆盖"转译器本质、两套手势逻辑、脚手架须撤除、身体记忆先于符号记忆"四命题。
- [x] CP-20：log.md 按 R/I/E/V/C 五阶段记录编纂过程、信源裁决、图片生成记录；V 阶段小节含审查意见清单（P1×3/P2×4/P3×3 共 10 条、无客套话）、采纳 8 条/不采纳 2 条结论与 before/after 修正说明；P0/P1 全部修复。

## E. 视觉资产（对应 AC-6，Task 6）

- [x] CP-21：`doc/_static/bundles/yishu/vocal/gesture-vocal-pedagogy/images/` 下存在 5 个非 0 字节 jpg（hero-gesture-voice、curwen-hand-signs-chart、vocal-breath-ball、conducting-patterns、child-class-gestures，实测 294–594KB）。
- [x] CP-22：正文 `/_static/bundles/yishu/vocal/gesture-vocal-pedagogy/images/` 引用恰好 5 处，与文件名一一对应；封面图在束根安全 blockquote 后、快速导航前；其余 4 图位置与 tasks.md Task 6 一致。
- [x] CP-23：每张图配完整中文 alt（画面描述）与图注，5 处图注全部诚实声明"示意、以文字/表格为准"。
- [x] CP-24：逐图人工审查——手部无六指/多指融合等严重解剖错误；合集图七型与课堂图手势为示意级别简化（平掌细分、单/双食指不精确），按 Task 6 预案接受并以文字规格为准，已在 log.md 记录；五图统一暖灰纸感风格、无乱码文字。

## F. 注册与提交（对应 AC-9/AC-12，Task 8）

- [x] CP-25：vocal/index.md 知识包表与 toctree 含 gesture-vocal-pedagogy；yishu/index.md 声乐组描述更新为两束并列；bundles/index.md 的 total_bundles（499）、mermaid yishu 行、域节标题束数、vocal 组行束数（1→2）均更新，无手填数字。
- [x] CP-26：三处注册说明文字与束实际内容一致（束数、篇数 8+3、图数 5 描述准确）。
- [x] CP-27：原子提交在子模块 awesome-okf-xs 内完成（commit a2eea489，28 文件 = 20 .md + 5 jpg + 3 注册文件，1827 insertions；`git add` 与 `commit` 分离、暂存集经 `git diff --cached` 核验无他会话 WIP；Conventional Commits 中文信息无乱码；未 push，`git show --stat` 已验证）。
