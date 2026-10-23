# 知乎专栏《AI 科学创新工坊第二弹》→ OKF v0.2 知识包 - 实施计划

> 方法论链路：seven-concepts 场景 4（知识沉淀）R→I→E→V→C；信源先行顺序：facts → references → concepts → bundle index → 上级索引 → C 阶段原子提交。
> 采集通道：知乎开放平台 CLI（`zhihu-cli search zhihu`，16 组锚点滑窗拼接，13 窗口命中）；直连 `zhuanlan.zhihu.com` 与 `api/v4/articles/<id>` 均为 403（code 40362）。
> 目标落点：`projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-ai-science-workshop/`（15 个 .md）。

## Task 1: R — 信源获取与公开性预检
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1 rule PASS：知乎开放平台 CLI 采集，16 组锚点滑窗中 13 个窗口命中，拼接为完整正文（`raw/article-raw.md`）；重叠区逐字一致、无缺口。
  - TR-1.2 rule PASS：直连 `zhuanlan.zhihu.com` 与 `www.zhihu.com/api/v4/articles/<id>` 均返回 403（code 40362），Playwright 无头 Chromium 亦 403 → 通道限制**显式登记**（7 处正文内链 href 不可复核），不据锚文本反推 URL。
  - TR-1.3 rule PASS：公开性预检结论为**公开内容**（无 `share?code=` / `token=` / 邀请码，匿名可读）→ 走标准工作流，spec 落 `.trae/specs/`，产出物落 `projects/awesome-okf-xs/doc/bundles/`。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 用 CLI 滑窗拼接取得源文正文全文，原始 13 窗口保留在 `raw/cli-windows.md` 供回溯。
  - 登记采集通道的 403 限制与「7 处 href 不可复核」这一**已知且显式**的约束（写进 spec Background 与 bundle 信源边界段）。
  - 公开内容判定结果决定后续工作流模式与落盘路径。
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `rule` TR-1.1: 合并全文可逐字读通，窗口衔接处无断句；证据=`raw/article-raw.md`
  - `rule` TR-1.2: 403 事实与 href 不可复核声明双处可查；证据=spec.md Background §1
- **Notes**: 通道限制直接决定 `status: flagged` 与 `stale_after` 的取值，是本束全部「单源」标注的成因。

## Task 2: R — F 编号事实台账（spec 侧 facts.md）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1 rule PASS：`facts.md` 含 F-001~F-083 连续编号事实表（20,181 bytes）；正则 `^\|\s*F-(\d{3})\s*\|` 提取 count=83、min=1、max=83，无缺号、无重复。
  - TR-2.2 rule PASS：每条含 claim / type / locator / source_id 四要素；type 区分元信息 / 原文数据主张 / 原文例证 / 原文引述 / 原文规则条款 / 原文名单。
  - TR-2.3 rule PASS：G1 门通过——事实栏零因果推断词；编者推断不入 facts（只在 concepts 中显式标注）。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 登记 F-001 起连续编号事实表，覆盖活动存在性、时间窗、赛道结构、奖池算术、工具链、投稿与评选规则、挑战题、参赛作品、诺奖指涉。
  - 分类仅用既定枚举；勘误结论按 spec 侧权威表述定稿。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-2.1: 编号从 F-001 连续无跳号；证据=正则提取输出
  - `rule` TR-2.2: 每条四要素可辨识；证据=文件内容
- **Notes**: facts.md 是 bundle `references/article-source.md` 的**唯一事实来源**，两侧声明列须逐字一致（此约束在 Task 8 曾触发一次 P1 级修复）。

## Task 3: R — P0 独立核验与勘误建账
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1 rule PASS：交付 19 项核验结论 C1~C19（活动与机构号真实存在、时间窗、40,000 元奖池算术自洽、双赛道奖励结构、20 工作日公布/发放、AI Works 部署教程、豆包下载页、上一期时间窗等逐项有主体依据）。
  - TR-3.2 rule PASS：交付 5 项源文勘误——①「豆包标准模式会员卡」非官方产品名（官方为「豆包专业版·标准套餐」，¥68 是连续包月价，F-073）；②投稿要求恒为 **4 条**（F-077，首轮「实为 5 项」为自我误判）；③诺奖年份误标（官方为**诺贝尔物理学奖 2026**、**Halzen 一人独享** Prize share 1/1，F-078）；④诺奖公布日 10-06 **早于**活动起始 10-09 三天（F-081）；⑤「650 亿穿过人体」系转述失真（官方为约 **100 万亿/秒**穿过人体，「650 亿」原指太阳中微子穿过小指甲，F-080）。
  - TR-3.3 rule PASS：去重判定落地——7 篇检出参赛作品中 1 篇与另一篇**同作者同署名、正文同句**，独立参赛作品为 **6 篇**（F-066~F-071，F-072）。
  - TR-3.4 rule PASS：单源标注清单与 flagged 判定依据齐备；判定核心声明失败 → 触发 `status: flagged` 管理路径。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 以「发布主体 + 指标名 + 时点 + 结论」三元组记录，不固化深链 URL（避免数月内转死链制造伪可溯源）。
  - 勘误四张清单（日期/版本、数字溯源、口径对照、引文逐字核对）在 `references/verification.md` 落盘。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 19 项结论逐项有主体依据；无编造 URL；证据=verification.md 结论表
  - `rule` TR-3.2: 5 项勘误编号连续无跳号、正文命中；证据=编号集合比对 + 关键词命中回验
