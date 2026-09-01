# 王阳明心学 OKF Wiki 知识包 - 需求规格（spec.md）

## Overview

* **Summary**：在 awesome-okf-xs 文档库 `doc/bundles/think/` 下新建**王阳明心学（Yangming）知识包分组**，含 5 个 OKF 束（bundle），系统覆盖王阳明（1472–1529）心学体系：《传习录》文本教程、心学义理四大纲领、修养工夫与现代实践、生平成学历程、思想源流与后学/东亚影响。

* **Purpose**：用户希望系统进修王阳明心学（含《传习录》知识库），以提升个人认知与实践能力；产出物须遵循 OKF v0.2 规范与本库既有束模板（facts/insights/log + concepts/examples/references），可被 Sphinx/MyST 构建、被门控脚本验收。

* **Target Users**：作者本人（个人进修补能）与 awesome-okf-xs 的中文读者（零基础入门 → 进阶研读分流）。

## Goals

* G1：建成 `think/yangming/` 分组，含组索引 + 5 束共 73 个文件，体例与道家段 P2 九束（2026-08-31 交付）完全同型。

* G2：《传习录》束完成 ≥10 组关键条目的**双源逐字原文核对**（维基文库 × ctext.org 或第二独立信源），异文登记不改字。

* G3：义理准确——心即理、知行合一、致良知、四句教、格物新解、工夫论等核心命题的出处、年代、语境与权威注解一致，无虚构引文。

* G4：教学落地——每束有阅读/实践示例（分阶段阅读计划、30 天工夫实践手册、进阶进学路径），呼应"进修提升能力"诉求。

* G5：注册进 `think/index.md` 与总索引 `doc/bundles/index.md`（计数按目录树地面真值），三门（utf8/toctrees/bundles）中**凡涉及 yangming 的检查全部通过**。

* G6：子模块内完成一次本地原子提交（不推送）。

## Non-Goals

* N1：**不**注册、不修改并行会话在建内容（`think/vocal/`、`workplace/`）；门控因二者产生的残余红灯如实报告，不代为修复。

* N2：**不**推送远端（推送闸门未开，待统一调度）。

* N3：**不**做《王文成公全书》《传习录》全文转录——采用"概览+选读精读+阅读计划"模式（同 four-books/qingjingjing 束）。

* N4：**不**改动 `confucian/` 分组（四书束保持原样；跨组引用仅在 yangming 侧单向链接）。

* N5：不产出 DOCX/PDF 等衍生格式；不新建主仓库 docs/ 文档。

## Background & Context

* 目标库：`projects/awesome-okf-xs`（git submodule，OKF v0.2 文档库，Sphinx+MyST 构建，invoke 门控）。

* 位置决策：think 域内思想家独立成组有强先例（laozi/zhuangzi/mozi/guiguzi 均为独立组）；儒家组 `confucian/` 当前仅收"四书"经典文本，宋明理学心学属学派/思想家层，故新建 `think/yangming/` 独立组（用户已认可"恰当位置"由代理判定）。

* 模板基线：`think/daojia/daojiao/qingjingjing/`（14 文件标准束：根 4 文件 facts/insights/log/index + concepts 6 篇含 index + examples 2 含 index + references 2 含 index；根 index frontmatter `type: OKF`、含 `okf_version: "0.2"`；facts.md 为 F 编号零推测事实+Rn 信源表；insights.md 为 G2 四元组洞察+G3 可复用模式）。

* 门控现状（2026-09-01 基线）：`check-bundles-index.py` 报 9 处、`check-toctrees.py` 报若干处失败，**全部**源于并行会话未注册的 `think/vocal/`（1 束，已建成未注册）与 `workplace/`（新域，缺 3 级 index.md，在建中）；子模块无 MERGE\_HEAD。

* 方法论：seven-concepts-cmd 场景 4（知识沉淀）链路 R→I→E→A→V→C；G1（事实无因果词）/G2（洞察四元组）/G3（模式可迁移）/G4（行动项原子化）质量门逐阶段拦截。

