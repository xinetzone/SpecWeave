---
id: "agent-skills-skills-index"
title: "20个核心技能索引"
category: learning
tags: [ai-agent, engineering-workflow, google-engineering, agent-skills, best-practices]
date: "2026-07-08"
status: stable
version: "1.0"
source: "https://cloud.tencent.com/developer/article/2658842"
summary: "按Define/Plan/Build/Verify/Review/Ship六个阶段分组的20个核心技能详解，每个技能对应解决AI的一个天然缺陷。"
---

# 20个核心技能索引

## Define（定义）阶段——解决"做正确的事"问题

| 技能 | 为什么需要 | AI的天然缺陷 |
|------|-----------|------------|
| **idea-refine** | 模糊想法→具体提案，通过发散/收敛思考澄清边界 | AI拿到模糊需求会直接脑补一个方案开始写，不会主动帮你发散收敛思考 |
| **spec-driven-development** | 写覆盖目标、命令、结构、代码风格、测试、边界的需求文档 | AI完全跳过需求文档环节，认为"写代码就是全部"，导致后期频繁返工 |

## Plan（规划）阶段——解决"正确地分解事"问题

| 技能 | 为什么需要 | AI的天然缺陷 |
|------|-----------|------------|
| **planning-and-task-breakdown** | 把需求拆成小可验证任务，带验收标准和依赖顺序 | AI倾向于一次性写完所有功能，或者任务拆解得太大不可验证，也不考虑依赖关系 |

## Build（构建）阶段——解决"正确地做事"问题

| 技能 | 为什么需要 | AI的天然缺陷 |
|------|-----------|------------|
| **incremental-implementation** | 薄垂直切片：实现→测试→验证→提交，特性标志、安全默认值、回滚友好 | AI喜欢"大爆炸式"开发，一次写几百行代码不提交不验证，出问题无法定位回滚 |
| **test-driven-development** | 红-绿-重构，测试金字塔(80/15/5)，DAMP胜过DRY，Beyonce规则 | AI写测试都是后补的，或者干脆不写测试，测试数量严重不足且覆盖不到边界 |
| **source-driven-development** | 基于官方文档做框架决策，验证引用来源，标记未验证内容 | AI会"幻觉"出不存在的API和用法，或者基于过时的博客内容做决策，不查官方文档 |
| **frontend-ui-engineering** | 组件架构、设计系统、状态管理、响应式设计、WCAG 2.1 AA无障碍 | AI写前端代码经常堆在一起，不考虑组件复用，忽略无障碍和响应式 |
| **api-and-interface-design** | 契约优先设计、Hyrum定律、一版本规则、错误语义、边界验证 | AI设计API经常随意改接口，不考虑向后兼容，错误处理模糊，边界条件缺失 |

## Verify（验证）阶段——解决"证明事做对了"问题

| 技能 | 为什么需要 | AI的天然缺陷 |
|------|-----------|------------|
| **browser-testing-with-devtools** | Chrome DevTools MCP获取实时运行时数据：DOM检查、控制台日志、网络跟踪、性能分析 | AI写完代码只看"有没有语法错误"，不会真正在浏览器里运行检查实际行为 |
| **debugging-and-error-recovery** | 五步分类法：复现→定位→简化→修复→防护，停机规则、安全回退 | AI调试时东改西改碰运气，没有系统化定位流程，也不修根因只改表面现象 |

## Review（评审）阶段——解决"事做得够不够好"问题

| 技能 | 为什么需要 | AI的天然缺陷 |
|------|-----------|------------|
| **code-review-and-quality** | 五轴评审、变更大小(~100行)、严重性标签(Nit/Optional/FYI)、评审速度规范、拆分策略 | AI写完代码不会自我评审，变更动辄几百上千行，也不区分问题严重性 |
| **code-simplification** | Chesterton栅栏、500行规则、保留精确行为同时降低复杂度 | AI经常写出"聪明但晦涩"的代码，过度抽象，文件动辄几千行没人能维护 |
| **security-and-hardening** | OWASP Top 10防护、认证模式、密钥管理、依赖审计、三层边界系统 | AI写代码完全不考虑安全，硬编码密钥、SQL注入、XSS等漏洞频发 |
| **performance-optimization** | 先测量方法、Core Web Vitals目标、分析工作流、包分析、反模式检测 | AI"凭感觉优化"，不测量就改，不知道真正的瓶颈在哪，优化方向完全错误 |

## Ship（发布）阶段——解决"安全地交付事"问题

| 技能 | 为什么需要 | AI的天然缺陷 |
|------|-----------|------------|
| **git-workflow-and-versioning** | 基于主干开发、原子提交、变更大小(~100行)、提交即保存点模式 | AI用Git就是一次add所有文件一个commit"完成"，不做原子提交，提交信息毫无意义 |
| **ci-cd-and-automation** | 左移、越快越安全、特性标志、质量门禁流水线、失败反馈循环 | AI不考虑CI/CD，认为"代码能在我这跑就行"，没有质量门禁概念 |
| **deprecation-and-migration** | 代码即负债思维、强制与建议废弃、迁移模式、僵尸代码移除 | AI只加代码不减代码，旧代码永远留在那里成为僵尸代码，技术债务越积越多 |
| **documentation-and-adrs** | 架构决策记录、API文档、内联文档标准，记录"为什么" | AI只写代码不写文档，即使写也只记录"做了什么"不记录"为什么这么做"，后人无法理解决策背景 |
| **shipping-and-launch** | 发布前检查清单、特性标志生命周期、分阶段推出、回滚流程、监控设置 | AI认为"代码合并就是发布完成"，没有回滚预案，没有监控，出问题手忙脚乱 |

---

**上一章**：[01 - 六阶段生命周期模型](01-lifecycle-model.md)
**下一章**：[03 - 7个触发命令机制](03-slash-commands.md)