- **Notes**: 勘误 ② 是**首轮核验的自我纠错**（把「活动说明 4 条条件」误并入投稿要求计数），已在 spec.md §6 标为 C13 自我纠错并留痕。

## Task 4: I — 骨架判定 + 归属决策 + 三层知识拆分
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1 rule PASS：操作可复现性两问判定为「是 / 否」——含四步流程与规则条款，但正文 **0 代码块、0 表格**、全为外链且 href 不可复核、验收依赖平台审核 → 第二问为「否」→ **不设 `examples/`**，description 标注「非操作教程」。与同簇先例（`zhihu-monetization` / `big-tech-pontzi-track-selection` / `ai-side-hustle-playbook`）一致。
  - TR-4.2 rule PASS：归属判定落 `sheke/industry/` 新建独立束 `zhihu-ai-science-workshop`；候选对照表含并入 `zhihu-monetization`（否决：突破其「三信源」前提 + 跨活动口径混用）、`jishu/ai/practice/`（否决：非技术实操）、新建分组（否决：违反单篇博文禁建分组）三条否决理由。
  - TR-4.3 rule PASS：三层拆分定为事实层 6 篇（00~05）+ 机制层 1 篇（06）+ 路径层 2 篇（07~08），依赖顺序「总览 → 事实 → 机制 → 路径」。
  - TR-4.4 rule PASS：计数基线表落盘（磁盘现值 → 本次新增后，逐面 11 项），并记录口径来源为 `check-bundles-index.py` 的 `_count_bundles` 递归规则。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - I 阶段产出：事实层/机制层/路径层三层边界与「单源约束下哪些结论不可迁移」的判定，写入 spec.md。
  - 确定 9 篇文档分工与依赖顺序，避免读者误按原文散点顺序阅读。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 两问判定与不设 examples 的理由在 log.md 与 spec.md 双处留痕；证据=文件内容
  - `rule` TR-4.2: 归属判定表可查；证据=spec.md §3
- **Notes**: 束名沿 `zhihu-` 前缀保持簇序；必须写明「科学季 2026 ≠ AI 科学创新工坊」的防混用注记（两活动主办方、时间窗、玩法、奖励形态均不同）。

## Task 5: E(信源先行) — references 三文件
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1 rule PASS：`references/article-source.md` 承载 F-001~F-083 完整事实表 + 「已知口径缺口」段 + 「本表不含推断」声明；与 spec `facts.md` 编号集合完全一致（bundle=83 / spec=83，差集为空）。
  - TR-5.2 rule PASS：`references/verification.md` 含 19 项结论表、替代指标表、勘误四张清单过筛记录、源文错误与勘误对照、flagged 判定依据、单源标注清单、证据 URL 全量清单。
  - TR-5.3 rule PASS：`references/index.md` 含 toctree 2 条 + 表格双轨；三文件 frontmatter 齐备（type: Reference / status: flagged / stale_after / sources）。
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `article-source.md`：F 表逐条附 locator（窗口号 + 段落）、原文主张与事实描述分列。
  - `verification.md`：核验方法与可回溯性声明、19 项结论、勘误清单、flagged 判定、单源标注、证据清单。
  - `index.md`：toctree 两条 + 列表双轨。
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 两文件 F 编号集合相等且连续；证据=正则提取结果
  - `rule` TR-5.2: verification.md 各类内容齐备；证据=逐节定位
  - `rule` TR-5.3: frontmatter 与 toctree 齐备；证据=文件检查
- **Notes**: 铁律——正文呈现必须是正确值，源文错误值只允许出现在引述与勘误表中。

