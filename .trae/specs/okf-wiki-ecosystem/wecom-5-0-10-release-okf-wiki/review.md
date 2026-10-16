# 企业微信 5.0.10 版本新功能发布页转 OKF Wiki - Independent Review

- [x] CP-R1: bundle 结构与 toctree 完整
  - **Type**: `rule`
  - **Covers**: AC-1 / TR-1.2 / TR-3.1
  - **Evidence**: 9 文件齐备；三个 toctree 块条目（排除 `:` 指令行）逐一对应真实文件；根 index 为唯一带 `okf_version: "0.2"` 的文件；`check-toctrees.py` 过滤 `wecom-5-0-10` 零命中。

- [x] CP-R2: 双份 F 编号一致且连续
  - **Type**: `rule`
  - **Covers**: AC-2 / TR-1.1
  - **Evidence**: 正则提取 spec `facts.md` 与 `references/article-source.md` 各 33 个编号，集合相等且 = {F-001…F-033}，脚本输出 `连续: True / 双份相等: True`。

- [x] CP-R3: 事实溯源与信源完整
  - **Type**: `rule`
  - **Covers**: AC-3 / TR-1.3 / TR-2.1 / TR-2.2 / TR-3.2
  - **Evidence**: 独立评审抽查 16 项具体声明（发布日期、7/11 模块、三态命令、npm v1.3.4/MIT、Agent 清单、docid 系列、灰度、F-016 单源、5.0.12 等）全部命中 F 出处，并对发布页与官方 AI 页重新 WebFetch 逐字复核；根 index sources 含 W + O1～O8；7/10/11、命令大小写、5.0.12、灰度、单源/转述分层均在正文落实。

- [x] CP-R4: 三级索引计数同步
  - **Type**: `rule`
  - **Covers**: AC-4 / TR-4.1 / TR-4.2
  - **Evidence**: `python scripts/check-bundles-index.py` 终采通过：9 域/61 组/632 束，frontmatter、计数行、节标题、分组表、toctree 五面一致；tencent 组 12 束（导航表+toctree+统计句一致，93 概念/25 示例/52 信源/1555 事实算术核对）；jishu/ai 六类 88/85/20/32/9/6=240 与目录树递归计数一致。

- [x] CP-R5: 规范与链接合规
  - **Type**: `rule`
  - **Covers**: AC-5 / TR-5.1
  - **Evidence**: `check-utf8.py` 全库 11536 文件通过；本束 9 文件相对链接机械解析零断链；零 `file:///`、零家目录路径；7 个含 frontmatter 文件必填字段齐备；`invoke gates.*` 因可选依赖未运行，已在 log.md 如实注明并实跑全部底层脚本，无谎报。

- [x] CP-U1: 读者可用性与知识组织质量
  - **Type**: `rubric`
  - **Covers**: AC-6 / TR-2.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 信息残缺或失真；3 = 事实完整但口径混杂需回源拼合；5 = 三层结构清晰、时效边界完备、互链得体
  - **Pass Threshold**: >= 4
  - **Evidence**: 独立评分 **5/5**——事件/机制/功能三层，F 标注与媒体口径分层，灰度/快照/5.0.12 时效完备，与 4 个同分组束互链。

- [x] CP-U2: 与同分组范例一致性
  - **Type**: `rubric`
  - **Covers**: AC-6 / NFR-2
  - **Scale**: 1-5
  - **Anchors**: 1 = 结构/风格偏离范例；3 = 形似但信息密度不齐；5 = 与 lightvela-personal-agent 同构且密度相当
  - **Pass Threshold**: >= 4
  - **Evidence**: 独立评分 **5/5**——frontmatter 形态、双声明块、导航/边界/关联/结论骨架、表格与 F 引用密度均同构。

## Review History

### Review R1（2026-10-14）

- **Result**: `pass`
- **Reviewer**: fresh-context 只读通用子代理（未参与实施），重新 WebFetch 两个官方 URL 独立比对。
- **Evidence**:
  - CP-R1～R5 全部 pass；CP-U1/CP-U2 均 5/5；无 actionable finding。
  - Advisory 3 项（不阻断）：①并行会话实时改写总索引，提交前需在无并发写入时复跑门禁；②概念 00/02 引用 O1 但 frontmatter 未列；③verification.md verified actor 与本束其他文件不统一。
  - 处置：②已补 O1 信源；③已统一为 `process:seven-concepts-v`；①已记入 log.md（终采门禁通过）。
  - Informational：ecosystems 类 15/87 vs 目录树 16/88（历史束 deepseek-harness 未接入该类导航）与 check-toctrees 全量既有未接入项均为开工前存在的库内漂移，按 spec Non-Goals 不扩大修改，已在 log.md 披露。
- **Blocked By**: 无
