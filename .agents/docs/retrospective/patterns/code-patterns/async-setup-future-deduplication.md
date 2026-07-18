---
id: "async-setup-future-deduplication"
source: "../../../../../external/tools/scikit-build-core/tests/packages/abi3_setuptools_ext/setup.py#L148-L190"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/async-setup-future-deduplication.toml"
---
# 装配并发去重（Async Setup Future Deduplication）

## 1. 问题

当多个协程/任务可能同时触发“装配某个组件/插件”（例如依赖装配、用户显式启用、后台预加载），会出现：

- 重复执行 setup（浪费、甚至导致重复注册）
- 并发竞态（中间态被读到，引发不可预测错误）
- 失败传播不一致（调用方 A 失败、调用方 B 挂起或误判成功）

## 2. 解决方案（模式）

以“组件标识（如 domain）”为 key，在共享上下文中维护一个 `Future`：

- 第一次请求创建 Future，并执行真实 setup
- 后续并发请求直接 await 该 Future
- setup 成功/失败都将结果/异常写回 Future，确保所有等待方一致感知

该模式在 Home Assistant Core 的 `async_setup_component` 中用于 domain 级去重（见 [setup.py](../../../../../external/anthropics/claude-quickstarts/browser-use-demo/setup.py#L148-L190)）。

## 3. 实施要点

### 3.1 状态存放位置

- 放在“运行时根对象”的共享字典中（类似 `hass.data`），确保跨模块可见且生命周期一致

### 3.2 异常处理

- 捕获 `BaseException` 并写回 Future，避免等待方永远挂起
- 写回异常后，可以尝试 `await future` 以触发“无人等待也清理状态”的逻辑（按系统需要选择）

### 3.3 与依赖装配结合

- 依赖装配触发的 setup 也必须走同一去重入口，避免“依赖路径”与“直接路径”重复执行

## 4. 反例

- 仅用布尔 flag（`is_loading`）而不用 Future：等待方无法自然 await，异常传播困难
- 只写成功不写失败：失败时等待方永久挂起

