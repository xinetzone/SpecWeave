---
okf_version: "0.2"
type: spec
title: "wigolo 本地 Web 情报层博文→OKF 知识包转化规划"
description: "将微信公众号博文《零API Key、零费用！这个GitHub开源神器让AI Agent彻底告别搜索付费焦虑》转化为 OKF 知识包，覆盖 wigolo 的项目事实、十工具架构、证据模型、安装接入、CLI/REST/Docker 用法与本地缓存知识库"
tags: [okf-bundle, blog-article, wigolo, mcp, ai-agent, local-first, web-search, developer-tools]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-09-16T20:30:00+08:00" }
---

# wigolo 博文 → OKF 知识包 转化规划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段工作流执行。

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 微信公众号公开文章 | https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w |
| 公众号 / 作者 | GHub开源甄选 / 小涛 | 原创，2026-09-15 07:01 发布于广东 |
| 访问控制 | 无（公开可访问） | `/s/<id>` 公开文章格式，无 share?code=/token=/邀请码参数 |
| 敏感度级别 | **公开内容** | 开源项目推介文，无个人隐私与商业秘密 |
| 工作流模式 | **标准工作流** | spec 在 `.trae/specs/okf-wiki-ecosystem/`，bundle 在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离预判 | **第三方综述（开源项目推介号）**，含厂商自述材料（README Benchmark） | 非官方号、非纯一手实测；营销叙事浓度中（"零费用""火得不行"）；关键命令经官方文档逐字核验 |

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是** | 含 `npx wigolo init --agents=claude-code`、`wigolo doctor`、`wigolo search`、`wigolo serve`、curl REST 调用、两条 `docker run`、LLM 环境变量配置，步骤顺序完整 |
| Q2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **是** | 有版本前提（Node 20+）、空间要求（1.5GB）、预期输出（doctor 全绿、返回摘录/评分）、作者"用了一段时间"的一手使用反馈；且全部命令经官方 README/docs 逐字核验一致 |

