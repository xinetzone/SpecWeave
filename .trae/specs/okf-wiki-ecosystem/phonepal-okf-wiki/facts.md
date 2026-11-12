# PhonePal（xiaoman）- R 阶段事实采集

> 采集时间：2026-11-12
> 信源：`external/dev/libs/others/xiaoman`，git 仓库 `git@github.com:aduoge/xiaoman.git`，HEAD = `580fdf750f946a6e411c3f54a86443c66aa46652`（2026-11-01，提交信息「文档中文化并整理 core-agent 代码结构」），仓库无 tag，工作树干净。
> 采集方式：逐文件通读 main 源码 + 脚本计数（`.temp/xiaoman-count/count_facts.py`），下文路径均相对仓库根，行号为该 commit 的 1-based 行号。
> 事实数量：82 条（F-001 ~ F-082）。事实只描述「代码里有什么」，因果与设计意图统一留给 I 阶段。

## 1. 仓库与构建

F-001: `settings.gradle.kts` 的 `include` 列出 8 个 Gradle 模块：`:core-api`、`:core-llm`、`:core-memory`、`:core-skills`、`:core-sentinel`、`:core-agent`、`:hands`、`:app`。
  - 源码：settings.gradle.kts:19-28

F-002: main 源集共 59 个 Kotlin 文件、6541 行；按模块计：core-api 6、core-llm 2、core-memory 5、core-skills 4、core-sentinel 2、core-agent 11、hands 7、app 22。
  - 源码：脚本 `count_facts.py` 对 `*/src/main/**/*.kt` 计数

F-003: `app/build.gradle.kts` 设置 `compileSdk = 35`、`minSdk = 30`、`targetSdk = 35`、`versionCode = 1`、`versionName = "0.1.0"`，Java/Kotlin toolchain 为 17。
  - 源码：app/build.gradle.kts:37-44,68

F-004: `BundleSkillsTask`（任务名 `bundleSkillAssets`）把根目录 `skills/examples/` 同步到 APK 资产目录 `skills/`，排除 `**/.*`。
  - 源码：app/build.gradle.kts:9-33,62-66

F-005: `gradle/libs.versions.toml` 声明 AGP 8.7.3、Kotlin 2.1.0、coroutines 1.9.0、serialization 1.7.3、OkHttp 4.12.0、snakeyaml-engine 2.8、Robolectric 4.14.1、Compose BOM 2024.12.01。
  - 源码：gradle/libs.versions.toml:1-14

F-006: `README.md` 的目录树列出 core-api / core-llm / core-memory / core-skills / core-sentinel / core-agent / hands / app / cli / skills/examples / docs / scripts；`LICENSE` 为 MIT。
  - 源码：README.md:70-86,97-99

## 2. core-api：接口与数据结构

F-007: `AgentEvent` 是 sealed class，共 10 个子类型：`Reply`、`SkillChosen`、`PhoneTaskStarted`、`StepPlanned`、`StepExecuted`、`StepBlocked`、`NeedsUser`、`MemoryUpdated`、`PhoneTaskFinished`、`Failed`。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Agent.kt:4-28

F-008: `AgentConfig` 的默认值为 `maxSteps = 30`、`stuckRepeats = 3`、`historyWindow = 8`、`maxNodes = 120`、`learnFromSuccess = true`。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Agent.kt:39-49

F-009: `Agent` 接口有 `handle(userMessage, listener, stop)` 与 `runPhoneTask(goal, skillName, listener, stop)` 两个挂起方法；`StopSignal` 只有一个 `stopped: Boolean` 属性；`UserChannel.ask(taskId, question, takeover)` 返回用户答复字符串。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Agent.kt:30-62

F-010: `Point` 把坐标归一化到 0..1000（`NORM = 1000`），构造时 `require` 范围；`Bounds.center` 由四边计算。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Device.kt:10-25

