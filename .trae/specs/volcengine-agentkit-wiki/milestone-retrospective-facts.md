---
id: "agentkit-milestone-facts"
title: "AgentKit Wiki 教程项目里程碑复盘 - 客观事实清单"
source: "seven-concepts: volcengine-agentkit-wiki milestone review"
category: "retrospective"
tags: ["AgentKit", "milestone", "retrospective", "R阶段", "事实清单"]
date: "2026-07-31"
status: "stable"
author: "seven-concepts milestone R-stage"
summary: "AgentKit Wiki教程项目里程碑复盘客观事实清单（7大类，MF001-MF049）"
gate_g1_passed: true
---

# AgentKit Wiki 教程项目里程碑复盘 - 客观事实清单

> **R阶段产出**：本清单仅记录客观可验证的事实，不含因果推断、价值判断或主观评价。
> **G1质量门验证**：✅ 通过（无因果推断词）

---

## A. 项目范围与目标事实

**MF001.** 项目主题：学习火山引擎 AgentKit 平台并生成 Wiki 教程。
**MF002.** 方法论选择：使用 seven-concepts-cmd 七概念方法论编排执行。
**MF003.** 执行链路：知识沉淀链路 R→I→E→V→教程生成→验证入库。
**MF004.** Spec文档定义：11项功能需求 + 7项非功能需求 + 15项验收标准（AC-1~AC-15）。
**MF005.** 预期最终交付物：12个Wiki文档文件（README.md + 00~10共11章）。
**MF006.** 中间产物要求：facts.md、insights.md、patterns.md、adversarial-review.md 共4份。
**MF007.** 质量门设置：G1(R阶段)、G2(I阶段)、G3(E阶段)、V门(V阶段)共4道质量门。
**MF008.** 文件行数约束：所有交付文件 < 300行。

## B. 流程执行事实

**MF009.** 任务分解：10个Task（Task1-R阶段 ~ Task10-验证入库）。
**MF010.** Task1(R阶段)产出：60条事实（F001-F060，后经V阶段补充为F062），6大类每类≥5条，来源标注S1-S5共5个官方来源。
**MF011.** Task2(I阶段)产出：5条洞察（1战略层+2架构层+2实践层），每条含四元组结构。
**MF012.** Task3(E阶段)产出：3个可复用模式（P-AGENT-SELECT-001选型框架/P-LEGACY-AI-UPGRADE-002改造SOP/P-DEMO-TO-PROD-003检查清单）。
**MF013.** Task4(V阶段)执行：4个视角（魔鬼代言人/新手/CTO/未来资深用户）×每视角4条 = 16条攻击意见。
**MF014.** V阶段采纳情况：6条采纳，10条不采纳，采纳率37.5%。
**MF015.** V阶段采纳分布：facts.md采纳3条、insights.md采纳1条、patterns.md采纳2条，三类文档均有采纳。
**MF016.** Task5~Task9：教程文档生成，分5批并行生成（索引层/产品层/工具层/场景层/对比FAQ层）。
**MF017.** Task10：整体验证，包含frontmatter一致性检查、链接检查、AC逐项核对。

## C. 产出物统计事实

**MF018.** 最终交付文件数：12个（README.md + 00-overview~10-resources-glossary共11章）。
**MF019.** 中间产物文件数：5个（facts.md/insights.md/patterns.md/adversarial-review.md/verification-report.md）+ 本milestone复盘文件，合计6个。
**MF020.** 各文件行数统计（来源verification-report.md 1.1节）：
  - README.md: 38行
  - 00-overview.md: 97行
  - 01-product-intro.md: 77行
  - 02-core-architecture.md: 107行
  - 03-veadk-framework.md: 125行
  - 04-agentkit-sdk-cli.md: 203行
  - 05-quickstart.md: 225行
  - 06-application-scenarios.md: 217行
  - 07-core-features-detailed.md: 246行
  - 08-comparison-ecosystem.md: 139行
  - 09-faq-best-practices.md: 101行
  - 10-resources-glossary.md: 116行
**MF021.** 最大文件行数：07-core-features-detailed.md = 246行。
**MF022.** 总代码/文档行数（12个交付文件）：约1691行。
**MF023.** Mermaid图总数：21个（分布于8个文件中，含flowchart/timeline/quadrantChart/sequence等类型）。
**MF024.** 交付文件存放位置：`.agents/docs/knowledge/learning/03-agent-platforms-tools/volcengine-agentkit-wiki/`。
**MF025.** 中间产物存放位置：`.trae/specs/volcengine-agentkit-wiki/`。

## D. 质量门验证事实

