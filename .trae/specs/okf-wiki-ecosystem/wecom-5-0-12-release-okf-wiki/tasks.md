# 企业微信 5.0.12 发布页 → OKF Wiki 知识包 - 实施计划

> 任务顺序遵循信源先行：references → concepts → 根 index/log → 索引接入 → 机械门禁 → 独立评审。所有计数以实施时机械真值为准。

## Task 1: references 信源三件套（article-source / verification / 子目录索引）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `wecom-5-0-12-release/references/article-source.md`：双份登记 F-001～F-051（内容以 spec `facts.md` 为准，frontmatter type=Reference、sources 列 W/O1～O10 中实际引用者），含来源代号表、两段 F 表、勘误四张清单落实节。
  - 新建 `references/verification.md`：结论块（预期 stable + ⚠️ 单源/口径提示）、日期与版本表（2026-10-14、5.8.0 vs changelog 5.7.7、10-15 直播、2026-10-12 存疑不录）、P0 声明核验表、口径并存表（授权能力三处、幻灯片发布页/能力页、AI 报告灰度跨版、通讯录/侧边栏两入口）、信源距离与厂商叙事评估（通稿/独立稿分层、规模数字转引标注）、V 四视角表、双份编号与状态裁决节。
  - 新建 `references/index.md`（无 frontmatter，toctree 收 article-source、verification）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: article-source.md 含 F-001～F-051 全部 51 行（正则 `^\|\s*F-\d{3}\s*\|` 计数=51）、编号连续；来源代号表覆盖 W/O1～O10
  - `rule` TR-1.2: verification.md 四类口径（5.8.0/5.7.7、幻灯片 11 模块、灰度标注消失、三处能力清单）逐项有独立小节或表格行；无实际访问之外的 URL
  - `rubric` TR-1.3: 核验结论可辩论性；scale 1-5；anchors 1=只给结论不给证据/3=有证据但口径混写/5=每条结论挂信源与状态标签、反方证据（changelog 5.7.7、能力页 11 模块）显式呈现；threshold >= 4；evidence 为评审通读
- **Notes**: F-049 为「存疑不录」过程事实，保留在编号序列内以维持连续性，状态列标 ❔。
- **Completion Evidence**（2026-10-14）：references/ 三件套建成；article-source.md 51 表行、verification.md 含 P0 总表/口径并存表/信源距离/V 四视角表/status stable 裁决；R1 CP-R2/R3 复核 F 集合 51 相等、独立 WebFetch 5 个 URL 证实。

## Task 2: concepts 四篇 + concepts/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `00-wecom-5-0-12-release-overview.md`（事件事实层）：版本一句话（企微×WorkBuddy 联合）、发布时间 2026-10-14 与开放范围（已认证企业/限免）、五项重点概览表、版本时效线 Mermaid（5.0.10→5.0.12→10-15 直播）、灰度项清单（频道、IP 文档场景）、与 5.0.10 束的读法分工、阅读路径。
  - `01-workbuddy-deep-integration-and-ai-agent.md`（机制层）：互通四件事（侧边栏领用/企微账号登录连上下文/微盘互通/加入大圆列表）、WorkBuddy 5.8.0 与十大能力通稿口径（含 changelog 5.7.7 反差与三处能力清单差异）、智能机器人三入口（通讯录/群/频道+path/101906 状态）、大圆技能+MCP 连接器+本地文件/运行命令（与 WorkBuddy 独立文件浏览器划界）、幻灯片 CLI/MCP 前瞻（O6 仍 11 模块）、管理员统一管控与多模型多 Agent。
  - `02-channels-knowledge-base-and-collaboration.md`（产品层）：频道（定义灰度/场景/邀请与搜索）、知识库（沉淀/权限/文件类型与目录）、记录面聊（智能文档沉淀/电脑与语音通话记录/聚合）、智能表格（AI 报告含灰度标注跨版说明、父子记录、42 函数等基础增强）、智能文档（引用转发/LaTeX）、聊天基础体验（Office 转在线文档、HTML/MD 预览、全屏输入、无障碍）。
  - `03-security-and-external-management.md`（治理层）：AI 使用继承三策略（文件防泄漏/敏感行为预警/IP 限制）、对外管理（四项对外策略+外部应用/转发限制）、IP 文档场景灰度、截屏录屏管理（苹果范围）、文件防泄漏精细化、连接微信服务总结早 9 点提醒、三个规则页更新；结尾「企业管理动作 vs 厂商单源」边界提示。
  - `concepts/index.md`：toctree 收 00～03。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 每篇 frontmatter 完整（type=Concept、sources 只列该篇实际引用信源）；所有数字/版本号/日期/功能专名后挂 F 编号；Grep 抽查「5.8.0」「42」「9 点」「1400 万」「7.5 亿」均带 F 引用
  - `rule` TR-2.2: 单源（F-045 清单条目）、媒体转述、通稿同源、官方前瞻、灰度五类措辞标签在各篇至少出现并与 facts.md 状态一致；不得出现「已 GA/已转正」类替官方宣布的表述
  - `rubric` TR-2.3: 三层结构质量（对应 AC-6）；scale 1-5；threshold >= 4；evidence 评审逐篇评分
  - `rubric` TR-2.4: 口径分层（对应 AC-5）；scale 1-5；threshold >= 4；evidence 评审抽查
