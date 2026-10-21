---
type: spec
source: "spec.md"
source_commit: "6ec56821d63100fe5bda45b759364f561c56b359"
---

# 本轮事实采集草稿

以下路径相对固定源码仓库根。行范围是静态源码证据；测试仅阅读，未运行。
正式知识文件在 E 阶段信源登记后生成，本文件保留 R 阶段证据，不作为对外教程入口。

## Task 2：配置、上下文、codemode

| 编号 | 客观事实 | 路径与行范围 |
|---|---|---|
| F-115 | Config.latest(entries, key) 找到最后一个该字段非 undefined 的 document，返回其字段值 info[key]；entries 返回 managed policies、wellknown、global supplementary、explicit、direct、project supplementary、content、managed settings 的有序序列。 | `packages/core/src/config.ts:24-29,254-290` |
| F-116 | ConfigDiscovery 分离 system/global/explicit/direct/project/claude/agents 来源；project walk 排除已解析的 global roots/files，direct 与 project 列表反转后返回。 | `packages/core/src/config/discovery.ts:67-145` |
| F-117 | ConfigInstructionPlugin 依次组合 global/project/configured 指令；配置 HTTP URL 获取 timeout 为 5 秒，失败保留旧副本，否则跳过 URL；空来源数组仍可产生 available；editor.unavailable 对应不可用状态或激活失败。 | `packages/core/src/config/plugin/instruction.ts:78-230` |
| F-118 | ConfigSkillPlugin 从 directory entry 的 skill/skills 子目录及 document skills 字段构造来源；重复技能 ID 由后读来源覆盖，watcher 100ms debounce 后 rescan/reload。 | `packages/core/src/config/plugin/skill.ts:85-116,147-193` |
| F-119 | SkillScan 在遇到 SKILL.md 的目录停止向下扫描；无 SKILL.md 的根还采集普通 .md；最大递归 depth=6。SkillFile.parse 从文件/父目录派生 ID，metadata opencode/autoinvoke 优先于 disable-model-invocation。 | `packages/core/src/config/plugin/skill-scan.ts:7-46`；`packages/core/src/config/plugin/skill-file.ts:39-63` |
| F-120 | SessionInstructions 的 inFlight Set 防同 Session/path 并发重复，持久去重来自模型可见 synthetic metadata.instruction.paths；发布后 ensuring 释放 claim。 | `packages/core/src/session/instructions.ts:35-109` |
| F-121 | SessionCompaction 默认 auto=true、keep=15000；非 manual 且 auto=false 返回 skipped（含 overflow）；ConfigCompactionPlugin 逐 document 消费 auto/buffer/keep.tokens。 | `packages/core/src/session/compaction.ts:203-239`；`packages/core/src/config/plugin/compaction.ts:10-26` |
| F-122 | compaction 分 summary/native；native request 需要 provenance 且经路由后 compatible；calculateCeiling 显式 buffer 直接扣除，否则按窗口保留15%，足够大时至少16000。 | `packages/core/src/session/compaction.ts:340-373,941-947` |
| F-123 | CodeMode.execute(options) 委托 make(options).execute(code)；executeProgram 使用 Acorn script parse，允许顶层 await/return，并通过 Interpreter.run 执行。 | `packages/codemode/src/codemode.ts:139-163`；`packages/codemode/src/interpreter/execute.ts:36-43,109-116` |
| F-124 | reusable runtime 复用 prepared tools/catalog；每次 executeProgram 的 Effect.suspend 新建 builtins、ToolRuntime 调用记录、logs、Pending 与 Interpreter。 | `packages/codemode/src/codemode.ts:145-163`；`packages/codemode/src/interpreter/execute.ts:27-44` |
| F-125 | ToolRuntime 将零参数归一为 {}、拒绝多个参数；Effect schema 解码输入，普通 JSON Schema 直接传值；没有 output schema 时返回 undefined。 | `packages/codemode/src/tool-runtime.ts:399-440`；`packages/codemode/src/tool-schema.ts:295-303` |
| F-126 | timeoutMs/maxToolCalls/maxOutputBytes 可选且无默认；值检查安全整数及各自下限。调用计数在输入解码后、before hook 前。 | `packages/codemode/src/codemode.ts:21-35,126-137`；`packages/codemode/src/tool-runtime.ts:392-417` |
| F-127 | 正常返回在 plain-data copy-out 后中断 pending；timeout 在 copy-out 前返回失败，在 copy-out 后未结束后台工作时可返回成功及 warning。 | `packages/codemode/src/interpreter/execute.ts:33-88` |
| F-128 | maxOutputBytes 在结果产生后裁剪 value/logs；warnings 有独立等额预算，toolCalls、error 与截断提示不受统一响应字节预算限制。 | `packages/codemode/src/interpreter/execute.ts:102-104,119-192` |
| F-129 | Core Tool.snapshot 将 codemode===false 的工具留在 direct，其余进入 CodeMode inventory；execute 子调用仍通过 beforeExecute 和 executeTool。 | `packages/core/src/tool.ts:227-281` |
| F-130 | Core CodeModeTool 以 WeakMap<Inventory, Runtime<Run>> 缓存 runtime，Run 服务逐调用注入；CodeMode.make 只传 tools/extensions/hooks，未传 limits；typed output 优先，否则 text/null。 | `packages/core/src/codemode/tool.ts:56-63,89-124,233-263` |

