---
id: "cordis-spatiotemporal-composability-wiki-05"
title: "Cordis — 插件系统与依赖注入"
source: "https://github.com/cordiverse/paper"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/05-plugin-system.toml"
---
# Cordis — 插件系统与依赖注入

> 一句话摘要：本章讲解 Cordis 的插件（Plugin）系统——插件可以以函数、构造函数或 `apply` 对象三种形态存在；`@Inject` 装饰器声明依赖；`RegistryService.plugin` 负责装配；`Service` 继承与 `reflect.provide/get` 实现依赖注入；并给出最小插件的完整代码。

---

## 1. Plugin 的三种形态

`Plugin` 类型（`packages/core/src/registry.ts`）允许同一装配接口承载三种插件写法：

```ts
export type Plugin<T = any> =
  | Plugin.Function<T>      // 函数插件
  | Plugin.Constructor<T>   // 构造器插件
  | Plugin.Object<T>        // 带 apply 方法的对象插件
```

### 1.1 公共属性（Plugin.Base）

```ts
interface Base<T = any> {
  name?: string                 // 插件名
  Config?: StandardSchemaV1<any, T>   // 配置校验 schema
  inject?: Inject               // 依赖声明（coeffect）
  provide?: string | string[]   // 插件提供的服务名
  intercept?: Dict<boolean>     // 拦截声明
}
```

### 1.2 三种形态对比

| 形态 | 示例 | 适用场景 |
|------|------|---------|
| **函数** | `(ctx, config) => { ... }` | 简单、无状态的插件 |
| **构造器** | `class P { constructor(ctx, config) {} }` | 需要实例状态、装饰器（`@Inject`）的插件 |
| **对象** | `{ apply(ctx, config) {} }` | 需要携带元数据（`name`/`Config`/`inject`）的插件 |

`RegistryService` 通过 `resolve` 归一化三种形态，得到可执行的 `callback`：

```ts
resolve(plugin: Plugin): Function | undefined {
  if (typeof plugin === 'function') return plugin
  if (plugin && typeof plugin === 'object' && typeof plugin.apply === 'function') return plugin.apply
}
```

---

## 2. `ctx.plugin()` 装配入口

```ts
ctx.plugin(plugin, config?)
```

- `plugin`：函数 / 构造器 / 对象插件
- `config`：传给插件的配置值（若有 `Plugin.Config` 会先校验）
- 返回：`Fiber & PromiseLike<Fiber>`，可 `await` 其激活完成

装配流程（`registry.ts` 的 `plugin()`）：

1. `resolve` 得到 `callback`
2. `assertActive` 确保当前上下文处于激活态
3. 创建/复用 `Plugin.Runtime`（缓存同一 callback）
4. `new Fiber(ctx, config, Inject.resolve(plugin.inject), runtime, ...)`
5. 返回带 `then` 的 Fiber 包装（`await` 即 `fiber.await()`）

---

## 3. 依赖注入：`@Inject`

### 3.1 类级注入

```ts
import { Context, Service } from 'cordis'

class MyService extends Service {
  @Inject('logger')
  static inject = ['logger']        // 类级依赖声明（等效写法）
  // ...
}
```

实际上 `@Inject` 作用于「类」时，把依赖写入类的静态 `inject` 字段；作用于「方法」时，`Inject` 会注册一个初始化钩子，让方法在依赖就绪后被调用。

### 3.2 `Inject.resolve`

```ts
export namespace Inject {
  export function resolve(inject: Inject | null | undefined, result = Object.create(null)) {
    // 数组 → { name: null }
    // 对象（含 checkProto 继承链）→ 递归合并
    return result
  }
}
```

它把 `inject` 归一化为 `Dict<name, config|null>`，作为 `Fiber.inject` 的初始依赖表。

---

## 4. 依赖供应的完整链路

一个完整「依赖注入」示例：

```ts
import { Context, Service } from 'cordis'

// 1) 定义可注入的服务
class Greeter extends Service {
  constructor(ctx: Context, config: Greeter.Config = {}) {
    super(ctx, 'greeter')
  }
  greet(name: string) {
    return `Hello, ${name}!`
  }
}

namespace Greeter {
  export interface Config { prefix?: string }
}

// 2) 装配一个消费该服务的插件
export default function myPlugin(ctx: Context, config: any) {
  // 供应服务（可逆效应：返回逆 = 撤销供应）
  ctx.plugin(Greeter)

  // 依赖注入读取服务
  const greeter = ctx.greeter          // 由 Reflect 代理拦截 get
  ctx.logger.info(greeter.greet('world'))
}
```

> **说明**：`ctx.greeter` 能工作，是因为 `ReflectService` 的 Proxy `get` 拦截器会在当前 fiber 的 `store` 中查找名为 `greeter` 的供应（见第 3 章第 5 节）。若当前上下文未注入该服务，会抛出「cannot get property "greeter" without inject」的增强错误。

---

## 5. Service 与 `provide`

### 5.1 通过 `Service` 基类

继承 `Service` 的类在构造时会自动 `provide` 自身：

```ts
class MyService extends Service {
  constructor(ctx, name = 'my-service') { super(ctx, name) }  // 自动 provide
}
```

### 5.2 通过静态 `provide`

`Service` 构造函数读取 `this.constructor['provide']` 作为默认名：

```ts
self.name = name ?? this.constructor['provide']
self.ctx.reflect.provide(name, self, self[symbols.check])
```

因此插件类可声明静态 `provide` 字段来指定服务名。

### 5.3 `check` 谓词

`Service.check`（符号方法）返回布尔值，用于判断「服务在当前上下文是否可用」。`Fiber._checkImpl` 会在依赖解析时调用它：

```ts
_checkImpl(name) {
  const impl = this.ctx.reflect._getImpl(name, true)
  if (impl.check && !impl.check.call(...)) return delete this._store[name]
  this._store[name] = impl
}
```

---

## 6. 声明式依赖与响应式更新

当服务被重新 `provide` 或 `set` 后，`notify` 使依赖它的插件**自动重新激活/停用**：

```ts
// reflect.notify 内部
fiber._checkImpl(name)   // 重新检查服务是否仍可用
fiber._refresh()          // 若 epoch 变化则触发 _reload/_unload
```

这意味着：**一个插件声明的依赖（coeffect）满足时自动激活，依赖失效时自动停用**，无需手动管理。

---

## 7. 完整最小示例

```ts
import { Context, Service } from 'cordis'

// 一个可注入的计数器服务
class Counter extends Service {
  private value = 0
  constructor(ctx: Context, config: Counter.Config = {}) {
    super(ctx, 'counter')
  }
  add(n: number) { this.value += n; return this.value }
  get current() { return this.value }
}
namespace Counter {
  export interface Config { initial?: number }
}

// 一个函数插件：供应 + 消费
export default function apply(ctx: Context) {
  ctx.plugin(Counter, { initial: 0 })

  ctx.logger.info('counter ready:', ctx.counter.current)
}
```

---

- [上一章：效应与协同效应机制](04-effects-coeffects.md) | [下一章：生命周期与状态机](06-lifecycle.md) →