# SST 架构洞察与知识地图

> 阶段：I（Insight）  
> 输入：`facts.md` 中 F-001–F-034、W-001–W-015  
> 工作流：源码事实固定于 SST v4.17.2 / `e49ac31411f63ab4ed0d802b7e15d95f6b827e47`；官网说明采集于 2026-10-20，单独标注。

## 核心洞察

### I-001：SST 的运行主线跨越 Go 编排层与 TypeScript/Pulumi 程序层

- **陈述**：Go CLI 负责发现项目、准备运行输入并映射部署命令；项目配置构建与 SST 平台程序执行则经过 JavaScript 构建入口和 Pulumi Automation 接口。
- **证据**：F-003、F-007、F-009、F-010、F-011、F-022。
- **反常识**：从终端只看到一个 `sst` 命令，容易把 SST 理解成单一语言实现，或误以为 Go CLI 直接定义并创建所有云资源。固定快照显示的是跨语言控制路径，资源组件与 CLI 编排处于不同层。
- **行动**：概念篇先给出“CLI → project → 配置构建 / platform.run → Pulumi 命令”的路径，再解释组件；所有箭头只表达事实清单能支持的调用或映射关系，不扩写为源码未证明的生命周期保证。

### I-002：Link 的核心边界是序列化后的环境变量，而不是跨运行时传递对象引用

- **陈述**：Linkable 资源公开 link 数据，平台侧把属性转为 `SST_RESOURCE_*` 环境变量，JavaScript SDK 再解析这些变量并通过 Proxy 暴露资源对象。
- **证据**：F-023–F-029；官网使用顺序由 W-008、W-009 佐证。
- **反常识**：应用代码最终可以像读取 SDK 资源属性一样消费链接结果，但源码中的跨边界载体是环境变量及 JSON 值，而不是把 Pulumi 资源对象直接注入应用进程。
- **行动**：单独绘制并讲解“资源 → `getSSTLink()` → `SST_RESOURCE_*` → SDK 解析 / Proxy”的数据链；示例分别标明官网配置写法与源码可证的传递机制。

### I-003：`sst dev` 同时包含本地进程编排和部署 / 事件通道，不能等同于无云依赖的纯本地模拟

- **陈述**：固定快照中的 runtime 会注入 `SST_LIVE`、`SST_DEV` 标记；Mosaic 提供本地 HTTP 事件端点与 deployer，后者在 dev 模式调用项目部署路径；Mosaic AWS 实现还包含 AppSync WebSocket 通信。
- **证据**：F-002、F-019、F-030–F-034；官网对 `sst dev` 与 Live 的描述见 W-010、W-013。
- **反常识**：命令名中的“dev”或页面中的“本地开发”并不证明所有工作都离线发生。官网将 Live 描述为本地机器与远端 Lambda 间通信，而该描述的细节不得自动回填为 v4.17.2 的源码事实。
- **行动**：教程拆分“本地 CLI / multiplexer / 事件处理”与“需要云端配置或远端资源的 Live 能力”；示例显式标明本轮未执行真实云部署，不把静态源码阅读称作端到端实测。

### I-004：项目 provider、Pulumi provider 与 SST 高层组件属于不同抽象层

- **陈述**：`pkg/project/provider` 定义项目初始化与 home/state 访问相关接口；平台组件导出 AWS、Cloudflare、Vercel 等命名空间；官网再把 SST built-in components 与 provider components 分层说明。
- **证据**：F-012–F-016、F-021–F-022；组件/provider 的产品级区分见 W-004–W-007。
- **反常识**：代码中同名的“provider”并非同一接口或职责。项目启动与状态后端接口不能直接当作 Pulumi 资源 provider；平台导出的组件命名空间也不能据此推断仓库内所有上游 provider/API 的数量。
- **行动**：在组件篇用对照表分别描述 project provider、Pulumi/provider components、SST built-in components；“150+ providers”只作为采集日官网宣称引用，不当作 v4.17.2 源码计数。

### I-005：应用、stage 与 state 的教学表述必须保留源码事实与官网现行说明的版本边界