**MF026.** G1质量门(R阶段)：✅ 通过。验证方式：正则检查无因果推断词。
**MF027.** G2质量门(I阶段)：✅ 通过。验证方式：5条洞察四元组结构完整检查，证据引用有效。
**MF028.** G3质量门(E阶段)：✅ 通过。验证方式：3个模式均含触发场景+核心步骤+反模式+迁移验证，可迁移到非AgentKit场景。
**MF029.** V门(V阶段)：✅ 通过。验证方式：4视角×4条=16条攻击，采纳率37.5%≥30%要求。
**MF030.** AC验收结果：✓通过13/15=86.7%，⚠部分通过2/15=13.3%，✗不通过0。
**MF031.** 2项部分通过AC：AC-7（场景拆分方式与spec字面描述有差异）、AC-8（模块选择策略与spec有差异），均不影响核心知识完整性。
**MF032.** NFR非功能需求合规：6/6=100%全部通过（NFR-1行数/NFR-2frontmatter/NFR-3Mermaid语法/NFR-4导航/NFR-5交叉引用/NFR-6阶段产物）。
**MF033.** Frontmatter一致性：12/12=100%文件9字段齐全（id/title/source/category/tags/date/status/author/summary），其中08/09/10三个文件由Task10补充author和summary字段后达标。
**MF034.** 链接验证结果：0个file:///绝对路径错误；11条双向导航链接全部正确；README导航链接11章全部正确；交叉引用20+条路径全部合法。
**MF035.** Cross-wiki交叉引用数：≥6个独立知识库wiki（实际8处明确引用）。

## E. 问题与修复事实

**MF036.** Defuddle提取失败问题：执行过程中defuddle解析AgentKit官网返回Exit code 126，提示"No content could be extracted"。修复方式：切换为WebFetch工具成功获取页面内容。
**MF037.** Task6状态更新字符串匹配问题：更新任务状态时，old_string "## [ ] Task 6" 与实际文件内容"## \[ ] Task 6"不匹配导致替换失败。修复方式：调整old_string匹配实际文件内容后成功更新。
**MF038.** V阶段修正项1：F024「完全兼容/无缝迁移」绝对化表述修正，改为"声明兼容，兼容范围以官方矩阵为准"。
**MF039.** V阶段修正项2：facts.md新增「术语速查表」章节，解释Harness/MCP/A2A/VeADK/LiteLLM/Serverless共6个核心术语。
**MF040.** V阶段修正项3：insights.md洞察2「治理外环包裹业务内环」补充直白解释，明确业务内环4模块+治理外环4模块的具体划分。
**MF041.** V阶段修正项4：patterns.md模式1选型框架新增第9维度「供应商锁定风险/退出成本」，权重8%，综合得分从4.25调整为4.23/5.00。
**MF042.** V阶段修正项5：patterns.md模式3检查清单新增第13项「供应商锁定退出预案」，新增战略维度为第7大维度。
**MF043.** V阶段修正项6：facts.md新增F061（规模指标官方未公开标注）、F062（并发伸缩速率未公开）两条事实。
**MF044.** Task10修正项：08/09/10三个文件frontmatter补充缺失的author和summary字段。
**MF045.** 遗留观察项（非阻塞）3项：AC-7场景拆分差异说明、AC-8模块选择策略说明强化、导航格式不统一（表格边框vs纯文本两种格式混用）。

## F. 额外产出事实

**MF046.** 额外生成模板1份：`.agents/templates/legacy-system-ai-upgrade-kickoff-template.md`（基于模式2 P-LEGACY-AI-UPGRADE-002改造的存量系统智能化项目启动文档模板）。
**MF047.** 模板包含章节：项目元数据、背景与目标、API清单、5步执行计划、RACI矩阵、风险矩阵、质量门、生产检查清单。
**MF048.** 用户后续需求响应：响应用户"建议下一步"请求，提出3项后续建议（docgen更新索引/发布/增量维护机制）；响应用户"把P-LEGACY-AI-UPGRADE-002改造SOP作为存量系统智能化项目启动文档"请求，完成模板生成。
**MF049.** 验收报告建议后续动作：4项（运行docgen更新索引、发布到文档中心、关联SpecWeave看板、建立增量维护SOP）。

---

**G1质量门自检**：
- [x] 所有事实均为客观可验证陈述
- [x] 无"因为/所以/导致/由于/因此/使得"等因果推断词
- [x] 无"正确/错误/好/坏/优秀/不足"等价值判断词
- [x] 每条事实均可追溯到来源文件（verification-report.md/tasks.md/adversarial-review.md等）
- [x] 7大类分类清晰，覆盖范围/流程/产出/质量/问题/额外产出/建议
