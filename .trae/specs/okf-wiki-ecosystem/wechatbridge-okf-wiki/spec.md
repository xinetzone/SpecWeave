---
type: Specification
title: "WeChatBridge（微信流）微信博文 → OKF Wiki 教程"
description: "把微信公众号《微信聊天记录只能烂在手机里？开源 WeChatBridge 一键转给 AI 和 Obsidian》全面学习并转化为 OKF v0.2 知识包"
tags: [spec, okf-wiki, blog-article, wechatbridge, seven-concepts, 博文转化]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-11-06T12:08:16+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-06T12:08:16+08:00" }
status: stable
stale_after: "2026-12-31"
---

# WeChatBridge（微信流）微信博文 → OKF Wiki 教程

## Why

用户以 `/七概念` 要求「全面学习」微信公众号文章
`https://mp.weixin.qq.com/s/QdCiRiwjjc5uOvBW0nBZxw`，并生成 OKF wiki 教程到
`projects/awesome-okf-xs/doc/bundles` 的恰当位置。

单篇博文直接改写为教程有四类固有风险，本 spec 用 `blog-article-to-okf-wiki` 七阶段工作流逐项拦截：

1. **第三方推介口吻被当成项目官方结论**——本文出自「虾说AI实验室 / 虾哥」，与官方 README 署名「向明 / 苍何」不同；
2. **时点漂移**——源文 2026-09-24 写「九个原生入口 / 纯 macOS 工具」，官方 README 核验时点 2026-11-06 已是「十二个入口 / macOS + Windows + iOS 开发中」；
3. **未逐字确认的完成态声明**——「已签名公证」在官方 README 中仅以路线图流程项出现；
4. **图片承载信息不可补写**——「系统演示」四处均为截图，正文无文字，一律按 K 类缺口登记。

教程的价值定位：把「微信合并转发归档 → AI Agent / 本地知识库」这条链路讲透，同时把
**源文时点口径**与**官方当前口径**并列呈现，让读者既拿到可照做的流程，也知道哪些数字会过期。

## 内容敏感度预检

| 项 | 判定 |
|----|------|
| 信源 | 微信公众号公开文章，URL 无 `code=` / `token=` / 邀请码，无访问控制 |
| 分级 | **Public（公开内容）** → 标准工作流 |
| spec 位置 | 主仓库 `.trae/specs/okf-wiki-ecosystem/wechatbridge-okf-wiki/` |
| 产出位置 | 子项目 `projects/awesome-okf-xs/doc/bundles/...` |
| 冲突消解 | 根 `AGENTS.md` 声明 `docs/` 为文档中心、`projects/` 默认只读引用；但 `projects/awesome-okf-xs/AGENTS.md` 明确「公开内容存放于 `doc/bundles/` 或 `doc/`」。按「嵌套优先 + 用户显式目标路径优先」，落 `doc/bundles/`，不改变根 `docs/` 结构 |

## 归属位置分析（博文类内容判定）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/products/wechatbridge/` | ✅ **采用** | 文章主线实体是 WeChatBridge 这一**终端工具产品**；`products/` 已有 `orca-ade`、`wigolo`、`knocket`、`octop`、`opencreator`、`agent-reach`、`craft-anything`、`wechat-intelligence-hub` 等「微信博文经 OKF v0.2 转化」先例，同构可容纳 |
| `jishu/ai/practice/` | ❌ | 该组是工程方法论/行业洞察（29 束），本文是单产品能力解析，不是实践方法论 |
| `jishu/ai/frameworks/` | ❌ | 非框架/运行时源码教程 |
| `jishu/comm/` | ❌ | 虽涉及微信转发，但主线不是通信协议 |
| 新建顶级分组 | ❌ | Skill §9 反模式 3：单篇博文禁止新建分组 |

**结论**：不新建分组，落既有 `jishu/ai/products/`，bundle 目录名 `wechatbridge`。

## 骨架判定（操作可复现性两问）

| 问 | 答案 | 依据 |
|----|------|------|
| ① 博文/核验材料中是否有读者可照做的安装/配置/命令流程？ | **是** | 官方 README 提供「三步上手」、下载安装表、从源码构建 4 行命令、开发验证命令、入口启用路径（F-077、F-089、F-092、F-094） |
| ② 是否有版本、有顺序、有输入输出，具备可复现性？ | **是** | 明确前置 macOS 14+ / 微信 4.1.13+ / Xcode 16 或 Swift 6 CLT；步骤有先后；产物路径 `macos/dist/微信流.app` 明确（F-088、F-090） |

