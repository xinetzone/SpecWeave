---
status: "draft"
id: "opentui-okf-wiki-insights"
title: "OpenTUI 架构洞察与知识地图"
source: "facts.md; OpenTUI source commit f8f608e2b9a41685d613a1156708ff06c826c3ce; https://opentui.com/docs/"
date: "2026-10-20"
methodology: "I stage of R-I-E-V-C"
content-sensitivity: "public"
tags: ["OpenTUI", "architecture", "learning-map"]
---

# OpenTUI 架构洞察与知识地图

> 以下洞察由 `facts.md` 的编号事实推导；“行动”决定 bundle 文档组织，不反向充当源码事实。

## 核心洞察

### I-001：理解 OpenTUI 要同时追踪应用层对象树与 native scene，而不是把它当成单层绘图库

- **陈述**：Core 暴露可组合的 renderable 树，native `Scene` 持有与 Yoga 布局及 cell 绘制相连的 scene 数据；二者之间的映射是解释布局、重排与帧输出的关键。
- **证据**：F-009、F-013、F-014、F-017、F-018、F-019。
- **反常识**：React/Solid JSX 并不意味着浏览器 DOM；框架 reconciler 将声明式节点接入 OpenTUI renderable/native scene 路径，终端帧仍由其自己的布局、绘制和输出过程形成。
- **行动**：先介绍 Core renderable/renderer，再串起 native Scene、Yoga、cell paint 与 output delivery；把框架 bindings 安排在 Core 基础之后。

### I-002：native 核心并不等同于完整的应用运行时

- **陈述**：终端 input、帧调度、output transport 与 native scene 渲染有明确边界；宿主 event loop 驱动应用时间和终端 I/O，native library 不自行启动应用事件循环或 rendering worker。
- **证据**：F-016、F-019、F-020、F-032。
- **反常识**：看到 Zig 渲染核心，不应推断所有调度和输出均在 Zig 后台线程执行；官方资料把宿主调度、native paint 与 output delivery 分别描述。
- **行动**：将 native rendering 按“host 驱动 → layout/paint → 编码/交付”讲解，并把交付完成与终端实际显示区分开。

### I-003：renderer 与 framework root 的所有权分离，是跨框架生命周期的首要约束

- **陈述**：应用创建 `CliRenderer` 并负责销毁；React root 管理 React tree，Solid render 管理 Solid root，但 renderer shutdown 仍是应用关闭流程中的独立责任。
- **证据**：F-015、F-021、F-022、F-023、F-031、F-032。
- **反常识**：React `root.unmount()` 不等于 renderer 关闭；调用 renderer `destroy()` 则会触发 React cleanup。Solid `render()` 也不能被误读为自动归还宿主终端所有权。
- **行动**：将 ownership 与 cleanup 提前纳入 Core、React、Solid 教程，并在所有示例中展示 `try/finally` 或明确 shutdown。

### I-004：终端交互语义不能从 Web UI 心智模型直接迁移

- **陈述**：Renderable focus、terminal-window focus、键盘分发、鼠标 hit testing 是不同机制；Core 不自动执行 Tab focus traversal，应用需要定义焦点次序与键盘替代路径。
- **证据**：F-013、F-025、F-026、F-027。
- **反常识**：终端窗口获得焦点不代表某个控件获得输入；组件声明成 JSX 元素也不会自动生成浏览器 accessibility tree 或 DOM click 语义。
- **行动**：单列 interaction/keyboard 教程，区分终端窗口事件和 renderable focus；用测试 renderer 演示可预测的输入与焦点行为。

### I-005：OpenTUI 的公开表面是“release packages × entrypoints × host/runtime”，不能只按 workspace 目录组织学习

- **陈述**：发布脚本登记 package root，而官方 entrypoints 还列出 framework、testing、runtime、host 等子路径；package 数量与可导入 entrypoint 数量不是同一指标。
- **证据**：F-003、F-004、F-005、F-006、F-007、F-008、F-010、F-035。
- **反常识**：七个发布 package 不意味着只有七个可导入模块，也不能把 platform packages、workspace 子目录或 generated files 直接计入该数字。
- **行动**：概念文档分别说明七个发布包的责任面、Core/React/Solid 常用入口与关键 subpaths；所有计数注明统计对象，完整 subpath 查阅官方入口参考表。