### 对照及边界

- 配置压缩测试完整读：`packages/core/test/config/compaction.test.ts`；mock LLM，测试 settings reload/manual，不代表真实 provider 验证。
- 技能测试片段读：`packages/core/test/config/skill.test.ts:1-120`，实际调用 ConfigCompatibilityPlugin 与 ConfigSkillPlugin；兼容性插件本轮未深读。
- codemode 测试片段读：`packages/codemode/test/codemode.test.ts:566-618`，明确 JSON Schema render-only 和出入 JSON 语义；其余测试由只读研究定位。
- Core 配置/skill/instruction/compaction 主实现与 discovery/scan/file 正文已读；config normalize/variable、全部 instruction tests、provider 压缩实现未穷尽。
- 解释器仅 execute 正文及关键工具路径；其余语法/stdlib、web extension 未完整读。没有运行源码测试，不提出进程级安全隔离保证。

## Task 3：扩展契约与产品状态

| 编号 | 客观事实 | 路径与行范围 |
|---|---|---|
| F-131 | Plugin.Info 的 source/features/state 为公开 Schema；state 为 active/failed；plugin.updated 是 data={} 的 ephemeral event。 | `packages/schema/src/plugin.ts:10-49` |
| F-132 | Event.latest 按 durable version 选择最新定义，歧义重复抛错；durableMap 只收 durable，以 type.version 为键，重复抛错。 | `packages/schema/src/event.ts:151-188` |
| F-133 | Effect Plugin 接口为 effect(context): Effect<void,never,R>，默认 R=Scope；Promise Plugin 为 setup(context): Promise<Cleanup|void>|Cleanup|void；adapter.acquireRelease 在释放时调用 Cleanup。 | `packages/plugin/src/effect/plugin.ts:57-64`；`packages/plugin/src/promise/plugin.ts:55-66`；`packages/plugin/src/promise/adapter.ts:619-622` |
| F-134 | PluginModule 在模块读取/npm 解析前执行 integration.use managed policy；default 导出必须有 string id 和 effect/setup function；install=false 的非本地缺入口返回 pending。 | `packages/core/src/plugin/module.ts:44-61,78-151` |
| F-135 | Plugin.activate 保留 id/revision 相同前缀，逆序关闭变化后缀并顺序加载；相同失败 revision 不因重排重试，新 revision 可重试，健康 fallback 可重新加载。Hook 按注册顺序遍历，Scope finalizer/dispose 移除注册。 | `packages/core/src/plugin.ts:90-180`；`packages/core/src/plugin/hooks.ts:69-95` |
| F-136 | TUI createStorage 的 update 在 Flock 内重读、mutation、writeJsonAtomic，再 setStore；writeJsonAtomic 临时文件+rename，失败清理临时文件并抛错。 | `packages/tui/src/context/storage.tsx:47-93`；`packages/tui/src/util/persistence.ts:22-33` |
| F-137 | TUI watcher 合并50ms事件后重读；读/解析失败回退 initial，watch 失败禁用 live reload；flush 等待 pending/allSettled，close 仅关 watcher/timer，不自动 flush。 | `packages/tui/src/context/storage.tsx:61-67,102-149` |
| F-138 | App settings 的 settings.v3 通过 persisted 分流 storage；persistStore 默认100ms延迟，异步 hydration 在未 touched 时应用，dirty 时暂存 remote，storage.setItem 没有 await。 | `packages/app/src/settings/model.tsx:306-310,345-347`；`packages/app/src/runtime/persistence/storage.ts:586-768`；`packages/app/src/runtime/persistence/persist.ts:5-115` |
| F-139 | Desktop createDesktopStorage 复用 App createNamespaceStorage，driver 接入 storeItems/update/clear；namespace 即时改 cache，以本地 sequence 与 host revision 排除旧 ACK/event，失败仅重新排队未被新值替代的 key。 | `packages/desktop/src/renderer/platform/storage.ts:11-38`；`packages/app/src/runtime/persistence/namespace.ts:57-170` |
| F-140 | StorageUpdate RPC payload 含 name/insert/remove，success 为 Number；handler 先 state.update 排队，广播其他窗口并返回 revision；state writer 延迟250ms执行 SQLite transaction，失败保留可重试记录。 | `packages/desktop/src/shared/ipc-rpc/storage.ts:10-17`；`packages/desktop/src/main/ipc-handlers/storage.ts:17-30`；`packages/desktop/src/main/storage/state.ts:12-93`；`packages/desktop/src/main/storage/write-behind.ts:3-48` |