- **Notes**: Mermaid 至少在 00 篇一张（版本线 timeline）；01 篇可加互通架构 flowchart。跨束引用 5.0.10 用相对路径 `../wecom-5-0-10-release/index.md`，篇内引用用 `00-...md` 同级。
- **Completion Evidence**（2026-10-14）：4 篇 concepts + 子目录索引建成，含 timeline + 3 张 flowchart；跨束链接实施时发现必须用 `../../`（concepts/ 在子目录），束内门禁抓出 4 处断链并已修复；R1 后补「领用入口 2 个 vs 使用面 3 个」口径划界句与 Mermaid F-036/F-037 内挂。

## Task 3: 根 index.md 与 log.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `index.md`：OKF v0.2 frontmatter（status: stable、stale_after: 2027-01-31、sources 全列）、内容性质块（版本资讯非操作教程、不设 examples 理由）、可信度状态块、「这束知识包讲什么」4 行文档表、已知边界（灰度两项、5.8.0 通稿口径、幻灯片前瞻、AI 报告灰度标注消失、单源清单、path/101906 未取正文）、主题关联（5.0.10 束 + workbuddy-one-sentence-mvp + workbuddy-sandbox + tencent-buddy-family 等）、一句话结论、toctree（concepts/index、references/index、log）。
  - `log.md`：初始版本条目，记录七阶段、51 条事实与双份一致、口径决策、并行在途观测（hwe-bench/kylin-wayland-compositor/iot/systems 改动）、门禁运行方式与未运行 invoke 的声明、R1 评审结论留位。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-3.1: index.md toctree 三条目（concepts/index、references/index、log）文件均存在；frontmatter 与 5.0.10 束同型且 sources ≥7 条
  - `rubric` TR-3.2: 已知边界可决策性；scale 1-5；anchors 1=边界缺失或与正文矛盾/3=主要边界有但分散/5=集中声明且每条挂 F、读者可直接判断可用性与等待项；threshold >= 4
- **Completion Evidence**（2026-10-14）：根 index.md（frontmatter sources 11 条、内容性质/可信度状态/已知边界/主题关联/一句话结论五段齐备，toctree 3 条目存活）与 log.md 建成；R1 CP-U1 评 5/5、TR-3.1 通过。

