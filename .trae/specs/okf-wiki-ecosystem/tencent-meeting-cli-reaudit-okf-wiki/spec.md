# 腾讯会议 CLI（tmeet）知识束 v0.4.0 全信源增量复核轮 - 需求文档

## Overview

- **Summary**：以七概念方法论（元编排 `seven-concepts-cmd，场景 4 知识沉淀，链路 R→I→E，V 强制；C 阶段只做变更完整性收口、不提交）对既有 OKF 知识束 `tencent-meeting-cli`（当前 v0.3.0，基线版本 v1.0.18，2026-10-04 交付）执行一次**全信源增量复核轮**：重新采集/比对该束登记的全部 10 个信源与 npm/GitHub 版本面，按漂移结果走「条件增补（v0.4.0）」或「零漂移最小留痕（内容版本不变）」两条互斥路径，并通过子项目质量门与 fresh-context 独立评审。
- **Purpose**：用户要求"全面学习 https://meeting.tencent.com/meeting-cli/index.html 并在恰当位置生成 OKF wiki 教程"；侦察证实该教程已存在且覆盖产品页全部业务域，故本轮目的从"新建"转为"验证时效性、捕获上游漂移、保持最高可信知识库的新鲜度与可审计性"，避免重复建设。
- **Target Users**：通过 awesome-okf-xs 文档库学习/集成腾讯会议 CLI 的工程师与 AI 智能体；负责该束新鲜度的后续维护者（复核证据可复现、到期可再跑）。

## Goals

- **G1 全信源漂移审计**：对 8 份信源文档（10 个 URL/文件）逐一重新采集并与束内登记事实比对，外加 npm registry 与 GitHub 版本面三证，形成可复现的漂移矩阵（时间戳、版本锚点、比对结论、证据）。
- **G2 条件化知识增量**：仅当发现真实漂移（新版本、命令/Skill/文档口径变化）时，按 v0.2.0/v0.3.0 既有多轮增量规范续编事实、定点修订并 bump 至 v0.4.0；零漂移时只做最小复核留痕，不为凑版本制造变更。
- **G3 门禁与独立评审闭环**：`invoke gates.all` 全绿、Sphinx 构建 0 error、fresh-context 独立评审 pass，变更文件清单显式可核对。

## Non-Goals

- **不新建知识束**、不在其他分组/目录另建教程（单一事实源：`jishu/ai/ecosystems/tencent/tencent-meeting-cli/`）。
- 不结构性重写 00~13 既有 14 篇概念文档与 4 篇示例；新信源只能"定点修订 + ⚠️ 口径并列"，不覆盖旧结论。
- 不做真实腾讯会议账号的运行期联调（静态学习性质不变，沿用"未运行验证声明"）。
- 不扩展覆盖开放平台 REST API 全量字段、企业灰度申请细节、计费策略与第三方评测。
- 不执行 `git commit`/`git push`、不更新主仓 gitlink；C 阶段交付工作区变更与提交建议，提交待用户单独指令。
- 不修复与本束无关的在途门禁欠债。

## Background & Context

- 既有束位置：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/tencent-meeting-cli/`，v0.3.0 = 14 概念（00~08 用户面 + 09~13 源码内部机制）+ 4 示例 + 8 信源文档（10 URL/文件）+ spec/facts.md（F-001~F-199）+ spec/insights.md（8 条四元组洞察）。
- 版本基线：npm 包 `@tencentcloud/tmeet` 与 GitHub tag 均为 **v1.0.18（2026-09-11，commit e631b355da2b001d24b82f453b65d96f39c59865）**；stale_after 窗口为 2027-04-03/04。
- Specify 阶段预侦察（2026-10-15）：① `npm view @tencentcloud/tmeet version` = 1.0.18，time 序列最新发布仍为 2026-09-11；② GitHub Commits API `since=2026-09-11T10:00:00Z` 返回 `[]`（默认分支零新提交）；③ 产品首页与安装指南实时抓取内容与 F-002/F-005~F-007/F-011/F-016/F-018/F-020、F-012/F-013/F-019/F-020 一致，零文本漂移。
- 10 个信源：产品首页、安装指南（cli-install-guide）、GitHub README（raw tag v1.0.18）、腾讯云文档 133827、腾讯文档用户手册（docs.qq.com，2026-06-25 保存）、docs/command.md（1594 行）、SKILL.md、CHANGELOG、package.json（后三者登记于 skill-manifest.md）、v1.0.18 固定 tag 源码主体（登记于 source-code.md）。
- 环境：子模块工具链可用（Python 3.13.9 + invoke 3.0.3）；子模块工作树当前清洁。
- 流程依据：OKF v0.2 frontmatter 规范、子项目 AGENTS.md（toctrees/bundles/utf8 三门）、TRAE-spec-mode 五阶段、七概念场景 4（G1 事实门/G2 洞察门/G3 模式门）、既有束 v0.2.0/v0.3.0 多轮增量先例（F 续号、口径并列、log 留 V 记录）。

