---
id: "retrospective-forum-posting-skill-optimization-export"
title: "导出建议 — 改进项、行动计划与模式萃取"
source: "forum-posting skill optimization session"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/export-suggestions.toml"
---
# 导出建议 — 改进项、行动计划与模式萃取

## 一、改进建议

| 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|------|---------|--------|---------|------|
| 三层路由仅在"工作目录在vendor内"时触发，导致根目录任务遗漏vendor方法论资产 | 在AGENTS.md启动协议中增加"任务类型预检"步骤，显式列出需要路由到vendor的任务类型 | 高 | 减少类似"优化skill却不用skill-creator"的路由遗漏 | ✅ 已完成（AGENTS.md步骤2.0+vendor方法论资产表） |
| 启动协议缺少自检检查点，容易跳步 | 在步骤4（加载Skill执行任务）前增加结构化自检问题清单 | 高 | 防止"读了但没匹配路由表"的浅尝辄止 | ✅ 已完成（AGENTS.md步骤3.5） |
| 缺乏SpecWeave专属的Skill开发补充规范 | 在.agents/rules/下创建skill-development.md，整合五要素模型、双方案模式、资产盘点、验证清单 | 高 | 将复盘萃取的最佳实践固化为可执行规范 | ✅ 已完成（.agents/rules/skill-development.md） |
| Skill创建缺少标准化模板 | 基于本次提炼的五要素模型，在`.agents/skills/`下创建SKILL-TEMPLATE.md | 中 | 新Skill有统一结构参考，降低质量方差 | ✅ 已完成（.agents/skills/SKILL-TEMPLATE.md，含五要素标注和检查清单） |
| vendor资产索引不够直观 | 在vendor/AGENTS.md或根AGENTS.md中增加"vendor方法论资产清单"，按任务类型映射（如skill优化→skill-creator） | 中 | Agent在启动协议阶段可以快速定位vendor资产 | ✅ 已完成（根AGENTS.md vendor方法论资产表 + vendor/AGENTS.md 按任务类型索引章节） |
| Context恢复场景下认知视野收窄 | 在检测到session为context continuation时，提示/自动重新执行启动协议 | 中 | 防止长会话后路由规范遗漏 | ✅ 已完成（AGENTS.md步骤2.2） |
| 缺乏Skill质量自动化检查手段 | 开发Skill lint脚本（如`.agents/scripts/check-skill-quality.py`），自动检测description触发词、长度、Why解释、检查清单等要素 | 低（调整自中） | 新建/优化Skill时有自动化质量门禁，减少人工review负担 | ✅ 已完成（.agents/scripts/check-skill-quality.py，支持评分/JSON/verbose输出） |
| 用户反馈缺少快速分类框架 | 建立反馈类型快速识别机制（流程缺失/质量问题/需求偏差） | 低 | 加速问题定位，减少误判 | ✅ 已完成（pattern-feedback-wording-diagnosis模式入库） |

## 二、行动计划

| 优先级 | 改进项 | 具体措施 | 建议时间 | 状态 |
|--------|--------|---------|---------|------|
| 高 | 三层路由任务类型预检 | 修改AGENTS.md启动协议步骤2，增加任务类型与vendor资产映射表 | 2026-06-29 | ✅ 已完成 |
| 高 | 启动协议自检检查点 | 在步骤4前增加3个自检问题：vendor资产匹配？规范读完？相关skill加载？ | 2026-06-29 | ✅ 已完成 |
| 高 | Context恢复协议重执行 | 在session continuation检测点增加启动协议重执行提示 | 2026-06-29 | ✅ 已完成 |
| 高 | SpecWeave Skill开发补充规范 | 创建.agents/rules/skill-development.md，固化五要素模型等最佳实践 | 2026-06-29 | ✅ 已完成 |
| 中 | Skill模板创建 | 在`.agents/skills/`下创建SKILL-TEMPLATE.md，包含五要素结构、双方案框架、Why解释示例、安全检查清单、使用验证清单 | 2026-06-29（提前完成） | ✅ 已完成 |
| 中 | vendor方法论资产清单（vendor/AGENTS.md） | 在vendor/AGENTS.md中增加"按任务类型索引"章节，显式列出skill-creator等9个vendor skill和flexloop规则体系的任务类型映射，含Why解释 | 2026-06-29（提前完成） | ✅ 已完成 |
| 低 | Skill lint脚本 | 开发`.agents/scripts/check-skill-quality.py`，检测核心要素完整性（description触发词、长度<500行、Why解释、安全清单、相对路径），输出评分和改进建议 | 2026-07-02 | ✅ 已完成（提前完成，支持--score/--json/--verbose/--threshold参数） |
| 低 | 反馈分类框架 | 基于pattern-feedback-wording-diagnosis模式建立用户反馈措辞→问题类型的快速映射规则，整合到skill-creator或独立文档 | 2026-07-03 | ✅ 已完成（模式入库governance-strategy/feedback-wording-diagnosis.md） |

