---
id: cordis-wiki-04-effects-coeffects
title: Cordis — 效应与协同效应机制
date: '2026-08-18'
category: learning
tags:
- cordis
- effect
- coeffect
- disposable
- symbols
- traceable
- inject
type: Concept
description: 深入讲解Cordis如何将可逆效应与响应式协同效应落地为源码机制，包括disposable、@Inject、symbols与traceable。
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

# Cordis — 效应与协同效应机制

> 一句话摘要：本章深入讲解 Cordis 如何把论文的「可逆效应」与「响应式协同效应」落地为源码机制——`Fiber.effect` 返回 disposable（逆）、`@Inject`/`provide` 实现依赖注入（coeffect）、`symbols` 符号体系、以及 `getTraceable`/`createCallable` 等可追踪代理。

---

## 1. 可逆效应：`ctx.effect()` 与 Disposable

Cordis 的「可逆效应」抽象集中体现在 `ctx.effect()`（定义于 `packages/core/src/fiber.ts`，再经 `ReflectService.mixin('fiber', [...])` 暴露到上下文上）。

### 1.1 Effect 的几种形态

```ts
export type Disposable<T = any> = () => T
export type Effect<T = any> =
  | SyncEffect<T>          // 返回 disposable 或 disposable 的（同步）可迭代
  | AsyncEffect<T>         // 返回 Promise<disposable> 或 disposable 的异步可迭代

type SyncEffect<T = any> =
  | Disposable<T>
  | Iterable<Disposable<T>, void, void>

type AsyncEffect<T = any> =
  | Promise<Disposable<T>>
  | AsyncIterable<Disposable<T>, void, void>
```

一个 effect 的返回值可以是一次性的 `dispose` 函数（`Disposable`），也可以是**多个** `dispose` 函数的（异步）迭代序列——这正是论文「扭转组合幺半群」的工程形态：一个插件的多次效应按顺序累积，卸载时**逆序**回收。

### 1.2 effect 的实现

`Fiber.effect` 的核心流程（简写）：

```ts
effect(execute: () => Effect, label = 'anonymous') {
  this.assertActive()
  const disposables: Disposable[] = []
  const dispose = () => {
    // 逆序执行所有 collect 到的 disposable
    let task
    for (const dispose of disposables.splice(0).reverse()) { /* 顺序 await */ }
    return task
  }
  // runners：execute 的结果被收集进 disposables
  const wrapper = defineProperty(() => { runner.epoch = false; return task ? task.then(dispose) : dispose() }, symbols.effect, meta)
  disposables.push(this._disposables.push(wrapper))
  return wrapper
}
```

**要点**：

1. `execute` 返回的每个 dispose 函数都被「收集（collect）」，并在 `dispose()` 中**逆序**执行——先注册的后清理，这是副作用回退的正确顺序。
2. wrapper 函数被标记了 `symbols.effect` 元信息（含 `label` 与子效应树），用于 `getEffects()` 观测。
3. 每个 wrapper 同时被推进其所属 `Fiber` 的 `_disposables` 列表，构成可遍历的效应树。

> **与论文对应**：`execute` 就是正向变换 `f`，它返回的 `dispose` 就是逆 `g`；`_disposables` 的逆序回收对应「扭曲组合」中逆以相反顺序累积（`(f1,g1)∘(f2,g2) = (f1∘f2, g2∘g1)`）。

### 1.3 典型用法

```ts
// 注册一个定时器，并返回清理函数（逆）
const dispose = ctx.effect(() => {
  const timer = setInterval(callback, 1000)
  return () => clearInterval(timer)      // ← 逆函数
}, 'ctx.interval()')
dispose()                                 // 手动撤销（执行逆）
```

---

## 2. 响应式协同效应：注入与提供

「coeffect」即「组件对环境的依赖」。在 Cordis 中，这一概念由 `inject`（声明依赖）与 `provide`（供应依赖）共同实现，并由 `ReflectService.notify` 驱动响应式更新。

### 2.1 声明依赖：`Inject`

`@Inject` 装饰器（`packages/core/src/registry.ts`）可以标注在类或类方法上：

```ts
export function Inject<K extends InjectKey>(name: K, config?) {
  return function (value: any, decorator: ClassDecoratorContext<any> | ClassMethodDecoratorContext<any>) {
    if (decorator.kind === 'class') {
      // 写入 value.inject[name] = config
    } else if (decorator.kind === 'method') {
      // 记录到 metadata.inject，并注册 init hook
    }
  }
}
```

类级 `@Inject('logger')` 表示「此类需要一个名字为 `logger` 的服务」。装配时，`RegistryService.plugin` 调用 `Inject.resolve(plugin.inject)` 把依赖表归一化为 `Dict<string | config>`。

### 2.2 供应依赖：`ReflectService.provide`

`provide` 把一个服务实现注册进 `store`，并返回「撤销供应」的逆函数（见第 3 章第 5 节）。服务按 `isolate` symbol 隔离（见第 7 章），因此同一个服务名在不同隔离域可以有不同的实现。

### 2.3 响应式通知：`notify`

当服务被 `provide` 或 `set` 变动时，`notify` 遍历所有插件的所有 fiber，判断其 `inject` 是否包含被变动的服务，据此更新依赖的可用性：

```ts
notify(names, filter) {
  for (const runtime of this.ctx.registry.values()) {
    for (const fiber of runtime.fibers) {
      for (const name of names) {
        if (!(name in fiber.inject)) continue
        fiber._checkImpl(name)
      }
      fiber._refresh()       // 触发激活/停用
    }
  }
}
```