F-011: `UiNode` 含 `id/text/description/resourceId/className/bounds/clickable/editable/scrollable/focused/password` 字段；`ScreenState` 含 `screenshotPng/widthPx/heightPx/packageName/activityName/nodes/secure/capturedAtMillis`，`fingerprint()` 用包名、Activity 与节点文本/中心坐标生成十六进制串。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Device.kt:28-65

F-012: `Action` 是 sealed class，以 `@SerialName` 区分 11 种：`tap`、`long_press`、`swipe`、`type`、`back`、`home`、`launch`、`deeplink`、`wait`、`ask_user`、`finish`；每种都带可选 `target` 与 `reason`。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Device.kt:67-110

F-013: `Device` 接口定义 `observe(): ScreenState`、`perform(action): ActionResult`、`installedApps(): List<AppInfo>` 三个挂起方法。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Device.kt:118-126

F-014: `ModelRole` 只有 `CHAT` 与 `OPERATOR` 两个枚举值；`ModelConfig` 含 `baseUrl/model/apiKey/temperature/maxTokens/timeoutSeconds(默认 120)/extraHeaders`，其 `toString()` 把 apiKey 固定显示为 `***`。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Llm.kt:7-27

F-015: `ChatRole` 有 `SYSTEM/USER/ASSISTANT/TOOL`；`ContentPart` 有 `Text` 与 `ImagePng` 两种；`ChatMessage` 携带 `toolCalls` 与 `toolCallId`；`ToolSpec.parameters` 是 JSON Schema 对象；`ChatRequest` 有 `jsonMode` 开关。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Llm.kt:29-65

F-016: `Note` 的字段为 `title/permalink/type/tags/extraFrontmatter/body/observations/relations/updatedAtMillis`；`Observation` 为 `(category, content, tags, context)`；`Relation` 为 `(type, target, context)`；`SearchHit` 为 `(permalink, title, snippet, score)`。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Memory.kt:26-45

F-017: `MemoryStore` 有 6 个挂起方法：`write`、`read`、`search`、`appendObservation`、`delete`、`list`。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Memory.kt:47-64

F-018: `Sentinel` 接口有 `guard(context, action): Decision` 与 `authorize(context, action): Boolean`；`Decision` 分 `Allow/Ask/Deny`；`ApprovalScope` 分 `ONCE/TASK`；`AuditRecord` 记录 `(timeMillis, taskId, stepIndex, action, decision, approved)`。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Sentinel.kt:4-61

F-019: `Skill` 字段为 `name/description/apps/channel/confirmBefore/memoryRefs/deeplinks/instructions/flow/source`；`SkillChannel` 有 6 个值：`api`、`cli`、`deeplink`、`gui`、`deeplink-then-gui`、`mixed`（默认 `GUI`）。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Skills.kt:21-42

F-020: `FlowStep` 是 sealed class，共 8 种：`Launch`、`Deeplink`、`Ai`、`Confirm`、`Tap`、`Type`、`Wait`、`Assert`；`SkillLoadResult` 同时返回 `skills` 与 `problems`。
  - 源码：core-api/src/main/kotlin/dev/phonepal/api/Skills.kt:58-74

## 3. core-agent：聊天编排与操作循环

F-021: `PhonePalAgent.handle` 的聊天空转最多 `MAX_TOOL_ROUNDS = 8` 轮；每轮把 assistant 的 tool_calls 与每个工具结果追加进本轮消息；`HISTORY_LIMIT = 20` 限制跨轮历史，且窗口不得以 assistant 消息开头；`MEMORY_HITS = 5`。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/PhonePalAgent.kt:61-86,132-138,192-198

F-022: `systemPrompt` 由人设（`Prompts.DEFAULT_PERSONA`）、技能索引（每行 `- name: description`）与记忆检索命中（`- title (permalink): snippet`）三段拼成。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/PhonePalAgent.kt:120-130

F-023: `runPhoneTask` 先按名字取技能（找不到则直接返回失败 `SKILL_NOT_FOUND`），再装载技能的 `memoryRefs` 与 `howto` 笔记；技能有非空 flow 时走 `FlowRunner`，否则走 `OperatorLoop`；成功且 `learnFromSuccess` 时调用 `learn`。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/PhonePalAgent.kt:88-118,140-155