- **陈述**：源码可证 `App` 结构包含 `Name`、`Stage`、`Removal`，并存在 stage 校验及 `.sst` 目录设置；本次查阅的官网另说明 personal stage 规则、本地 JSON state 与远端备份等行为。
- **证据**：F-004、F-005；官网依据 W-002、W-003。
- **反常识**：源码结构字段与官网操作说明看起来可以拼成同一个版本的完整事实，但两者证据时间和版本口径不同；现有固定快照事实不能单独证明官网描述的 state 文件格式、备份位置或 passphrase 存储行为。
- **行动**：配置 / stage / state 篇并列标注“v4.17.2 源码可证”与“官网 2026-10-20 说明”；对未在固定快照事实中核验的行为使用来源限定语，不写成 v4.17.2 保证。

## 知识地图

### 学习顺序

1. **产品与应用模型**：先理解官网所称 SST 应用、配置入口、组件、link 与命令工作流，再明确本教程采用的源码版本边界。
2. **配置、stage 与 state**：区分源码中的 App / Stage 字段和官网说明的 CLI stage/state 使用行为。
3. **CLI 到项目生命周期**：沿 `Discover`、`Project.New`、`Project.Run` 与 Pulumi 命令映射理解执行主线。
4. **组件与 provider 边界**：区分项目 provider 接口、平台组件命名空间和官网描述的 provider 扩展方式。
5. **服务端、运行时与平台连接点**：解释 RPC 注册、runtime dispatch、配置构建和平台程序入口。
6. **资源链接**：从 Linkable 机制追踪环境变量序列化与 SDK Proxy。
7. **Live / Mosaic 开发机制**：最后讨论事件流、部署触发与 AppSync 路径，并明确官网产品描述与固定提交源码的证据边界。

### 拟建文档与证据映射

| 文档 | 定位 | 主要事实 |
|---|---|---|
| `concepts/00-application-model.md` | 入门：产品边界、应用配置入口与教程版本口径 | F-001、F-003；W-001、W-004 |
| `concepts/01-config-stage-state.md` | 入门：配置发现、App / Stage 字段、官网 stage/state 说明 | F-003–F-005；W-002、W-003、W-015 |
| `concepts/02-cli-project-lifecycle.md` | 核心：CLI、项目构建、stack 输入及 Pulumi 命令映射 | F-002、F-007–F-011；W-010、W-011 |
| `concepts/03-components-and-providers.md` | 核心：组件命名空间及不同 provider 抽象边界 | F-012–F-014、F-021；W-004–W-007 |
| `concepts/04-runtime-server-architecture.md` | 核心：RPC 服务、runtime dispatch 与平台程序入口 | F-015–F-022 |
| `concepts/05-resource-linking.md` | 核心：Linkable、环境变量与 JS SDK Proxy | F-023–F-029；W-008、W-009、W-012 |
| `concepts/06-live-mosaic-development.md` | 高级：Mosaic HTTP/event/deployer 与 Live 边界 | F-019–F-020、F-030–F-034；W-002、W-010、W-013 |
| `examples/01-minimal-component-app.md` | 示例：官方快速开始及最小应用/组件路径 | W-001、W-004、W-005；引用源码处仅使用已核实符号 |
| `examples/02-link-resources-to-runtime.md` | 示例：资源 Link 到运行时代码的配置与数据流 | F-023–F-029；W-008、W-009、W-012 |
| `examples/03-local-development-and-deployment.md` | 示例：`sst dev`、差异查看、部署与 stage 命令路径 | F-002、F-008–F-011、F-030–F-033；W-002、W-010、W-011、W-013 |

## G2 自检

- [x] 洞察共 5 条，每条包含陈述、证据、反常识、行动四项。
- [x] 每条洞察均引用 `facts.md` 中的编号事实；官网材料使用 W 编号并保留日期口径。
- [x] 五条洞察分别覆盖跨语言执行路径、Link 数据边界、dev/Live 运行边界、provider 抽象分层、版本/证据边界。
- [x] 学习路径从产品模型推进到 CLI、组件、运行时与高级开发机制。
- [x] 未将官网当前说明静默合并为 v4.17.2 源码行为；未把代表性覆盖扩写为穷尽性结论。