> **与论文对应**：`fiber.inject` 就是「协同效应规范」；`notify` 就是「上下文变化通知」；`_checkImpl`/`_refresh` 的结果对应「激活/停用/中性」三种 response。

---

## 3. 符号体系（symbols）

Cordis 大量使用 `Symbol.for(...)` 定义内部符号（`packages/core/src/utils.ts`），以规避命名冲突并实现跨模块协作：

```ts
export const symbols = {
  // 内部符号
  shadow: Symbol.for('cordis.shadow'),
  caller: Symbol.for('cordis.caller'),
  receiver: Symbol.for('cordis.receiver'),
  metadata: Symbol.for('cordis.metadata'),
  initHooks: Symbol.for('cordis.initHooks'),
  // 上下文符号
  effect: Symbol.for('cordis.effect'),
  filter: Symbol.for('cordis.filter'),
  isolate: Symbol.for('cordis.isolate'),
  intercept: Symbol.for('cordis.intercept'),
  // 服务符号
  init: Symbol.for('cordis.init'),
  check: Symbol.for('cordis.check'),
  config: Symbol.for('cordis.config'),
  invoke: Symbol.for('cordis.invoke'),
  // ...
}
```

| 符号 | 用途 |
|------|------|
| `isolate` | 服务隔离键映射（`Context[symbols.isolate]`） |
| `intercept` | 服务配置拦截映射（`Context[symbols.intercept]`） |
| `effect` | 标记一个函数为 effect，`getEffects()` 据此识别 |
| `filter` | 事件/服务的作用域过滤（coeffect 的观测等价载体） |
| `shadow` | 上下文派生时保留的原型信息，用于 `getTraceable` |
| `invoke` | 标记服务「可调用」，`applyTraceable` 据此路由 |
| `tracker` | 追踪元数据，供 `createTraceable` 生成代理 |

---

## 4. 可追踪代理：`getTraceable` 与 `createCallable`

Cordis 用 Proxy 实现了一个「可追踪（traceable）」机制，让从服务获取的值自动绑定到正确的上下文。

### 4.1 getTraceable

```ts
export function getTraceable<T>(ctx: Context, value: T): T {
  if (!isObject(value)) return value
  if (Object.hasOwn(value, symbols.shadow)) return Object.getPrototypeOf(value)
  const tracker = value[symbols.tracker]
  if (!tracker) return value
  return createTraceable(ctx, value, tracker)
}
```

若一个值带有 `symbols.tracker` 元数据，就为其生成一个带上下文感知的 Proxy，使访问它的属性（如调用 `service.method()`）时，`this` 能正确指向调用方上下文。

### 4.2 createCallable

```ts
export function createCallable(name: string, proto: {}, tracker: Tracker) {
  const self = function (...args: any[]) {
    const proxy = createTraceable(self['ctx'], self, tracker)
    return Reflect.apply(proxy, this, args)
  }
  defineProperty(self, 'name', name)
  return Object.setPrototypeOf(self, proto)
}
```

`LoggerService` 就是通过 `createCallable` 变成「既可当服务引用、又能像函数一样调用」的对象。

---

## 5. DisposableList：逆序回收的数据结构

`DisposableList`（`packages/core/src/utils.ts`）是效应回收的底层结构：

```ts
export class DisposableList<T extends WeakKey> {
  private map = new Map<number, T>()
  push(value: T) { /* 返回 () => this.map.delete(sn) */ }
  clear() {
    const values = [...this.map.values()]
    this.map.clear()
    return values.reverse()          // ← 逆序返回
  }
}
```

`clear()` **逆序**返回所有元素，配合 `Fiber.effect` 中的逆序执行，实现了「后注册先清理」的副作用回退顺序。

---

## 6. 效应 / 协同效应在实例中的体现

以 `TimerService.timeout`（`packages/timer/src/index.ts`）为例，它同时兼具两种机制：

```ts
timeout(callback, delay) {
  const dispose = this.ctx.effect(() => {
    const timer = setTimeout(() => { dispose(); callback() }, delay)
    return () => clearTimeout(timer)     // 可逆效应：提供逆
  }, 'ctx.timeout()')
  return dispose
}
```

再以 `Service` 的依赖注入（`service.ts` 构造函数）为例：

```ts
self.ctx.reflect.provide(name, self, this[symbols.check])   // 协同效应：供应服务
return self
```

二者共享同一个 `Context` 与 `Fiber`——这正是论文「统一上下文类型」的实现。

---

## 7. 小结表

| 概念 | 论文术语 | Cordis 实现 |
|------|---------|-----------|
| 副作用 + 撤销 | 可逆效应（revertible effect） | `ctx.effect()` 返回 disposable |
| 逆序回退 | 扭曲组合（twisted composition） | `DisposableList.clear().reverse()` |
| 依赖声明 | 协同效应规范（coeffect spec） | `@Inject` / `inject` |
| 依赖供应 | 上下文变换 | `reflect.provide` |
| 变化通知 | 响应式协同效应（reactive coeffect） | `reflect.notify` → `_checkImpl`/`_refresh` |
| 依赖可用性判定 | 激活/停用/中性 | Fiber 的 epoch 重算与状态切换 |
| 统一上下文 | 统一上下类型（unified context type） | `Context` 同时承载 `fiber` + `isolate`/`intercept` |

---

- [上一章：核心抽象与架构](/concepts/03-core-architecture.md) | [下一章：插件系统与依赖注入](/concepts/05-plugin-system.md) →