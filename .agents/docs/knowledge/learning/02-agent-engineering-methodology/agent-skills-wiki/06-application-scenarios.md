---
id: "agent-skills-application-scenarios"
title: "潜在应用场景"
category: learning
tags: [ai-agent, engineering-workflow, google-engineering, agent-skills, best-practices]
date: "2026-07-08"
status: stable
version: "1.0"
source: "https://cloud.tencent.com/developer/article/2658842"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/agent-skills-wiki/06-application-scenarios.toml"
summary: "覆盖遗留系统重构、新功能从零开发、紧急Bug修复、代码库健康度提升、团队AI编程规范落地等5个实战应用场景。"
---
# 潜在应用场景

## 场景1：遗留系统重构——安全地偿还技术债务

**场景描述**：团队接手一个运行多年的遗留代码库，没有测试、文档缺失、代码耦合严重、到处是"不知道为什么存在但不敢删"的代码。需要逐步重构但不能影响线上稳定性。

**适用技能组合**：
- `/spec` → spec-driven-development：先写重构目标和验收标准（"重构后所有现有功能不变"是首要验收标准）
- `/plan` → planning-and-task-breakdown：把大重构拆成小步骤，每次只重构一个模块
- `/test` → 先给现有行为写 characterization tests（特性描述测试）——用Beyonce规则，把现在的所有行为（包括看起来像bug的）都用测试固定下来
- `/code-simplify` → code-simplification：严格遵守Chesterton栅栏，拆一个函数前先搞清楚它为什么存在，500行规则拆分大文件
- incremental-implementation：薄垂直切片，重构一个模块→测试→提交，不要大爆炸重构
- security-and-hardening：重构同时顺手修明显的安全漏洞，但不要混在同一个PR里

**解决的痛点**：AI重构遗留系统时要么不敢动（"这代码太乱了我重写吧"结果重写出更多bug），要么乱删代码（"这看着没用"结果删掉了处理某个边缘case的关键逻辑），要么一次改太多出问题无法回滚。

**预期效果**：重构过程安全可控，每一步都有测试保护，小步提交随时可以回滚；重构后的代码复杂度显著降低，测试覆盖率从0提升到保护现有行为的水平；没有引入回归bug。

---

## 场景2：新功能从零开发——从想法到上线的标准化流程

**场景描述**：团队要开发一个全新功能，目前只有一个模糊的产品想法，需要从需求到上线走完整流程，要求代码质量高、有测试、有文档、可安全发布。

**适用技能组合**：
- `/spec` → idea-refine（发散收敛澄清需求）+ spec-driven-development（写完整需求文档）
- `/plan` → planning-and-task-breakdown：拆解为原子任务，明确依赖和验收标准
- `/build` → incremental-implementation（薄切片）+ test-driven-development（红-绿-重构，测试金字塔）+ api-and-interface-design（契约优先API）+ frontend-ui-engineering（组件化+无障碍）+ source-driven-development（基于官方文档决策）
- `/test` → browser-testing-with-devtools（真实浏览器检查DOM/网络/性能）+ debugging-and-error-recovery（遇到问题系统化调试）
- `/review` → code-review-and-quality（五轴评审，~100行PR）+ security-and-hardening（OWASP检查）+ performance-optimization（先测量再优化）
- `/ship` → git-workflow（原子提交）+ ci-cd-and-automation（左移门禁）+ documentation-and-adrs（记录架构决策）+ shipping-and-launch（分阶段发布+回滚+监控）

**解决的痛点**：AI开发新功能时经常跳过需求和规划直接写代码，写完不测试不评审，最后交付的代码质量差、没有文档、上线出问题无法回滚。

**预期效果**：交付的功能需求明确、代码结构清晰、测试覆盖率符合金字塔比例、有安全评审、有性能验证、有ADR记录决策背景、可以分阶段灰度发布、出问题有明确回滚流程。代码评审时每个PR都是~100行的小变更，评审速度快质量高。

---

## 场景3：紧急Bug修复——压力下保持工程纪律

**场景描述**：线上出了紧急Bug，需要快速修复，但又不能"快而脏"导致引入新问题或者留下技术债务。