* 记忆库硬约束：frontmatter 双引号内嵌 ASCII 引号陷阱（中文语境用全角“”）；共享索引 git 竞态纪律（add 与 commit 分两次调用、暂存集核对、不 reset 他方文件）；新增束后必跑门控、计数以门控重算为准禁止手填。

* 内容敏感度：公开内容（Public，公版典籍与公开学术资料）→ 标准工作流；规格产物在主仓 `.trae/specs/create-yangming-okf-wiki/`，知识包在子模块 `doc/bundles/think/yangming/`。

## 束组结构设计（5 束 · 73 文件）

```
doc/bundles/think/yangming/
├── index.md                    # 组索引（type: group；谱系 mermaid；5 束导航；cross-ref 四书/孟子/佛家/道家）
├── chuanxilu/                  # 束1《传习录》阅读教程（14 文件）
│   ├── facts.md insights.md log.md index.md
│   ├── concepts/ 00-overview 01-compilation-versions 02-volumes-structure
│   │              03-core-entries-map 04-selected-readings + index
│   ├── examples/ 01-reading-plan + index
│   └── references/ sources.md + index
├── doctrine/                   # 束2 心学义理体系·四大纲领（15 文件）
│   ├── facts.md insights.md log.md index.md
│   ├── concepts/ 00-overview 01-xin-ji-li 02-zhi-xing-he-yi 03-zhi-liang-zhi
│   │              04-siju-jiao 05-gewu-daxue + index
│   ├── examples/ 01-doctrine-map + index
│   └── references/ sources.md + index
├── gongfu/                     # 束3 修养工夫论与现代实践（14 文件）
│   ├── facts.md insights.md log.md index.md
│   ├── concepts/ 00-overview 01-lizhi 02-jingzuo 03-shishang-molian
│   │              04-xingcha-kezhi + index
│   ├── examples/ 01-modern-practice-30days + index
│   └── references/ sources.md + index
├── biography/                  # 束4 王阳明生平与成学历程（14 文件）
│   ├── facts.md insights.md log.md index.md
│   ├── concepts/ 00-overview 01-life-chronology 02-longchang-awakening
│   │              03-shigong 04-tianquan-and-final + index
│   ├── examples/ 01-chronology-map + index
│   └── references/ sources.md + index
└── lineage/                    # 束5 思想源流·后学分化·东亚影响（15 文件）
    ├── facts.md insights.md log.md index.md
    ├── concepts/ 00-overview 01-sources-mengzi-luxiang 02-zhu-wang-divergence
    │              03-disciples-schools 04-critique-revival 05-east-asia-modern + index
    ├── examples/ 01-study-path + index
    └── references/ sources.md + index
```

文件计数：束1=14、束2=15、束3=14、束4=14、束5=15，合计 72 束内文件 + 组 index 1 = **73 个新文件**。

## Functional Requirements

* **FR-1**：5 束均按标准模板原子化生成，根 index.md 的 `{toctree}` 收录 concepts/index、examples/index、references/index、facts、insights、log 六项；各子目录 index.md 收录其全部内容页；无悬空 toctree 占位、无孤立文件。

* **FR-2**：facts.md 每束一份，事实为陈述句、带 F 编号与 \[Rn] 信源键、无因果推断词（G1）；信源表登记 URL；争议（成书/条数/学派归属等）并列 ≥2 说不作裁决。

* **FR-3**：《传习录》束选读页（04-selected-readings）收录 ≥10 组关键原文（徐爱录首条、心即理、知行合一、致良知、四句教/天泉证道、岩中花树、事上磨练、拔本塞源、训蒙大意、大学问节文等），每组经双源逐字核对并在 facts.md/log.md 留核对记录，异文登记不改字。

* **FR-4**：insights.md 每束一份，含 ≥3 条 G2 四元组洞察（现象/根因/影响/建议）与 ≥2 个 G3 可复用模式（触发场景/核心步骤/反模式/迁移示例）。

* **FR-5**：examples/ 每束 1 篇实操页：束1=分阶段阅读计划；束2=义理地图/命题关系导引；束3=现代人 30 天心学工夫实践手册；束4=年表与研读地图；束5=读物分级与五阶段进学路径。

