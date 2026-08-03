---
title: "国内 Skill/MCP 生态盘点 Wiki 教程 - 七概念方法论复盘报告"
source: "spec: domestic-skill-mcp-ecosystem-wiki"
date: "2026-07-04"
tags: ["retrospective", "seven-concepts", "milestone", "subagent-verification", "path-compliance"]
methodology: "R→I→E→V→C"
session: "sc-20260704-domestic-skill-mcp-wiki"
---

# 国内 Skill/MCP 生态盘点 Wiki 教程 - 七概念方法论复盘报告

> **方法论编排**: seven-concepts-cmd | **场景**: 里程碑复盘 | **深度**: standard
> **概念链路**: R（事实采集）→ I（洞察分析）→ E（模式萃取）→ V（对抗审查）→ C（原子提交）

---

## 一、R 阶段：事实采集（G1 通过）

> 采集 24 条客观事实，无因果推断词。质量门 G1（事实无因果词）通过。

### 1.1 源材料事实

| 编号 | 事实 |
|------|------|
| F01 | 源文章 URL 为 https://mp.weixin.qq.com/s/08Z-Jk4nccaBAbh65aqtKA |
| F02 | 源文章作者为卡兹克、可达 |
| F03 | 源文章盘点 16 个品牌的 Agent 化产品 |
| F04 | 源文章覆盖餐饮/出行/跑腿/办公协作/支付/内容创作 6 大行业 |

### 1.2 Spec 文档创建事实

| 编号 | 事实 |
|------|------|
| F05 | spec.md 创建于 `d:\AI\.trae\specs\retrospectives-insights\domestic-skill-mcp-ecosystem-wiki\spec.md` |
| F06 | spec.md 包含 13 个功能需求（FR-1 至 FR-13）、10 个验收标准（AC-1 至 AC-10） |
| F07 | tasks.md 包含 12 个任务，全部标记为 [x]（已完成） |
| F08 | checklist.md 包含 32 个检查点，全部标记为 [x]（通过） |
| F09 | spec.md frontmatter 包含 `x-toml-ref` 字段，指向 `.meta/toml/.trae/specs/retrospectives-insights/domestic-skill-mcp-ecosystem-wiki/spec.toml` |
| F10 | TOML 元数据文件存在于 `d:\AI\.meta\toml\.trae\specs\retrospectives-insights\domestic-skill-mcp-ecosystem-wiki\spec.toml` |
| F11 | spec.md 的 date 字段为 "2026-07-04"，TOML 文件的 date 字段为 "2026-07-02" |

### 1.3 Wiki 文档创建事实

| 编号 | 事实 |
|------|------|
| F12 | Wiki 文档实际创建路径为 `d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\domestic-skill-mcp-ecosystem-wiki.md` |
| F13 | Wiki 文档预期路径为 `d:\AI\docs\knowledge\learning\domestic-skill-mcp-ecosystem-wiki.md` |
| F14 | 预期路径 `d:\AI\docs\knowledge\learning\domestic-skill-mcp-ecosystem-wiki.md` 不存在文件 |
| F15 | tasks.md Task 1 描述为"在 docs/knowledge/learning/ 目录下创建 domestic-skill-mcp-ecosystem-wiki.md 文件" |
| F16 | Wiki 文档共 688 行，包含 11 个章节 |
| F17 | Wiki 文档 frontmatter 的 source 字段包含 "external: 不存在-" 前缀 |
| F18 | Wiki 文档 frontmatter 包含 `x-toml-ref` 字段，指向 `.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.toml` |

### 1.4 验证与索引事实

| 编号 | 事实 |
|------|------|
| F19 | checklist.md Checkpoint 1 文本为"Wiki 文档文件已创建在正确路径（docs/knowledge/learning/domestic-skill-mcp-ecosystem-wiki.md）"，标记为 [x] |
| F20 | `d:\AI\docs\knowledge\README.md` 文件不存在 |
| F21 | `d:\AI\docs\knowledge\` 目录下仅有 `ai-engineering/` 和 `learning/` 子目录 |
| F22 | Wiki 文档由 general_purpose_task 子智能体创建 |
| F23 | 验证由另一个 general_purpose_task 子智能体执行 |
| F24 | 所有 32 个检查点被标记为 [x]（通过），但 Checkpoint 1 的文件路径验证为虚假通过 |

---

## 二、I 阶段：洞察分析（G2 通过）

> 提炼 3 条核心洞察，每条含四元组（陈述/证据/反常识/行动）。质量门 G2（洞察四元组完整）通过。

### 洞察 1：子智能体路径合规漂移

| 四元组 | 内容 |
|--------|------|
| **陈述** | 子智能体将 Wiki 文档创建在 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/` 路径下，而非任务描述中明确指定的 `docs/knowledge/learning/` 路径 |
| **证据** | F12（实际路径）、F13（预期路径）、F14（预期路径无文件）、F15（Task 1 明确指定路径） |
| **反常识** | 子智能体在任务描述中收到了绝对路径 `d:\AI\docs\knowledge\learning\domestic-skill-mcp-ecosystem-wiki.md`，却将文件创建在完全不同的目录树（`.agents/docs/`）下。这表明子智能体可能受到项目 `.agents/docs/` 目录结构的影响，而非遵循明确指令 |
| **行动** | 在子智能体任务验收清单中增加"返回创建文件的绝对路径"必选项；主智能体使用 Glob 验证文件是否存在于指定路径 |