F-024: `learn` 把成功路径写成 `- [path] a → b → c #<skill或包名>` 观察条目，permalink 为 `howto/<key>`，笔记类型 `howto`；重复的相同观察不会再次追加。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/PhonePalAgent.kt:157-182,196-200

F-025: `OperatorLoop.run` 的每一轮依次做：检查停止信号、`device.observe()`、受保护屏幕转交用户、卡死计数、拼提示词、调用操作模型、解析、单步约束校验、nodeId 存在性校验、发 `StepPlanned`、处理 `finish/ask_user`、经 Sentinel 执行。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/OperatorLoop.kt:51-149

F-026: 卡死判定：动作执行后屏幕 `fingerprint()` 连续不变，`stuckRepeats` 触发一次警告反馈，再触发即返回失败；解析失败累计 `PARSE_FAILURE_LIMIT = 3` 次则失败；模型调用 `completeWithRetry` 对 `LlmException` 重试一次。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/OperatorLoop.kt:63-74,85-92,201-206,238-240

F-027: 单步约束 `StepConstraint(kind, target, text)` 在 flow 的 `tap`/`type` 步骤使用：只接受对应动作类型，`type` 可强制覆盖文本，最多 `SINGLE_STEP_TRIES = 3` 轮。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/OperatorLoop.kt:94-105；core-agent/src/main/kotlin/dev/phonepal/agent/FlowRunner.kt:32-36,90-94

F-028: `OperatorLoop.execute` 先 `sentinel.authorize`；被拦截时发 `StepBlocked` 并把拦截原因作为下一步反馈；放行后 `device.perform`，异常转成 `ActionResult(false, ...)`；成功时累加 `task.steps` 并把 `ScreenText.pathLabel` 记入路径。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/OperatorLoop.kt:151-173

F-029: 操作提示词按固定分节拼接：目标/子目标、技能说明、技能记忆引用、howto 笔记、最近 `historyWindow` 步、上一步反馈、单步约束、当前屏幕（节点列表 + 截图）、`NEXT_STEP`；请求带 `jsonMode = true`。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/OperatorLoop.kt:208-236

F-030: `AgentTools` 向聊天模型提供 6 个工具：`memory_search`、`memory_read`、`memory_write`、`memory_forget`、`list_skills`、`phone_task`，参数以 JSON Schema 描述。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/AgentTools.kt:12-66

F-031: `ChatTools.execute` 按工具名分发；参数不是合法 JSON 对象、缺字段或运行异常都转成 `{"error": "..."}` 作为 tool 结果返回，不抛出到聊天循环。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/ChatTools.kt:32-63

F-032: `memory_write` 读取已有笔记后按 `(category, content)` 与 `(type, target)` 去重合并观察与关系，保留旧 tags、额外 frontmatter 与正文前言；`memory_forget` 真正删除文件。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/ChatTools.kt:90-138

F-033: `FlowRunner` 逐条执行 flow：`launch/deeplink/tap/type/wait` 直接或经单步约束执行，`ai` 交给子目标操作循环，`confirm` 通过 `UserChannel` 问用户，`assert` 让操作模型判定屏幕；任一步失败即返回。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/FlowRunner.kt:18-58

F-034: `FlowRunner.fill` 用正则 `\{([A-Za-z0-9_\-\p{IsHan}]+)\}` 找占位符：已知值直接替换；缺失时先问操作模型（`{"values": {...}}`），仍缺再问用户；URL 场景做 UTF-8 百分号编码。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/FlowRunner.kt:64-91

F-035: `isYes` 先排除空串、以「不/别/no」开头的回答，再匹配中文「是/好/确认/确定/可以/行/对/嗯」或英文 `yes/ok/okay/y/sure/yeah`（英文要求词边界）。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/FlowRunner.kt:96-102