**适用技能组合**：
- debugging-and-error-recovery：严格按五步分类法——复现→定位→简化→修复→防护，不要东改西改碰运气
- `/test` → test-driven-development：先写一个能复现这个bug的测试（红），再修复让它通过（绿），这是最快最可靠的方式
- `/build` → incremental-implementation：修复要小而精确，不要"顺手重构"周围代码（外科手术式精确修改）
- `/review` → code-review-and-quality：即使是紧急修复也要过评审，而且因为变更小（应该<50行）评审速度很快
- `/ship` → git-workflow（原子提交，提交信息明确说明修复了什么）+ shipping-and-launch（快速发布但要有回滚预案）
- 事后：documentation-and-adrs——记录这个bug为什么发生、怎么修复的、以后怎么避免

**解决的痛点**：紧急修复时AI容易"慌不择路"——同时改十几个地方碰运气，不写测试，修复完也不验证，结果要么没修好要么引入新bug，留下一堆"临时修复"的TODO永远不清理。

**预期效果**：Bug定位快（系统化流程不是碰运气）、修复精确（只改该改的地方）、有测试保护（这个bug以后不会再出现）、变更小评审快、可以快速安全上线，事后有根因分析和预防措施。

---

## 场景4：代码库健康度提升——系统性清理技术债务

**场景描述**：代码库经过一段时间迭代后积累了不少技术债务：重复代码、大文件、僵尸代码、安全漏洞、测试缺失、文档过期。需要系统性提升健康度但不要影响功能开发。

**适用技能组合**：
- `/review` → code-review-and-quality（健康度扫描，按严重性分类问题：Critical/High/Medium/Low/Nit）
- code-simplification：500行规则拆分大文件，Chesterton栅栏原则清理僵尸代码，降低复杂度
- security-and-hardening：依赖审计、密钥扫描、OWASP Top 10漏洞修复，三层边界系统加固
- `/test` → test-driven-development：给缺失测试的核心模块补测试（Beyonce规则），达到测试金字塔比例
- deprecation-and-migration：代码即负债思维——删除不用的功能，标记废弃API，提供迁移路径，清理僵尸代码
- documentation-and-adrs：更新过期文档，补写缺失的ADR，记录"为什么"而不只是"是什么"
- ci-cd-and-automation：把这些检查加入CI左移——以后每次提交自动检查代码大小、安全漏洞、测试覆盖率，防止债务复发

**解决的痛点**：AI做"代码清理"时要么改得太猛引入大量bug，要么只改表面格式不改实质问题，要么清完之后没有防护机制很快又回到原来的状态。

**预期效果**：代码库健康度指标（平均文件大小、循环复杂度、测试覆盖率、安全漏洞数、文档新鲜度）有可量化的提升；所有清理都有小PR提交，可验证可回滚；加入CI门禁后技术债务不会快速反弹。

---

## 场景5：团队AI编程规范落地——让团队所有AI用同一套标准工作

**场景描述**：团队里多个人都在用AI写代码，但每个人用的prompt不一样，AI遵循的标准不一样，有的人让AI写测试有的人不写，代码风格质量参差不齐。需要一套统一的规范让所有AI（不管是谁用的）都输出符合团队标准的代码。

**适用技能组合**：
- 全部7个斜杠命令作为团队标准工作流：所有人不管用什么AI工具，都按/spec→/plan→/build→/test→/review→/ship流程走
- spec-driven-development：团队统一的spec模板，所有需求都要按这个模板写
- code-review-and-quality：团队统一的代码评审标准（五轴评审、严重性标签、变更大小限制），AI提交的代码必须先自评审再给人审
- test-driven-development：团队统一的测试标准（金字塔80/15/5、DAMP、Beyonce规则）
- git-workflow-and-versioning：团队统一的Git规范（原子提交、提交信息格式、基于主干开发）
- 工具适配：根据团队用的工具（Claude Code/Cursor/Gemini CLI/其他）按Agent Skills的方式安装配置，确保所有人的AI都加载了相同的技能

**解决的痛点**：团队推广AI编程时最大的问题不是AI写不出代码，而是输出质量不稳定——同一个需求不同的人用AI写出来的代码天差地别，好的很好差的很差，没有统一标准就无法规模化推广。

**预期效果**：不管是谁用AI写代码，不管用什么工具，输出的代码都遵循团队统一的质量标准；新人加入团队只需要学会7个斜杠命令就能按规范工作；代码评审有统一标准，评审效率提升；技术债务不会因为AI的"最短路径倾向"快速积累。

---

**上一章**：[05 - 与SpecWeave对比分析](05-specweave-comparison.md)
**下一章**：[07 - 延伸学习资源](07-resources.md)