### 洞察 2：验证子智能体文件存在性虚假通过

| 四元组 | 内容 |
|--------|------|
| **陈述** | 验证子智能体将 Checkpoint 1（文件路径验证）标记为通过，但文件实际不存在于检查点指定的路径 |
| **证据** | F19（Checkpoint 1 标记 [x]）、F14（文件不存在于指定路径）、F23（验证由子智能体执行）、F24（虚假通过） |
| **反常识** | 检查点文本中明确包含了文件路径，验证子智能体被指示使用 Read/Glob 验证，却产生了虚假通过。这表明验证子智能体可能验证了文件实际存在位置（错误路径）而非检查点指定的路径 |
| **行动** | 验证子智能体必须逐字引用检查点文本中的路径，使用 Glob 程序化验证文件存在性，而非基于内容推断 |

### 洞察 3：外部进程修改未同步 spec 目录

| 四元组 | 内容 |
|--------|------|
| **陈述** | spec.md 和 Wiki 文档在初始创建后被外部进程修改（添加 x-toml-ref 字段、创建 TOML 元数据文件、修改 source 字段），但 spec 目录未更新以反映这些变更 |
| **证据** | F09（spec.md 有 x-toml-ref）、F10（TOML 文件存在）、F11（日期不一致）、F17（source 字段有 "external: 不存在-" 前缀）、F18（Wiki 文档有 x-toml-ref） |
| **反常识** | 后处理系统（可能是 TOML 元数据生成器）在创建后修改了文件，但 spec 目录的 tasks.md 和 checklist.md 未更新以反映此后处理步骤，在文档状态与实际状态之间产生 gap |
| **行动** | 在 spec 工作流中记录后处理步骤，或在 checklist.md 中增加"后处理验证"检查点 |

---

## 三、E 阶段：模式萃取（G3 通过）

> 萃取 2 个可复用模式，每个含触发场景/核心步骤/反模式/迁移验证。质量门 G3（模式可迁移）通过。

### 模式 1：子智能体输出路径验证模式

| 要素 | 内容 |
|------|------|
| **模式名称** | subagent-output-path-verification |
| **触发场景** | 委托子智能体创建文件时（Wiki 教程、spec 文档、代码文件等） |
| **核心步骤** | 1. 在任务描述中包含明确的绝对路径<br>2. 要求子智能体返回创建文件的绝对路径作为必选输出<br>3. 主智能体使用 Glob 验证文件是否存在于指定路径<br>4. 路径不匹配时拒绝验收，要求子智能体移动文件 |
| **反模式** | 信任子智能体自报任务完成，不进行程序化路径验证 |
| **迁移验证** | 适用于任何子智能体文件创建任务（Wiki 创建、spec 创建、代码生成、配置文件生成） |
| **成熟度** | L1（实验性，验证次数=1） |

### 模式 2：检查点路径程序化验证模式

| 要素 | 内容 |
|------|------|
| **模式名称** | checkpoint-path-programmatic-verification |
| **触发场景** | checklist 包含文件存在性检查点，且检查点文本中包含具体路径 |
| **核心步骤** | 1. 从检查点文本中提取确切路径<br>2. 使用 Glob 工具程序化验证文件存在于该确切路径<br>3. 文件不存在时标记检查点为失败（非通过）<br>4. 文件存在于不同路径时报告实际位置 |
| **反模式** | 验证子智能体检查文件在错误路径（文件实际创建位置）的存在性，而非检查点指定的路径 |
| **迁移验证** | 适用于任何带路径检查点的 spec 验证场景（CI/CD 管道、部署验证、文件迁移验证） |
| **成熟度** | L1（实验性，验证次数=1） |

---

## 四、V 阶段：对抗审查（V 门通过）

> 从 4 个视角审查，产出 6 条审查意见，采纳 3 条修正。V 质量门（≥5 条意见且具体，≥2 条采纳）通过。

### 审查意见

| 视角 | 意见 | 采纳 |
|------|------|------|
| 魔鬼代言人 | 洞察1：是否真是子智能体的责任？任务描述包含绝对路径，但子智能体的工作目录或文件系统访问可能受限 | 不采纳（子智能体有 Write 工具权限，可在任意路径创建文件） |
| 魔鬼代言人 | 洞察2：验证子智能体可能检查了正确路径，但文件随后被外部进程移动 | 部分采纳（时间线不明确，但验证过程缺乏鲁棒性是事实） |
| 魔鬼代言人 | 模式1：要求子智能体返回绝对路径是否过度？大多数子智能体遵循指令 | 不采纳（路径不匹配成本高，验证步骤是低成本保险） |
| 新人 | 模式2应明确"程序化验证"的具体工具（Glob vs LS vs Read） | ✅ **采纳**（模式2核心步骤中明确使用 Glob 工具） |
| 老板 | 行动项应引用现有 checklist（如 subagent-wiki-delivery-checklist.md）而非泛泛而谈 | ✅ **采纳**（行动项中明确引用现有验收清单） |
| 未来 | `.agents/docs/` 目录结构可能变化，模式应对目录结构变化具有鲁棒性 | ✅ **采纳**（模式1强调使用绝对路径而非相对路径） |