## Task 6: E — concepts 九篇 + 子索引
- **Status**: `completed`
- **Completion Evidence**:
  - TR-6.1 rule PASS：`concepts/index.md` 含 toctree 9 条 + 项目符号列表；九篇概念文全部为原创改写，无原文长段镜像、无图片引用。
  - TR-6.2 rule PASS：事实层逐条挂 F 编号引用；机制层因果表述显式标注「洞察/推断」；路径层收益零承诺（仅挂 F 或标「待验证」）。
  - TR-6.3 rule PASS：防混用注记在涉及「科学季 / AI Works / 奖励结构」的文档（00 / 04 / 08）显性化。
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `00-overview`（定位/沿革/时间轴/阅读地图）、`01-campaign-facts`、`02-track-rules`、`03-participation-flow`、`04-science-challenges`、`05-participant-works`（事实层 6 篇）。
  - `06-mechanism-insights`（机制层四元组洞察）、`07-participation-path`（路径层）、`08-risks-and-boundaries`（风险边界）。
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 每个具体数字/日期/名称均有 F 回指，无 F 台账外的具体数字；证据=逐数回查
  - `rule` TR-6.2: 无长段逐字复制、无图片引用；证据=对照检查
  - `rule` TR-6.3: 编者补充/推断标注齐备；证据=逐处抽查
- **Notes**: 06 篇的根因/影响/建议三项必须全部标「洞察/推断」，否则跨过 G1 事实层红线。

## Task 7: E — bundle 根 index.md + log.md
- **Status**: `completed`
- **Completion Evidence**:
  - TR-7.1 rule PASS：根 index.md frontmatter 九字段齐备（okf_version / type / title / description / tags / generated / verified / status / stale_after / sources），`okf_version: "0.2"` **仅**出现在根 index.md（子文件不带）。
  - TR-7.2 rule PASS：顶部 flagged 状态提示块 + 阅读地图 + 核心概念 + 主题关联（`zhihu-monetization` / `big-tech-pontzi-track-selection` / `ai-monetization` / `ai-side-hustle-playbook`）+ 信源与边界段 + 隐藏 toctree 三条。
  - TR-7.3 rule PASS：`log.md` 含九个小节（骨架判定 / 归属决策 / 三层结构 / G3 生成顺序 / 双份一致性 / 核验状态 / 5 项源文勘误 / 去重判定 / 防混用对照 / 索引更新 / 结构范式）+ Verification 段（八项实测结果与门禁边界说明）。
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - `index.md`：OKF v0.2 根 frontmatter + flagged 提示块 + 阅读地图 + 主题关联 + 隐藏 toctree（concepts/index、references/index、log）。
  - `log.md`：R→I→E→V 全过程、勘误与去重结论、防混用对照、计数对账处置、门禁实测方式、已知缺口。
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: okf_version 仅 1 处；frontmatter 九字段齐备；证据=机械扫描
  - `rule` TR-7.2: flagged 提示块在顶部；toctree 三条目拼写正确；主题关联相对路径可达；证据=文件检查
  - `rule` TR-7.3: log.md 含九小节与门禁结论；证据=文件内容
- **Notes**: 主题关联指向同簇兄弟束，须在 C 阶段提交时核对其可达性（Task 9 已在暂存树实测）。