F-036: `OperatorReplyParser` 先剥 Markdown 代码围栏，再取第一个括号配平的 `{...}`；`typeSynonyms` 把约 50 个同义词/别名归一到 11 种 Action；点可写成 `[x,y]`、`{x,y}` 或 `"x,y"`，统一 clamp 到 0..1000。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/OperatorReplyParser.kt:27-95,200-234

F-037: 所有面向模型的中文文本集中在 `Prompts` object，包括人设、操作员系统提示、受保护屏幕话术、卡死/解析失败/最大步数等常量，以及目标、屏幕、单步约束等拼接函数。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/Prompts.kt:5-94

F-038: `ScreenText.nodeLine` 输出 `[id] ClassName "text" desc=... res=... (l,t,r,b) clickable editable ...`；文本压缩空白并截到 60 字符加省略号；`pathLabel` 对 `tap/long_press/type/launch/deeplink/swipe/back` 生成路径标签，对 `home/wait/ask_user/finish` 返回 null。
  - 源码：core-agent/src/main/kotlin/dev/phonepal/agent/ScreenText.kt:19-65

## 4. core-sentinel：模型外的安全闸门

F-039: `PolicySentinel` 的判定顺序是「先 deny，再 ask，最后 allow」；deny 三条：受保护屏幕上的设备动作（`back/home/wait` 除外）、向密码字段输入、技能声明 `apps` 时操作清单外包（启动器与自身包除外）。
  - 源码：core-sentinel/src/main/kotlin/dev/phonepal/sentinel/PolicySentinel.kt:19-43,100-138

F-040: ask 规则：`tap/long_press/type` 的 target 或被操作节点的 text/description 命中确认词；`deeplink` 的 scheme+host 不匹配技能 `deeplinks` 中任一模板（无技能或无模板时一律询问）。
  - 源码：core-sentinel/src/main/kotlin/dev/phonepal/sentinel/PolicySentinel.kt:140-180

F-041: `authorize` 对 `Ask` 先查本任务已授予的 TASK 级批准（键为 `word:<词>` 或 `deeplink:<scheme://host>`）；否则经 `ApprovalGateway` 往返；批准为 TASK 时写入 `taskApprovals`；`endTask(taskId)` 清空；每次决策写 `AuditSink`。
  - 源码：core-sentinel/src/main/kotlin/dev/phonepal/sentinel/PolicySentinel.kt:61-96

F-042: 内置确认词共 17 个：支付、付款、确认支付、立即支付、转账、发送、删除、下单、提交订单、确认呼叫、呼叫、购买、pay、send、delete、purchase、order；技能 `confirm_before` 与 `extraConfirmWords` 只能追加，`normalize` 去空、去重（忽略大小写）。
  - 源码：core-sentinel/src/main/kotlin/dev/phonepal/sentinel/ConfirmWords.kt:10-20

F-043: 确认词按子串匹配，但首/尾为拉丁字母或数字时加词边界断言，因此 `order` 命中 `Place Order`、不命中 `border`；`longestIn` 在多个命中词中取最长。
  - 源码：core-sentinel/src/main/kotlin/dev/phonepal/sentinel/ConfirmWords.kt:22-34

F-044: 默认启动器包名集合共 12 个：AOSP 三个、Pixel、Samsung、小米、华为、荣耀、OPPO、vivo、OnePlus、魅族。
  - 源码：core-sentinel/src/main/kotlin/dev/phonepal/sentinel/PolicySentinel.kt:222-236

## 5. core-memory：Basic Memory 格式与中文检索

F-045: 笔记文件是带 frontmatter 的 Markdown；`Observations` 行格式 `- [category] content #tag (context)`，`Relations` 行格式 `- 关系 [[目标]] (context)`；正文中的 `[[wiki link]]` 额外算作 `links_to` 关系；围栏代码块内的行不参与解析。
  - 源码：core-memory/src/main/kotlin/dev/phonepal/memory/BasicMemoryFormat.kt:12-30,115-131,237-255