### 对照及边界

- Schema event 测试正文已读；Core plugin 测试、module policy 测试由子代理片段核对。主代理回读 schema/plugin/event、Plugin 接口、Core module/hooks 及 activation 关键正文。
- TUI storage/persistence、App persist/namespace、Desktop storage handler/state/write-behind 正文主代理回读；state 测试27-108和 persist 测试39-90对照。
- 子代理完整读取 App storage/schema 与 Desktop preload、IPC transport/client/main 接线；主代理独立核对其关键 storage 路径。
- 未穷尽 App global-sync、TUI session sync、其他 Desktop handlers/draft/migrations。仅有持久化代表性状态链，不宣称全部 UI 状态流已审计；没有真实 Electron E2E。

## Task 4：回放、云端与更新

| 编号 | 客观事实 | 路径与行范围 |
|---|---|---|
| F-141 | simulationReplacements 替换 HTTP layer；未设 OPENCODE_DRIVE 时仅安装模拟网络，设置后解析 Drive manifest 并安装 SimulatedProvider/OpenAI route；安装失败 Layer.orDie 中止启动。 | `packages/simulation/src/backend/index.ts:24-57` |
| F-142 | SimulatedProvider.layerDrive 给每个 invocation 建容量256的 responses queue；stream acquireRelease 在释放时关闭 queue 并清除 pending；llm.attach 替换旧订阅，chunk/finish/disconnect 分别入队、结束或失败。 | `packages/simulation/src/backend/simulated-provider.ts:154-295,314-355` |
| F-143 | Timeline.create 写 version=1/base64 header；output/resize 写 JSONL，pointer 写 sidecar，共用 performance.now 单调时钟；finish 等待自身及子流完成并传播流失败。 | `packages/simulation/src/recording.ts:65-162` |
| F-144 | recordingLayer 的 record 路径捕获真实响应、脱敏存储副本，经 Deferred 按请求开始顺序 append；实际调用返回未脱敏响应快照。replay 对脱敏请求从未领取 interaction 中匹配并 claim。 | `packages/http-recorder/src/http/recorder.ts:72-149` |
| F-145 | resolveAutoMode 在 CI 非空且不为 false/0 时返回 replay，否则按 cassette.exists 选择 replay/record；makeReplayPoolState 缓存读取并通过 SynchronizedRef 原子领取。成功 scope 检查未用记录，failure、尝试但零领取及 missing cassette 有例外。 | `packages/http-recorder/src/replay/state.ts:5-79` |
| F-146 | cassette store 默认目录是 cwd/test/fixtures/recordings；路径拒绝绝对路径和 ..；append 在 semaphore 内检查 possible secrets、写临时文件后 rename。multi-step 夹具含 step=1/2 请求与 first/second 响应；HTTP 测试定义乱序、并发 claim、未用记录、CI missing 及 live/redacted 区分。 | `packages/http-recorder/src/cassette/store.ts:7-159`；`packages/http-recorder/test/fixtures/recordings/http/multi-step.json:1-41`；`packages/http-recorder/test/http.test.ts:22-149,180-193,253-277` |
| F-147 | Console Zen responses POST 直接调用 proxyInference；代理按路径映射及 key 归一转发 Resource.INFERENCE.fetch；fetch 异常返回503/no-store，上游404转换400。 | `packages/console/app/src/routes/zen/v1/responses.ts:1-6`；`packages/console/app/src/lib/inference-proxy.ts:3-60` |
| F-148 | Stats daemon 以1小时节奏运行；UTC日首次 full，full 失败再 incremental，仍记录当天 full 已尝试；重启 initialDelay 依据 lastSyncedAt。 | `packages/stats/server/src/stat-sync.ts:8-60` |
| F-149 | files Worker 只接受 /files/ 的 GET/HEAD/OPTIONS；缓存可直接返回，未返回时 head 后处理条件请求及单段 Range；get 用 etagMatches，head/get 间对象变化返回503/no-store；完整且可缓存且不大于512MiB时异步入 cache。 | `services/files/src/index.ts:1-163` |
| F-150 | Desktop updater main 仅 packaged 且非 dev 启用平台；machine 分 check/stage/install/restart，以 Deferred 合并并发，已有 downloaded 时传 differential:false；平台 disableDifferentialDownload 设置仅对 Windows 生效，macOS另有分支；platform autoDownload=false，restart handoff 10秒未开始报错。 | `packages/gui-extensions/src/updater/main.ts:9-50`；`packages/gui-extensions/src/updater/machine.ts:44-85,150-260`；`packages/gui-extensions/src/updater/platform.ts:8-24,60-73,99-133` |
| F-151 | TUI UpdateSource 接口分 subscribe/check/apply；install 在 available 时 apply，resolve 后 installed，reject 后 failed；restart 在 installed 时调用 exit；通知持久化历史与主动检查状态分开。 | `packages/tui/src/context/update-notification.tsx:18-140` |

