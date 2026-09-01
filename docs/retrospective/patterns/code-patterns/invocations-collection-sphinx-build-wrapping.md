---
type: Pattern
id: "invocations-collection-sphinx-build-wrapping"
source: "spec:update-invocations-bundle-optimize-okf"
maturity: "L1"
validation_count: 1
---
# invocations Collection 封装 Sphinx 构建

## 模式类型

代码模式 / CLI 任务化 / 工程搭建

## 成熟度

L1 已验证（1次验证，2026-08-24 awesome-okf-xs `tasks.py`）

## 模式概述

为 Sphinx 文档项目引入 `invoke` 任务化入口时，直接复用 vendor `invocations.docs` 的 Collection，以 `@task(default=True)` 包装一个 `build` 任务注入 `-E -b html`，`clean/browse/tree/doctest` 直接复用原任务不重实现，通过 `ns.configure` 注入 `sphinx.source/target/target_file`，并解决 Windows 无 `pty` 模块导致的崩溃问题。核心价值是**避免重复实现已有任务、消除 CI 命令漂移、做到 `invoke build` 与 `sphinx-build -E -b html` 完全等价**。

## 问题现象

1. **CI 命令硬编码**：CI 直接写 `sphinx-build -E -b html doc _build/html`，参数散落各处，改默认值要改多处，易漂移。
2. **重复实现已有任务**：手写自己项目的 `clean/browse/doctest/tree`，与 `invocations.docs` 功能重复，违背 DRY。
3. **Windows 崩溃**：`invocations.docs.build` 硬编码 `pty=True`，Windows 无 `pty` 模块直接中止。
4. **leave空目录**：clean 只删 target，留下空的 `_build` 父目录。
5. **依赖不全**：只装 `invoke` 不装 `invocations`，`from invocations import docs` 直接 `ModuleNotFoundError`。

## 解决方案

### 步骤1：声明依赖

`pyproject.toml` 的 doc 可选依赖同时声明 `invoke` 与 `invocations==<vendor版本>`（如 `4.1.0`）。

### 步骤2：顶层 Collection 布局

`tasks.py` 顶层 `from invoke import Collection, task`、`from invocations import docs`，最终导出 `ns = Collection(...)`；`invocations` 各模块通过 `ns`/`Collection` 后自动注册子命令。

### 步骤3：包装 build 注入默认 opts

```python
@task(default=True, help=docs.build.help)
def build(c, clean=False, browse=False, nitpick=False,
          opts="-b html -E", source=None, target=None) -> None:
    if clean:
        docs._clean(c)
    if nitpick:
        opts += " -n -W -T"
    cmd = "sphinx-build{} {} {}".format(
        (" " + opts) if opts else "",
        source or c.sphinx.source, target or c.sphinx.target)
    c.run(cmd, pty=...)
    if browse:
        docs._browse(c)
```
- 用 `docs.build.help` 保证参数说明与 vendor 一致。
- 等价性：`invoke build` → `sphinx-build -b html -E <source> <target>`。

### 步骤4：ptWindows pty 适配

把 `c.run(cmd, pty=...)` 的 pty 改为可配置：

```python
pty = c.config.get("run", {}).get("pty", sys.platform != "win32")
```

POSIX 默认 True（对齐 CI 行为），Windows 默认 False，可用配置键 `run.pty` 显式覆盖。

### 步骤5：复用而非重实现

`browse = docs._browse; tree = docs.tree; doctest = docs.doctest`；clean 仅删 `sphinx.target` 后额外回收空父目录：

```python
@task(name="clean")
def clean(c):
    docs._clean(c)                       # 删 _build/html
    parent = os.path.dirname(c.sphinx.target)
    while parent and os.path.isdir(parent) and not os.listdir(parent):
        os.rmdir(parent); parent = os.path.dirname(parent)  # 回收空 _build
```

### 步骤6：配置注入与 CI 接线

```python
ns.configure({"sphinx": {"source": "doc", "target": "_build/html", "target_file": "index.html"}})
```
CI 改为 `invoke build`，本地验证 `invoke build` 产出 `_build/html/index.html`、`invoke clean` 生效。

