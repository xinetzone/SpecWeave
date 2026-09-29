---
id: "agent-knowledge-base-okf-wiki"
title: "微信博文→OKF Wiki：给项目建 Agent 知识库，一套完整方法"
type: okf-wiki-spec
source: "https://mp.weixin.qq.com/s/307ZX4doB9hoTP-u6hVDDw"
created: 2026-09-28
workflow: "process:blog-article-to-okf-wiki@R-I-E-V-C"
---

# 微信博文 → OKF Wiki 转化 Spec

## 1. 任务定义

将微信公众号「Datawhale干货」文章《给项目建Agent知识库，一套完整方法来了！》（作者：王大鹏，2026-09-24）按 OKF v0.2 转化为可溯源知识包。

- 内容级别：**公开（Public）**——公开发布的公众号文章，无 token/code 访问控制
- 方法论链路：R（事实采集+核验）→ I（骨架/归属/拆分）→ E（bundle 生成）→ V（对抗审查+机械门禁）→ C（原子提交，待用户指令）
- 目标 bundle：`jishu/ai/ai-agent/agent-knowledge-base/`

## 2. 骨架判定（操作可复现性两问）

| 判问 | 结论 | 依据 |
|---|---|---|
| ① 是否有读者可照做的安装/配置/代码/调用/实测流程？ | 否 | 全文为方法论论述，无工具、命令、代码、配置步骤 |
| ② 是否经作者实测、具备版本/输入输出/步骤顺序的可复现性？ | 否 | 无版本号、无具体输入输出，案例为说明性思想实验 |

→ **不设 `examples/`**。骨架：`index + concepts/ + references/ + log.md`，description 标注"方法论，非操作教程"。

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/ai-agent/` | ✅ 采纳 | 主线实体为"Agent 知识库/专家底座"工程方法论；该组已有非源码类先例（pi-agent-harness 博文综述、a2a-mcp-convergence 技术分析、llm-hallucination-governance 法学论文等），"📰 产品资讯"板块可容纳 |
| `jishu/ai/datawhale/` | ❌ 排除 | Datawhale 是信源而非主线实体；该组 18 束全部对应 datawhalechina 具体 GitHub 仓库，本文无对应仓库，语义不符 |

单篇博文不新建分组（最小变更）。

## 4. 三层知识拆分（concepts 4 篇）

| 篇目 | 知识层 | 覆盖 F 编号 |
|---|---|---|
| `00-judgment-first-slot-structure` | 问题结构层：HTTP 500 误判案例、判断优先、预期参照、机制与槽位 | F-005 ~ F-020 |
| `01-normal-process-extraction` | 流程梳理层：从完整业务流程出发、文档与代码核对、留问与冲突、专家认知公式① | F-021 ~ F-030 |
| `02-evidence-and-expert-base` | 验证与底座层：多源冲突处理、依据/适用条件/待确认、专家知识公式②、专家底座、求证方法、解题能力公式③ | F-031 ~ F-045 |
| `03-knowledge-layering-iteration` | 分层与迭代层：五类知识按更新速度分存、复盘结论归位、用新问题检查旧知识、定期复核 | F-046 ~ F-060 |

## 5. P0 核验计划（勘误四张清单）

| 清单 | 适用性 | 结论 |
|---|---|---|
| ① 日期/版本表 | 文章发布日期 | 2026-09-24，搜狐 Datawhale 认证号转载页时间戳旁证；微信原文日期未独立提取（⚠️ 单旁证，标注口径） |
| ② 成效数字溯源表 | 不适用 | 全文无提效倍数/工时/成本数字 |
| ③ 口径对照表 | 不适用 | 无规模/份额数字 |
| ④ 引文逐字核对表 | 部分适用 | 无外部人物引语；三个乘法公式为作者自创框架（作者明示"设计简写，不是数学计算"），一律按"作者观点"呈现，不加引号、不固化为公理 |

另核验：HTTP 500 语义（RFC 9110/MDN，服务器端错误不表征请求副作用）；Datawhale 社区身份（公开开源社区）。

→ 未发现源文硬错误，`status: stable`；`stale_after: 2027-06-30`（方法论性质，半年复核点）。

## 6. 交付清单

**bundle（子模块 awesome-okf-xs）**：

- `agent-knowledge-base/index.md`、`log.md`
- `concepts/index.md` + 4 篇概念文档
- `references/index.md` + `article-source.md`（F 编号双份登记）+ `verification.md`
- 组索引 `ai-agent/index.md`：53 → 54
- 总索引 `bundles/index.md`：571 → 572；jishu 431 → 432；ai 211 → 212

**spec（主仓库）**：本目录 `spec.md` + `facts.md`

## 7. 质量门

- G1（事实无推断词）：facts.md 纯客观登记，因果性论断均归为"作者观点/文章论点"
- G2（洞察四元组）：概念文档按"现象+机制+影响+做法"组织
- G3（模式可迁移）：三篇方法论含触发条件+核心步骤+反模式（见 V 阶段核验）
- G4（原子行动项）：C 阶段按显式文件列表原子提交，不 push