F-046: `render` 在正文为空时按 observations/relations 生成 `# 标题`、`## Observations`、`## Relations`；正文非空时只把缺失的观察/关系插入对应小节，不覆盖用户已有内容；frontmatter 固定写 `title/type/permalink/tags`，其余键原样保留。
  - 源码：core-memory/src/main/kotlin/dev/phonepal/memory/BasicMemoryFormat.kt:59-72,133-191

F-047: `MemoryIndex.sync` 递归扫描根目录下的 `*.md`（跳过点开头文件/目录），按 mtime + size 判断是否需要重读，并剔除已消失文件；`put` 时正文权重 1.0、标题 `TITLE_BOOST = 3.0`、标签 `TAG_BOOST = 2.0`。
  - 源码：core-memory/src/main/kotlin/dev/phonepal/memory/MemoryIndex.kt:22-61,121-128

F-048: 检索使用 BM25（`K1 = 1.2`、`B = 0.75`），标题包含整串时乘 1.5、正文包含整串时乘 1.2；只有命中「主词」（query 权重 ≥ 1.0 的词）的笔记才参与排序，CJK 单字弱匹配（权重 0.3）单独命中时被过滤。
  - 源码：core-memory/src/main/kotlin/dev/phonepal/memory/MemoryIndex.kt:67-106,121-128

F-049: `Tokenizer` 把非 CJK 连续字母数字转小写作为一个词；CJK 连续段同时产出单字与相邻双字；查询时双字权重 1.0、单字权重 `WEAK_WEIGHT = 0.3`，单字查询本身仍为主词。
  - 源码：core-memory/src/main/kotlin/dev/phonepal/memory/Tokenizer.kt:9-56

F-050: 搜索摘要 `Snippets` 逐行打分取最高者，最长 `MAX_LENGTH = 120` 字符，按命中位置向两侧裁剪，并处理代理对边界。
  - 源码：core-memory/src/main/kotlin/dev/phonepal/memory/MemoryIndex.kt:131-172

F-051: `FileMemoryStore` 把 permalink 映射为 `<root>/<permalink>.md`，写入用「临时文件 + ATOMIC_MOVE（不支持时退化为 REPLACE_EXISTING）」，随后 `setLastModified(clock())`；所有操作经 `Mutex` 串行化并切到 `Dispatchers.IO`。
  - 源码：core-memory/src/main/kotlin/dev/phonepal/memory/FileMemoryStore.kt:19-33,67-80,113-131

F-052: `fileFor` 用 canonical path 前缀校验防止 permalink 逃出记忆目录；空 permalink 时按标题生成 slug，冲突则追加 `-2`、`-3`…。
  - 源码：core-memory/src/main/kotlin/dev/phonepal/memory/FileMemoryStore.kt:95-112

## 6. core-skills：技能加载与校验

F-053: `DirectorySkillRepository` 接收多个根目录，后加载的同名技能覆盖先加载的（App 传入「内置技能目录, 用户技能目录」）；缺失根目录静默跳过；坏技能记入 `problems` 且不影响其他技能；用户同名技能损坏时内置技能保持生效。
  - 源码：core-skills/src/main/kotlin/dev/phonepal/skills/DirectorySkillRepository.kt:15-53,58-94

F-054: `SkillParser.KEYS` 共 7 个合法键：`name`、`description`、`apps`、`channel`、`confirm_before`、`memory`、`deeplinks`；未知键报问题（防拼写错误静默丢字段）；`name` 需匹配 `^[a-z0-9-]+$`；`description` 必须非空且单行。
  - 源码：core-skills/src/main/kotlin/dev/phonepal/skills/SkillParser.kt:17-73

F-055: `parseFolder` 允许 `name` 与文件夹名不一致：报问题但仍按 frontmatter 的 `name` 返回技能；只有 `SKILL.md` 完全合法后才解析 `flow.yaml`（因为 flow 要对照 deeplinks 与 apps 校验）。
  - 源码：core-skills/src/main/kotlin/dev/phonepal/skills/SkillParser.kt:28-39