## 适用场景

- ✅ 已有 Sphinx 文档项目想加 `invoke` 任务化入口。
- ✅ 想复用 vendor `invocations` 的 docs/pytest/ci 等 Collection 而非重写。
- ✅ 需要 `invoke build` 与 CI 原 sphinx-build 命令严格等价。

- ❌ 只想一次性快速构建 Sphinx，不需要任务化入口。
- ❌ 项目强绑定非 Linux/POSIX 且有更复杂构建脚本，pure 任务层无法承载。

## 实际案例

awesome-okf-xs：`invoke build` 产出 `_build/html/index.html`，`invoke clean` 生效，CI pages.yml 改为 `invoke build`，pyproject doc 依赖加 `invoke` + `invocations==4.1.0`。

## 失败案例

- **场景**：初期直接给 `build` 硬编码 `pty=True`，在 Windows 本地 `invoke build` 因无 `pty` 模块中止。
- **教训**：复用 vendor 任务时需审查其默认参数是否依赖 POSIX 专属能力（pty），并做成可配置。

## 反模式

### 反模式1：CI 硬编码 sphinx-build 命令

参数散落、变更漂移。**正确做法**：包装成 `invoke build`，默认值集中在 `opts` 一处。

### 反模式2：重复实现 invocations.docs 已有任务

clean/browse/doctest 手写一遍，与 vendor 重复。**正确做法**：直接赋值复用 `docs._clean/_browse/tree/doctest`。

### 反模式3：build 硬编码 pty=True

Windows 无 `pty` 模块直接崩溃。**正确做法**：pyt 可配置，Windows 默认 False。

### 反模式4：硬编码 DOC/SOURCE 路径而非 ns.configure

路径散落、与 vendor `c.sphinx.source/target` 读取机制脱节。**正确做法**：通过 `ns.configure` 注入 `sphinx.source/target`。

### 反模式5：clean 不回收空父目录

删完 target 留下空的 `_build`。**正确做法**：循环回收空父目录。

### 反模式6：依赖只加 invoke 不加 invocations

`from invocations import docs` 崩溃。**正确做法**：doc 依赖同时声明 `invoke` 与 `invocations==<版本>`。

### 反模式7：复用假想的配置键

引用 vendor 不存在的配置键（如 `packaging.find_opts`）。**正确做法**：仅引用 vendor 源码真实存在的配置键。

## 检验标准

| 维度 | 检验点 |
|---|---|
| 等价性 | `invoke build` 命令字符串与 `sphinx-build -b html -E src tgt` 完全一致 |
| 复用 | clean/browse/tree/doctest 不重实现 |
| 跨平台 | Windows 本地 `invoke build` 不崩溃（pty 可关） |
| 配置 | path 来自 `c.sphinx.source/target`，非硬编码 |
| 依赖 | 同时声明 invoke + invocations |
| G3（模式） | 含触发场景、核心步骤、反模式（≥6）、迁移验证 |

## 跨场景迁移

- **其他 Sphinx 项目**：复制 build 包装 + 配置注入，改 source/target 即可。
- **复用 pytest/ci/checks Collection**：同样顶层 `from invocations import pytest` 并 `ns.add_collection`，统一入口。
- **非 Sphinx 构建**：把"包装 vendor 任务 + ns.configure 注入 + 平台参数可配置"的思想迁移到任意 CLI 构建。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---|---|---|
| cli-as-api-design | 相关 | 把 sphinx-build 子命令封装成稳定的 `invoke build` API |
| thin-wrapper-pattern | 上位 | build 是 vendor 任务的薄包装，只加默认 opts |
| config-source-priority-explicitness | 相关 | run.pty 默认值来自平台、可被 c.config 显式覆盖 |
| source-code-to-okf-adversarial-update | 相关 | 封装前需对账 bundle 确认 vendor 配置键真实存在 |

<!-- changelog -->
- 2026-08-24 | pattern | 初始创建：从 awesome-okf-xs invoke 任务化实践萃取