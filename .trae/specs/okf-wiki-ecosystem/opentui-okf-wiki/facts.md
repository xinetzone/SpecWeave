---
status: "draft"
id: "opentui-okf-wiki-facts"
title: "OpenTUI 编号事实清单"
source: "OpenTUI source commit f8f608e2b9a41685d613a1156708ff06c826c3ce; https://opentui.com/docs/"
date: "2026-10-20"
methodology: "R stage of R-I-E-V-C"
content-sensitivity: "public"
tags: ["OpenTUI", "source-facts", "OKF"]
---

# OpenTUI 编号事实清单

> R 阶段事实台账。事实仅记录固定源码或官方文档中可定位的声明；架构解释与学习建议另列于 `insights.md`。源码链接均固定到 commit `f8f608e2b9a41685d613a1156708ff06c826c3ce`，不使用本机绝对路径。

## 信源与版本坐标

- 源码仓库：[`anomalyco/opentui`](https://github.com/anomalyco/opentui)，固定 commit `f8f608e2b9a41685d613a1156708ff06c826c3ce`。
- 源码工作树没有精确匹配的 release tag；源码引用使用不可变 commit URL。
- 官方文档含有 `0.6.6` 发布说明；Core package manifest 的 `version` 字段也记录 `0.6.6`。发布文档版本、manifest 字段和源码 commit 是不同坐标，本清单不据同名版本推断它们是同一个 release 标识。
- 数量核验：从 `scripts/npm-publish.ts` 的 `RELEASE_PACKAGES` 数组范围中筛选 `releasePackage(...)` 行，PowerShell 计数结果为 `release_package_count=7`；同一数组列出的名称为 core、react、solid、three、qrcode、keymap、ssh。计数对象是发布脚本中的 release package entries，不是 workspace 所有目录、平台包或 subpath exports。

## 编号事实

### 仓库与包

- **F-001**：根 `package.json` 将 Bun `1.4.1` 声明为 package manager；README 写明开发需要 Bun `1.4.1` 或更高版本、Zig `0.16.0`。[README](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/README.md#L54) · [根 package manifest](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/package.json)
- **F-002**：`packages/core/package.json` 的 `version` 是 `0.6.6`；其 `engines` 分别声明 Bun `>=1.3.14` 与 Node `>=26.4.0`。[Core manifest](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/package.json#L12-L13) · [Core engines](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/package.json#L135-L138)
- **F-003**：发布脚本 `RELEASE_PACKAGES` 中的七个条目是 `@opentui/core`、`@opentui/react`、`@opentui/solid`、`@opentui/three`、`@opentui/qrcode`、`@opentui/keymap`、`@opentui/ssh`。上述数量来自脚本计数，范围仅限该数组。[发布清单](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/scripts/npm-publish.ts#L43-L50)
- **F-004**：官方 package-entrypoints 文档分别列出 Core、React、Solid、Keymap、QRCode、SSH 与 Three 的 package root/subpath、运行环境和指南链接；它也列出 `@opentui/core/testing`、`@opentui/react/test-utils` 等子路径。[Package entry points](https://opentui.com/docs/reference/package-entrypoints/)
- **F-005**：官方 entrypoints 文档列出 `@opentui/react/renderer`，并说明其声明包括 `createRoot`、`createPortal`、`flushSync` 与 `Root`；该 subpath 不作为 workspace React manifest 中的单独 package exports 项目呈现。[Package entry points](https://opentui.com/docs/reference/package-entrypoints/) · [React manifest exports](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/react/package.json#L15-L40)
- **F-006**：官方 entrypoints 文档将 `@opentui/core` 描述为 renderer、renderables、input、buffers、audio、plugins、Tree-sitter 与共享类型入口；将 `@opentui/three` 描述为 Three.js WebGPU renderer、renderable、sprites、effects、resource pools 与 physics adapters 入口。[Package entry points](https://opentui.com/docs/reference/package-entrypoints/)
- **F-007**：官方 entrypoints 文档将 `@opentui/keymap` 列为 host-agnostic 键位映射入口，并列出 extras、addons、OpenTUI/React/Solid hosts、HTML host 与 testing subpaths。[Package entry points](https://opentui.com/docs/reference/package-entrypoints/)
- **F-008**：官方 entrypoints 文档将 `@opentui/qrcode` 列为 QR 编码与 `QRCodeRenderable` 入口，将 `@opentui/ssh` 列为 SSH server builder、认证、中间件、会话和日志入口。[Package entry points](https://opentui.com/docs/reference/package-entrypoints/)

### Core 与 renderable tree

- **F-009**：`packages/core/src/index.ts` 从 `renderer.js` 与 `renderables/index.js` 导出 renderer 和 renderables，并以 `Yoga` 名称导出 `yoga.js` 命名空间。[Core index](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/index.ts#L18-L29) · [Yoga export](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/index.ts#L156-L158)
- **F-010**：Core 的 package manifest 将 `.` 指向 `src/index.ts`，将 `./testing` 指向 `src/testing.ts`，并声明 `./yoga`、runtime-plugin、parser worker 与 node-assets 等 exports。[Core exports](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/package.json#L91-L138)
- **F-011**：`packages/core/src/testing.ts` 再导出 test renderer、mock keys、mock mouse、Tree-sitter mock、terminal capabilities 与 spy 模块。[Testing exports](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/testing.ts#L1-L7)
- **F-012**：`TextRenderable` 在 `packages/core/src/renderables/Text.ts` 中继承 `TextBufferRenderable`，构造函数参数为 `ctx: RenderContext` 与 `options: TextOptions`。[TextRenderable](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/renderables/Text.ts#L9-L31)
- **F-013**：`BaseRenderable` 声明 `parent`、抽象 `add(...)` 与 `remove(...)`；`Renderable` 维护 `focusable` 与 `focused` 状态，并实现 `focus()`/`blur()` 相关逻辑。[Renderable base](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L240-L287) · [Renderable focus](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L301-L339) · [focus methods](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L579-L655)
- **F-014**：`Renderable.add(...)` 将输入转换为 renderable 并放入子项结构；`remove(...)` 从父节点布局子项中移除节点并清除其 parent 关系。[add](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L1657-L1688) · [remove](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/Renderable.ts#L1753-L1781)
- **F-015**：Core quickstart 调用 `createCliRenderer()` 后通过 `renderer.root` 添加内容，并明确要求创建应用 renderer 的代码在各关闭路径调用 `renderer.destroy()`。[Quickstart](https://opentui.com/docs/getting-started/quickstart/)
- **F-016**：`createCliRenderer(config: CliRendererConfig = {})` 返回 `Promise<CliRenderer>`；`CliRenderer` 提供 `destroy()`，配置类型包含 `targetFps`。[Renderer factory](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/renderer.ts#L155-L175) · [factory signature](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/renderer.ts#L847-L847) · [destroy interface](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/renderer.ts#L330-L340)
- **F-017**：官方 native rendering 文档描述 scene 节点对应 Yoga node，并将过程分为树结构、Yoga 布局、终端 cell 绘制、输出目标交付等部分。[Native rendering](https://opentui.com/docs/native/overview/)
- **F-018**：native `Scene` 通过 Yoga API 创建、移动和移除 Yoga children；源码注释说明 scene state 扩展既有 Yoga owner，而非再持有一份 layout node。[Scene](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/native/src/scene.zig#L232-L241) · [Yoga child operations](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/native/src/scene.zig#L467-L498)
- **F-019**：官方 native frames 文档区分 layout/paint/output 编码与传输阶段，并说明 Yoga layout、分配、排序、paint-list preparation、painting 和 output encoding 仍包含同步工作。[Frames and output](https://opentui.com/docs/native/frames/)
- **F-020**：官方 host I/O 文档说明 OpenTUI 使用宿主 event loop 进行调度与终端输入，Context I/O 本身不安装终端 transport 或 event loop；native overview 同样说明 native library 不启动 application event loop 或 rendering worker。[Host I/O and time](https://opentui.com/docs/native/host-io-time/) · [Native rendering](https://opentui.com/docs/native/overview/)

### React、Solid 与交互

- **F-021**：React 官方示例从 `@opentui/core` 导入 `createCliRenderer`，从 `@opentui/react` 导入 `createRoot`，再执行 `createRoot(renderer).render(<App />)`。[React bindings](https://opentui.com/docs/bindings/react/)
- **F-022**：React `createRoot(renderer)` 接收一个已有 `CliRenderer` 并返回带有 `render(node)`、`unmount()` 的 root；官方生命周期说明指出 root 不拥有 renderer，`unmount()` 不销毁 renderer，而 `renderer.destroy()` 会清理其 React root。[React lifecycle](https://opentui.com/docs/bindings/react/#lifecycle-and-cleanup) · [React reconciler](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/react/src/reconciler/renderer.ts#L14-L56)
- **F-023**：Solid 官方示例从 `@opentui/solid` 导入 `render`，用 `render(() => <App />)` 挂载 Solid 组件。[Solid bindings](https://opentui.com/docs/bindings/solid/)
- **F-024**：Solid reconciler 源码从 `./renderer/index.js` 导入 `createRenderer`，并导出 `_render(code, root)`；Solid hooks 源码导入 Solid 的 `createSignal`、`createEffect` 等响应式原语。[Solid reconciler](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/solid/src/reconciler.ts#L25-L31) · [Solid render](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/solid/src/reconciler.ts#L455-L465) · [Solid hooks](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/solid/src/elements/hooks.ts#L1-L12)
- **F-025**：官方 interaction 文档将 terminal-window focus 与 renderable focus 分开描述；一个 renderer 跟踪当前 renderable focus，且 Core 不提供自动 Tab traversal 或 focus-order 属性。[Interaction](https://opentui.com/docs/core-concepts/interaction/)
- **F-026**：官方 interaction 文档说明 renderable 只有在 `focusable` 为 true 时调用 `focus()` 才能获得焦点；官方 keyboard 文档说明键盘事件可直接监听 renderer，也可交给当前 focused renderable。[Interaction](https://opentui.com/docs/core-concepts/interaction/) · [Keyboard input](https://opentui.com/docs/core-concepts/keyboard/)
- **F-027**：官方 keyboard 文档将 `@opentui/keymap` 描述为提供 scoped layers、named commands、multi-stroke sequences、active-key queries 与 command metadata 的可选键位映射层。[Keyboard input](https://opentui.com/docs/core-concepts/keyboard/) · [Keymap overview](https://opentui.com/docs/keymap/overview/)

### 测试与生命周期

- **F-028**：`TestRendererOptions` 扩展 `CliRendererConfig`，增加 `width`、`height`、`kittyKeyboard` 与 `otherModifiersMode` 字段；`createTestRenderer(options)` 返回 `Promise<TestRendererSetup>`。[Test renderer types](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/testing/test-renderer.ts#L14-L72) · [factory](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/testing/test-renderer.ts#L197-L197)
- **F-029**：`TestRendererSetup` 暴露 renderer、mock input/mouse、render/flush/wait helpers、frame capture、resize、dispose 与 `Symbol.asyncDispose`。[Test renderer setup](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/testing/test-renderer.ts#L53-L72)
- **F-030**：官方 testing 文档的示例以 `createTestRenderer({ width, height })` 创建测试环境，并在 `finally` 中调用 `setup.renderer.destroy()`；文档也允许 `await setup.dispose()` 清理。[Testing](https://opentui.com/docs/core-concepts/testing/)
- **F-031**：React reconciler 在 renderer 发出 `CliRenderEvents.DESTROY` 时执行 cleanup；官方 React 生命周期文档指出 renderer 销毁会卸载其 React root。[React reconciler](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/react/src/reconciler/renderer.ts#L29-L56) · [Lifecycle](https://opentui.com/docs/core-concepts/lifecycle/)
- **F-032**：官方 lifecycle 文档说明 `renderer.destroy()` 同步且幂等，并停止 input 与 scheduling；正常关闭如需等待 renderer output，应等待 `closed`。[Lifecycle](https://opentui.com/docs/core-concepts/lifecycle/)
- **F-033**：官方 release `0.6.6` 说明 nullish layout writes 会将 layout 恢复为构造时默认值；该发布说明与源码 commit、Core manifest 版本分别登记，不以此证明 release tag 匹配。[0.6.6 release notes](https://opentui.com/docs/releases/0.6.6/)
- **F-034**：官方 docs 的 quickstart 使用 `BoxRenderable`、`TextRenderable` 与 `createCliRenderer`；`TextRenderable` 的构造函数接受 render context 和 text options。[Quickstart](https://opentui.com/docs/getting-started/quickstart/) · [Text source](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/src/renderables/Text.ts#L9-L31)
- **F-035**：官方 package-entrypoints 文档将发布包的 root/subpath 列为不同 public entrypoint；子路径 exports 与 release package 数量是不同统计对象。[Package entry points](https://opentui.com/docs/reference/package-entrypoints/) · [Core exports](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/package.json#L31-L62)

## G1 自检

- 事实未将设计动机或因果推断作为事实结论；解释性判断留待 I 阶段。
- API、package 名称、版本字段和生命周期行为均链接到固定源码 commit 或官方文档。
- 唯一在本台账明确给出并需脚本计数的发布包数，已按 `RELEASE_PACKAGES` 数组条目计数为 7；未将 exports subpath 或 platform packages 混入该计数。
- 本台账未把本机绝对路径作为长期来源坐标。
