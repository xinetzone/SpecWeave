---
type: review
title: V 阶段对抗审查与机械门禁记录（gpt6-astra-usage-guide）
date: 2026-09-16
reviewer: process:seven-concepts-v（四视角 + 8 项机械门禁）
---

# V 阶段对抗审查记录

> 审查对象：`projects/awesome-okf-xs/doc/bundles/jishu/ai/gpt6-astra-usage-guide/`（10 文件）
> 审查方法：四视角内容审查 + 机械门禁脚本（PowerShell 实测）+ 子模块官方 gate 脚本

## 1. 四视角审查意见（7 条，采纳修复 4 条）

| # | 视角 | 意见 | 分级 | 处置 |
|---|------|------|------|------|
| 1 | 🔴 魔鬼代言人 | 多处 Markdown 链接使用 GitHub 风格 `#中文锚点`（02 篇目录 5 条、跨文件锚点 4 条），Sphinx/MyST 的锚点 slug 规则与 GitHub 不同，存在构建断链风险 | P1 | ✅ 已修复：全部改为无锚点的文件链接 + "第 N 节"文字指引 |
| 2 | 🟢 新人 | F-019 覆盖面表直接使用 persisted reasoning / compaction 等术语，首次接触的读者不理解其与"自动阻断"的关系 | P2 | ✅ 已修复：00 篇第 5 节补术语注 |
| 3 | 🔴 魔鬼代言人 | bundle 根 index.md 的 7 条兄弟束链接误用 `../../`（多跳一级，实际根 index 只需 `../`），机械门禁实测全部断链 | P0 | ✅ 已修复为 `../`，复跑 45 条链接全可达 |
| 4 | 🟢 新人 | 00 篇插入"6.1 工程责任"位置在"6. 两项限制"之前，章节序号倒置 | P2 | ✅ 已修复：移为第 8 节（迁移要点之后） |
| 5 | 🟠 老板 | "更低单任务 API 成本"为 OpenAI 官方自述（厂商口径），若不加标注易被当独立事实引用 | P1 | ✅ 写作时已落实（00/03 双处标"厂商自述，需自有负载实测"），复核通过 |
| 6 | 🔵 未来 | 模型文档变化快（档位、定价、事件规范），需复核安排 | P2 | ✅ 已落实：stale_after 2027-03-16 + 03 篇第 6 节列 4 个复核触发点 |
| 7 | 🔴 魔鬼代言人 | 博文标题"Skill 被干掉"若在正文无辨析，读者可能把引流标题当结论 | P1 | ✅ 已落实：01 篇第 2 节"标题命题辨析"对照表（F-042），index 已知边界第 2 条 |

无"写得很好"式表演意见；P0/P1 全部修复后复核。

## 2. 机械门禁结果（8 项，全通过）

| 门禁项 | 方法 | 结果 |
|--------|------|------|
| 双份 F 编号一致 | 正则 `^\|\s*F-(\d{3})\s*\|` 提取 spec facts.md 与 article-source.md 集合 | ✅ 43=43，F-001～F-043 连续无跳号 |
| UTF-8 strict roundtrip | `[System.Text.UTF8Encoding]::new($false,$false)` 解码全部 10 文件 + facts.md | ✅ 无异常 |
| BOM | 逐文件读首 3 字节 | ✅ 无 BOM |
| 三级 toctree 完整 | 解析 3 个 index.md 的 toctree 块（排除 `:` 指令行），9 条目逐一 Test-Path | ✅ 9/9 存在 |
| 相对链接可达 | 正则提取 10 文件全部 Markdown 链接（排除 http/mailto/纯锚点），45 条逐一路径解析 | ✅ 45/45 可达（修复 #3 后复跑） |
| 敏感信息零残留 | 正则 `C:\\Users`、`/Users/`、`file:///` | ✅ 零命中 |
| frontmatter 完整 | 逐文件核对 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources | ✅ 齐备；sources 含博文 + 4 个官方核验源 + 2 二手源 |
| BFS 可达性 | doc/index.md → jishu → ai → 本 bundle → concepts/references 链路 6 节点 | ✅ 全部存在；ai/index.md 直属束 58 目录 = 58 toctree 条目（含本束） |

## 3. 全库 gates 实测（子模块官方脚本）

| 脚本 | 结果 | 与本 bundle 的关系 |
|------|------|-------------------|
| `scripts/check-utf8.py` | ✅ 通过（10321 文件） | 含本 bundle 全部文件 |
| `scripts/check-toctrees.py` | ❌ 17 处，**全部属于并行会话在途束**：`ai-agent/ai-agent-book`（缺 log.md、9 文件不可达）、`free-llm-api-hands-on`（缺 index.md、4 文件不可达）、`llama-cpp-local-inference`（缺 log.md） | 0 处涉及 gpt6-astra-usage-guide |
| `scripts/check-bundles-index.py` | ❌ 目录树 546 vs 计数 545（+1） | 差值来自上述在途束（free-llm-api-hands-on 无 index.md 被地面真值计 1）；非本 bundle 造成 |

**处置决策**：本 bundle 计数取并行会话最后一致基线（544/411/192）+1 = **545/412/193**，不把在途且缺 index.md 的他会话束计入官方计数——否则将与并行会话收尾时的 +1 冲突，造成双重计数。待并行会话完成其 log/index 后全库 gates 自然转绿；本 bundle 作用域内已独立证明干净（58=58、BFS 可达、零断链）。

## 4. G1-G3 质量门

- **G1（事实无因果词）**：43 条事实，主观内容 4 条（F-004/F-037/F-042/F-043）显式标注；数字/事件名/参数完整可溯 → ✅
- **G2（洞察四元组）**：3 条洞察（授权梯度/skill 治理权重/不中断续接原语与不可回滚），含陈述/证据/反常识/行动（spec §8）→ ✅
- **G3（知识可迁移）**：02 篇 11 个配方含使用场景与组合建议；00/01 含边界与反模式（标题党辨析、过度测试、免责清单滥用）；核验四清单方法本身可迁移至其他"二手编译→知识库"任务 → ✅

## 5. 结论

本 bundle 内容层与结构层审查通过；全库 gate 红灯为并行会话在途产物，已在 log.md 留痕，不属本次修复范围。C 阶段（原子提交）待用户显式确认。