* **FR-6**：references/sources.md 每束一份，含权威性评级（A/B/C 口径）、权威底本（《王文成公全书》隆庆本/《王阳明全集》、邓艾民《传习录注疏》、陈荣捷《传习录详注集评》、《明儒学案》、冈田武彦《王阳明大传》等）、在线信源分层（维基文库/ctext/学术站）。

* **FR-7**：组索引 `yangming/index.md` 含 frontmatter（`type: group`、okf\_version）、谱系 mermaid、5 束导航表、cross-ref（confucian/four-books、buddhism、daojia）、`{toctree}` 收录 5 束 index。

* **FR-8**：`think/index.md` 增加 yangming 导航行与 toctree 条目（description 补阳明心学）；`doc/bundles/index.md` 的 think 域节注册 yangming 行，计数按目录树地面真值更新（新增后总览：353 束 / 72 组 / 16 域；think 域 48 束 / 25 组——含并行会话 vocal/workplace 地面真值）。

* **FR-9**：全部正文中文、文件名 kebab-case 英文；交叉引用用相对路径；frontmatter 含 type/title/description/tags/generated/status/stale\_after/okf\_version（log.md 用 created 字段）；generated.by 标注实际生产者。

* **FR-10**：子模块内一次原子提交，显式 add 仅 73 新文件 + bundles/index.md + think/index.md；add 与 commit 分两次工具调用，中间 `git diff --cached --name-only` 核对无 vocal/workplace 混入；不 push。

## Non-Functional Requirements

* **NFR-1（可信）**：所有直接引文（引号文段）须可回溯至 facts.md 信源或双源核对记录；关键年代（1508 龙场悟道、1509 知行合一、1519 平濠、1521 致良知、1527 天泉证道、1529 卒）与权威资料一致；禁止虚构条目编号、页码、引文。

* **NFR-2（可构建）**：全部新增文件 UTF-8 无 BOM；YAML frontmatter 可被 `yaml.safe_load` 解析（全束扫描 rc=0）；MyST 构建兼容（双引号标量内禁嵌 ASCII 引号，中文引号用全角“”；波浪号区间写法注意下标误解析风险）。

* **NFR-3（可审计）**：log.md 记录 R-I-E-A-V 各阶段执行、双源核对清单与口径说明；事实编号 F/R 在束内自洽、引用一一对应。

* **NFR-4（边界）**：不修改 vocal/、workplace/ 路径下任何文件；不触碰主仓除 `.trae/specs/create-yangming-okf-wiki/` 外的文件。

## Constraints

* **Technical**：Windows + PowerShell 环境；Python 3.13 可运行门控脚本；网络可用（WebSearch/WebFetch 双源核对）；子模块为 git submodule，提交在子模块内进行。

* **Business**：公开内容标准工作流；本地提交不推送；计数一律以门控脚本重算为准。

* **Dependencies**：既有门控脚本（scripts/check-\*.py）、qingjingjing 等束模板、维基文库/ctext 等公开信源可用性。

## Assumptions

* A1：《传习录》全文在维基文库（zh.wikisource.org）与 ctext.org 可获取，足以支撑 ≥10 组双源核对；若个别条目第二信源不可达，换用中华文库/权威学术站并在信源表注明。

* A2：用户具备中文古文阅读基础，教程以"导读+原文+注疏脉络+实践"分层呈现。

* A3：并行会话将自行完成 vocal/workplace 的注册与补全；本次提交后其未跟踪文件保持未跟踪状态，不影响本束提交正确性。

## Acceptance Criteria

### AC-1：束组结构完整落地

* **Type**: `rule`

* **Given**：任务完成

* **When**：枚举 `doc/bundles/think/yangming/` 目录树

* **Then**：存在组 index.md 与 5 个束目录（chuanxilu/doctrine/gongfu/biography/lineage），每束含 facts.md、insights.md、log.md、index.md 与 concepts/examples/references 三子目录（各含 index.md），总文件数 73

* **Pass Condition**：目录枚举输出与设计完全一致（73 文件、5 束、17 篇 concepts 内容页、5 篇 examples、5 篇 sources）

* **Evidence**：文件枚举命令输出 + tasks.md 完成证据

