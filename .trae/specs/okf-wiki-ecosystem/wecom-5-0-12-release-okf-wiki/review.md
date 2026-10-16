# 企业微信 5.0.12 版本更新发布页转 OKF Wiki - Independent Review

- [x] CP-R1: bundle 结构与 toctree 完整
  - **Type**: `rule`
  - **Covers**: AC-1 / FR-1 / NFR-1
  - **Evidence**: 10 文件齐备（index.md、log.md、concepts/index.md + 00～03、references/index.md + article-source.md + verification.md），无 examples/；三个 toctree 块 9 条目逐一 Test-Path 存在；根 index 含 okf_version "0.2"/status stable/stale_after 2027-01-31/sources（W+O1～O10 实际引用者）；6 个内容文件 type=Concept/Reference、generated/verified 为 process:seven-concepts-*、status/stale_after/sources 齐备；子目录 index 无 frontmatter 与 5.0.10 基准同构；文件名 ASCII kebab-case。

- [x] CP-R2: 双份 F 编号一致、连续、四类口径落地
  - **Type**: `rule`
  - **Covers**: AC-2 / FR-2 / FR-3 / FR-4
  - **Evidence**: 正则提取 spec facts.md 与 references/article-source.md 各 51 个编号，集合相等 = {F-001…F-051}，表行各 51，F-049 为 ❔ 存疑保留行；四类口径（5.8.0 vs changelog 5.7.7 与三处能力清单、幻灯片前瞻、AI 报告灰度标注消失、机器人两入口）在 verification.md 与 4 篇 concepts 全部落地；灰度两项（F-018/F-031）、单源清单 F-045、规模数字媒体转引 F-038～F-040 均标注；「已上线/已可调用/GA」既成表述扫描零违规命中。

- [x] CP-R3: 事实溯源真实、无编造信源
  - **Type**: `rule`
  - **Covers**: AC-2 / NFR-4
  - **Evidence**: 评审独立 WebFetch 复核 5 个 URL：W 发布页（五项重点、幻灯片 CLI/MCP 原文 F-017、频道与 IP 灰度标注、AI 报告段无灰度字样 F-050、path/101906 锚文本、无日期无成效数字）、O1 上证报（操子怡 2026-10-14 13:23、1400 万/7.5 亿/2000 万/50+、网盘版十大能力）、O8 changelog（最新 5.7.7/2026-10-08，无 5.8.x）、O6 能力页（恰 11 模块、无幻灯片）、O9 path/101906（仅上下篇导航无正文，束内未编造标题）；抽查声明全部命中 F 出处。

- [x] CP-R4: 三级索引与计数机械同步
  - **Type**: `rule`
  - **Covers**: AC-3 / FR-5
  - **Evidence**: `check-bundles-index.py` 终采退出码 0（9 域/61 组/634 束五面一致）；tencent 13 束/97 概念/25 示例/54 信源/1619 事实经评审独立复算吻合（剔除本束 1568 + 51；旧投影 1555 的 13 条历史漂移校正披露属实）；新束在 tencent 导航表/toctree/相关链接三处到位；ecosystems 腾讯行 13（页内 88 为已登记导航口径、树真值 89 带免责注）、jishu/ai 241（六类 89/85/20/32/9/6）、jishu 241、总索引 634；check-toctrees 全量 81 处既有污染，过滤 wecom-5-0-12 零命中。

- [x] CP-R5: 链接/编码/合规与双向互链
  - **Type**: `rule`
  - **Covers**: AC-4 / NFR-2 / FR-6 / FR-7
  - **Evidence**: check-utf8.py 通过（11556 文件）；束内 41 条 Markdown 相对链接逐一 os.path 解析全部存活（concepts/ 跨束为 ../../ 深度）；零 file 协议绝对链接、零 C:\Users（实施方初检曾自抓 4 处 ../ 断链并修复）；双向互链成立（新束 4 文件 5 链→5.0.10；5.0.10 束仅 index.md 主题关联 +1 行回链，无其他改写）；log.md 七阶段/口径决策/并行观测/invoke gates.* 未运行如实声明齐备。

