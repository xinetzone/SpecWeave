---
id: cordis-wiki-01-background-paper
title: Cordis — 背景理论与论文
date: '2026-08-18'
category: learning
tags:
- cordis
- paper
- spatiotemporal-composability
- revertible-effects
- reactive-coeffects
- theory
type: Reference
description: 讲解支撑Cordis的学术论文核心思想，从动态组合两大维度出发，将效应与协同效应抬升为运行时机制，构成编程范式。
sources:
- id: cordis-paper
  resource: https://github.com/cordiverse/paper
  title: A Programming Paradigm for Spatiotemporal Composability
generated:
  by: "process:docs-to-okf-conversion"
  at: "2026-08-22T00:00:00Z"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00Z"
status: "stable"
stale_after: "2027-08-22"
---

# Cordis — 背景理论与论文

> 一句话摘要：本章讲解支撑 Cordis 的学术论文《A Programming Paradigm for Spatiotemporal Composability》的核心思想——从「动态组合」的两大正交维度（时间与空间）出发，把经典的效应（effect）与协同效应（coeffect）概念抬升为运行时机制（可逆效应与响应式协同效应），并统一为单一上下文类型，构成一种编程范式。

---

## 1. 论文元信息

| 项目 | 值 |
|------|-----|
| **标题** | A Programming Paradigm for Spatiotemporal Composability |
| **版本** | 预印本（Preprint），草稿日期 2026 年 8 月 13 日 |
| **性质** | 活跃修订中的预印本，内容可能大幅变更 |
| **全文** | `paper.pdf`（约 88 页，含约 126 篇参考文献） |
| **配套实现** | Cordis（本教程讲解的框架） |

> 论文在开头的摘要中已明确「正在活跃修订、内容可能大幅变化、依赖具体结论前请回看最新版本」。因此本章聚焦于论文**已相对稳定的核心概念与形式化框架**，而非某一推导的细节结论。

---

## 2. 问题：动态组合缺乏形式化基础

现代软件——从插件系统到自我进化的 Agent harness（驾驭框架）——越来越需要**动态组合（dynamic composition）**能力：组件在运行时到达与离开，依赖在运行时演化。论文指出，尽管需求普遍存在，**其形式化基础仍然薄弱**。

论文把「动态组合」问题分解为两个正交的维度：

| 维度 | 关心的问题 | 对应的形式化工具 |
|------|-----------|-----------------|
| **时间可组合性（Temporal）** | 如何让组件的副作用在移除时被完整回退？ | 效应（effect）系统 |
| **空间可组合性（Spatial）** | 如何声明并响应式地管理组件间的依赖？ | 协同效应（coeffect）系统 |

论文的洞察是：**effect 与 coeffect 恰好从两个方向完备地刻画了「组件如何修改环境」与「组件如何依赖环境」**，因此可以成为动态组合的形式化词汇。

---

## 3. 预备知识：效应与协同效应

### 3.1 效应（Effects）

在简单类型 λ 演算中，类型判断 `Γ ⊢ t : T` 表示「在上下文 Γ 下，项 t 有类型 T」。效应系统把类型进一步精炼，用效应代数描述计算可能产生的副作用：

```
Γ ⊢ t : T^effect
```

- **单子式效应（Monadic effects）**：Moggi 用单子 `(T, η, μ)` 将效应式计算封装为 `T(A)` 类型的值；Wadler 在 Haskell 中普及了这一做法（Maybe、State、IO 等单子）。
- **代数效应（Algebraic effects）**：Plotkin 与 Power 证明代数运算决定单子；Plotkin 与 Pretnar 引入效应处理器（effect handler），用带定界续延（delimited continuation）的语义解释效应运算，统一了异常、协程、非确定性等概念。Koka、Eff、OCaml 5 均已采纳。

**核心含义**：effect 刻画「计算对世界的**影响**」。

### 3.2 协同效应（Coeffects）

协同效应系统是 effect 的对偶：它精炼的是**上下文**而非类型：

```
Γ^coeffect ⊢ t : T
```

- **余单子式协同效应（Comonadic coeffects）**：Uustalu 与 Vene 用余单子结构建模上下文依赖式计算；Petricek 等人将 coeffect 发展为对「上下文依赖」的统一静态分析。Environment 余单子建模对固定环境 `E` 的依赖，Stream 余单子建模对时序数据的依赖。
- **分级协同效应（Graded coeffects）**：用预序半环 `(S, ≤, +, ×, 0, 1)` 作为 coeffect 代数，量化变量使用的资源（0=未用、1=线性、n=有界、∞=无限制）。

**核心含义**：coeffect 刻画「世界对计算的**约束**」。

### 3.3 与动态组合的关系

论文指出，经典 effect/coeffect 系统是**静态工具**：效应在词法固定的作用域内被追踪、被编译期处理器释放；coeffect 标注在执行前就被验证。但动态组合要求这些保证对**运行时到达与离开的组件**、对**持续演化的上下文**也成立——没有固定词法作用域能界定「部署后加载的插件」，没有编译期上下文能预判「运行时配置才出现的依赖」。

> **核心转折**：与其给静态类型系统加更多标注，不如把 effect/coeffect 的**概念结构物化（reify）**，让运行时可以直接操作它们，从而动态地建立静态系统所提供的保证。

---

## 4. 两大运行时机制

### 4.1 可逆效应（Revertible Effects）

时间可组合性要求：组件被卸载时，共享环境恢复到组合之前的状态。这要求组件对环境的每一次修改都**可追踪（trackable）且可恢复（recoverable）**。

