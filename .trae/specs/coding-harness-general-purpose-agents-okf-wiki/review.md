---
type: review
title: "Coding Harness → OKF 知识包对抗审查与门禁记录"
generated_at: "2026-11-10"
---

# 对抗审查与门禁记录

## 一、四视角审查

### 1. 事实溯源视角

| 检查项 | 结果 |
|---|---|
| 正文中的日期、卷号、评级是否有 F 出处 | 通过（F-001～F-004、F-027～F-031） |
| 四家 SDK 的包名、传输方式、能力是否有官方文档支撑 | 通过（F-037～F-046） |
| 是否把作者观点写成事实 | 通过；F-014、F-019、F-020、F-023～F-025 明确标注作者观点/经验 |
| 是否把厂商自述案例写成可复现结论 | 通过；F-015 标注“厂商自述（无公开证据）” |
| 是否伪造官方 URL | 无；所有 URL 均来自实际抓取或官方仓库 |
| 勘误是否在正文落实 | 通过；E-1～E-4 在对应概念文档中以“口径/版本边界”呈现 |

### 2. 结构规范视角

| 检查项 | 结果 |
|---|---|
| bundle 目录结构 | `index.md` + `log.md` + `concepts/` + `references/`；无 `examples/`（两问判定） |
| frontmatter 必填字段 | 通过；6 篇概念与根 index 均含 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources |
| 子目录 index | `concepts/index.md`、`references/index.md` 均含 toctree |
| 根 index toctree | 收录 concepts/index、references/index、log |
| 事实双份登记 | 通过；47/47，编号连续无跳号 |

### 3. 读者可用性视角

| 检查项 | 结果 |
|---|---|
| 阅读路径是否清晰 | 通过；根 index 给出 7 步阅读顺序 |
| 概念之间是否互链 | 通过；00→01→02→03→04→05→06 形成链路 |
| 主题关联是否可达 | 通过；6 个兄弟 bundle 链接逐一 Test-Path |
| 本 bundle 相对链接 | 0 断链（脚本逐条验证） |
| 是否提供可操作入口 | 提供官方文档入口与最小调用形状；明确“非操作教程” |

### 4. 时效边界视角

| 检查项 | 结果 |
|---|---|
| `stale_after` | 2027-04-30；下一期雷达约 2027-04，SDK 可能破坏性变更 |
| OpenCode 版本边界 | 已标注核验时为 V1 文档，并提示 V2 入口（E-4） |
| Radar 评级时效 | 已标注“以 2026 年 11 月页面为准” |
| 厂商案例边界 | 已标注 .NET 案例为自述，不作为可复现证据 |

## 二、机械门禁

| 门禁 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | ✅ 13149 个文件均为有效 UTF-8 |
| 双份 F 编号 | 正则提取两份表行 | ✅ spec 47 / bundle 47，集合相等且连续 |
| 本 bundle toctree | `python scripts/check-toctrees.py <bundle>` | ✅ 引用有效、内容可达 |
| 本 bundle 相对链接 | 逐条 `Path.exists()` | ✅ 0 缺失 |
| frontmatter | 手工字段扫描 | ✅ 必填字段齐备 |
| 敏感绝对路径 | Grep `C:\Users` / `/Users/` / `D:\spaces` | ✅ 0 命中 |
| 全库 toctree | `python scripts/check-toctrees.py` | ✅ 全部 index.md 引用有效、内容可达 |
| 全库索引计数 | `python scripts/check-bundles-index.py` | ✅ 9 域 / 64 组 / 729 束，五面一致 |

## 三、计数对账

### 最终工作树

| 层级 | 最终值 | 说明 |
|---|---|---|
| practice | 32 | 30 基线 + 本束 + 并发束 `claude-agent-sdk-production` |
| ai | 296 | 293 基线 + 本束 + 并发束 `agent-framework-selection-2026` + 并发束 `claude-agent-sdk-production` |
| jishu | 534 | 531 基线 + 上述 3 束 |
| bundles | 729 | 725 索引基线 + 既有 1 束漂移修正 + 上述 3 束 |

说明。

1. 本 spec 的知识包贡献其中 1 束；另 2 束由并发会话生成。`agent-framework-selection-2026` 已在 `369bdba5` 提交；`claude-agent-sdk-production` 在本轮收尾时以独立提交入库，以保证共享索引不引用未跟踪文件。
2. 最终计数以目录树为地面真值：`check-bundles-index.py` 报 729 束、`check-toctrees.py` 全库通过。
3. 本 spec 只拥有 `coding-harness-general-purpose-agents/` 的内容；另两束的内容不由本 spec 背书。

## 四、勘误清单

| 编号 | 问题 | 处理 |
|---|---|---|
| E-1 | 博文把“沙箱”与“审批”都归到 Claude Agent SDK | 正文分层：审批在 permissions 层，沙箱在托管/运行时层 |
| E-2 | 博文称 Pi“刻意”把护栏留给扩展 | 正文保留结论，标注“刻意”为作者措辞；官方原文为 minimal/extensible |
| E-3 | 博文把 Codex SDK 与 app-server 并列 | 正文分栏：SDK 走 stdio JSONL，app-server 走 JSON-RPC |
| E-4 | OpenCode 文档存在 V1/V2 分界 | 正文标注核验版本，提示以当前文档为准 |

## 五、结论

本 bundle 的事实、结构、链接、frontmatter、UTF-8 均通过门禁；全库 `check-bundles-index.py` 与 `check-toctrees.py` 也已通过。共享索引的最终计数包含并发会话的 2 束；本 spec 只对本 bundle 的 13 个文件负责。