## 三、模式成熟度更新

| 模式 ID | 模式名称 | 成熟度 | 触发原因 | 当前状态 |
|---------|---------|--------|---------|---------|
| pattern-skill-description-seo | Skill Description SEO模式 | L1（首次提炼） | 本次forum-posting优化验证了description对trigger的关键作用 | ✅ 已整合进skill-five-elements-model要素1，不单独入库 |
| pattern-browser-automation-dual-scheme | 浏览器自动化双方案决策树模式 | L1（首次提炼） | 双方案+决策树设计有效降低了Agent方案选择负担 | ✅ 已整合进skill-five-elements-model要素2，不单独入库 |
| pattern-mcp-utility-functions | MCP工具函数封装模式 | L1（首次提炼） | 4个JS工具函数显著减少了重复代码和出错概率 | ⏸️ 待后续评估（代码级模式，本次先不入库） |
| pattern-skill-five-elements | Skill五要素模型 | L1（首次提炼） | 从skill-creator原则+本次实践中提炼的高质量Skill结构模型 | ✅ 已入库（ai-collaboration/skill-five-elements-model.md） |
| pattern-process-vs-experience | 流程合规vs经验直觉区分模式 | L1（首次提炼） | 识别出"凭经验做对"和"按方法论做对"的本质差异，强调可预测性优于偶然正确性 | ✅ 已入库（governance-strategy/process-vs-experience-intuition.md） |
| pattern-nonlinear-correction-cost | 协议违规非线性纠偏成本模式 | L1（首次提炼） | 前置小成本（读规范）避免后续大成本（返工重构），地基错误类比 | ✅ 已入库（governance-strategy/nonlinear-correction-cost.md） |
| pattern-feedback-wording-diagnosis | 用户反馈措辞诊断模式 | L1（首次提炼） | "为何没有X"=流程缺失，"X不好用"=质量问题，"X应该是Y"=需求偏差 | ✅ 已入库（governance-strategy/feedback-wording-diagnosis.md） |
| pattern-availability-heuristic-structural-guard | 可得性启发结构性防范模式 | L1（首次提炼） | 系统性认知偏差不能靠"更认真"解决，需要结构性机制（预检清单、自检点） | ✅ 已入库（governance-strategy/availability-heuristic-structural-guard.md） |
| pattern-context-recovery-protocol | Context恢复协议重执行模式 | L1（首次提炼） | 收到summary/"继续"后必须重新执行完整启动协议，重建全局视野 | ✅ 已入库（ai-collaboration/context-recovery-protocol.md，本次经验萃取新增） |
| pattern-template-variance-control | 模板质量方差控制模式 | L1（首次提炼） | 用预装最佳实践的模板+检查脚本双保险，降低质量方差 | ✅ 已入库（ai-collaboration/template-variance-control.md，本次经验萃取新增） |
| pattern-task-type-first-indexing | 任务类型优先索引模式 | L1（首次提炼） | 按"做什么事"而非"是什么资产"组织索引，零摩擦命中正确资产 | ✅ 已入库（governance-strategy/task-type-first-indexing.md，本次经验萃取新增） |
| pattern-spec-as-code-automated-gates | 规范即代码自动化门禁模式 | L1（首次提炼） | 可程序化验证的规范都写成检查脚本，作为强制门禁 | ✅ 已入库（tools-automation/spec-as-code-automated-gates.md，本次经验萃取新增） |
| pattern-asset-inventory-before-optimization | 优化前资产盘点 | - | 优化Skill前先盘点已有脚本/库/规范/vendor资产 | ✅ 已整合进skill-five-elements-model前置步骤，不单独入库 |

## 四、已完成产出物归档