**判定：两问皆"是" → 技术教程/选型类骨架，设 examples/**

**骨架**：
```
jishu/ai/wigolo/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-what-is-wigolo.md                      # 项目身份与发布事实（What/When/Who）
│   ├── 01-ten-tools-and-evidence-model.md       # 十工具矩阵 + 证据/评分/诚实输出模型
│   └── 02-local-first-architecture.md           # 本地优先架构、隐私模型与四种部署形态
├── examples/
│   ├── index.md
│   ├── 00-install-and-agent-wiring.md           # init 接入 9 类 Agent + doctor 体检
│   ├── 01-cli-search-and-cache.md               # CLI 搜索/并行扇出/域名锁定/深度/缓存语义检索
│   └── 02-rest-docker-and-llm.md                # REST API + Docker 自托管 + LLM 配置
└── references/
    ├── index.md
    ├── article-source.md                        # 博文事实清单（F 编号双份登记之一）
    └── verification.md                          # P0 核验报告（含勘误四张清单）
```

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/wigolo/`（选定，直挂束） | ✅ | ① 主线实体 wigolo 是 AI Agent 的 MCP Web 情报工具，归 ai 生态；② 组内直挂束先例充分：单工具推介束（browseract/open-code-review/echobird）、微信博文转化束（free-llm-api-roundup、mattpocock-skills）均直挂本组；③ 名称独特无同名冲突 |
| `jishu/ai/ai-agent/` 子分组 | ❌ | 该组定位为"Agent 运行时框架与架构模式（工具调用循环/多代理编排/记忆系统/框架源码解读）"；wigolo 是被 Agent 调用的工具层服务，不是 Agent 框架 |
| 新建顶级分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**最终路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/wigolo/`

## 4. 时效性

| 项目 | 结论 |
|------|------|
| 博文发布时间 | 2026-09-15 |
| 官方核验时间 | 2026-09-16（GitHub API + main 分支 README/docs） |
| `stale_after` | **2026-12-31**（工具处于 Public Beta、更新频繁，年末复核） |
| 高时效字段 | Star 数（动态）、Beta 功能集、CLI 参数名、Docker 发布标签、免费 LLM 额度政策 |
| 已知边界声明 | ① Star 为 2026-09-16 时点快照；② Benchmark 为官方自述演示（单会话、Claude Fable 5），非第三方独立评测；③ 博文 `--limit` 与官方 headless 文档签名 `--max-results` 存在口径差异；④ `:full` 官方文档确认为构建目标，预构建标签未在文档确认 |

## 5. P0 必核验清单与结论摘要

| 核验对象（F 编号） | 类型 | 权威信源 | 结论 |
|--------------------|------|----------|------|
| 仓库存在/创建时间/语言/owner（F-003/F-005/F-006） | 日期身份 | GitHub API `repos/KnockOutEZ/wigolo` | ✅ 2026-04-12 创建、TypeScript、owner=User |
| Star「三千多颗」（F-005） | 动态数字 | GitHub API stargazers_count | ⚠️ 发文时口径，2026-09-16 实测 **5268**（时效差异，非硬错） |
| AGPL-3.0（F-006） | 许可证 | README license badge | ✅（API 为 NOASSERTION，以作者 badge/LICENSE 为准） |
| Node ≥20 / 1.5GB（F-015/F-016） | 版本要求 | README Quickstart、installation.md | ✅ 逐字一致，另确认支持 macOS/Linux/Windows |
| init/doctor/serve 命令与端口（F-016/F-018/F-020） | 命令 | README、cli.md | ✅ 3333、POST /v1/{tool}、OpenAPI 3.1 |
| 18 引擎 / 10 工具 / 免 key 范围（F-008/F-009/F-010） | 能力声明 | README Tools 表 | ✅ 18 adapters；10 工具；6 免 key + research/agent/answer 需 LLM（博文"两个"未计 search format=answer，补正） |
| 四工具对比测试（F-012） | 厂商自述 | README Benchmark 段 | ⚠️ 属实但为**官方自述演示**（Claude Fable 5 单会话，口径 July 2026），非独立评测 |
| Docker 镜像/slim/:full（F-022/F-023） | 部署 | installation.md | ✅ 镜像名与 stdio 命令逐字一致；slim 懒加载一致；⚠️ `:full` 文档仅确认构建目标 |
| Gemini/多 provider 环境变量（F-024/F-025） | 配置 | README、cli.md | ✅ 逐字一致；补充 WIGOLO_LLM_API_KEY 统一通道 |
| `--limit=3` CLI 示例（F-019） | 命令参数 | cli.md | ⚠️ headless 签名为 `--max-results`；`--limit` 为 `wigolo shell` 内参数 |
| GitHub Trending（F-005） | 曝光事实 | README 徽章 | ⚠️ 官方证据为 Trendshift（#79424），与 GitHub Trending 为不同产品，无法直接证实 |
| include_domains / search_depth（F-028/F-029） | 参数 | cli.md | ✅ `--include-domains`、`--search-depth` 存在（wire 名下划线/CLI kebab） |

**汇总**：P0/P1 核验 18 项 —— ✅ 14、⚠️ 4、❌ 0。无核心声明失败 → `status: stable`，4 项 ⚠️ 在 verification.md 完整勘误并在正文标注口径。

## 6. 三层知识拆分（知识地图）

| 博文内容层 | 映射篇目 | F 编号支撑 |
|-----------|---------|-----------|
| 发布事实层（项目是什么/何时开源/谁做的/什么许可） | concepts/00-what-is-wigolo.md | F-001~F-006、F-034~F-037、F-053 |
| 机制原理层（十工具、18 引擎、证据模型、诚实输出） | concepts/01-ten-tools-and-evidence-model.md | F-007~F-014、F-040~F-045 |
| 架构模式层（本地优先/隐私边界/MCP·REST·Docker·SDK 四形态） | concepts/02-local-first-architecture.md | F-011、F-020~F-025、F-046~F-052、F-054 |
| 可演练：安装接入 | examples/00-install-and-agent-wiring.md | F-015~F-018、F-038/F-039、F-054 |
| 可演练：CLI 搜索与缓存技巧 | examples/01-cli-search-and-cache.md | F-019、F-027~F-030、F-042、F-051 |
| 可演练：REST/Docker/LLM 进阶 | examples/02-rest-docker-and-llm.md | F-020~F-026、F-048~F-050 |

## 7. ADDED Requirements（验收标准）

- bundle 13 个文件齐备，每个 index.md 含隐藏 toctree，条目逐一对应磁盘文件
- 全部具体声明（数字/命令/版本/工具名）携带 F 编号，无 facts.md 之外编造
- 4 项 ⚠️ 勘误在正文呈现官方正确值并标注博文口径；Benchmark 标注"官方自述"
- frontmatter 双信源（博文 URL + GitHub 仓库/raw 文档），stale_after=2026-12-31
- 双份 F 编号一致（facts.md ↔ article-source.md 均为 F-001~F-055，连续无跳号）
- ai 组 index 导航表 + toctree 接入（187→188 束）；bundles/index.md 计数三处同步（ai 187→188、jishu 406→407、total 538→539、组 59 不变）
- V 阶段执行四视角审查与 8 项机械门禁；invoke gates 不可用时执行手动等效清单并在 log.md 注明