F-056: `FlowParser.STEP_KINDS` 共 8 种：`launch`、`deeplink`、`ai`、`confirm`、`tap`、`type`、`wait`、`assert`；`wait` 取值限定整数 0..`600000` 毫秒；`launch` 的包名必须在技能 `apps` 内（若声明了 apps）；任何问题都会让整个 flow 返回 null。
  - 源码：core-skills/src/main/kotlin/dev/phonepal/skills/FlowParser.kt:15-108

F-057: `YamlDoc` 基于 snakeyaml-engine 的 Compose 保留行号，`lineOffset` 用于把 frontmatter 内的相对行号换算成文件行号；重复键、非字符串键均报问题；`stringList` 接受单字符串、`null` 或字符串序列。
  - 源码：core-skills/src/main/kotlin/dev/phonepal/skills/Yaml.kt:14-106

## 7. core-llm：OpenAI 兼容客户端

F-058: `OpenAiCompatibleClient` 对 408/409/429/5xx 与 IO 异常最多重试 `maxRetries = 2` 次，退避从 `baseDelayMillis = 500` 开始按 2 的幂增长，`Retry-After` 头优先（秒转毫秒）。
  - 源码：core-llm/src/main/kotlin/dev/phonepal/llm/OpenAiCompatibleClient.kt:43-91,217-219,238-244

F-059: 收到 400 且响应体含 `response_format` 时，客户端关闭该实例的 JSON 模式并重发一次；`jsonModeUnsupported` 为 `@Volatile`，后续请求不再携带 `response_format`。
  - 源码：core-llm/src/main/kotlin/dev/phonepal/llm/OpenAiCompatibleClient.kt:62-83,110

F-060: 图片按 `data:image/png;base64,...` 放入 `image_url` 内容块；带图消息的 `content` 是数组，纯文本消息是字符串；assistant 的 tool_calls 转成 OpenAI `tools/tool_calls` 结构。
  - 源码：core-llm/src/main/kotlin/dev/phonepal/llm/OpenAiCompatibleClient.kt:93-155

F-061: 错误信息在抛出前用 `redact` 把 API Key 替换为 `***`；`toString()` 同样不暴露 Key；HTTP 超时同时设置 `callTimeout` 与 `readTimeout`。
  - 源码：core-llm/src/main/kotlin/dev/phonepal/llm/OpenAiCompatibleClient.kt:56-59,232-234

## 8. hands：无障碍手眼

F-062: `AccessibilityDevice.observe` 串行执行：取服务实例（未连接抛 `ServiceNotConnectedException`）、读屏幕尺寸、截屏、读节点、取前台包名/Activity；每次动作后默认等待 `settleDelayMs = 600` 毫秒。
  - 源码：hands/src/main/kotlin/dev/phonepal/hands/AccessibilityDevice.kt:39-81,202-215

F-063: 截屏受系统限制按 `SCREENSHOT_INTERVAL_MS = 1050` 毫秒节流，最多尝试 3 次；`ERROR_TAKE_SCREENSHOT_SECURE_WINDOW` 直接标记 `secure = true`；Android 11–13 把受保护窗口截成纯黑帧，代码用 16×16 采样判黑后同样标记 `secure`。
  - 源码：hands/src/main/kotlin/dev/phonepal/hands/AccessibilityDevice.kt:85-105,143-161,363-372；hands/src/main/kotlin/dev/phonepal/hands/Geometry.kt:61-76

F-064: 节点收集以 `rootInActiveWindow` 优先，再按 layer 从上到下补应用窗口与聚焦的系统窗口，跳过 IME 与状态/导航栏；`NodeCompactor` 先序遍历，保留可见且「有文本/描述/可点击/可长按/可编辑/可滚动」的节点，最多 200 个、文本最多 200 字符、深度 64，id 即列表下标，密码字段的 text 被置空。
  - 源码：hands/src/main/kotlin/dev/phonepal/hands/AccessibilityDevice.kt:163-190；hands/src/main/kotlin/dev/phonepal/hands/NodeCompactor.kt:36-107

