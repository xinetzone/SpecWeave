# SST 源码与官方文档事实清单

## 信源基线

- 源码仓库：`https://github.com/anomalyco/sst`
- 固定 tag：`v4.17.2`
- 固定 commit：`e49ac31411f63ab4ed0d802b7e15d95f6b827e47`
- 源码链接格式：`https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/<path>#L<line>`
- 官方文档采集日期：`2026-10-20`
- 官方文档链接均指向公开 `https://sst.dev/docs/` 页面。网页事实描述该采集日期可见的官网说明，不等同于固定源码版本的实现事实。
- 本清单不引用本地 checkout 路径或网页抽取临时文件路径。

## 源码事实

### CLI、项目与部署路径

- **F-001**：CLI 根命令声明名称为 `sst`，其描述包含 “The CLI helps you manage your SST apps.”。来源：[cmd/sst/main.go#L150-L160](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/main.go#L150-L160)。
- **F-002**：CLI 命令表中包含 `dev` 命令；该命令的长描述列出 multiplexer、frontend/process、linked resources、watcher 等本地开发行为。来源：[cmd/sst/main.go#L386-L469](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/main.go#L386-L469)。
- **F-003**：`project.Discover()` 获取当前工作目录，并向上查找 `sst.config.ts`；查找后创建解析得到的 `.sst` 工作目录。来源：[pkg/project/project.go#L115-L130](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L115-L130)。
- **F-004**：`project.App` 结构体包含 `Name`、`Stage`、`Removal` 等字段；`project.State` 结构体包含 `Purge`、`Compress`、`Retention` 等字段。来源：[pkg/project/project.go#L30-L55](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L30-L55)。
- **F-005**：`project.New(input *ProjectConfig)` 使用 `InvalidStageRegex` 检查输入 stage，并据 `input.Config` 设置项目根目录与 `.sst` 目录。来源：[pkg/project/project.go#L160-L203](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L160-L203)。
- **F-006**：`project.New` 创建 runtime collection，传入 Node、worker、Python、Go 和 Rust runtime 实例。来源：[pkg/project/project.go#L192-L210](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L192-L210)。
- **F-007**：`project.New` 调用 `js.Build` 构建配置入口；构建参数包含项目根目录及对配置函数 `$config` 的 banner 定义。来源：[pkg/project/project.go#L211-L244](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L211-L244)。
- **F-008**：`StackInput` 字段包含 `Command`、`Target`、`Exclude`、`ServerPort`、`Dev`、`Verbose`、`Continue`、`SkipHash` 和 `PolicyPath`。来源：[pkg/project/stack.go#L18-L30](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/stack.go#L18-L30)。
- **F-009**：`(*Project).Run(ctx, input)` 构建并运行 SST 平台程序；函数实现中存在对 `js.Build` 的调用。来源：[pkg/project/run.go#L35-L55](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/run.go#L35-L55)、[pkg/project/run.go#L150-L190](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/run.go#L150-L190)。
- **F-010**：`Project.Run` 将 `diff` 映射为 Pulumi `preview`，`refresh` 映射为 `refresh --yes --run-program`，`deploy` 映射为 `up --yes -f`，`remove` 映射为 `destroy --yes -f`。来源：[pkg/project/run.go#L329-L337](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/run.go#L329-L337)。
- **F-011**：`CmdDeploy` 以 `Command: "deploy"` 创建 `project.StackInput`，并传递 target、exclude、dev、server port、verbose、continue 和 policy 参数。来源：[cmd/sst/deploy.go#L175-L199](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/deploy.go#L175-L199)。

### Provider、服务端与 runtime

- **F-012**：`provider.Home` 接口声明 bootstrap、按 key/app/stage 读写/删除数据、passphrase、stage 列表及清理相关方法。来源：[pkg/project/provider/provider.go#L23-L40](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/provider/provider.go#L23-L40)。
- **F-013**：`provider.Provider` 接口声明 `Init(app, stage, args)` 与 `Env()` 方法。来源：[pkg/project/provider/provider.go#L43-L46](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/provider/provider.go#L43-L46)。
- **F-014**：源码包含 AWS 与 Cloudflare 的 project provider 实现文件。来源：[pkg/project/provider/aws.go](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/provider/aws.go)、[pkg/project/provider/cloudflare.go](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/provider/cloudflare.go)。
- **F-015**：`server.New()` 创建 JSON-RPC server，并将 `/rpc` 注册为 HTTP handler；handler 对非 POST 请求返回 Method Not Allowed。来源：[pkg/server/server.go#L31-L51](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/server/server.go#L31-L51)。
- **F-016**：`Server.Start()` 注册 `resource`、`aws`、`runtime` RPC 服务。来源：[pkg/server/server.go#L54-L62](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/server/server.go#L54-L62)。
- **F-017**：`runtime.Runtime` 接口及 `BuildInput`、`RunInput` 类型定义在 `pkg/runtime/runtime.go`；`Collection.Runtime` 按 runtime 的 `Match` 结果查找实现。来源：[pkg/runtime/runtime.go#L18-L108](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/runtime/runtime.go#L18-L108)。
- **F-018**：`Collection.Build()` 按 `BuildInput.Runtime` 选择 runtime 并调用其 `Build()`。来源：[pkg/runtime/runtime.go#L113-L157](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/runtime/runtime.go#L113-L157)。
- **F-019**：`Collection.Run()` 在调用匹配 runtime 的 `Run()` 前，将 `SST_LIVE=true` 与 `SST_DEV=true` 追加到环境变量。来源：[pkg/runtime/runtime.go#L220-L229](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/runtime/runtime.go#L220-L229)。
- **F-020**：`pkg/bus` 提供 `Subscribe`、`SubscribeAll`、`Publish` 等函数。来源：[pkg/bus/bus.go#L21-L67](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/bus/bus.go#L21-L67)。

### Platform、组件、Link 与 SDK

- **F-021**：`platform/src/components/index.ts` 导出 `aws`、`cloudflare`、`vercel` 命名空间及其他组件导出。来源：[platform/src/components/index.ts#L1-L4](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/index.ts#L1-L4)。
- **F-022**：`platform/src/auto/run.ts` 导出 `run(program: automation.PulumiFn)`，并在该模块注册 stack transformations。来源：[platform/src/auto/run.ts#L12-L28](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/auto/run.ts#L12-L28)。
- **F-023**：`Link.Linkable` 接口声明 `urn` 与 `getSSTLink()`；`Link.isLinkable()` 通过对象是否包含 `getSSTLink` 属性判断。来源：[platform/src/components/link.ts#L97-L105](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/link.ts#L97-L105)。
- **F-024**：Link 构建逻辑读取 linkable 对象的 `getSSTLink()`，并将其 properties 与 URN 末段名称组合为链接数据。来源：[platform/src/components/link.ts#L112-L129](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/link.ts#L112-L129)。
- **F-025**：`Link.propertiesToEnv()` 将每项属性序列化为 `SST_RESOURCE_<key>` 环境变量，并增加含 app name 与 stage 的 `SST_RESOURCE_App`。来源：[platform/src/components/link.ts#L159-L174](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/link.ts#L159-L174)。
- **F-026**：`Linkable` 类实现 `getSSTLink()`，并提供静态 `wrap()` 与 `env()` 方法；`wrap()` 将 `getSSTLink` 写到所包装资源类的 prototype。来源：[platform/src/components/linkable.ts#L182-L208](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/linkable.ts#L182-L208)、[platform/src/components/linkable.ts#L215-L235](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/linkable.ts#L215-L235)、[platform/src/components/linkable.ts#L276-L315](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/linkable.ts#L276-L315)。
- **F-027**：AWS `Function` 类实现 `Link.Linkable`；相关实现构造 `SST_RESOURCE_App` 并读取已链接资源的 `getSSTLink()`。来源：[platform/src/components/aws/function.ts#L1713-L1748](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/aws/function.ts#L1713-L1748)、[platform/src/components/aws/function.ts#L1898-L1915](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/aws/function.ts#L1898-L1915)。
- **F-028**：JS SDK 的 `loadResourceEnvironment()` 读取以 `SST_RESOURCE_` 开头的字符串环境变量，并解析 JSON 值。来源：[sdk/js/src/resource/shared.ts#L21-L36](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/sdk/js/src/resource/shared.ts#L21-L36)。
- **F-029**：JS SDK 的 `createResource()` 返回 Proxy；若读取未链接属性且缺少 `SST_RESOURCE_App` 与 `raw.App`，实现抛出提示 SST links 未激活的错误。来源：[sdk/js/src/resource/shared.ts#L40-L76](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/sdk/js/src/resource/shared.ts#L40-L76)。

### Mosaic 与 Live

- **F-030**：Mosaic dev 服务注册 `/stream`、`/api/deploy`、`/api/env` 与 `/api/completed` handler。来源：[cmd/sst/mosaic/dev/dev.go#L44-L126](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/dev/dev.go#L44-L126)。
- **F-031**：`/stream` handler 设置 NDJSON content type、订阅事件总线并逐项编码事件消息写入 HTTP response。来源：[cmd/sst/mosaic/dev/dev.go#L44-L78](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/dev/dev.go#L44-L78)。
- **F-032**：`/api/deploy` handler 发布 `DeployRequestedEvent`。来源：[cmd/sst/mosaic/dev/dev.go#L80-L81](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/dev/dev.go#L80-L81)。
- **F-033**：Mosaic deployer 订阅文件变更、部署请求与构建成功事件；处理部署时调用 `Project.Run()`，传入 `Command: "deploy"` 与 `Dev: true`。来源：[cmd/sst/mosaic/deployer/deployer.go#L21-L50](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/deployer/deployer.go#L21-L50)。
- **F-034**：Mosaic AWS 启动代码调用 provider 的 `ResolveAppSync()`；AppSync 实现包含 WebSocket connection 的 `Subscribe()` 与 `Publish()` 方法。来源：[cmd/sst/mosaic/aws/aws.go#L20-L39](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/aws/aws.go#L20-L39)、[cmd/sst/mosaic/aws/appsync/appsync.go#L105-L170](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/aws/appsync/appsync.go#L105-L170)、[cmd/sst/mosaic/aws/appsync/appsync.go#L254-L360](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/aws/appsync/appsync.go#L254-L360)。

## 官方文档事实

以下条目是 2026-10-20 查阅页面所陈述的内容。其版本口径为官网当日可见说明，不能仅凭这些陈述推断 v4.17.2 源码行为。

- **W-001**：Basics 页面称 SST 应用通过根目录 `sst.config.ts` 以代码配置，并介绍组件、资源链接、项目结构及 `sst dev`、`sst deploy` 等工作流。来源：[SST Basics](https://sst.dev/docs/)，采集日期：2026-10-20。
- **W-002**：CLI reference 的 `stage` 章节称 stage 用于为应用资源添加前缀，以便同一账户中运行多个环境；未显式传入 stage 时，CLI 使用本机用户名，并将生成的 personal stage 写入 `.sst/stage` 供后续读取。来源：[CLI reference: stage](https://sst.dev/docs/reference/cli/#stage)，采集日期：2026-10-20。
- **W-003**：State 页面称 SST 在本地生成 JSON state file，并将状态备份到应用 home provider 的 bucket；页面另说明 passphrase 存储于 SSM parameter。来源：[State](https://sst.dev/docs/state/)，采集日期：2026-10-20。
- **W-004**：Components 页面将组件分为 SST built-in components 与 provider components，并说明高层组件可由较低层 provider resources 组合。来源：[Components](https://sst.dev/docs/components/)，采集日期：2026-10-20。
- **W-005**：Components 页面称内置组件命名空间包括 `sst.aws.*` 与 `sst.cloudflare.*`，并分别说明其内部使用 Pulumi AWS 与 Cloudflare provider。来源：[Components](https://sst.dev/docs/components/)，采集日期：2026-10-20。
- **W-006**：Providers 页面称 SST 基于 Pulumi/Terraform，并在 2026-10-20 的页面中宣称支持 150+ providers；页面也说明可用 `sst add <provider>` 添加 provider。来源：[Providers](https://sst.dev/docs/providers/)、[Provider directory](https://sst.dev/docs/all-providers#directory)，采集日期：2026-10-20。
- **W-007**：Providers 页面说明 provider 版本由 `sst.config.ts` 中的配置固定，并介绍 provider credentials 的配置方式。来源：[Providers](https://sst.dev/docs/providers/)，采集日期：2026-10-20。
- **W-008**：Linking 页面将资源链接描述为把基础设施信息传入 runtime code 的方式，并按创建资源、通过 `link` 属性关联、在 runtime 使用 SDK 访问的顺序说明。来源：[Resource Linking](https://sst.dev/docs/linking/)，采集日期：2026-10-20。
- **W-009**：Linking 页面说明通过 `sst dev` 可将链接资源加载到本地开发环境，并介绍 `sst.Linkable`、`Linkable.wrap` 与 `Linkable.env()`。来源：[Resource Linking](https://sst.dev/docs/linking/)，采集日期：2026-10-20。
- **W-010**：CLI reference 页面说明 `sst dev` 默认启动 multiplexer，协调应用部署、本地函数和前端进程，加载 linked resources 并监视配置变更；页面列出 `multi`（默认）、`basic` 与 `mono` 模式。来源：[CLI reference: dev](https://sst.dev/docs/reference/cli/#dev)，采集日期：2026-10-20。
- **W-011**：CLI reference 页面列出 `sst deploy --stage <name>`、`sst diff`、`sst remove --stage <name>` 等命令示例，并说明 deploy 可指定 target 或 exclude component。来源：[CLI reference](https://sst.dev/docs/reference/cli/)，采集日期：2026-10-20。
- **W-012**：SDK 页面列出的应用对象包括 functions、frontends 与 container applications；页面分别给出 JavaScript/TypeScript、Python、Go 和 Rust 的资源访问说明。来源：[SDK reference](https://sst.dev/docs/reference/sdk/)，采集日期：2026-10-20。
- **W-013**：Live 页面称 Live 通过 AWS AppSync Events 在本地机器和远端 Lambda function 之间通信，并说明 `sst dev` 会创建相应 AppSync Events API、部署 stub function。来源：[Live](https://sst.dev/docs/live/)，采集日期：2026-10-20。
- **W-014**：Console 页面将 Console 描述为管理 SST apps 的网页 dashboard，并列出资源、更新、日志、告警与 git push 部署等功能。来源：[Console](https://sst.dev/docs/console/)，采集日期：2026-10-20。
- **W-015**：Basics 页面称 SST 可采用 monorepo 结构，示例将 `sst.config.ts` 保留在根目录并将配置拆分到 `infra/`；CLI reference 另说明 `--config` 可用于在含多个 SST app 的 monorepo 中选定配置文件。来源：[SST Basics: Monorepo](https://sst.dev/docs/#monorepo)、[CLI reference: config](https://sst.dev/docs/reference/cli/#config)，采集日期：2026-10-20。

## G1 自检

- 源码事实仅描述指定 commit 中可定位的符号、字段、调用或命令映射；未把架构解释、因果关系或设计意图混入 R 阶段。
- 官网事实以 `W-` 编号独立登记，并注明页面与采集日期；未将官网当前说明归并为 v4.17.2 的源码事实。
- 本清单未登记未经脚本计数的源码数量断言。
