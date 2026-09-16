---
id: firecrawl-blog-okf-wiki
title: Firecrawl 微信博文 → OKF Wiki 知识包转化方案
source: https://mp.weixin.qq.com/s/gjio8RIefYti1_p2s__A8w
created: 2026-09-16
workflow: seven-concepts（R→I→E→V→C）+ blog-article-to-okf-wiki 七阶段
status: active
---

# Firecrawl 博文 → OKF Wiki 转化方案

## 1. 任务定义

将微信公众号「开源软件社」博文《狂揽 17 万 Star！这个开源项目，把整个互联网变成了 AI 的数据库》（2026-09-01，推介开源项目 **Firecrawl**）按 OKF v0.2 规范转化为可溯源知识包（bundle），落入 `projects/awesome-okf-xs/doc/bundles/`。

## 2. 内容敏感度预检（阶段 0）

- URL：`mp.weixin.qq.com/s/gjio8RIefYti1_p2s__A8w`，无 `share?code=`/`token=`/邀请码参数，公众号公开推文。
- 判定：**公开内容（Public）** → 标准工作流：spec 在 `.trae/specs/okf-wiki-ecosystem/`，产出在子模块 `projects/awesome-okf-xs/doc/bundles/`。

## 3. 信源距离预判（R 阶段前置）

- 博文性质：第三方开源推介号的**编译性项目介绍**（非厂商自宣账号、非作者一手实测），事实几乎全部转译/翻译自官方 GitHub README 与仓库元数据。
- 核验手段：GitHub REST API（元数据/Star/语言/许可）+ 官方 README（端点/SDK/模型/许可原文）+ firecrawl.dev 官方 v2.5 发布文（96%/3.4s benchmark 溯源）。
- 厂商自述数字：96% 覆盖、P95 3.4s 虽出现在官方 README，但源头是厂商自家 benchmark（无第三方独立复测），bundle 中一律标"厂商自述基准"。

## 4. 骨架判定（操作可复现性两问）

| 两问 | 判定 | 依据 |
|------|------|------|
| ① 有读者可照做的安装/配置/代码/调用流程？ | 是 | 含 5 条包管理器安装命令、Python scrape/agent 片段、CLI init、MCP 配置 |
| ② 流程经作者实测、具备可复现性（版本/输入输出/步骤顺序）？ | **否** | 代码逐字来自官方 README 宣传示例（Stripe founders 例子即 README 原文）；无 SDK 版本、无真实运行输出、无实测过程/踩坑、API key 获取一句话带过 |

**结论：技术综述/开源项目盘点类 → index + concepts/ + references/ + log，不设 examples/**（与 threeui/a2a-mcp 正例同型；空 examples 制造伪结构）。index 顶部声明"非一手实测操作教程"。

## 5. 归属位置分析

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/firecrawl/`（选定） | ✅ | ① 主线实体 Firecrawl 自我定位 "web context API for agents"，属 AI Agent 数据/工具生态；② 同品类博文转化束先例：`wigolo`（本地 Web 搜索/抓取 MCP 工具）、`browseract`（浏览器自动化 Agent）；③ 该组存在大量单篇博文直挂束（loopx/uumit/gpt6/mattpocock 等），板块语义吻合 |
| `jishu/data/` | ❌ | PyData 科学计算栈（NumPy/pandas/Dolt），非网页采集工具 |
| `jishu/web/` | ❌ | FastAPI/GraphQL/HTML 等 Web 开发框架，主题不符 |
| `sheke/industry/` | ❌ | AI 行业商业快照，本文是技术项目介绍而非行业分析 |
| 新建分组 | ❌ | 单篇博文禁止新建分组（最小变更原则） |

bundle 目录名取 `firecrawl`（与 wigolo/loopx/browseract 产品名直挂同型）。

## 6. 知识地图（三层拆分，I 阶段产出）

| 博文内容层 | 映射篇目 |
|-----------|---------|
| 事件/事实层（What）：定位、Star/许可/语言/活跃度、七端点全景 | `concepts/00-project-and-endpoints.md` |
| 机制/原理层（How）：Search→Scrape→Interact 数据管线、Agent=/extract 进化、Pydantic 结构化、spark 模型与 effort、Actions、媒体解析 | `concepts/01-agent-data-workflow.md` |
| 生态/边界层：九 SDK + CLI + MCP + Skills 接入、AGPL-3.0/MIT、开源 vs 云、robots.txt 合规、四类用户、竞品语境 | `concepts/02-access-license-boundaries.md` |
| 信源层 | `references/article-source.md`（F 双份登记）+ `references/verification.md`（P0 核验+勘误） |

## 7. 事实集与核验结论（R 阶段产出摘要）

- 完整事实与编号：[facts.md](facts.md)（F-001~F-048：博文 34 条 + 核验补充 14 条，连续无跳号）。
- 19 个 P0/P1 核验项：17 ✅、1 ❌（**F-038 勘误**：博文称"默认 spark-1-mini"，官方 README 明确默认 spark-1-pro，mini 仅便宜 60%）、其余 ⚠️ 为时点/口径标注。
- Star 时点：博文 171,711（2026-08）→ GitHub API 现值 179,337（2026-09-16），半月增约 7.6k，趋势吻合。
- 96%/3.4s 溯源至官方 v2.5 发布文（2025-10-30），厂商自述基准，正文标注。
- 状态判定：唯一 ❌ 为细节性事实（非文章核心声明，核心为"项目是什么/能干什么"且全部 ✅），勘误完整 → `status: stable`，不置 flagged。

## 8. 产出物清单（E 阶段，9 文件）

```
jishu/ai/firecrawl/
├── index.md                               # 根索引（非操作教程声明+勘误提示+主题关联+toctree）
├── log.md                                 # 变更日志
├── concepts/
│   ├── index.md                           # 表格 + toctree
│   ├── 00-project-and-endpoints.md
│   ├── 01-agent-data-workflow.md
│   └── 02-access-license-boundaries.md
└── references/
    ├── index.md                           # 表格 + toctree
    ├── article-source.md                  # F 编号双份登记
    └── verification.md                    # 两轮 26 簇核验+勘误四清单+误判修订
```

索引接线：`jishu/ai/index.md`（导航表行 + toctree 条目，束目录已被并行会话计入地面真值）、`bundles/index.md`（与目录树真值对齐：total 555、jishu 422、ai 203，五面一致）；`jishu/index.md` 历史全页计数漂移另案处理。

## 9. 质量门（G1~G4）

- G1（事实无因果词）：facts.md 客观/观点分列，V 类显式标注。
- G2（洞察四元组）：本场景为知识沉淀，勘误四元组（错误声明+官方正确值+影响+正文处理）入 verification.md。
- G3（可迁移/结构完整）：两问判据记录在案，骨架与正例同型。
- G4（机械门禁）：双份 F 编号集合正则比对、三级 toctree 条目 Test-Path、相对链接全可达、UTF-8 strict、frontmatter 完整、计数同步。

## 10. 已知边界（写入 bundle index）

1. 非一手实测教程：代码片段为官方 README 示例，作者未提供实测过程/版本/输出。
2. 96%/3.4s 为厂商自述基准（v2.5 发布文），无第三方独立复测。
3. Star/功能集为动态信息：博文时点 2026-08（171,711），核验快照 2026-09-16（179,337）；`stale_after: 2026-12-31`。
4. 三创始人姓名出自官方 README 结构化输出示例，非团队名册页。
5. AGPL-3.0 主仓 + MIT（SDK/部分 UI）双许可，闭源商用前须自行对照 LICENSE。