F-065: 点击优先对 `nodeId` 调 `ACTION_CLICK`（长按 `ACTION_LONG_CLICK`）；不可点击、已失效或被拒时回退为对节点中心手势按压；坐标动作经 `Coordinates.denormalize` 还原像素并限制在屏幕内。
  - 源码：hands/src/main/kotlin/dev/phonepal/hands/AccessibilityDevice.kt:239-270；hands/src/main/kotlin/dev/phonepal/hands/Geometry.kt:40-45

F-066: 长按时长 clamp 到 400..5000 毫秒，滑动时长 clamp 到 50..5000 毫秒，`wait` 最长 30000 毫秒；`type` 用 `ACTION_SET_TEXT`，`submit` 时再发 `ACTION_IME_ENTER`；截图长边缩到 1280 像素且不放大。
  - 源码：hands/src/main/kotlin/dev/phonepal/hands/AccessibilityDevice.kt:217-237,288-318,363-372；hands/src/main/kotlin/dev/phonepal/hands/Geometry.kt:48-59

## 9. app：Android 装配层

F-067: `AppGraph` 是手写依赖容器：外部文件根下分 `memory/`、`skills/`、`traces/`，内置技能解压到 `filesDir/bundled-skills/`；技能仓库根顺序为「内置, 用户」；`PolicySentinel` 的 `selfPackage` 取 `app.packageName`。
  - 源码：app/src/main/kotlin/dev/phonepal/app/AppGraph.kt:39-74

F-068: `AppGraph.agent()` 在设置变化时重建 `PhonePalAgent`；未配置两个模型时返回 null；设置通过 `SettingsStore` 读取，API Key 存在 `EncryptedSharedPreferences`（AES256_SIV/AES256_GCM），普通字段存普通 SharedPreferences。
  - 源码：app/src/main/kotlin/dev/phonepal/app/AppGraph.kt:100-121；app/src/main/kotlin/dev/phonepal/app/settings/SettingsStore.kt:13-16,75-97

F-069: `AgentSession` 用 `AtomicBoolean running` 保证同一时刻只有一个聊天轮或手机任务；聊天列表最多 `MAX_ITEMS = 500` 条；它同时实现 `UserChannel` 与 `ApprovalGateway`：下一条聊天输入可回答待答问题，审批卡/通知回答审批请求。
  - 源码：app/src/main/kotlin/dev/phonepal/app/session/AgentSession.kt:57-67,123-141,184-214,255-257

F-070: 每个任务在轨迹中必须以终止事件收尾：无法运行、忙、崩溃或取消时，`AgentSession` 自己补发 `Failed` + `PhoneTaskFinished`。
  - 源码：app/src/main/kotlin/dev/phonepal/app/session/AgentSession.kt:143-167,227-248

F-071: 轨迹每行固定 8 个键 `time, run, kind, step, action, text, ok, decision`，缺失值为 JSON null；`kind` 是 `AgentEvent` 类名；`decision` 形如 `allow|ask|deny: <reason>`；`TraceWriter` 写 `trace.jsonl`、`audit.jsonl` 与 `step-<n>.png`，并把 API Key（长度 ≥ 4）替换为 `***`。
  - 源码：app/src/main/kotlin/dev/phonepal/app/trace/TraceFormat.kt:13-100；app/src/main/kotlin/dev/phonepal/app/trace/TraceWriter.kt:10-17,89-98

F-072: debug 包导出 `DebugReceiver`，支持 `dev.phonepal.debug.RUN`（goal/skill/run_id）、`STOP`、`RELOAD_SKILLS` 三个广播；`BundledSkills.extract` 用 `.version` 标记（版本号-安装时间）决定是否重新解压 assets。
  - 源码：app/src/debug/kotlin/dev/phonepal/app/debug/DebugReceiver.kt:10-50；app/src/main/kotlin/dev/phonepal/app/BundledSkills.kt:7-20