## 知识地图

### 学习路径

1. **建立全局模型**：阅读项目和 package 总览，区分固定源码 commit、官方 docs 0.6.6、package manifest version 与开发工具版本。
2. **从 Core 起步**：学习 `createCliRenderer`、renderable tree、Text/Box、layout、输入与 focus。
3. **掌握清理和测试**：认识 renderer ownership、`destroy()`、`closed`、`createTestRenderer(options)` 与 mock input/mouse。
4. **选择声明式绑定**：需要 React 时学习 `createRoot(renderer)` 与独立 unmount 语义；需要 Solid 时学习 `render(...)`、signals/effects 与其 renderer API。
5. **深入机制与生态包**：追踪 native Scene、Yoga、paint/output；再根据需求查阅 Keymap、QRCode、Three、SSH。

### 计划文档与事实覆盖

| 次序 | 计划文件（bundle 内路径） | 文档重点 | 事实依据 |
|---:|---|---|---|
| 1 | `concepts/00-ecosystem-overview.md` | OpenTUI 定位、源码与文档版本坐标、架构鸟瞰 | F-001–F-004、F-017–F-020 |
| 2 | `concepts/01-packages-and-entrypoints.md` | 七个 release packages 与主要入口边界 | F-003–F-008、F-010、F-035 |
| 3 | `concepts/02-core-renderer-and-renderables.md` | renderer、renderable tree、Core 导出与 Text/Box | F-009、F-012–F-016、F-034 |
| 4 | `concepts/03-layout-and-native-rendering.md` | Yoga、native Scene、cell painting 与输出阶段 | F-017–F-020 |
| 5 | `concepts/04-input-focus-and-keymap.md` | keyboard、mouse、focus 和 Keymap 边界 | F-025–F-027 |
| 6 | `concepts/05-lifecycle-and-resource-ownership.md` | renderer/root/service 的关闭责任与 release 边界 | F-015、F-022、F-031–F-033 |
| 7 | `concepts/06-react-binding.md` | React renderer root、JSX 与 cleanup | F-021–F-022、F-031 |
| 8 | `concepts/07-solid-binding.md` | Solid render、响应式更新与入口 | F-023–F-024 |
| 9 | `concepts/08-testing.md` | test renderer、mock input/mouse、frame capture、dispose | F-011、F-028–F-030 |
| 10 | `concepts/09-ecosystem-packages.md` | Keymap、QRCode、Three、SSH 的适用入口和检索路径 | F-003–F-008 |
| 11 | `examples/01-core-hello-terminal.md` | 最小 Core 程序与显式 renderer cleanup | F-012、F-015–F-016、F-034 |
| 12 | `examples/02-test-renderer-and-input.md` | 创建测试环境、帧断言与 finally 清理 | F-025–F-030 |
| 13 | `examples/03-react-entrypoint.md` | React root 挂载、JSX 前置配置与 renderer 清理 | F-015、F-021–F-022、F-031–F-032 |
| 14 | `examples/04-solid-entrypoint.md` | Solid render、已有 renderer 的所有权与销毁 | F-015、F-023–F-024、F-031–F-032 |
| 15 | `examples/05-native-rendering-boundaries.md` | 用 test renderer 观察 native-backed cell frame，并区分内存 sink 与终端 transport | F-017–F-020、F-028–F-030 |

### 生成批次建议

- **Batch A**：先登记 references；随后生成 concepts 00–04（5 个文件）。
- **Batch B**：生成 concepts 05–09（5 个文件）。
- **Batch C**：生成 examples 01–05（5 个文件），分别覆盖 Core、test renderer、React、Solid 与 native rendering 边界。
- **Batch D**：所有内容稳定后生成 concepts/examples/references 目录索引、bundle 根索引与 log，再更新父级导航。

每批不超过 7 个内容文件；导航索引集中在最后生成。

## G2 自检

- 所有洞察均包含陈述、事实证据、反常识点与文档组织行动。
- 学习地图按 Core → interactions/lifecycle/testing → framework bindings → native/生态包排列。
- 七个发布包的计数只使用 F-003 的 release-script 口径；不把 exports subpaths 当作独立 packages。
- 实施时如从事实台账发现新 API/范围，应先补 F 编号与来源，再生成教程正文。