- [x] CP-U1: 内容可信度与读者可用性
  - **Type**: `rubric`
  - **Covers**: AC-5
  - **Scale**: 1-5
  - **Anchors**: 1 = 单源/通稿/前瞻/灰度与已证事实混写；3 = 主要声明有出处但口径分层不统一；5 = 每条数字/版本/功能可回溯 F，五类标签（单源/媒体转述/通稿同源/官方前瞻/灰度）全文一致，「已知边界」直接支持使用与等待决策
  - **Pass Threshold**: >= 4
  - **Evidence**: 独立评分 **5/5**——抽查数字/版本/日期/功能名全部可回溯 F；五类标签全文一致；根 index 已知边界直接支持读者决策；四类易混口径以反差证据呈现而非结论化。Advisory A-1（入口计数术语）已在概念 01 加口径划界句收口。

- [x] CP-U2: 知识三层结构与范例一致性
  - **Type**: `rubric`
  - **Covers**: AC-6 / NFR-1
  - **Scale**: 1-5
  - **Anchors**: 1 = 按发布页顺序平铺无分层；3 = 有分层但层间重复或跳转不清；5 = 总览答「何时/什么/时效位置」、机制篇答「怎么打通/边界」、产品篇答「能用什么」、治理篇答「企业怎么管」，阅读路径明确、Mermaid 有 F 依据，且与同目录 5.0.10 束同构同密度
  - **Pass Threshold**: >= 4
  - **Evidence**: 独立评分 **5/5**——四层分工精确命中锚点，层位声明/篇间互链/阅读路径齐全，4 张 Mermaid（timeline+3 flowchart）节点带 F 依据（R1 后 5.8.0 节点补 F-036/F-037），frontmatter/block/toctree/F 引用密度与 5.0.10 范例同构，并合理地由三层扩为四层。

## Review History

### Review R1（2026-10-14）

- **Result**: `pass`
- **Reviewer**: fresh-context 只读通用子代理（未参与实施），独立 WebFetch 复核 W/O1/O6/O8/O9 共 5 个 URL。
- **Evidence**:
  - CP-R1～R5 全部 pass；CP-U1/CP-U2 均 5/5；无 P0/P1 finding。
  - Advisory 6 项（不阻断）：A-1 入口计数两套口径缺显式划界；A-2 摘要行功能名漂移（对外联系管理/安全四机制→官方名对外管理）；A-3 timeline/flowchart 节点缺内挂 F-037；A-4「5.0.10 周期开放 11 模块」时点表述偏松；A-5 utf8 文件数 11555 vs 复跑 11556、R1 留位需回填；A-6 根 sources O10 仅 privacy 一个 URL、W 页概览/详情邮件微差未登记。
  - 处置：A-1～A-5 已全部收口（概念 01 增「领用入口 2 个 vs 使用面 3 个」划界句；概念 01/00 与 tencent 导航行、5.0.10 回链措辞统一；11 模块句加时点状语；Mermaid 节点补 F-036/F-037；log 注明 utf8 计数变化与并行来源）；A-6 经评为非错误（AC-1 只要求列实际引用者；F-044 忠实引用概览原文），保持现状。收口后无并行写入窗口复跑 check-bundles-index 通过（634 束五面一致）。
  - Informational：ecosystems 已登记 88 vs 目录树 89（历史束 deepseek-harness 未接入该类导航）、check-toctrees 全量 81 处污染、并行会话在途束（hwe-bench、kylin-wayland-compositor、sheke ai-solo-company-truth）均为开工前/并行存在，按 spec Non-Goals 不扩大修改，已在 log.md 披露。
  - 评审受限项（不影响裁决）：5.0.10 束整束未跟踪，「仅 +1 行」以全束 grep + 其自有 F-031/log 间接证据成立；O2～O5/O7 未逐一独立抓取；F-048 负向检索结论未复验。
- **Blocked By**: 无
