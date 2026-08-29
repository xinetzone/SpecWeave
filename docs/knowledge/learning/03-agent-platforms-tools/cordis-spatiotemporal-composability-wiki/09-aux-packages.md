---
id: "cordis-spatiotemporal-composability-wiki-09"
title: "Cordis — 辅助包"
source: "https://github.com/cordiverse/paper"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/09-aux-packages.toml"
---
# Cordis — 辅助包

> 一句话摘要：本章快速讲解六个辅助包（create / group / include / logger-console / timer / utils）的职责与关键用法，它们是 Cordis 核心库之外的可选能力扩展，可在需要时按需装配。

---

## 1. `create`：项目脚手架

`packages/create` 提供 `create-cordis` CLI，从 npm 模板脚手架一个新项目：

- `bin.ts` 调用 `scaffold()`，使用默认模板 `@cordisjs/boilerplate`。
- 流程：`getName`（交互或参数）→ `prepare`（目录校验）→ `scaffold`（下载模板 tar 解压）→ `stageYarnBin`（yarn 二进制安置）→ `initGit` → `install`。

关键 CLI 参数（`yargs-parser`）：

| 参数 | 别名 | 含义 |
|------|------|------|
| `--template` | `-t` | 指定 npm 模板 |
| `--ref` | `-r` | 指定模板版本（默认 latest） |
| `--forced` | `-f` | 强制覆盖非空目录 |
| `--git` | `-g` | 初始化 git |
| `--yes` | `-y` | 跳过安装 |

```bash
create-cordis my-app -t @cordisjs/boilerplate
```

---

## 2. `group`：分组插件

`packages/group` 只是 re-export loader 的 `Group`：

```ts
import { Group } from '@cordisjs/plugin-loader'
export default Group
```

`Group` 允许把一组插件声明为一个可复用装配单元（见第 7 章第 6 节），便于复杂应用的模块化装配。

---

## 3. `include`：配置文件导入

`packages/include` 把 YAML/JSON 配置文件读取为装配条目并支持写回（详见第 7 章第 5 节）。核心职责：

- 注册 YAML `!!js` 标签，解析配置中的 JS 表达式。
- `applyPatches` 支持 `insert`/按 `id` 覆盖。
- `refresh` 在文件变化时重新读取并对装配树做增量更新。

---

## 4. `logger-console`：控制台日志导出器

`packages/logger-console` 提供 `ConsoleExporter`，把 Cordis 的日志消息输出到控制台：

- `shared.ts` 的 `ConsoleExporter` 完成格式化渲染（时间戳、颜色、label 对齐、diff 时长）。
- `index.ts`（Node 版）用 `node:util.inspect` 支持 `%o`/`%O` 对象格式化，并检测 `supports-color`。
- `browser.ts` 用原生 `console[method]`。

```ts
import { ConsoleExporter } from '@cordisjs/plugin-logger-console'
export default function apply(ctx: Context) {
  ctx.plugin(ConsoleExporter)   // 装配后，ctx.logger 输出到控制台
  ctx.logger.info('hello cordis')
}
```

---

## 5. `timer`：定时器核心服务

`packages/timer` 提供 `TimerService`，并把定时能力 `mixin` 到上下文：

```ts
ctx.mixin('timer', ['timeout', 'interval', 'throttle', 'debounce', 'setTimeout', 'setInterval'])
```

所有定时器都通过 `ctx.effect()` 注册清理，因此**随上下文销毁自动清除**：

```ts
// 超时（返回 dispose，或 Promise）
const dispose = ctx.timeout(() => { ... }, 1000)
const stop = ctx.interval(() => { ... }, 500)

// 节流 / 防抖（带 dispose）
const throttled = ctx.throttle(fn, 200)
const debounced = ctx.debounce(fn, 300)
```

关键实现：`throttle`/`debounce` 通过 `_schedule` 统一包装，返回值挂载 `.dispose` 方法。

> `setTimeout`/`setInterval` 是 `timeout`/`interval` 的**已废弃别名**，建议使用 `ctx.timeout()`/`ctx.interval()`。

---

## 6. `utils`：`List` 响应式列表

`packages/utils` 提供 `List<T>`——一个随上下文生命周期管理的响应式列表：

```ts
export class List<T> {
  private sn = 0
  private inner = new Map<number, T>()

  push(value: T) {
    this.ctx.effect(() => {
      this.inner.set(++this.sn, value)
      return () => this.inner.delete(this.sn)   // 随上下文销毁自动移除
    }, `${this.trace}.push()`)
  }

  filter(predicate) { /* 惰性迭代 */ }
  map(mapper) { /* 惰性迭代 */ }
  [Symbol.iterator]() { return this.inner.values() }
}
```

**要点**：每个 `push` 都是一个可逆效应——元素加入时记录逆（删除），上下文销毁时自动移除，与 Cordis 的时空可组合性保持一致。

---

## 7. 辅助包装配示意

```ts
import { Context } from 'cordis'
import Timer from '@cordisjs/plugin-timer'
import ConsoleExporter from '@cordisjs/plugin-logger-console'

export default function apply(ctx: Context) {
  ctx.plugin(Timer)
  ctx.plugin(ConsoleExporter)

  ctx.on('ready', () => {
    ctx.interval(() => ctx.logger.info('tick'), 1000)   // 自动随上下文销毁
  })
}
```

---

- [上一章：热更新 HMR](08-hmr.md) | [下一章：使用示例](10-usage-examples.md) →