| 产出物 | 路径 | 状态 |
|--------|------|------|
| forum-posting SKILL.md v1.1.0 | [.agents/skills/forum-posting/SKILL.md](../../../../../../skills/forum-posting/SKILL.md) | ✅ 已完成 |
| AGENTS.md 启动协议增强（步骤2.0/2.2/3.5+vendor方法论资产表） | [AGENTS.md](../../../../../../../AGENTS.md) | ✅ 已完成 |
| SpecWeave Skill开发补充规范 | [.agents/rules/skill-development.md](../../../../../../rules/skill-development.md) | ✅ 已完成 |
| .agents/rules/README.md 索引更新 | [.agents/rules/README.md](../../../../../../rules/README.md) | ✅ 已完成 |
| Skill五要素模型模板（SKILL-TEMPLATE.md） | [.agents/skills/SKILL-TEMPLATE.md](../../../../../../skills/SKILL-TEMPLATE.md) | ✅ 已完成（本批次新增） |
| vendor/AGENTS.md 按任务类型索引章节 | [vendor/AGENTS.md](../../../../../../../vendor/AGENTS.md) | ✅ 已完成（本批次新增） |
| Skill质量自动化检查脚本 | [.agents/scripts/check-skill-quality.py](../../../../../../scripts/check-skill-quality.py) | ✅ 已完成（本批次新增，支持评分/JSON/verbose输出） |
| Skill五要素模型模式 | [skill-five-elements-model.md](../../../../patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md) | ✅ 已完成（本批次新增） |
| 流程合规vs经验直觉区分模式 | [process-vs-experience-intuition.md](../../../../patterns/methodology-patterns/governance-strategy/process-vs-experience-intuition.md) | ✅ 已完成（本批次新增） |
| 协议违规非线性纠偏成本模式 | [nonlinear-correction-cost.md](../../../../patterns/methodology-patterns/governance-strategy/nonlinear-correction-cost.md) | ✅ 已完成（本批次新增） |
| 用户反馈措辞诊断模式（反馈分类框架） | [feedback-wording-diagnosis.md](../../../../patterns/methodology-patterns/governance-strategy/feedback-wording-diagnosis.md) | ✅ 已完成（本批次新增） |
| 可得性启发结构性防范模式 | [availability-heuristic-structural-guard.md](../../../../patterns/methodology-patterns/governance-strategy/availability-heuristic-structural-guard.md) | ✅ 已完成（本批次新增） |
| Context恢复协议重执行模式 | [context-recovery-protocol.md](../../../../patterns/methodology-patterns/ai-collaboration/context-recovery-protocol.md) | ✅ 已完成（本次经验萃取新增） |
| 模板质量方差控制模式 | [template-variance-control.md](../../../../patterns/methodology-patterns/ai-collaboration/template-variance-control.md) | ✅ 已完成（本次经验萃取新增） |
| 任务类型优先索引模式 | [task-type-first-indexing.md](../../../../patterns/methodology-patterns/governance-strategy/task-type-first-indexing.md) | ✅ 已完成（本次经验萃取新增） |
| 规范即代码自动化门禁模式 | [spec-as-code-automated-gates.md](../../../../patterns/methodology-patterns/tools-automation/spec-as-code-automated-gates.md) | ✅ 已完成（本次经验萃取新增） |
| Skill五要素模型（补充资产盘点前置步骤） | [skill-five-elements-model.md](../../../../patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md) | ✅ 已更新（本次经验萃取补充） |
| 复盘报告索引 | [README.md](README.md) | ✅ 已完成 |
| 洞察原子化目录（14个原子文件） | [insights/](insights/README.md) | ✅ 已完成（本次原子化新增：5 findings+3 laws+6 metas+README索引） |
| 执行复盘 | [execution-retrospective.md](execution-retrospective.md) | ✅ 已完成 |
| 洞察萃取 | [insight-extraction.md](insight-extraction.md) | ✅ 已完成 |
| 导出建议 | [export-suggestions.md](export-suggestions.md) | ✅ 当前文件（本批次更新状态） |

## 五、经验教训总结（供下次同类任务参考）

> 📂 经验教训已原子化拆分，单主题深度阅读见 [insights/](insights/README.md) 目录。

