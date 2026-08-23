---
id: "cordis-spatiotemporal-composability-wiki-11"
title: "Cordis — FAQ 与注意事项"
source: "https://github.com/cordiverse/paper"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/11-faq-notes.toml"
---

# Cordis — FAQ 与注意事项

> 一句话摘要：本章汇总学习与使用 Cordis 时的常见问题与注意事项，重点是「API 未稳定、活跃开发中」的核心提醒，以及异步效应、注入语义、HMR 前置条件等易踩坑点。

---

## 1. ⚠️ 核心提醒：API 尚未稳定

Cordis 官方 README 明确声明：

> **Cordis is under active development. The API is not yet stable and may change without notice.**

配套论文也是「活跃修订中的预印本」。这意味着：

- 本教程的**所有代码片段、文件名、API 签名均基于学习时的快照**，不应视为长期契约。
- 集成到项目前，务必以当前仓库的最新源码为准，不要盲目信任历史文档。
- 论文中的具体推导结论，使用前请回看最新版本。

---

## 2. 异步效应（Async Effect）

**Q**：`ctx.effect()` 的异步形态什么时候用？

**A**：当你的副作用初始化本身是异步的时候（如异步建连、异步订阅）：

```ts
ctx.effect(async () => {
  const conn = await createConnection()
  return () => conn.close()   // 返回 Promise<Disposable>
})
```

运行时在卸载时会 `await` 这个逆函数链（`fiber._unload` 里 `Promise.all`），保证异步清理也顺序完成。注意：`fiber._execute` 对异步可迭代会检查 `epoch`，若在迭代期间 epoch 发生变化会中断本次效应。

---

## 3. 注入语义：为什么报 `cannot get property`

**Q**：访问 `ctx.someService` 报 `cannot get property "someService" without inject` 怎么办？

**A**：Cordis 的依赖访问是「显式声明」的。必须先用 `@Inject('someService')` 或 `static inject = ['someService']` 声明依赖，`ReflectService` 的 Proxy 才会在当前光纤的 `store` 中解析它。未声明直接访问会抛出增强错误。这是「空间可组合性」的刻意设计——依赖必须显式化，才能被响应式追踪。

---

## 4. HMR：需要 `--expose-internals`

**Q**：启动 HMR 报 `--expose-internals is required for HMR service`？

**A**：HMR 依赖 Node 内部的 `ModuleLoader.loadCache`。启动命令需带上 `--expose-internals`：

```bash
node --expose-internals ./main.ts
```

缺少该标志时 `ModuleLoader.fromInternal()` 返回 `undefined`，`Hmr` 构造器直接抛错。

---

## 5. HMR 的 Node 版本兼容

**Q**：HMR 在哪些 Node 版本上可用？

**A**：`ModuleLoader` 接口在 Node 22/23 与 Node 24+ 之间有破坏性差异（`internal.ts` 中分别定义 `ModuleLoaderV1` 与 `ModuleLoaderV2`）：

| Node 版本 | 接口 | 关键差异 |
|-----------|------|---------|
| 22 / 23 | `v1` | `resolve()`、`getModuleJobForImport()` |
| 24+ | `v2` | `resolveSync()`、`getOrCreateModuleJob()`、`loadCache` 类型变化 |

Cordis 已做双版本兼容，但不同 Node 版本下 HMR 的内部缓存处理路径不同，升级 Node 时需重新验证 HMR 行为。

---

## 6. 服务隔离（isolate）的理解

**Q**：两个插件都 `provide` 同名服务会怎样？

**A**：默认会冲突（`reflect.provide` 对同一 symbol 重复注册会抛「service has been registered」）。要允许同名服务在不同作用域共存，用 loader 的 `isolate`：

```yaml
plugins:
  - id: a
    name: ./impl-a
    isolate: { storage: true }     # a 私有实现
  - id: b
    name: ./impl-b
    isolate: { storage: true }     # b 私有实现
```

`isolate: true` 使用 `LocalRealm`（每 entry 独立 symbol）；`isolate: 'label'` 使用 `GlobalRealm`（同 label 共享）。

---

## 7. 配置合并的粒度

**Q**：配置文件变更时，是否所有插件都会重启？

**A**：不会。`Entry.update()` 会用 `deepEqual` 计算 diff，只有变化字段才会触发「部分释放（partial-dispose）」与重装配；`diff` 为空时直接返回。这是「配置合并」设计的核心，避免无谓的重启开销。

---

## 8. 定时器的正确用法

**Q**：为什么建议用 `ctx.timeout()` 而非 `setTimeout()`？

**A**：`setTimeout`/`setInterval` 是 `TimerService` 中标注 `@deprecated` 的别名。`ctx.timeout()`/`ctx.interval()` 返回的定时器被 `ctx.effect()` 包裹，随上下文销毁自动清除，避免泄漏。同理 `throttle`/`debounce` 返回值带 `.dispose`。

---

## 9. 根上下文与子上下文

- **根光纤**（`runtime === null`）永不销毁，`ctx.dispose()` 实际是 `restart()` 自身。
- 普通 `ctx.plugin()` 创建子光纤时，父子之间通过 `parent.fiber.effect()` 建立「可逆嵌套」，卸载子光纤会逆序回收其全部副作用。

---

## 10. 学习建议与坑位清单

| 坑位 | 说明 | 规避方法 |
|------|------|---------|
| API 版本漂移 | 框架活跃开发，签名经常变 | 以仓库当前源码为准 |
| 忘记声明 `@Inject` | 访问服务报 `without inject` | 先声明 `inject` 再访问 |
| 异步清理被跳过 | 未返回逆函数 | `effect` 回调务必返回 dispose |
| HMR 不生效 | 缺少 `--expose-internals` | 启动带上该标志 |
| 同名服务冲突 | 默认全局共享 | 用 `isolate` 隔离作用域 |

---

- [上一章：使用示例](10-usage-examples.md) | [下一章：总结与资源](12-summary-resources.md) →