## Task 4: 三级索引接入、计数复算与 5.0.10 束回链
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 更新 `tencent/index.md`：导航表加 5.0.12 行（13 束）、toctree 追加、关于本段计数（束 12→13、概念 93→97、信源 52→54、事实 1555→1606，以真值复算为准）+ 生成来源说明追加「+5.0.12 51 条」、相关链接加行。
  - 更新 `ecosystems/index.md`（腾讯行 12→13、组/类总计数）、`jishu/ai/index.md`（六类计数 +4 概念）、`jishu/index.md`（ai 行）、`doc/bundles/index.md`（total_bundles 632→633、jishu 469→470、ai 概念 240→244 等，全部以门禁脚本真值为准）。
  - 在 `wecom-5-0-10-release/index.md` 回补：「主题关联」加 5.0.12 束链接一行（最小改动，不动其他文字与计数）。
  - 机械复算：用自包含 Python 脚本（.temp 临时文件，用后删除）按 marker 目录（concepts/examples/references）+ 锚点束=1 + 导航目录递归求和口径清点 tencent/ai/jishu 三级真值，并与 check-bundles-index.py 输出对齐。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: `python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0、五面一致；输出计数与写入索引的数字逐项相等
  - `rule` TR-4.2: `python scripts/check-toctrees.py` 全量输出过滤 `wecom-5-0-12` 零命中；既有/并行污染项只在 log.md 列名披露
  - `rule` TR-4.3: 5.0.10 束 index.md 恰好新增 1 条互链（git diff 核对），新束 index 含反向链接
- **Notes**: 若观察到并行会话实时改写总索引，以最后一次无写入窗口的脚本输出为准并在 log 记录。
- **Completion Evidence**（2026-10-14）：五个上游索引全部接入，机械真值 634 束/470/241（ecosystems 89）/tencent 13 束·97 概念·25 示例·54 信源·**1619 事实**；复算发现并校正 tencent 事实旧投影 13 条历史漂移（1555→1568 地面真值，已在 tencent/index.md 与 log.md 注明）；并行会话同期 sheke +1 已在总索引计数面最小对齐并披露；5.0.10 束仅 +1 行回链（R1 全束 grep 证实唯一新增超链接）；check-bundles-index 终采五面一致。

## Task 5: V 阶段机械门禁与四视角自审
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 运行 check-utf8.py；Grep 全部新文件的 Markdown 链接并逐一 Test-Path；Grep 零 `file:///`、零 `C:\Users`/家目录；frontmatter 必填字段逐文件核对；双份 F 集合脚本比对；核对新束无 examples/ 且根 index 内容性质块说明两问判否。
  - 四视角自审（魔鬼代言人/新人/业务方/未来）结论并入 verification.md（Task 1 已建表则只补修正项）；advisory 当场收口。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: UTF-8 门禁通过；链接/路径/敏感信息 Grep 零违规；双份 F 集合 {F-001…F-051} 相等
  - `rubric` TR-5.2: 四视角攻击覆盖度；scale 1-5；anchors 1=自审走过场/3=有攻击无修正记录/5=每视角有具体攻击点与处置且可复核；threshold >= 4
- **Completion Evidence**（2026-10-14）：check-utf8 通过（11556 文件）；束内机械门禁（F 双份集合 range(1,52)、41 条相对链接全存活、零 file 协议链接/零家目录路径、frontmatter、无 examples/）全过；四视角自审表在 verification.md 落表；toctrees 全量 81 处污染过滤本束零命中。

## Task 6: 独立上下文评审 R1 与收尾
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 新建 `review.md`（CP-R1～R5 规则检查点 + CP-U1/U2 量规，覆盖 AC-1～AC-6）。
  - 委派一个 fresh-context 只读 general_purpose_task 执行独立评审（给绝对路径、运行命令、评审合同：结构规范/双份F/口径分层/链接门禁/计数一致/两束互链）。
  - 按结果路由：pass 则写 Review History 并向用户汇报、询问是否原子提交；fail 则 materialize findings 为 Issue 回 Implement；advisory 能当场收口的当场收口并记录。
- **Acceptance Criteria Addressed**: AC-1～AC-6
- **Test Requirements**:
  - `rule` TR-6.1: review.md 每个 AC 至少被一个检查点覆盖；R1 结果为 pass（fail 必有 pending issue 且回归后开新 R2）
  - `rubric` TR-6.2: 评审独立性与证据质量；scale 1-5；anchors 1=主会话自审冒充/3=独立评审但证据笼统/5=fresh 子代理、逐检查点给命令/文件证据与评分；threshold >= 4
- **Notes**: 不执行 git commit；评审通过后在汇报中给出 C 阶段提交方案（子模块→主仓 spec→子模块指针，显式文件列表）供用户决策。
- **Completion Evidence**（2026-10-14）：review.md 建成（CP-R1～R5 + CP-U1/U2 覆盖 AC-1～6）；fresh-context 只读子代理独立评审裁决 **pass**（5 个 rule 全过、双 rubric 5/5、无 P0/P1，独立 WebFetch 5 个 URL）；Advisory A-1～A-5 已收口、A-6 经评非错误保留；Review History 已回填；C 阶段方案随交付汇报提交用户决策，未执行任何 git 提交。