1. **收到任务后的第一步必须是完整执行启动协议**：读AGENTS.md → 按路由表确定所有需读规范 → 读取规范 → **自检确认无遗漏** → 再开始工作。不能因为"工作目录就在根目录"就跳过vendor路由检查。→ [meta-06-startup-protocol-self-checkpoint.md](insights/meta-06-startup-protocol-self-checkpoint.md)
2. **"优化Skill"这个任务类型 = 必须用skill-creator**：vendor/flexloop/apps/chaos/.agents/skills/skill-creator 是创建和优化Skill的方法论权威来源。→ [law-02-three-layer-routing-task-type-precheck.md](insights/law-02-three-layer-routing-task-type-precheck.md)
3. **Skill description不是功能简介，是触发广告**：必须包含所有可能的触发词、同义词，并显式声明"必须使用此技能"。→ [finding-02-skill-description-seo.md](insights/finding-02-skill-description-seo.md)
4. **解释Why比罗列MUST更重要**：AI模型在边界情况下需要理解决策意图，纯规则列表无法覆盖所有情况。→ [finding-03-why-explanation-principle.md](insights/finding-03-why-explanation-principle.md)
5. **优化现有Skill前先做资产盘点**：检查项目中是否已有相关脚本、工具、知识库可以整合进Skill，而不是只盯着现有Skill文档的内容。→ [law-01-skill-five-elements-model.md](insights/law-01-skill-five-elements-model.md)（前置步骤）
6. **流程合规的价值是"可预测性"而非"这次正确性"**：凭经验可能做对一次，但按方法论才能每次做对。不能因为"结果看起来一样"就跳过流程。→ [meta-01-process-vs-experience.md](insights/meta-01-process-vs-experience.md)
7. **协议违规有非线性返工成本**：跳过启动协议看似省5分钟，实际可能导致30分钟以上的重构返工。→ [meta-02-nonlinear-correction-cost.md](insights/meta-02-nonlinear-correction-cost.md)
8. **Context恢复后要主动重建全局视野**：长会话或context continuation后，不要假设summary包含了足够的路由信息，应重新执行启动协议。→ [meta-03-context-compression-cognitive-narrowing.md](insights/meta-03-context-compression-cognitive-narrowing.md)
9. **用户反馈的措辞是诊断线索**："为何没有X"指向流程缺失，优先排查协议合规问题而非结果质量问题。→ [meta-04-feedback-wording-diagnosis.md](insights/meta-04-feedback-wording-diagnosis.md)
10. **系统性认知偏差要靠结构性机制防范**："就近直觉"（可得性启发）不是粗心，需要预检清单、自检点等结构机制来对抗，不能只靠"更认真"。→ [meta-05-availability-heuristic-structural-guard.md](insights/meta-05-availability-heuristic-structural-guard.md)
11. **模板是降低质量方差的最经济手段**：将五要素模型、Why解释格式、安全检查清单固化为模板，比反复review纠错效率高一个数量级——新Skill直接填模板就天然包含了最佳实践。→ [template-variance-control.md](../../../../patterns/methodology-patterns/ai-collaboration/template-variance-control.md)
12. **按任务类型索引比按资产类型索引更符合启动协议需求**：启动协议步骤2.0是"任务类型预检"，按任务类型组织vendor资产索引（而非按Skills/Scripts分类），能让Agent在预检阶段零摩擦命中正确资产，不需要先知道资产叫什么名字。→ [task-type-first-indexing.md](../../../../patterns/methodology-patterns/governance-strategy/task-type-first-indexing.md)
13. **自动化检查脚本是固化质量标准的最佳载体**：把五要素模型的检查逻辑写进check-skill-quality.py，比写在文档里反复提醒有效得多——机器不会忘、不会偷懒、不会有认知偏差，是结构性防范的第三道防线。→ [spec-as-code-automated-gates.md](../../../../patterns/methodology-patterns/tools-automation/spec-as-code-automated-gates.md)
14. **Context恢复后必须重新执行完整启动协议**：即使有summary，也不能假设summary包含了所有路由信息——上下文压缩会导致认知视野收窄，必须重新读AGENTS.md、重新走任务类型预检，避免遗漏vendor方法论资产。→ [meta-03-context-compression-cognitive-narrowing.md](insights/meta-03-context-compression-cognitive-narrowing.md)
15. **相关模式应该聚合而非碎片化**：Skill Description SEO和双方案决策树不需要单独作为独立模式，它们是Skill五要素模型的组成部分，整合进五要素模型比碎片化更易于理解和复用。→ [law-01-skill-five-elements-model.md](insights/law-01-skill-five-elements-model.md)
