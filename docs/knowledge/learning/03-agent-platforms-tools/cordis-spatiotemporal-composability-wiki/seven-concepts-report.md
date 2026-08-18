---
id: cordis-wiki-seven-concepts-report
title: "Cordis 时空可组合性 Wiki 教程 — 七概念方法论执行报告"
date: "2026-08-18"
category: "learning"
tags: ["cordis", "spatiotemporal-composability", "seven-concepts", "methodology", "knowledge-precipitation", "R-I-E"]
---

# Cordis 时空可组合性 Wiki 教程 — 七概念方法论执行报告

## 执行概览

| 项目 | 值 |
|------|-----|
| **会话ID** | sc-20260818-cordis-wiki |
| **场景** | 知识沉淀（场景4） |
| **链路** | R → I → E |
| **目标** | 学习 `cordis` monorepo 与配套论文 `paper`，生成结构化中文 wiki 教程 |
| **执行日期** | 2026-08-18 |
| **质量门结果** | G1✅ G2✅ G3✅ |

---

## R（Retrospective）— 事实采集

### 输入
- Cordis 源码 monorepo：`d:\AI\.chaos\temp\cordis\`
- 配套论文：`d:\AI\.chaos\temp\paper\`（`README.md` + `paper.pdf`）
- 参考 wiki 格式：`okf-kit-wiki`、`open-code-review-wiki` 系列

### 采集范围
| 模块 | 文件数 | 核心内容 |
|------|--------|---------|
| 根配置 | 5+ | package.json（workspaces）、tsconfig.base.json、vitest.config.ts、yakumo.yml、yarnrc.yml |
| core 核心库 | 9 | context.ts、service.ts、fiber.ts、registry.ts、reflect.ts、events.ts、logger.ts、utils.ts、index.ts |
| loader 声明式装配 | 7 | index.ts、internal.ts、config/{entry,group,isolate,tree,utils}.ts |
| hmr 热更新 | 2 | index.ts、error.ts（+ locales） |
| create 脚手架 | 2 | index.ts、bin.ts |
| group/include | 2 | 各自 index.ts |
| timer | 1 | index.ts |
| logger-console | 3 | index.ts、shared.ts、browser.ts |
| utils | 1 | index.ts |
| paper 论文 | 2 | README.md、paper.pdf（使用 pypdf 提取全文） |

### G1 质量门检查
- ✅ 事实记录中无因果推断词（"因为"/"导致"/"所以"）
- ✅ 各包的职责边界、公开 API、状态枚举均来自源码实际定义
- ✅ 论文核心概念（可逆效应/响应式协同效应/统一上下文/组件演算）均已核对原文术语

---

## I（Insight）— 洞察分析

### 洞察1：效应与协同效应的「运行时物化」是设计灵魂
- **现象**：论文的 effect 被直接建模为「变换 + 逆函数」，coeffect 被建模为「依赖规范」
- **根因**：动态组合没有固定词法作用域和编译期上下文可供静态追踪，只有把概念结构物化为运行时对象才能建立等价保证
- **影响**：`ctx.effect()` 返回 disposable、`@Inject` 声明依赖，二者成为整个框架的两大支柱
- **建议**：面向运行时动态系统的框架，应优先考虑「把静态概念结构物化为一等对象」，而非给类型系统加更多标注

### 洞察2：epoch 信号统一了「激活/停用/中性」三类通知
- **现象**：`Fiber._refresh` 用依赖实现 uid 拼接出 epoch 字符串，哨兵 `INACTIVE` 表示有依赖缺失
- **根因**：把「依赖是否满足」压缩为一个可比较的字符串，使依赖变化天然归约为 epoch 是否变化
- **影响**：`_setEpoch` 仅凭 epoch 变化自动触发 `_reload`/`_unload`，衰老/停用/激活被统一为同一机制
- **建议**：响应式系统的通知机制应追求「可比较的单值信号」，而非散落的事件类型

### 洞察3：Fibre 本身也是可逆效应，形成嵌套回收
- **现象**：`Fiber` 构造器用 `parent.fiber.effect()` 包裹子光纤的创建与销毁
- **根因**：组件的组合性要求「父组件的移除自动回收子组件」，这只有把子组件生命周期纳入父组件的效应回收才能结构性地保证
- **影响**：卸载一个父插件时，其所有子插件副作用逆序回收，实现论文的「组合性从单组件推广到系统」
- **建议**：可组合对象应自相似——对象本身遵循与对象内部副作用相同的回收协议

### 洞察4：配置合并（reconciliation）避免无谓重启
- **现象**：`Entry.update` 用 `deepEqual` 计算 diff，diff 为空直接返回
- **根因**：声明式配置变化是常态，若每次都整体重建会造成大量抖动
- **影响**：只有真正变化的字段才触发部分释放与重装配，配合 `isolate` 实现服务作用域的增量迁移
- **建议**：声明式装配系统必须以「增量 diff + 最小重载」为默认策略，而非整体重建

### 洞察5：HMR 通过「依赖图分类 + 缓存备份回滚」实现安全热更
- **现象**：`analyzeChanges` 递归划分 accepted/declined，`partialReload` 先备份 loadCache 再重导入，失败回滚
- **根因**：热更的最大风险是「改一半崩溃」，需要区分可热更/需全量重启文件，并给失败兜底
- **影响**：热更失败不会破坏运行态，缓存回滚恢复了旧实现，与「可逆效应」哲学同构
- **建议**：增量热更应把「回滚」作为一等设计，而非事后补救

### 洞察6：论文（theory）与 Cordis（implementation）形成封闭回环
- **现象**：论文五项贡献（可逆效应/响应式协同效应/统一上下文/组件演算/Cordis 实现）在源码中逐一有对应落点
- **根因**：论文旨在「为动态组合提供形式化基础」，实现则是把形式化概念物化为可运行的 TypeScript 抽象
- **影响**：研究者与工程师可在同一术语体系下对话，理论指导实现、实现验证理论
- **建议**：框架级项目宜配套形式化文档，形成「概念—实现」可对照的资产

### G2 质量门检查
- ✅ 每个洞察包含现象描述（源码/论文依据）
- ✅ 每个洞察包含根因分析
- ✅ 每个洞察包含影响评估
- ✅ 每个洞察包含改进建议（可迁移）

---

## E（Extraction）— 模式萃取

### 萃取产物
13 个原子化 wiki 章节文件 + 本方法论报告

### 章节结构
- 00-overview.md：概述、术语表、章节导航、阅读路径、架构鸟瞰
- 01-background-paper.md：论文背景、effect/coeffect 预备知识、两大机制、理论到实现映射
- 02-repo-structure.md：monorepo 结构、10 包职责速查
- 03-core-architecture.md：Context/Service/Fiber/Registry/Events/Reflect/Logger 七类核心抽象
- 04-effects-coeffects.md：可逆效应（disposable）、依赖注入、符号体系
- 05-plugin-system.md：Plugin 三种形态、@Inject、Service、provide/get
- 06-lifecycle.md：Fiber 六态状态机、epoch、加载/卸载、控制原语
- 07-loader-config.md：Loader/Entry/Tree/Group、isolate、interpolate、Include
- 08-hmr.md：文件监听、accepted/declined 分类、缓存备份回滚
- 09-aux-packages.md：create/group/include/logger-console/timer/utils
- 10-usage-examples.md：最小插件、依赖注入、可逆副作用、Mermaid 架构图
- 11-faq-notes.md：API 未稳定、异步效应、注入语义、HMR 前置条件
- 12-summary-resources.md：总结、速查表、资源链接

### G3 质量门检查
- ✅ 模式可迁移：wiki 结构可作为其他 TypeScript 框架/元框架教程的模板
- ✅ 触发条件明确：每章开头一句话摘要说明查阅场景
- ✅ 反模式标注：FAQ 中列出 API 漂移、漏声明 @Inject、异步清理遗漏等坑位
- ✅ 迁移验证：章节编号、frontmatter、导航格式与现有 `okf-kit-wiki` 一致

---

## 方法论执行总结

七概念知识沉淀链路（R→I→E）成功执行：

1. **R 阶段**：研读 cordis monorepo 10 个包约 30 个核心源文件 + 论文全文，覆盖所有公开 API 与核心流程
2. **I 阶段**：6 个核心设计洞察被识别，每个包含完整四元组（现象/根因/影响/建议）
3. **E 阶段**：13 个原子化 wiki 章节被撰写，结构化覆盖从理论到工程辅助包的完整知识体系

质量门全部通过，产出物满足 spec.md 定义的所有验收标准。