### AC-2：阳明范围 toctree 导航零缺陷

* **Type**: `rule`

* **Given**：5 束与组索引建成

* **When**：运行 `python scripts/check-toctrees.py`

* **Then**：输出中不存在任何路径含 `yangming` 的失败条目（未收录/缺失 index/悬空占位）

* **Pass Condition**：门控输出过滤 `yangming` 关键词为空

* **Evidence**：门控完整输出存档 + 过滤结果

### AC-3：总索引与域索引按地面真值注册

* **Type**: `rule`

* **Given**：共享索引更新完成

* **When**：运行 `python scripts/check-bundles-index.py`

* **Then**：不存在涉及 yangming 的对账问题；残余失败条目仅涉及 vocal/workplace；frontmatter 计数（353/72/16）与 think 节标题（48 束·25 组）与目录树地面真值一致

* **Pass Condition**：门控输出中无 yangming 相关失败；计数行=地面真值

* **Evidence**：门控输出 + 两个索引文件 diff

### AC-4：frontmatter 与编码全绿

* **Type**: `rule`

* **Given**：73 个新文件落盘

* **When**：运行 UTF-8 门控与 yaml.safe\_load 全束扫描

* **Then**：gates.utf8 通过（新增文件零违规）；每个 .md frontmatter 可解析且含非空 type；okf\_version 仅出现在允许位置（束根/组索引/各页按既有模板携带）；无 Malformed YAML

* **Pass Condition**：`check-utf8.py` 无新增违规；yaml 扫描脚本 rc=0

* **Evidence**：两门输出 + 扫描脚本输出

### AC-5：事实登记与双源原文核对可信（G1）

* **Type**: `rule`

* **Given**：5 束 facts.md 与 chuanxilu 选读页完成

* **When**：审查 facts.md 与 log.md 核对记录

* **Then**：事实均为带 F 编号+\[Rn] 信源的陈述句、无因果推断词；chuanxilu 束 ≥10 组原文经双源逐字核对、异文登记不改字；信源表 URL 抽查 ≥8 个真实可达

* **Pass Condition**：G1 检查单逐项通过；双源核对记录 ≥10 组；URL 抽查全部命中

* **Evidence**：facts.md/log.md + WebFetch 记录汇总

### AC-6：无虚构引文与事实（V 对抗审查）

* **Type**: `rule`

* **Given**：独立审查阶段

* **When**：fresh context 审查员抽查全部直接引文与关键事实

* **Then**：被抽查引文（≥15 段）逐条可在双源核对记录/权威信源中找到出处；关键年代/人名/事件（1472/1508/1509/1519/1521/1527/1529、徐爱/钱德洪/王畿/王艮、四句教文本等）与权威资料一致；束内/跨束相对链接无断链

* **Pass Condition**：抽查零虚构；断链检查零命中

* **Evidence**：review\.md 独立审查记录

### AC-7：教学可用性与实践导向

* **Type**: `rubric`

* **Dimension**：内容对"进修提升能力"目标的教学满足度

* **Scale**: 1-5

* **Anchors**：1 = 仅资料堆砌、无路径无实践；3 = 有阅读计划但义理讲解一般或实践页空泛；5 = 义理准确分层、30 天工夫手册可直接执行、阅读/进学路径清晰且初学者可入门

* **Pass Threshold**: >= 4

* **Evidence**：独立审查评分与评语 + gongfu/examples 与 chuanxilu/examples 内容抽查

### AC-8：本地原子提交合规

* **Type**: `rule`

* **Given**：全部验证通过

* **When**：子模块内执行提交

* **Then**：单次提交仅含 73 新文件 + doc/bundles/index.md + think/index.md；暂存集经 `git diff --cached --name-only` 核对无 vocal/workplace/其他混入；未执行 push

* **Pass Condition**：`git show --stat HEAD` 文件清单与预期集合一致；无 push 记录

* **Evidence**：git show 输出 + 暂存核对记录

## Open Questions

* 无（束结构、并行 WIP 处置、提交策略三问已于 2026-09-01 经用户确认：5 束细分 / 严格只注册阳明 / 本地提交不推送）。

