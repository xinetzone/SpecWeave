# planning-with-files OKF 知识包 Spec

## Why

用户要求使用七概念方法论编排（seven-concepts-cmd）对微信公众号文章《planning-with-files:像 Manus 一样工作》进行系统性学习与知识萃取,并将成品作为 OKF bundle 存放到 awesome-okf-xs 文档库。该文章介绍了 GitHub 开源项目 OthmanAdi/planning-with-files(23k+ Star),将 Manus(被 Meta 20 亿美元收购)的"上下文工程"方法论开源化。通过 R→I→E→V→C 五阶段链路,从文章事实中萃取可复用的 AI Agent 上下文工程模式,沉淀为结构化知识资产。

## What Changes

- 按 R 阶段(复盘):采集文章客观事实(≥20 条,无因果词)——项目元数据、3-File Pattern、Hooks 6 动作、4 大规则、5 种安装、社区生态
- 按 I 阶段(洞察):提炼 3 条核心洞察(含四元组:现象+根因+影响+建议)——AI Agent 瓶颈本质、RAM-Disk 范式映射、Hooks 自动化价值
- 按 E 阶段(萃取):产出 1-2 个可迁移模式文档(含触发场景+核心步骤+反模式+迁移验证)——3-File Pattern 模式、Hooks 自动化模式
- 按 V 阶段(对抗审查):对萃取的模式执行多视角攻击(魔鬼代言人/新人/老板/未来),验证可迁移性与边界条件
- 按 C 阶段(原子提交):将产出物作为 OKF bundle 入库到 `doc/bundles/jishu/ai/planning-with-files/`,更新上级 index 导航
- **BREAKING**:无(新增知识包,不修改现有文档)

## Impact

- Affected specs: 无直接修改;产出为 awesome-okf-xs 文档库的新增 bundle
- Affected code: 无代码改动;产出为 OKF v0.2 格式 Markdown 文档
- 关联资产:
  - [jishu/ai/index.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/index.md) 需新增 planning-with-files 条目
  - [jishu/ai/context-optimization/index.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/context-optimization/index.md) 上下文优化束可交叉引用
  - [jishu/ai/ai-engineering-methodology/index.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/ai-engineering-methodology/index.md) AI 工程方法论束可交叉引用

## ADDED Requirements

### Requirement: R 阶段 — 文章事实采集(G1 质量门)

系统 SHALL 从文章中采集≥20 条客观事实,纯描述性,不含因果推断词("因为"/"导致"/"所以")。

#### Scenario: 事实采集完整

- **WHEN** R 阶段执行
- **THEN** 产出 `facts.md`,包含≥20 条客观事实
- **AND** 事实覆盖:项目元数据(名称/作者/Star/许可证/发布时间)、Manus 收购事件、Context Window 4 类痛点、3-File Pattern 三文件职责、RAM-Disk 原理映射、Hooks 6 个自动动作、4 大核心规则、5 种 IDE 安装方式、社区生态 5 个扩展项目、实测对比数据
- **AND** G1 质量门通过:全文无因果推断词,纯客观描述

### Requirement: I 阶段 — 核心洞察提炼(G2 质量门)

系统 SHALL 提炼 3 条核心洞察,每条包含四元组(现象描述+根因分析+影响评估+改进建议)。

#### Scenario: 洞察四元组完整

- **WHEN** I 阶段执行
- **THEN** 产出 `insights.md`,包含 3 条核心洞察
- **AND** 洞察1:AI Agent 瓶颈在工程化方法而非模型能力(现象:50 次工具调用后目标漂移;根因:Context Window 是易失 RAM;影响:复杂任务不可靠;建议:文件系统外存)
- **AND** 洞察2:RAM-Disk 范式映射是上下文工程的底层原理(现象:3-File Pattern 朴素但有效;根因:Context Window=RAM 易失,Filesystem=Disk 持久;影响:跨模型跨工具通用;建议:重要信息写磁盘)
- **AND** 洞察3:Hooks 自动化降低对 AI 自觉性的依赖(现象:4 大规则需 AI 自觉遵守;根因:无自动化触发时规则形同虚设;影响:可靠性取决于 AI 服从性;建议:关键节点自动触发)
- **AND** G2 质量门通过:每条洞察四元组完整

### Requirement: E 阶段 — 可迁移模式萃取(G3 质量门)

系统 SHALL 萃取 1-2 个可迁移模式,每个模式包含触发场景+核心步骤+反模式+迁移验证。

#### Scenario: 模式文档完整

- **WHEN** E 阶段执行
- **THEN** 产出 `patterns.md`,包含 1-2 个结构化模式
- **AND** 模式1:3-File Pattern(文件系统外存模式)——触发场景:多步骤 AI Agent 任务;核心步骤:创建 task_plan/findings/progress 三文件 + 每阶段更新;反模式:单文件混杂所有信息/不更新进度;迁移验证:SpecWeave spec.md/tasks.md/checklist.md 已验证
- **AND** 模式2:Hooks 自动化模式——触发场景:需 AI 在关键节点执行固定动作;核心步骤:识别关键节点→编写 Hook 脚本→自动触发;反模式:依赖 AI 自觉性/过度自动化;迁移验证:SpecWeave 阶段守卫可改造为 Hooks
- **AND** G3 质量门通过:每个模式含触发场景+核心步骤+反模式+迁移验证

### Requirement: V 阶段 — 对抗审查

系统 SHALL 对萃取的模式执行多视角对抗审查,至少覆盖 4 个视角(魔鬼代言人/新人/老板/未来)。

#### Scenario: 对抗审查执行

- **WHEN** V 阶段执行
- **THEN** 产出审查意见,记录每个视角的攻击点与修正建议
- **AND** 魔鬼代言人:质疑"20 亿归因单一方法论"过度简化,质疑文件膨胀风险
- **AND** 新人视角:3-File Pattern 学习成本低但 Hooks 配置复杂,需提供 quickstart
- **AND** 老板视角:ROI 评估——5 分钟安装成本 vs 复杂任务可靠性提升
- **AND** 未来视角:Context Window 扩大(1M context)后方法论是否仍有效
- **AND** 审查意见已融入最终产出物

### Requirement: C 阶段 — OKF bundle 入库

系统 SHALL 将 R/I/E/V 阶段产出物作为 OKF bundle 入库到 awesome-okf-xs 文档库。

#### Scenario: bundle 入库完整

- **WHEN** C 阶段执行
- **THEN** 在 `doc/bundles/jishu/ai/planning-with-files/` 创建以下文件
- **AND** `index.md`:OKF v0.2 frontmatter(type: group)+ 束简介 + toctree 引用全部子文档
- **AND** `facts.md`:R 阶段事实清单
- **AND** `insights.md`:I 阶段核心洞察
- **AND** `patterns.md`:E 阶段萃取模式 + V 阶段审查记录
- **AND** `log.md`:CMD-LOG 执行日志
- **AND** 更新 `jishu/ai/index.md` 分组导航表,新增 planning-with-files 条目
- **AND** 所有文件遵循 OKF v0.2 frontmatter 规范(type 必填,推荐 title/description/sources/tags)
- **AND** 所有文件使用中文正文 + kebab-case 英文文件名
- **AND** Markdown 交叉引用使用相对路径

## MODIFIED Requirements

无

## REMOVED Requirements

无
