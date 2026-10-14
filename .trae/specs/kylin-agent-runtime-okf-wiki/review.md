# Kylin Agent Runtime 源码 → OKF Wiki - 独立评审记录

- 评审对象：`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/kylin-agent-runtime/`（束内 19 个文件）
- 信源快照：openkylin/agent-runtime @ `ee0c1709199b37ebccdc69b545f266e52e5ed6c9`
- 评审方式：两轮 fresh-context 独立子代理（实现者与评审者上下文隔离），评审者独立运行门禁与计数、独立抽读源码取证

## Review History

### R1（2026-10-14）：fail → 2 条 actionable，已全部整改

- 独立证据：快照 hash/工作树亲验；13 条 F 事实抽查 13/13 命中；16 个自选符号 + 55 个精确行号核实（15 项属实，1 项引出 R1-01）；examples 命令逐字比对 README/源码；AC-6 评 4/5。
- **R1-01（actionable，低）**：concepts/02 称 `recovery_policy_for_tool` "返回四元组"；源码签名 `-> str`，四个分支各返回一个策略名字符串。已整改为"返回四个策略名之一的字符串，取值域 {resume_children, safe_retry, verify_effects, confirm_before_retry}"。
- **R1-02（actionable，低）**：facts.md 缺 F-128（实 149 条却多处声称 150），insights/source-code-map/index/log 存在悬空引用与勘误计数 6/8 不一致。已补写 F-128（cron/ 4 个 py 目录事实），编号连续 150；map 勘误统计改 8；log 补全 E-002~E-006/E-008 与整改留痕。
- 顺手整改的 advisory：R1-06（03 篇 `gateway status` 由错挂 F-011 改挂 F-136，README 确无该命令）；R1-07（F-064 四个传输行号统一为 register_transport 调用行 179/154/289/660）。
- 不整改的 advisory（隔离留痕）：R1-03（中级索引散文/表行与树真值不一致，git 证实为既有/并行欠债）、R1-04（簇级"405 内容文档"为表内自报口径，本束 +10/+2/+2 与磁盘精确相符）、R1-05（验证脚本对下划线符号/函数白名单覆盖偏宽）。

### R2（2026-10-14）：pass

- R1-01/R1-02 经独立对照源码与文档确认到位；R1-06/R1-07 同样属实；整改触及文件无断链、frontmatter 无破损、无自相矛盾。
- 束内三脚本复跑 rc=0；未引入回归。

## 检查点（最终状态）

- [x] CP-R1（AC-1 信源固定与溯源）：**pass** — references 含全 hash/describe/版本/抓取日期/SIG 边界；verify_bundle 全束 file:/// 与本地路径零命中；快照两次复验 ee0c170 零改动。证据：references/{source-code-map,community-sig}.md、verify_bundle.py。
- [x] CP-R2（AC-2 事实层零推断+脚本计数）：**pass** — 150 条 F 编号连续、推断词扫描零命中；10 条 Q 全附口径；R（PowerShell）与 V（Python recount.py，19 项）两套独立计数 ALL MATCH；8 条勘误留痕（含 E-007 行号、E-008 继承关系修正）。证据：spec/facts.md、.trae/specs/.../recount.py。
- [x] CP-R3（AC-3 束结构与 OKF 规范）：**pass** — 10 概念+2 示例+2 信源+spec×2+log+3 子目录 index 齐备；frontmatter 9 键齐、子目录 index 无 frontmatter 且含 toctree、根 toctree 6 条目；87 个束内链接全可达；UTF-8 无 BOM（check-utf8 rc=0，11536 文件）。
- [x] CP-R4（AC-4 API/命令零虚构）：**pass** — verify_symbols 115 类名/常量+40 函数全命中；R1 评审自选 16 符号+55 行号独立核实；examples 24 条 shell 命令逐字可溯；R1-01 语义错误已修。证据：verify_symbols.py、R1/R2 评审报告。
- [x] CP-R5（AC-5 四级导航计数一致）：**pass（对本束增量）** — 本束 ai-agent 55→56、frameworks 83→84、ai 234→235、总索引 628→630 基线 +1 的每个 hunk 经 git diff 证明正确；check-bundles-index 在本束登记后一度 rc=0（630 五面一致）。当前门禁 rc=1 仅因并行会话新增未登记束（wecom-5-0-10-release 等），与本束无关，本束在五级索引均被正确计入。
- [x] CP-R6（AC-6 教程质量 rubric）：**pass，4/5** — 学习路径 00→09 连贯且跨篇呼应；5 条洞察四元组扎实；上下游差异化（分发层麒麟化/符号层留 Hermes 血）逐行有代码事实；扣分项：06/07 麒麟增量点到为止、与 hermes-agent 束缺文档级锚点对照。证据：spec/insights.md、concepts/00/01/06/07、两轮评审批注。
- [x] CP-R7（AC-7 独立评审）：**pass** — R1 fail（2 低危 actionable）→ 整改 → R2 fresh-context 复审 pass；无未处理 actionable finding。

## 并行/既有欠债隔离清单（不属本束，不阻塞）

- check-toctrees 红项（R1 时点 97~104、R2 时点 91）全部归属：ecosystems/deepseek-harness、practice/agent-self-evolution-evaluation、practice/microsoft-mxc-agent-containment、comm/wifit3、gui/tauri、systems/kylin-wayland-compositor、sheke/industry 三束等并行/历史束；kylin-agent-runtime 两轮 grep 零命中、零断链。
- check-bundles-index 在 R2 时点 rc=1：并行束 tencent/wecom-5-0-10-release 未登记（total 631 vs 树 632）；非本束引入。
- 中级索引历史不一致（frameworks 散文值、products 29/32、ai 域 234/238 差 4、ai-agent 簇"405 内容文档"自报口径）：git 证实 HEAD 即存在，本束仅在各自基数上做正确 +1，未扩大修改面。

## 最终结论

**最近一次 Review 结果 = pass（R2）**。全部 7 条 AC 满足：6 条 rule AC 均有评审者独立取证，AC-6 rubric 4/5 过阈；束本身在结构、计数、符号、链接、编码五个维度零遗留问题。