## Functional Requirements

- **FR-1（R·版本面三证）**：以可复现命令/请求取得三项版本证据并记录时间戳：npm registry latest 与 time 序列；GitHub 默认分支 since 2026-09-11 提交列表；tag `v1.0.18` 指向 commit SHA 与 e631b355… 比对。
- **FR-2（R·逐源漂移比对）**：对 10 个信源逐一重新采集（QQ 文档按 v0.2.0 已验证的 dop-api/opendoc JSON 复现路径；云文档抓取正文与页面更新时间），与束内对应事实段做机械比对，逐源产出结论：`零漂移` / `文本漂移（列差异）` / `不可达（列证据与降级处置）`。比对覆盖：版本/命令计数与命令名、安装命令与环境要求、Agent 名单、业务域清单、FAQ、页面更新时间元数据、tag 内文件哈希或行数锚点。
- **FR-3（R·漂移矩阵落盘）**：形成 `drift-matrix.md`（spec 工作目录内实施证据），每源一行：信源 ID、URL、采集时间（UTC）、方法、基线锚点、本次锚点、结论、受影响 F 编号（若有）。
- **FR-4（I/E·零漂移路径）**：当全部信源零漂移（不可达源不得证伪、按维持原判处理）时：① 在束 `log.md` 追加「复核轮 2026-10-15（内容版本不变）」节，含三证证据与逐源结论摘要、方法与复现入口；② tencent 分组 `index.md`「关于本分组」段补一句复核日期与零漂移结论；③ 不改 version 字段、不改 facts/insights/concepts/examples/references 正文；④ 不新增事实编号。
- **FR-5（I/E·增补路径，仅漂移触发）**：当发现影响用户面/命令面/源码机制的漂移时：① facts.md 自 F-200 起连续续号，每条带来源锚点与三级证据（代码证实/文档声称/推断）；② 新增/更新对应 references 信源文档（登记新页面时间或新版本）；③ 受影响概念/示例定点修订，旧口径以「⚠️ 口径」并列不覆盖；④ 若上游发布新版本，源码信源 rebase 到新 release tag 后复核受影响机制事实；⑤ 根 index.md、references/index.md、concepts/index.md、tencent/index.md 计数与描述连锁更新，log.md 追加 v0.4.0 节（含 V 审查表）；⑥ 触发 G2 洞察门：仅当新事实改变结构性认识时才新增洞察，禁止为凑数造洞察。
- **FR-6（V·对抗审查）**：按既有先例执行四视角审查（魔鬼/新人/老板/未来），重点攻击：漂移判定是否有据（防"为留痕虚构漂移"与"有漂移漏判"双向错误）、证据可复现性、F 编号连续性、计数算术闭合、版本号语义恰当（零漂移不 bump）、变更文件是否越界。
- **FR-7（C·门禁与收口）**：运行 `invoke gates.all`（utf8/toctrees/bundles）与 Sphinx 构建（`invoke build`，不可用则 `sphinx-build -b dummy` 定向验证）；`git -C` 核对变更文件清单仅限白名单；确认无 commit/push；输出提交建议（中文 Conventional Commits 文案）但不执行。

## Non-Functional Requirements

- **NFR-1 G1 事实门**：漂移矩阵为纯客观记录，无因果推断词；差异描述逐字/逐值对比，结论只允许"零漂移/漂移（引原文）/不可达"三类。
- **NFR-2 证据可复现**：每条结论附采集时间、命令或 URL、关键响应值（版本号/SHA/行数/页面更新时间）；第三方时间敏感请求注明 UTC。
- **NFR-3 零虚构**：增补路径中每个新事实可在新抓取内容或固定 tag 源码中命中；命令/符号/计数沿用 Grep/API 机械复核纪律。
- **NFR-4 OKF v0.2 合规**：任何改动文件保持 frontmatter 合规（必填 type、generated/verified/status/stale_after/sources 约定）、中文正文、kebab-case 文件名、相对链接、无 file:///、index 的 toctree 与人类导航并存。
- **NFR-5 最小变更与批次卫生**：零漂移路径改动文件 ≤ 2（束 log.md + tencent/index.md）；不触碰无关束与无关门禁项。
- **NFR-6 子模块纪律**：只在子模块工作树内写文件；不切 tag、不升级外部克隆；显式文件清单纳入评审证据。

## Constraints

- **Technical**：Windows + PowerShell 7+；网络抓取（WebFetch/HTTP API）；invoke 3.0.3 质量门；GitHub 未认证 API 限额（60/h）内完成，必要时用网页抓取替代。
- **Business**：全部信源为公开官方内容（Public），产出物归子模块 `doc/bundles/`；不提交、不发布。
- **Dependencies**：`docs.qq.com` 与 `cloud.tencent.com` 页面可访问性；若反爬/动态渲染导致不可达，按 FR-2"不可达"降级（维持原事实、注明复核未覆盖），不阻塞其余路径。
- **方法论**：seven-concepts-cmd 场景 4（R→I→E，V 强制，C 收口不提交）；多轮增量纪律沿用束内 v0.2.0/v0.3.0 先例。