## Task 8: V — 三级索引接入 + 机械门禁与三脚本复核
- **Status**: `completed`
- **Completion Evidence**:
  - TR-8.1 rule PASS：组级 `sheke/industry/index.md` 三处同步（description 29→30、导航表 +1 行、toctree +1 条）；域级 `sheke/index.md` 两处（域简介 29→30、industry 导航行 29→30 + 简介追加）；总 `doc/bundles/index.md` 五处（`total_bundles` 665→666、计数行、mermaid sheke 74→75、社科域节标题 74→75、社科域分组表 industry 行 29→30）。
  - TR-8.2 rule PASS：8 项机械门禁全绿（PASS 17 条）——①UTF-8 strict ②双份 F 编号 83/83 且 83 行声明列逐字一致 ③三级 toctree 全可达 ④三级计数 10 个计数面一致（总 671 / sheke 76 / industry 30）⑤相对链接全可达且零绝对路径 ⑥敏感信息零残留 ⑦frontmatter 结构与字段完整（14 个含 frontmatter 文件）⑧5 项勘误落实回验命中。
  - TR-8.3 rule PASS：三个权威脚本复核——`check-bundles-index.py` exit 0（9 域 / 63 组 / 671 束，五面一致）；`check-utf8.py` exit 0（12,254 个文件均为有效 UTF-8）；`check-toctrees.py` 在本束范围内**零报错**（其报出的 2 条位于他人在途未跟踪目录 `sheke/finance/ponzi-scheme/`，与本束无关，已在 log.md 门禁边界说明中如实登记）。
  - TR-8.4 rule PASS：门禁过程发现并修复三类缺陷——①**F 编号重排后的 45 处交叉引用漂移**（facts/article-source 两表按勘误段重排为 F-073~F-083 后，concepts/00~04、verification.md 与两表备注列仍指向旧编号 F-070~F-080），经 45 处定向锚定替换后逐一对齐；②**frontmatter 首行开围栏丢失** 14 个文件（批量归一化脚本拼接缺陷），已由定向修复脚本补回；③**F-073 双份登记措辞不一致** + **`concepts/00-overview.md` 跨束链接少一层 `../`**，已按 spec 侧权威表述与实际目录层级修正。
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 三级索引接入遵循「跟随目录树地面真值 + 在 log.md 注记」处置，并区分本任务增量与他人在途增量。
  - 仓库级 `check-links.py` 不覆盖子模块路径，故以自写等效清单替代并在 log.md 注明。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-8.2: 8 项逐项有证据；证据=`gate_v.py` 输出（PASS 17 条）
  - `rule` TR-8.3: 三个官方门禁实测输出留存；本束 toctree 命中 0；证据=命令原始输出
  - `rule` TR-8.4: 四类缺陷均有修复记录；证据=log.md Verification 段结论
- **Notes**: 计数面共 10 处（总索引 5 + 域级 3 + 组级 2），必须逐面核对而非只看 `total_bundles`。

## Task 9: C — spec 四件套归档 + 原子提交（子模块 → 主仓库）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-9.1 rule PASS：spec 区四件套齐备且全为 `check-spec-output-archive.py` 白名单文件（`spec.md` / `tasks.md` / `review.md` / `facts.md`）；`raw/` 已被 `.trae/specs/.gitignore` 排除，不入提交集。
  - TR-9.2 rule PASS：子模块原子提交 `19bae835`——提交集恰为 18 个文件（15 个本束新文件 + 3 份共享索引的**本任务增量**）。共享脏文件（`doc/bundles/index.md`、`doc/bundles/sheke/index.md`、`doc/bundles/sheke/industry/index.md`）采用 `git show HEAD:<path>` 取 HEAD 基线 → 临时副本施加本任务增量 → `git hash-object -w` + `git update-index --cacheinfo` 精确写入索引，**未触碰**工作区他人在途改动（finance/ponzi-scheme 与 jishu/ai 4 束保持未跟踪、jishu 与 ai 计数维持 HEAD 值）。
  - TR-9.3 rule PASS：提交前在**暂存树**（`git write-tree` → `commit-tree` → 临时 worktree 检出）实测两个权威门禁均 exit 0——`check-bundles-index.py` 报「9 域 / 63 组 / 666 束，五面一致」、`check-toctrees.py` 报「全部 index.md 引用有效，所有内容文档均可达」，证实**将要落库的那棵树**自身自洽，而非仅工作区自洽。
  - TR-9.4 rule PASS：主仓提交集仅两类路径——spec 四件套 + `projects/awesome-okf-xs` gitlink 指针前移（a046ea05 → 19bae835）；主仓工作区的他人在途改动（`docs/retrospective/**`、`.trae/specs/retrospectives-insights/**`、根目录 4 个 png）**一律未纳入**。不 push。
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 子模块内先提交，再在主仓提交 gitlink 指针（`projects/awesome-okf-xs` 为 git submodule，禁止本地修改后直接提交主仓）。
  - 共享脏文件隔离手法——不改动工作区，改用 `git show HEAD:<path>` 取出 HEAD 版本 → 在临时副本上只施加本任务增量 → `git hash-object -w` + `git update-index --cacheinfo` 精确写入索引，避免触碰并发会话的在途改动。
  - 提交遵循 Conventional Commits（`type(scope): subject`，主体中文），不 push。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-9.2: 提交集文件清单逐条可核；`git diff --cached --stat` 输出 18 files / 1865 insertions / 8 deletions；证据=命令原始输出
  - `rule` TR-9.3: 暂存树上两个门禁 exit 0；证据=命令原始输出
  - `rule` TR-9.4: 主仓提交集仅含 spec 四件套与 gitlink；证据=提交后 `git show --stat`
- **Notes**: 暂存树实测是本次比先例多出的一道关卡——工作区自洽不代表落库树自洽（他人在途增量被排除后，计数必须回落到 HEAD 基线 + 本任务增量 = 666）。