### 对照及边界

- HTTP recorder 主实现、replay state、cassette store、HTTP 测试和 support、固定 multi-step JSON 夹具完整读；redaction/matching 内部及 WebSocket recorder 本轮未穷尽。测试定义不代表运行结果。
- simulation backend/provider/Timeline 正文主代理读取；simulation provider 测试与 WebSocket fixture 由只读代理核对。未穷尽 Drive controller、network route 和 UI 自动化实现。
- Console proxy 与 responses 调用方、Stats daemon、files Worker 正文已读；新 inference 鉴权/计费、Stats core 查询/写库、其他 services 未读，不描述线上可用性。
- GUI updater AGENTS/main/machine/platform 正文已读；machine.test.ts:1-200 片段对照缓存再确认、离线保留 staged、并发 install；TUI notification 正文读，底层安装实现未读。未运行真实更新、付费模型、源码测试或云部署。

## 六主题覆盖矩阵

| 主题 | 代表性实现链 | 对照 | 未读范围 |
|---|---|---|---|
| 配置与上下文 | discovery → ordered entries → instruction/skill/compaction plugin → Session | config compaction 测试正文；skill/codemode 测试片段 | normalize/variable、全部指令测试、Provider 压缩 |
| Codemode | Core inventory/Run → cached runtime → Acorn/Interpreter → ToolRuntime hooks | Core codemode 测试；JSON Schema render-only 片段 | 全部语法/stdlib/web extension、进程隔离证明 |
| Schema/Plugin | public Info/Event → module policy → activate prefix/suffix → Scope cleanup | Event 测试；module/plugin 测试由代理片段核对 | 其他领域契约与完整插件生态 |
| 产品状态 | TUI lock/atomic write；App deferred persist；Desktop RPC/revision/write-behind | App persist/Desktop state 测试片段 | session/global-sync、draft、全部迁移、Electron E2E |
| 验证与回放 | simulation HTTP replacement/Drive stream；recorder snapshot → redact → cassette → pool | HTTP 测试/JSON fixture；simulation provider 测试由代理核对 | 全部 recorder transports、Drive UI/controller |
| 云端与更新 | Zen proxy → INFERENCE；Stats daemon；files head/get；GUI updater machine；TUI apply | responses 调用方；updater machine 测试片段 | inference 鉴权计费、Stats core、其他 services、真实部署更新 |

## R 证据修订记录

2026-10-21 机械 EOF 检查修正 F-116/F-118/F-119/F-121 共五处过长行范围；F-119 补全文件路径。续接 Task 4 后再次检查，修正 F-146/F-149/F-150 三处范围。未改变对应机制结论。最终 V 仍须验证每条坐标与正文一致。

2026-10-21 Task8只读内容核验后，修正F-115字段值、F-117远程失败语义及F-150平台分支；F-149明确缓存先返回。正式表补齐F-115/F-122/F-124/F-130/F-137/F-146/F-150的可点击证据；F-146 live/redacted测试坐标修为253-277，285-309仅属204/二进制测试。保留本记录，不改旧轮历史。