## Assumptions

- Specify 阶段预侦察结论（npm/GitHub/产品页/安装指南零漂移）在 Implement 当日仍成立；Implement 首日重跑三证，若状态变化以新证据为准并自动进入增补路径。
- 固定 tag v1.0.18 内容不可变；tag 内文件（README/command.md/SKILL.md/CHANGELOG/package.json）只需锚点抽检（SHA/行数），无需全文重抓比对，除非三证显示出现更新 tag。
- 云文档/QQ 文档页面更新时间若晚于束内登记（2026-07-08 / 2026-06-25）即判定为"需内容比对"信号，进入增补评估；时间相同或不可得则维持。
- 零漂移路径下，tencent 分组索引的束/概念/信源/事实计数全部不变，gates.bundles 五面对账应自然通过。

## Acceptance Criteria

### AC-1: 漂移矩阵完整覆盖全部信源与版本面
- **Type**: `rule`
- **Given**: R 阶段完成
- **When**: 检查 spec 工作目录 `drift-matrix.md`
- **Then**: 含版本面三证 + 10 个信源逐源条目，每条有采集 UTC 时间、方法、基线/本次锚点、三类结论之一
- **Pass Condition**: 条目数 = 13（3 版本面 + 10 信源；SKILL/CHANGELOG/package.json 可合并于 skill-manifest 一行但须分别给锚点）；无"未检查"项，不可达项有降级说明
- **Evidence**: drift-matrix.md + 命令/请求输出摘录

### AC-2: 版本面零变更或漂移被如实捕获
- **Type**: `rule`
- **Given**: R 阶段版本面证据
- **When**: 比对 npm/GitHub/tag SHA
- **Then**: 零变更时三值与基线一致（1.0.18 / since 2026-09-11 零提交 / e631b355…）；有变更时漂移矩阵登记新版本、受影响范围并触发 FR-5
- **Pass Condition**: 三项证据齐全且结论与实际响应一致；结论→路径选择可追溯
- **Evidence**: npm registry JSON、GitHub API 响应、tag ref SHA

### AC-3: 路径执行与版本号语义正确
- **Type**: `rule`
- **Given**: 漂移矩阵最终结论
- **When**: 执行落盘
- **Then**: 零漂移 → 仅 log.md 与 tencent/index.md 改动，无 version bump、无 F 编号新增、无正文事实改写；有漂移 → F 自 F-200 连续续号、旧结论口径并列、version=0.4.0 且计数连锁
- **Pass Condition**: `git diff --stat` 与路径白名单/编号扫描均符合所走路径
- **Evidence**: git 状态输出、facts.md 编号区间、log.md 版本节

### AC-4: 子项目质量门与构建全绿
- **Type**: `rule`
- **Given**: 落盘完成
- **When**: 在子模块目录运行 `invoke gates.all` 与文档构建
- **Then**: utf8/toctrees/bundles 三项通过，Sphinx 构建 0 error
- **Pass Condition**: 命令退出码 0 且输出无 error/断链/孤立文档告警（本束相关）
- **Evidence**: 命令完整输出

### AC-5: OKF 规范与变更边界
- **Type**: `rule`
- **Given**: 全部变更
- **When**: 审查 diff
- **Then**: 无 file:/// 链接、无绝对路径引用；改动文件仅限白名单（束目录内文件 + tencent/index.md + spec 工作目录）；无 commit/push 发生
- **Pass Condition**: diff 文件清单逐项命中白名单；`git log` 无新增提交
- **Evidence**: git status/diff/log 输出

### AC-6: 复核轮文档质量
- **Type**: `rubric`
- **Dimension**: 留痕/增补内容的可审计性与信息密度
- **Scale**: 1-5
- **Anchors**: 1 = 留痕空洞或夸大漂移、证据无法复现；3 = 结论完整但证据链有缺口或含冗余复述；5 = 证据精确可复现、差异定位到 F 编号与原文、零推断词、读者可独立重跑
- **Pass Threshold**: >= 4
- **Evidence**: log.md 复核节（或 v0.4.0 节）+ drift-matrix.md

### AC-7: fresh-context 独立评审通过
- **Type**: `rule`
- **Given**: 实施队列清空
- **When**: 未参与实施的 fresh context 按 review.md 检查清单独立复核
- **Then**: review.md 结果 pass，每个 AC 有独立证据，无遗留 actionable 发现
- **Pass Condition**: Review R1（或必要时整改后 Rn）= pass
- **Evidence**: review.md

## Open Questions

- 无（范围双问题已经用户确认：全信源 v0.4.0 复核轮；不提交仅交付工作区变更）。