论文将一个 effect 建模为类型 `Γ → Γ × (Γ → Γ)` 的函数：应用于当前上下文后，返回「被修改的上下文」和一个「显式逆函数（inverse）」。**提供逆函数使效应可被回退，把逆函数交还给运行时使效应可被追踪**。通过在执行期间追踪并组合这些逆函数，完整的环境恢复成为结构性保证。

关键构造（本节仅列结论，详细推导见论文 Section 3）：

| 构造 | 定义 | 含义 |
|------|------|------|
| **扭转组合（twisted composition）** | `(f1,g1) ∘ (f2,g2) := (f1∘f2, g2∘g1)` | 正向变换依次执行，逆变换以相反顺序累积 |
| **效应上下文（effect context）** | `∂Γ := Γ × (Γ → Γ)` | 一对 `(γ, φ)`：当前状态 γ + 逆累积器 φ |
| **track** | `(f,g) ↦ (γ,φ) ↦ (f(γ), φ∘g)` | 追踪一次效应：变换状态、累积逆 |
| **recover** | `(γ,φ) ↦ (φ(γ), id)` | 应用累积的逆恢复初始状态并重置逆 |

逆变换的累积顺序与正向变换相反（`g2∘g1` 而非 `g1∘g2`），这正对应「后进先出」（栈式）的副作用回退语义。效应上下文构成一个「扭转组合幺半群」，这是整套可逆性保证的代数基础。

> **与 Cordis 的对应**：Cordis 的 `ctx.effect()`（见 `packages/core/src/fiber.ts`）正是「可逆效应」的工程化形态——`effect` 执行函数返回一个 `dispose` 函数（即逆），运行时（Fiber）收集这些 dispose 并在卸载时以**逆序**执行。

### 4.2 响应式协同效应（Reactive Coeffects）

空间可组合性要求：组件间依赖被声明并可响应式管理。论文将每个组件的依赖声明为**协同效应规范（coeffect specification）**，上下文每次变化时，运行时依据该规范通知组件三种结果之一：

- **激活（activating）**：上下文变化使一个此前缺失的依赖变得可用；
- **停用（deactivating）**：上下文变化使一个此前可用的依赖失效；
- **中性（neutral）**：上下文变化与该组件的依赖无关。

> **与 Cordis 的对应**：Cordis 的 `@Inject` 装饰器（`packages/core/src/registry.ts`）与 `Fiber` 的 epoch 重算机制（见第 4、6 章）正是「响应式协同效应」——插件声明注入（`inject`），当被注入的服务通过 `provide`/`notify` 发生变化时，运行时据此重新计算并激活/停用相关光纤。

### 4.3 统一上下文类型

论文将效应上下文与协同效应上下文**统一为单一上下文类型（unified context type）**。在协同效应上定义一个**观测等价（observational equivalence）**，为效应提供「独立性（independence）」语义，从而构成一种编程范式。

> 这在 Cordis 中体现为：`Context` 同时承载「效应追踪」（`fiber`/`effect`）与「协同效应解析」（`isolate`/`intercept`/`reflect.provide/get`），二者共享同一个 `Context` 对象的继承与作用域体系。

---

## 5. 论文贡献（Section 1.3）

论文归纳了五项贡献，与 Cordis 的对应关系如下：

| # | 贡献 | 对应 Cordis |
|---|------|------------|
| 1 | 形式化**可逆效应**：每次上下文变换携带显式逆，运行时追踪，恢复保持组合性 → 局部时间可组合性 | `Fiber.effect` 返回 disposable，`_disposables` 逆序回收 |
| 2 | 形式化**响应式协同效应**：组件声明所需协同效应，上下文变化通知激活/停用/中性 → 局部空间可组合性 | `@Inject`/`inject` 声明依赖，`Reflect.provide`/`notify` 响应变化 |
| 3 | **统一**效应与协同效应上下文为单一上下文类型，观测等价为效应提供独立性 → 编程范式 | `Context` 统一承载效应与依赖 |
| 4 | 给出**动态组合演算**：把两大机制组合为「组件」，赋予生命周期运算语义，元理论把可组合性从单组件推广到整个交织系统 | `Fiber` 状态机 + `Registry`/`Loader` 编排 |
| 5 | 以 **Cordis** 实现：核心库（效应追踪 + 协同效应解析）+ 声明式加载器（配置合并 + 热更新） | 本教程的 `packages/core`、`plugin-loader`、`plugin-hmr` |

---

## 6. 理论到实现的映射总览

| 论文概念 | Cordis 概念 | 源码位置 |
|---------|-----------|---------|
| 可逆效应（revertible effect） | `ctx.effect()` 返回 disposable | `packages/core/src/fiber.ts` |
| 逆函数（inverse） | `dispose` 函数（逆序执行） | `fiber.ts` 的 `effect`/`_unload` |
| 效应追踪（effect tracking） | `DisposableList`/`_disposables` | `packages/core/src/utils.ts`、`fiber.ts` |
| 响应式协同效应 | `@Inject`/`inject` 依赖声明 | `packages/core/src/registry.ts` |
| 激活/停用/中性 | Fiber 的 epoch 重算与 `_checkImpl`/`_refresh` | `packages/core/src/fiber.ts`、`reflect.ts` |
| 协同效应解析 | `Reflect.provide`/`get`/`notify` | `packages/core/src/reflect.ts` |
| 统一上下文 | `Context`（含 isolate/intercept） | `packages/core/src/context.ts` |
| 组件（component） | `Plugin`（函数/构造器/对象） | `packages/core/src/registry.ts` |
| 组件生命周期演算 | `Fiber` 状态机 | `packages/core/src/fiber.ts` |
| 声明式装配 + 热更新 | `plugin-loader` + `plugin-hmr` | `packages/loader`、`packages/hmr` |

---

- [上一章：概述](/index.md) | [下一章：文件结构与 Monorepo](/concepts/02-repo-structure.md) →