## 10. cli：技能开发者工具

F-073: CLI 顶层 6 个命令：`lint`、`push`、`run`、`stop`、`logs`、`traces`，其中 `traces` 又有 `pull`、`show` 两个子命令；run id 只允许字母、数字、`.`、`_`、`-`；`--follow` 持续打印事件并以终止事件的成败作为退出码。
  - 源码：cli/phonepal_cli/main.py:19-26,75-121,193-243

F-074: CLI 的 lint 规则与 Kotlin 端逐条对齐（7 个键、6 个 channel、8 种 flow 步骤、`MAX_WAIT_MILLIS = 600000`、包名正则），并自带手写 YAML 子集解析器（支持块/流式集合、引号、块标量，不支持锚点/别名/标签，报错带行号）。
  - 源码：cli/phonepal_cli/lint.py:18-27；cli/phonepal_cli/yamlsub.py:1-16

## 11. 测试与 CI（计数经脚本复核）

F-075: Kotlin 测试共 20 个文件、162 个 `@Test` 方法；CLI 共 4 个测试文件、68 个 `test_*` 函数。
  - 源码：脚本 `count_facts.py` 对 `*/src/test*/**/*.kt` 与 `cli/tests/test_*.py` 计数

F-076: CI 在 ubuntu-latest + JDK 17 上跑 `./gradlew test :app:assembleDebug`，随后用 Python 3 跑 `python -m unittest discover -s tests -v` 与 `python3 cli/phonepal.py lint skills/examples/*/`，并上传 debug APK 产物。
  - 源码：.github/workflows/ci.yml:8-28

F-077: 5 个 `core-*` 模块的构建脚本都只应用 `kotlin.jvm` 与 `kotlin.serialization` 插件，未应用 Android 插件；对 `core-*/**/*.kt` 搜索 `^import android\.` 无匹配。
  - 源码：core-api/build.gradle.kts、core-llm/build.gradle.kts、core-memory/build.gradle.kts、core-skills/build.gradle.kts、core-sentinel/build.gradle.kts、core-agent/build.gradle.kts

F-078: `core-*` 的第三方运行时依赖只有两个：`core-llm` 依赖 OkHttp，`core-memory` 与 `core-skills` 依赖 snakeyaml-engine；`core-api`、`core-sentinel`、`core-agent` 无第三方运行时依赖（协程与序列化由 Kotlin 插件提供）。
  - 源码：core-llm/build.gradle.kts、core-memory/build.gradle.kts、core-skills/build.gradle.kts

F-079: 设置页可调的 `maxSteps` 范围是 `1..200`（默认取 `AgentConfig().maxSteps = 30`）；温度解析范围是 `0.0..2.0`；默认 Base URL 为火山方舟 `https://ark.cn-beijing.volces.com/api/v3`。
  - 源码：app/src/main/kotlin/dev/phonepal/app/settings/AppSettings.kt:27-29,46-48,92

F-080: README 声明需要 Android 11（API 30）及以上；不支持 iOS，原因是 iOS 不允许一个 App 读取或操作其他 App；模型侧需要两个兼容 OpenAI 接口的服务，其中一个必须能看图的屏幕操作模型。
  - 源码：README.md:9-12

F-081: `Notifier` 创建状态、审批、提问三类通知，状态通知带「停止」动作；`OverlayController` 在会话忙碌且无障碍服务已连接时显示 `StatusOverlay`（步骤文字 + 停止按钮），停止回调调用 `session.stop()`。
  - 源码：app/src/main/kotlin/dev/phonepal/app/Notifier.kt:17-46；app/src/main/kotlin/dev/phonepal/app/OverlayController.kt:14-44

F-082: `RecordingDevice` 包装一个 `Device`：`observe()` 后把非空截图交给回调（App 中即 `traces::saveScreenshot`），`perform` 与 `installedApps` 直接转发。
  - 源码：app/src/main/kotlin/dev/phonepal/app/trace/RecordingDevice.kt:12-27
