---
type: Spec
id: spec-loopx-long-horizon-agent-blog-okf-wiki
title: 微信博文《一个悄然崛起的国产开源项目，让 AI Agent 跑满 200 小时不掉线》→ OKF 知识包
date: 2026-09-16
source: https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ
workflow: blog-article-to-okf-wiki（R→I→E→V→C 七阶段，七概念场景4：知识沉淀）
maturity: L3 模式第 14 次应用
tags: [okf, 博文转化, loopx, agent-control-plane, long-horizon, loop-engineering]
---

# Spec：LoopX 长程 Agent 控制面博文 → OKF Wiki 教程

## 0. 内容敏感度预检

- 信源 URL：`https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ`（微信公众号公开文章，无 `share?code=`/`token=`/邀请码参数）
- 公众号「极客之家」公开推文，定位"长期分享实用开源项目"
- **判定：公开内容（Public）** → 标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`

## 1. 信源元信息

| 项 | 值 |
|---|---|
| 标题 | 一个悄然崛起的国产开源项目，让 AI Agent 跑满 200 小时不掉线 |
| 公众号 | 极客之家 |
| 作者 | 丛林 |
| 发布时间 | 2026-09-03 14:05（文末定位：山西；标注原创） |
| 正文长度 | 2777 字符（browser 子代理提取 `#js_content` innerText，一次成功） |
| 主线实体 | LoopX（github.com/huangruiteng/loopx）——长程 Agent 控制面/状态内核 |

## 2. 信源距离预判

- 信源性质：**第三方开源推荐号 + 作者一手轻量实测**（"我装的时候是这样的"），作者丛林 ≠ LoopX 维护者 huangruiteng
- **非厂商自宣**：无提效倍数/ROI 类成效数字；唯一热度数字（5000+ Star）为客观指标，按 P0 核验
- 官方自述（定位语、200h 案例、能力边界）经官方 README/PyPI/TS-RFC/OpenViking PR 序列四源交叉核验

## 3. 骨架判定（操作可复现性两问）

| 判据 | 结论 |
|---|---|
| ① 有读者可照做的安装/配置/调用流程？ | 是：pip 安装三命令、connect、start-goal --guided、dashboard，构成完整上手链路 |
| ② 经作者实测、有版本/输入输出/步骤顺序？ | 是：作者自述实际安装（Python 3.11+、重启宿主、status 预期输出、PowerShell 7 平台分支） |

**两问皆"是" → 技术教程/工具实操骨架，设 `examples/`（2 篇，严格限定在博文覆盖的安装-连接-建目标-工作台范围）。**

## 4. 归属位置分析

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/loopx/`（选定） | ✅ | ① 主线实体 LoopX 是 AI Agent 长程控制面，归属 ai 域无疑；② ai 分组已有大量"单工具直挂束"先例（echobird/browseract/planning-with-files/context-optimization/codex-agent-workflow-practices 等 50+ 直挂束）；③ 与 codex-agent-workflow-practices、agent-platform-notes、ai-engineering-methodology 形成主题互链 |
| `jishu/ai/ai-agent/` | ❌ | 该组聚焦 Agent 运行时框架源码解读（PocketFlow/agency 等）；LoopX 官方明确"not another agent framework"，是控制面而非 Agent 框架 |
| `sheke/industry/` | ❌ | 行业快照组承载商业趋势分析；本文是工具实操教程而非行业分析 |
| 新建分组 | ❌ | 单篇博文禁止新建分组（L3 反模式 #3） |

## 5. P0 核验摘要（详见 facts.md 与 bundle references/verification.md）

核验时点：2026-09-16。12 项 P0：**10 ✅ / 2 ⚠️ / 0 ❌**。

两项 ⚠️ 均为**时效/版本口径**项，非核心声明证误：

1. **版本滞后（勘误四清单①日期/版本表）**：博文称"项目还在 v0.4.x 阶段"，但发文当天（2026-09-03）PyPI 最新已是 0.5.4（0.5.0 线始于 2026-08-19）；至核验时最新 1.0.5（2026-09-15）
2. **实现形态演进（清单③口径对照）**：博文称"纯 Python 写的""没有三方依赖"——对 0.4.x/0.5.x Python 包成立（PyPI requires_dist 至今零强制运行时依赖）；但 TS 控制面迁移 RFC 2026-08-15 已 Accepted，1.0 起官方要求 Node.js 22.18+ 运行托管 TypeScript Effect 内核。博文未捕捉发文前 19 天已公开的迁移动向

核心声明（本地优先状态内核、quota should-run 不计费规则、人类门禁与非自动生产控制、200h OpenViking 公开序列及其边界、多宿主接入、安装命令、Python 3.11+、PowerShell 7）全部 ✅ 逐字或同口径通过。

**状态决策：`status: stable`**（无核心声明失败；两项 ⚠️ 在 verification.md 完整勘误、正文呈现当前值与博文口径双标注）。`stale_after: 2026-11-30`（项目周级迭代 + 内核迁移进行中，短于常规年末窗口）。

## 6. 知识地图（三层拆分）

| 层 | 篇目 | F 编号依据 |
|---|---|---|
| 发布事实层 | concepts/00-loopx-overview.md | F-006~F-010, F-035, F-037~F-041 |
| 机制原理层 | concepts/01-control-plane-mechanism.md | F-010~F-018, F-044~F-047, F-049 |
| 证据与适用层 | concepts/02-evidence-and-fit.md | F-019~F-020, F-027~F-034, F-042~F-043, F-048 |
| 实操：安装自检 | examples/00-install-and-doctor.md | F-021~F-023, F-026, F-038, F-040 |
| 实操：连接建目标 | examples/01-connect-goal-dashboard.md | F-024~F-026, F-046, F-049 |

## 7. 产出文件清单（12 个文件）

```
projects/awesome-okf-xs/doc/bundles/jishu/ai/loopx/
├── index.md                         # 束根索引（frontmatter + 文档结构 + 已知边界 + toctree）
├── log.md                           # 生成与 V 阶段审查记录
├── concepts/
│   ├── index.md                     # 子目录索引（含 toctree）
│   ├── 00-loopx-overview.md
│   ├── 01-control-plane-mechanism.md
│   └── 02-evidence-and-fit.md
├── examples/
│   ├── index.md
│   ├── 00-install-and-doctor.md
│   └── 01-connect-goal-dashboard.md
└── references/
    ├── index.md
    ├── article-source.md            # 博文事实清单（F-001~F-036，双份登记）
    └── verification.md              # P0 核验报告（12 项 + 2 条勘误）
```

索引接入：`jishu/ai/index.md`（导航表 + toctree）、`bundles/index.md`（ai 187→188、jishu 406→407、total 539→540 四面同步）。

## 8. 质量门计划

- G1（事实无因果词）：facts.md 博文事实逐条客观陈述，观点 5 条显式标注"作者观点"
- G3（信源先行/可迁移）：references 先写，concepts/examples 全部具体声明带 F 编号
- G4（V 机械门禁）：双份 F 编号集合比对、三级 toctree、相对链接、UTF-8 strict、计数对账（直接运行 `scripts/check-bundles-index.py` 与 `check-toctrees.py`，不经过 invoke）