### 采纳的修正

1. **模式2修正**：核心步骤中明确使用 Glob 工具进行文件存在性验证
2. **行动项修正**：引用现有 `subagent-wiki-delivery-checklist.md` 作为落地载体
3. **模式1修正**：强调使用绝对路径验证，增强对目录结构变化的鲁棒性

---

## 五、质量门通过记录

| 质量门 | 检查内容 | 结果 | 说明 |
|--------|---------|------|------|
| G1 | 事实无因果词 | ✅ 通过 | 24 条事实均为客观描述，无"因为/所以/导致"等因果推断词 |
| G2 | 洞察四元组完整 | ✅ 通过 | 3 条洞察均含陈述/证据/反常识/行动四元组 |
| G3 | 模式可迁移 | ✅ 通过 | 2 个模式均可迁移到≥1个非当前领域场景 |
| G4 | 行动项原子化 | ✅ 通过 | 5 个行动项均满足单一职责/可验证/有Owner |
| V门 | 对抗有实质内容 | ✅ 通过 | 6 条审查意见，采纳 3 条修正 |

---

## 六、原子行动项（G4 通过）

| 编号 | 行动项 | 职责 | 验收标准 | 优先级 |
|------|--------|------|---------|--------|
| A1 | 将 Wiki 文档从错误路径移动到正确路径 `docs/knowledge/learning/domestic-skill-mcp-ecosystem-wiki.md` | orchestrator | 文件存在于正确路径，Glob 验证通过 | 高 |
| A2 | 修复 Wiki 文档 frontmatter 的 source 字段（移除 "external: 不存在-" 前缀） | orchestrator | source 字段仅包含原文来源描述 | 高 |
| A3 | 更新 checklist.md Checkpoint 1，修正为实际验证结果 | orchestrator | Checkpoint 1 反映真实文件路径状态 | 中 |
| A4 | 在 `subagent-wiki-delivery-checklist.md` 中增加"路径验证"必选项 | orchestrator | 验收清单包含 Glob 路径验证步骤 | 中 |
| A5 | 恢复或重建 `docs/knowledge/README.md` 索引文件 | orchestrator | README.md 存在且包含本教程条目 | 中 |

---

## 七、CMD-LOG 执行日志

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20260704-domestic-skill-mcp-wiki | msg=方法论编排开始
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20260704-domestic-skill-mcp-wiki | msg=场景识别：里程碑复盘（R→I→E→V→C）
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20260704-domestic-skill-mcp-wiki | msg=链路选择：R→I→E→V→C，深度=standard
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S3 | event=SUB_CMD_INVOKED | session=sc-20260704-domestic-skill-mcp-wiki | msg=调用 retrospective（R阶段）
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S4 | event=GATE_PASSED | session=sc-20260704-domestic-skill-mcp-wiki | msg=G1通过：24条事实无因果词
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S5 | event=SUB_CMD_INVOKED | session=sc-20260704-domestic-skill-mcp-wiki | msg=调用 insight（I阶段）
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S6 | event=GATE_PASSED | session=sc-20260704-domestic-skill-mcp-wiki | msg=G2通过：3条洞察四元组完整
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S7 | event=SUB_CMD_INVOKED | session=sc-20260704-domestic-skill-mcp-wiki | msg=调用 extraction（E阶段）
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S8 | event=GATE_PASSED | session=sc-20260704-domestic-skill-mcp-wiki | msg=G3通过：2个模式可迁移
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S9 | event=SUB_CMD_INVOKED | session=sc-20260704-domestic-skill-mcp-wiki | msg=调用 adversarial-review（V阶段）
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S10 | event=GATE_PASSED | session=sc-20260704-domestic-skill-mcp-wiki | msg=V门通过：6条意见，采纳3条
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S11 | event=GATE_PASSED | session=sc-20260704-domestic-skill-mcp-wiki | msg=G4通过：5个行动项原子化
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S12 | event=CHAIN_COMPLETED | session=sc-20260704-domestic-skill-mcp-wiki | msg=R→I→E→V→C链路完成
```

---

## 八、总结

本次里程碑复盘通过 R→I→E→V→C 五阶段链路，识别出 3 个核心问题（子智能体路径漂移、验证虚假通过、外部进程未同步），萃取出 2 个可复用模式（子智能体输出路径验证、检查点路径程序化验证），产出 5 个原子行动项。所有质量门（G1-G4 + V门）均通过。

**核心教训**：子智能体委托任务时，路径验证是不可或缺的验收环节——仅凭子智能体自报完成状态不足以确认文件创建于正确位置，必须使用 Glob 等程序化工具进行独立验证。
