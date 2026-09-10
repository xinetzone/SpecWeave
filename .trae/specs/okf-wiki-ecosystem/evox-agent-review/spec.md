---
theme: okf-wiki-ecosystem
project: evox-agent-review
created: 2026-09-09
status: active
---

# EvoX 国产 Agent 平台分析 — Spec 规划

## 内容敏感度预检

| 项目 | 结论 |
|------|------|
| 信源 URL | `https://mp.weixin.qq.com/s/2ajOzriMAKqi8f3pu5N7zw`（微信公开文章，无访问控制参数） |
| 判定 | **公开内容** → 标准工作流 |
| Spec 目录 | `.trae/specs/okf-wiki-ecosystem/evox-agent-review/` |
| 产出物路径 | `projects/awesome-okf-xs/doc/bundles/jishu/ai/evox-agent-review/` |
| 可提交 Git | 是 |

## 归属位置分析

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/agent-platform-notes/evox-agent-review/`（**选定**） | ✅ | ① 文章主线实体为 EvoX（evomap.ai），国产通用 Agent 平台；② 分组内已有 Octo（明略科技）等多 Agent 协作平台散篇，定位一致；③ 同主题可交叉引用 `concepts/octo-platform.md`；④ 单篇博文不新建顶级分组，符合最小变更原则 |
| `jishu/ai/` 同级新建 `evox-agent-review/` | ❌ | 会脱离 agent-platform-notes 聚合束，破坏分组语义；违反单篇博文不新建分组的规则 |
| `jishu/ai/ai-agent/` | ❌ | 源码/框架类，主题不符（本文是产品分析，非框架解读） |

**选定路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/agent-platform-notes/evox-agent-review/`

## 性质分流与目录骨架判定

| 项目 | 结论 |
|------|------|
| 内容性质 | **商业分析/技术战略资讯类**（产品发布+团队背景+差异化能力展示，含案例演示但无可复现操作） |
| 操作可复现性两问 | Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？→ **否**（案例为平台功能展示，非可复现教程）；Q2：这些流程是否经作者实测、具备可复现性？→ **否** |
| 目录骨架 | `index.md` + `concepts/` + `references/` + `log.md`（**无 `examples/`**） |
| index 顶部声明 | "商业分析/战略资讯，非源码教程" |
| stale_after | `2027-03-01`（约6个月，资讯类时效短） |
| 厂商自宣属性 | 作者为第三方博主，但全文核心成效数据（563题/26%/71%）为厂商主导实验，需在 index 顶部加"厂商自述数据"提示块 |

## 知识结构三层拆分（I 阶段）

| 博文内容层 | 映射篇目 | 说明 |
|-----------|---------|------|
| 事件时间线层（What/When/Who） | `concepts/00-evox-timeline.md` | EvoX 发布背景、Beta上线时间、核心团队、产品功能概览 |
| 驱动逻辑层（Why：蜂群+自进化机制原理） | `concepts/01-swarm-self-evolution-mechanism.md` | 蜂群架构（多Agent并行协作）+ 自进化机制（点赞沉淀记忆）原理分析 |
| 竞争/格局层（外部对标+案例实践） | `concepts/02-competitive-positioning-and-cases.md` | 与 Octo 等多 Agent 平台对标；三个案例（筛岗+简历/香港打卡手册/反诈游戏）实践分析 |

## 事实采集计划（R 阶段）

- **F-001 ~ F-0XX**：博文全文可验证事实编号登记
- **P0 核心声明**：F-001（563题逻辑题，单线程26% vs 蜂群71%）— 已通过 WebSearch 多源交叉确认（AITNTNews、牛客网均确认相同数据），为厂商/客户自述，正文需标注
- **信源距离预判**：第三方博主报道 + 厂商主导实验数据 → 成效数字默认 P0 必核验，正文标注"厂商/客户自述"
- **勘误四清单重点**：①日期/版本表（发布时间/Beta上线时间核对）；②成效数字溯源（563题数据独立出处）；③无引文逐字核对需求（无官方引文）

## 父级索引接入计划（V 阶段）

- `agent-platform-notes/index.md` 新增条目 + toctree 追加
- `bundles/index.md` 全库计数同步