→ 骨架为**技术教程/选型**：`index + concepts/ + examples/ + references/ + log`。
**重要边界**：源文本身无操作序列（F-039），examples/ 全部来自官方 README 的文档化流程，
**非源文作者实测、本知识包未实机验证**，每篇 examples 顶部显式声明。

## 七概念链路与质量门

| 概念 | 动作 | 产物 |
|------|------|------|
| **R** 事实 | 全文抓取 → F-001~F-107 登记 → WebFetch 官方 README 做 18 项 P0 核验 | `facts.md`、`references/article-source.md`、`references/verification.md` |
| **I** 洞察 | 骨架两问 + 三层知识拆分（发布事实 → 链路机制 → 入口/沉淀 → 边界与可迁移模式） | 知识地图（6 concepts + 3 examples） |
| **E** 萃取 | 信源先行：references → concepts → examples → 各级 index 最后写 | 完整 bundle |
| **V** 审查 | 四视角对抗审查 + 双份 F 编号集合比对 + 三级 toctree + 计数五面同步 | `log.md`、索引接线 |
| **C** 提交 | 原子化、显式文件列表；用户未要求 push | 提交记录（本次仅落盘，不提交） |

- **G1**：F 编号事实不含因果词；观点一律标 V，自述标 S，结构缺口标 K，官方补充标 H。
- **G2**：洞察四元组见 `concepts/05`，全部标注「编者洞察，非官方结论」。
- **G3**：可迁移模式脱离本项目仍成立（官方导出通道补入口、场景提示词前置、本地优先失败兜底）。
- **G4**：改动按「bundle 文件 / 分组索引 / 总索引」分组，可独立回滚。

## ADDED Requirements

### REQ-1 事实可溯源

- R 阶段建立 F-001 起的连续编号清单，spec `facts.md` 与 bundle `references/article-source.md` 双份登记且集合相等。
- 所有具体声明（数字、版本、命令、入口名、署名）在 concepts/examples 中携带 F 编号；`facts.md` 之外不得新增事实。

### REQ-2 时点差异并列，不静默照搬

- 「九个原生入口」（源文 2026-09-24，F-018/F-041）与「十二个内置入口」（官方 2026-11-06，F-067/F-068）**并列**呈现，正文以官方当前值为主、源文值标注时点。
- 「macOS 工具」（F-011）与官方多端状态（F-078/F-079/F-095）并列。
- 「已签名公证」（F-015）不得以完成态断言写入正文，只能标注为源文口径且官方未逐字确认。
- 「不调微信接口」（F-026）标注为源文措辞，官方逐字措辞另列（F-082）。

### REQ-3 图片缺口不补写

- 「系统演示」四处截图（F-038）在概念文档中只登记为「图片承载，正文无文字」，不推断截图内容。

### REQ-4 状态与时效管理

- P0 结论 14✅ / 4⚠️ / **0❌**，按 Skill §6 步骤 6.4「P0 出现 ❌ 且失败项为核心声明才 flagged」，本次设 `status: stable`；
  四项 ⚠️ 均为时点/口径漂移，改由 index 顶部「阅读前必知的四条口径差异」块 + 短 `stale_after: 2026-12-31` 兜住，并在 log 中记录该取舍理由。

### REQ-5 导航与计数

- 根 index 的 toctree 必须含 `concepts/index`、`examples/index`、`references/index`、`log`（`check-toctrees.py` 的 `check_consistency` 强制）。
- 分组 `products/index.md` 加导航行 + toctree 条目；计数 39→40。
- 总索引五面同步：frontmatter `total_bundles`、正文计数行、mermaid 域计数、`jishu` 节标题、分组表 `ai` 行。
- 以**落盘前重新回读**的磁盘值为基准做 +1，不沿用会话摘要快照（本仓库存在并行会话 WIP）。

### REQ-6 并行 WIP 隔离

- 本次只修改本 bundle 与三级索引；不触碰并行会话的 `workbuddy-wechat-chat-forward-skills/`（另一篇源文 `BvTuiZelPTb1ZgLT3NoMHQ`）。
- 该 WIP 造成的 toctree gate 报错在 `log.md` 中显式登记为外部未提交变更，不谎报「全库 gates 通过」。
