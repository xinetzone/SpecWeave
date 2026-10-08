---
type: Review
title: "DeepSeek Harness 入口桥（specweave-dsh-bridge）独立对抗性评审报告"
status: final
created: 2026-09-30
reviewer: "独立对抗性评审者（全新上下文子会话，只读，不共享实现过程）"
source: "spec.md / tasks.md（同目录）；被审对象 specweave-dsh-bridge/（index.js、lib/*.js、tests/**、README.md、ACCESS.md、package.json、cordis.patch.yml、skills/**）"
---

# DeepSeek Harness 入口桥 - Independent Review

> 本文件由实现者依据独立评审子会话的报告**逐字转录**（评审者只读，不写文件）。
> 评审者独立复跑了测试套件，并用真实 `@deepseek-ai/dsh-tools` 编译四个工具以验证契约，
> 未采信实现者的任何自我结论。

## 检查点

- [x] **CP-R1**: 测试套件可独立复跑，且断言强度足以在实现回退时失败
  - **Type**: `rule` — **Covers**: AC-1、AC-2、AC-3、AC-4 — **Evidence**: 评审者独立复跑 `node --import ./tests/stub-loader.js tests/bridge.test.js` → `tests 34 / pass 34 / fail 0`；断言为值级 `deepEqual`/正则（注入用例断言 `source.kind`/`root`、文本含 `[SpecWeave 启动协议]`、消息条数、`reject` 用 `deepEqual` 原样比对）

- [x] **CP-R2**: lib 边界行为（截断、转义、检测、匹配）不崩溃且无未处理异常
  - **Type**: `rule` — **Covers**: AC-1、AC-2 — **Evidence**: 评审者以 `--input-type=module -e` 探针实测：`truncateUtf8` 在 0/负数/NaN/Infinity/小数上限下全程无 U+FFFD、无 RangeError；框架转义对抗（`root` 注入 700×`X` + `</system-reminder>`）闭合标签恒为 1 且位于末尾；`detectWorkspace` 对空串/UNC/不存在路径/null/数字均安全；无 unhandledRejection

- [x] **CP-R3**: 四个工具的 `parameters` 用 author DSL 且无非法键；`output.schema` + `output.render` 齐备
  - **Type**: `rule` — **Covers**: AC-3 — **Evidence**: 评审者用**真实** `@deepseek-ai/dsh-tools`（`.temp/dsh-extract`）编译并注册：`APPLY ERROR: none`；`required: true` 被正确编译为对象级 `required` 数组；缺参调用抛 `ToolArgsError`；四个 `render` 均为 function

- [x] **CP-R4**: `/specweave` 命令定义合法且返回值形状正确
  - **Type**: `rule` — **Covers**: AC-3 — **Evidence**: `name` 匹配 `/^[a-z][a-z0-9_-]*$/u`（dsh-commands:78/150）；description/hint 非空（:151-158）；返回 `{kind:'success'|'error', text}`（:187-202）；`rawInput`/`agent` 用法与真实调用一致（:379-388）

- [x] **CP-R5**: `specweave-protocol` 技能注册合法
  - **Type**: `rule` — **Covers**: AC-3 — **Evidence**: `name` 匹配 `SKILL_NAME`（dsh-skill:17/466）；description 非空（:467）；`invocation` 形状合法（:504-509）；`source`/`provider`/`content`/`whenToUse` 均为 string（:482-489）

- [x] **CP-R6**: `agent/pre-step` 瀑布监听用法正确
  - **Type**: `rule` — **Covers**: AC-2 — **Evidence**: 非 owner 分支返回的正是 `next()` 结果；改写用 `{...decision, messages}` 展开；`startsRequestSeries` 有断言保留；与宿主 `dsh-agent-instructions:1271-1288` 同构

- [x] **CP-R7**: 注入消息的 `source` 合法且不影响宿主其它机制
  - **Type**: `rule` — **Covers**: AC-2 — **Evidence**: `source.kind='specweave-bridge'` 且 `form:'instructions'`；用官方 `createUserMessage`；非 `'user'` kind 使 `/name` 手势扫描跳过（dsh-tool-skill:381-394）；不被 runtime-context 投影误认领（dsh-agent-loop:220-222）；经 `step()` 以 `surfaceOp:'append'` durable 落盘（:1061）⇒ 回放可重建

- [x] **CP-R8**: 未触碰宿主反模式，依赖声明符合 bundle 契约
  - **Type**: `rule` — **Covers**: AC-5 — **Evidence**: `inject=['tools']` 且可选服务走 `ctx.inject`（practices.md:20）；无 `system-prompt/assemble` 监听、无 `ctx.systemPrompt.section`、不追加新 session 事件类型、不写 profile、不代执行脚本；全插件仅 1 处 `agent/pre-step` 监听

- [x] **CP-U1**: 文档与实际行为一致（含声明的准确性）
  - **Type**: `rubric` — **Covers**: AC-5 — **Scale**: 1-5 — **Anchors**: 1 = 文档描述与代码不符或有无法验证的强断言；3 = 主要事实正确但存在过度声明；5 = 组件表/config 键/安装与验证步骤逐项与代码一致，限制如实声明且不含零 footprint 之类的过度声明 — **Pass Threshold**: >= 4 — **Evidence**: R1 发现组件表与 Config 8 键逐项一致、`install_bundle` 用法与 host-plugin.md 一致、测试条数与实测一致，但 README 首段「完全静默（零 footprint）」属过度声明（F-08）→ R1 判 3 分；修后 README 改为「brief 注入完全静默；工具/命令/技能为宿主级注册」→ R2 复评

- [x] **CP-U2**: 每条 AC 都被可执行断言覆盖
  - **Type**: `rule` — **Covers**: AC-1、AC-2、AC-3、AC-4、AC-5 — **Evidence**: AC-1 → 检测用例组；AC-2 → 注入用例组（6 例）；AC-3 → 注册/工具用例组（7 例）；AC-4 → 门控/开关用例；AC-5 为 rubric，证据为 `index.js` 注册清单 + README 设计原则 + 本评审 R1/R2 结论

## Review History

### Review R1
- **Result**: `fail`
- **Evidence**:
  - 独立复跑：`ℹ tests 27 / ℹ pass 27 / ℹ fail 0`（当时版本）
  - 契约验证：用真实 `@deepseek-ai/dsh-tools` 编译注册四个工具成功，`APPLY ERROR: none`；8 项宿主契约检查（parameters DSL / output / 命令 / 技能 / pre-step / source / 反模式 / 依赖）全部通过
  - **必改 F-01（P2）**：乐观写缓存（`injected.set(session, root)` 先于消息落盘）在「pre-step 与 step 之间被中止」时会让本会话**永久失去 brief 且无自愈**——证据：宿主消息只在 `step()` 落盘（dsh-agent-loop:1061），其间存在 `throwIfAborted()`（:919）；探针（伪 session、surface 永不更新）得到「2 条 → 1 条」，证明抑制来自内存缓存而非日志
  - **必改 F-02（P3）**：`renderStartupBrief` 在 `maxBytes` < 框架 61 字节时仍返回 61 字节，违反 NFR-1；实测 `maxBytes=0/10/-5` 均返回 61 字节
  - 另有 9 条 P3：`output.render` 零断言覆盖、首步空批次会「凭空造步」、双向子串匹配噪声、>64 层路径检测失败、检测缓存无上限、`specweave_protocol` 工作区外返回空串、`specweave_route` 描述与实现不符、surface 扫描异常被当作「未注入」、`import.meta.dirname` 的 Node 版本门槛
- **Actions**: 全部处置（见下表）；套件由 27 项扩至 34 项，其中「已注入不重复」用例改为先落盘到伪 surface 再断言（原断言编码的正是 F-01 的缺陷行为）

### Review R2
- **Result**: `fail`（仅因 1 条由修复引入的回归）
- **Evidence**:
  - 独立复跑：`ℹ tests 34 / ℹ pass 34 / ℹ fail 0`（34 项属实）
  - **F-01 的三项点名要求全部实测成立**：(a) 置 `confirmed` 仅发生在「claim 批次已含本插件消息」与「surface 扫描 present」两处，插件从不在别处重建该消息，故 claim 命中只可能来自已提交批次；模拟「pre-step 与 step 之间被中止」（surface 永远为空）连打两步 → **两次都注入**；(b) 用 `scans` 计数器实测：落盘后首次扫描 1 次，其后恒为 1（短路在扫描之前）；(c) 扫描抛错时不确认、下一步恢复注入，且带其它 root 的 claim 不影响本 root 注入
  - **F-02** 超限已修（所有取值 ≤ 上限），但残留 ±1：`FRAME_BYTES=62` 而真实框架 61，`maxBytes∈[62,63]` 会产出「无正文框架」并被确认
  - **R2-N1（P2，回归）**：F-05 的反向匹配门槛用 UTF-16 长度，击穿全部 2 字中文查询（`链接`/`重复`/`原子`/`技能`/`角色`/`规范`/`提交`/`导出`/`看板` 共 9 项由「能命中」变为 0 命中）
  - **R2-N3（P3）**：`surface` 形状异常时三态恒为 `unknown`，每步一条 warn
  - **R2-N4（P3）**：`ACCESS.md` 仍称「换目录开会话桥接层完全静默」，与同文件后文及已修的 README 自相矛盾
  - 契约、命令、技能、pre-step、source、反模式、依赖等 8 项检查**重验全部通过**；用真实 `@deepseek-ai/dsh-tools` 重新编译注册成功（`APPLY ERROR: none`）；检测缓存上限实测正确
- **Actions**: R2-N1 改为「含非 ASCII 一律放行反向匹配，仅短纯 ASCII 受限」；R2-N2 让 `FRAME_BYTES` 与渲染头尾由**同一组常量**派生并加 `MIN_BODY_BYTES` 正文下限；R2-N3 加按会话节流的告警；R2-N4 改写措辞。套件扩至 35 项，并补齐评审指出的两处覆盖缺口（框架字节钉死、`disposed` 守卫）

### Review R3
- **Result**: `pass`
- **Evidence**:
  - 独立复跑：`ℹ tests 35 / ℹ pass 35 / ℹ fail 0`（35 项属实）
  - **R2-N1 回归消除**：评审自建回归表 10 项（`链接`/`重复`/`原子`/`技能`/`角色`/`规范`/`提交`/`导出`/`看板` 等）全部复原，噪声面 `e`/`a`/`ui` 保持 0 命中；`matchCheckCommands` 行为与 R2 完全一致
  - **R2-N2**：`FRAME_BYTES=61`（±1 消除，头尾同源）；对 `maxBytes=100…300` 全扫 201 个取值，**不存在「只有框架、没有正文」的带，也无任何输出超限**
  - **R2-N3**：`surface.nodes={}` 连打 5 步 → 注入 0 条、warn 恰好 1 条（节流生效，`WeakSet` 无引用泄漏）
  - **R2-N4**：`ACCESS.md` 已与 README 同口径且不再自相矛盾
  - 覆盖缺口闭合：框架边界被钉死（边界值必须 `bytes > FRAME_BYTES`）、`disposed` 守卫有测试（卸载后异步注册为 0）
  - 契约 8 项重验全部通过；用真实 `@deepseek-ai/dsh-tools` 编译注册 `APPLY ERROR: none`
  - **未发现新的功能回归**
- **Actions**: R3 判定为 pass；评审同时给出 4 条不阻断的 P3（文档阈值未同步、匹配语义只写半句、节流无断言、工作区内小上限时兜底文案自相矛盾），已全部闭环并补测试

### Review R4
- **Result**: `pass`
- **Evidence**:
  - 独立复跑：`ℹ tests 37 / ℹ pass 37 / ℹ fail 0`（评审另计 `test(` = 37、`assert.` = 158，确认 37 为真实用例数）
  - **Delta 1 兜底文案**：8 组矩阵（cap ∈ {4096, 189, 188, 100} × 工作区内/外）实测**无任何组合**再自称「不在 SpecWeave 工作区内」；工作区内大上限仍返回真 brief、工作区外仍返回兜底
  - **Delta 2 上限告警**：不可能在工作区外或其它路径触发（工作区外 cap=100 三步 → warn=0）；不改变返回决策（同一对象引用，三步注入 0/0/0）；每会话至多一条（三步 → warn=1，两会话 → warn=2）；抑制分支不写 `injected`、不置 `confirmed`
  - **未发现新的功能回归**；三态自愈/O(1)、brief 全扫、路由与校验命令抽查均与 R3 一致
- **Actions**: 判定为验收通过。评审同时给出 3 条不阻断的 P3（两处文档数字错误、两类告警共用节流集合），已全部闭环——其中"文档数字漂移"这一类被固化为**可失败的断言**（见下）

## R4 发现处置对照（pass 后的 P3 闭环）

| ID | 严重度 | 发现 | 处置 | 回归证据 |
|---|---|---|---|---|
| R4-N1 | P3 | README/ACCESS 的测试条数写成 55，实测 37（tasks.md 又是 37，三处不一致） | 三处统一为**实际用例数 38**（含新增的防漂移用例） | 新增用例「文档：三处文档引用的测试条数与套件实际用例数一致（防数字漂移）」把三处口径与真实用例数绑定 |
| R4-N2 | P3 | README 把纯 ASCII 反向匹配门槛写成「≥5 字符」，代码为 ≥3 | 改为 ≥3 | 同一条 README 行由评审以 `matchRoutes('link')` 实测佐证 |
| R4-N3 | P3 | 两类告警共用同一 `WeakSet`，先到先占可能互相屏蔽；DocBlock 已过期 | 拆为 `scanWarned` / `capWarned` 两个集合并更新注释 | 两类告警各自的 warn 计数断言（扫描失败 1 条、上限抑制 1 条） |

> **预防措施**：R4-N1 属「改文档时把数字写错」这一类，已按「修复→预防→闭环」固化为测试套件中的**文档一致性断言**——
> 套件自动统计自身 `test(` 用例数，并断言 README、ACCESS、tasks.md 三处引用的数字与之相等；任何一处漂移都会让套件变红。

## 验收结论

- **最终判定**：`pass`（R4 独立评审）+ `pass`（装配验证轮）。R1 的 2 条必改、R2 的 1 条回归 + 3 条 P3、R3 的 4 条 P3、R4 的 3 条 P3、装配轮的 2 条缺陷均已闭环。
- **最终套件**：41 项全通过（含 6 条由评审或真机验证转化而来的回归防线：子区域误判、注入自愈、2 字中文召回、文档数字漂移、零宿主导入、render 承载答案）。
- **仍不可离线验证**（见下节「未验证项」）：Cordis 运行时对注入回调内异步 `effect` 的认领语义。

### 装配验证轮（任务 6；由实现者在用户指示下执行，非评审者所为）
- **Result**: `pass`（首轮 `fail` → 修复后 `applied`）
- **Evidence**:
  - 首轮 `plugin_manager install_bundle`：包写入成功（profile `dependencies` 增加 `link:` 条目、`dsh.profile.bundles` 追加本包），但 **`application: failed`**——`specweave-bridge (@specweave/dsh-bridge): failed to import`；在 profile 解析环境下复现得 `ERR_MODULE_NOT_FOUND: Cannot find package '@deepseek-ai/schemastery'`
  - 根因（取证）：宿主包只存在于 dsh 安装的 `app.asar` 内（`app.asar.unpacked` 仅含原生模块），profile 的 `node_modules` 只含被安装包本身，因此 **profile 安装的 bundle 无法解析任何 `@deepseek-ai/*`**；官方 bundle 模板同样不含任何 import
  - 修复：去掉全部宿主导入（工具定义改为宿主支持的**原生 JSON Schema 子集**；user 消息用与宿主等价的最小实现构造，行为对照 `dsh-llm/lib/types/message.js:34-58`；不再导出 `Config`，因其需要 schemastery）→ 修复后 `set_bundle`（禁用→启用）两次均返回 **`application: applied`、`warnings: []`**
  - 端到端：本会话 system-reminder 实际出现 `[SpecWeave 启动协议]` 注入文本；宿主下发四个 `specweave_*` 工具 schema（`required: ["task"]` 等原生形态被接受）；`specweave_route 复盘`、`specweave_status` 实机执行成功
  - **装配期发现的第二个缺陷**：`output.render` 的返回值**就是**进入模型历史的工具结果内容（对照 `dsh-tool-skill` 的 `renderSkillContent` 用法），而原 render 过于简略——`specweave_route` 只报「命中 N 项」（模型看不到命中的规范路径）、`specweave_protocol` 只回一句标题 → 已改为承载答案本身，并在新进程内复核四段 render 文本
- **Actions**: 新增 FR-10（零宿主导入）、FR-11（render 承载答案）与 AC-6（装配可用）；新增两条测试守卫（源码不得出现 `@deepseek-ai/` 导入、render 输出必须含答案）；README 增「为什么不导入宿主包」章节
- **遗留**：已安装包为 `link:` 指向仓库目录，**源码更新后需重启 dsh** 才会加载新的 JS 模块代（宿主既有语义）；当前会话加载的是修复 render 之前的生成代——注入与工具均正常，仅工具结果文案较简。

## R3 发现处置对照（pass 后的 P3 闭环）

| ID | 严重度 | 发现 | 处置 | 回归证据 |
|---|---|---|---|---|
| R3-N1 | P3 | README 阈值仍写 61（实为 189），且低于阈值时无任何诊断 | README 改注 189 = 框架 61 + 最小正文 128；注入侧新增一次性告警（与扫描失败告警共用按会话 `WeakSet` 节流） | 「注入：上限低于最小可用值时一次性告警且不注入」 |
| R3-N2 | P3 | 匹配语义只写「≥3 字符」半句 | README 补全两分支规则：含非 ASCII 任意长度启用反向匹配，纯 ASCII 需 ≥3 字符 | 文档 |
| R3-N3 | P3 | 节流本身无断言 | harness 的 `logger.warn` 改为计数收集；断言扫描失败连打 3 步只有 1 条 warn | 「注入：surface 扫描失败时本轮既不注入也不确认」 |
| R3-N4 | P3 | 工作区内小上限时兜底文案自称「不在 SpecWeave 工作区内」 | 兜底文案重命名为 `FALLBACK_PROTOCOL` 并改为位置中立表述，工作区内/外共用且不再产生矛盾 | 「工具：工作区内小上限时 specweave_protocol 不得自称"不在工作区内"」 |

## R2 发现处置对照

| ID | 严重度 | 发现 | 处置 | 回归证据 |
|---|---|---|---|---|
| R2-N1 | P2（回归） | 反向匹配门槛用 UTF-16 长度，2 字中文查询全部失配 | 门槛改为 `非 ASCII 一律放行 ‖ 纯 ASCII 长度 ≥3`；中文 2 字词恢复反向召回，单字母仍被挡 | 「路由：短 ASCII 任务不启用反向匹配，2 字中文任务仍可命中」+ 手工抽样 22 条查询对照 |
| R2-N2 | P3 | `FRAME_BYTES` 比真实框架大 1，`[62,63]` 区间产出无正文框架且会被确认 | 头尾与 `FRAME_BYTES` 由同一组常量派生；新增 `MIN_BODY_BYTES=128` 与 `MIN_BRIEF_BYTES`，低于该上限直接返回空串 | 「brief：上限低于「框架+最小正文」时返回空串，达到阈值时必须带正文」（断言边界值字节数 > `FRAME_BYTES`） |
| R2-N3 | P3 | 扫描异常每步刷 warn | 按会话 `WeakSet` 节流，同会话只告警一次 | 「注入：surface 扫描失败时本轮既不注入也不确认」 |
| R2-N4 | P3 | `ACCESS.md` 过度声明残留 | 与 README 同口径改写 | 文档 |
| 覆盖缺口 | — | `FRAME_BYTES` 未钉死、`disposed` 零覆盖 | 边界用例断言「真的带正文」；harness 记录 effect disposer，新增卸载后不得注册技能的用例 | 两处新用例 |

## R1 发现处置对照

| ID | 严重度 | 发现 | 处置 | 回归证据 |
|---|---|---|---|---|
| F-01 | P2 | 乐观缓存致 brief 可能永久丢失 | 改为 `WeakMap<session,{root,confirmed}>` + 三态扫描（`present`/`absent`/`unknown`）：仅在观察到落盘证据时置 `confirmed`；未确认则下一步重新注入（自愈）；扫描失败既不注入也不确认 | 「未落盘时下一步重新注入（自愈），落盘后 O(1) 跳过」「surface 扫描失败时本轮既不注入也不确认」 |
| F-02 | P3 | brief 可超出 `maxBriefBytes` | 新增导出 `FRAME_BYTES`，上限小于框架时返回空串 | 「brief：上限小于框架字节数时返回空串而非超限文本」 |
| F-03 | P3 | `output.render` 零断言 | 遍历所有已注册工具断言 `render` 为函数且 `schema` 存在 | 「工具：每个工具都声明 output.render 与 output.schema」 |
| F-04 | P3 | 首步空批次会凭空造步 | 加护栏 `step === 1 && messages.length === 0` 直接返回（对齐 dsh-agent-instructions:1277-1280） | 「注入：首步空批次不注入」 |
| F-05 | P3 | 双向子串匹配噪声大 | 反向匹配加 ≥3 字符门槛；README 记录匹配语义 | 「路由：短任务不启用反向子串匹配（噪声防线）」 |
| F-06 | P3 | >64 层路径检测失败 | README「已知限制」明确回溯上限 | 文档 |
| F-07 | P3 | 检测缓存无上限 | `MAX_DETECTION_CACHE_ENTRIES = 128`，超限整体清空 | 代码审查 |
| F-08 | P3 | 工作区外 `specweave_protocol` 返回空串 | 新增 `WORKSPACE_AGNOSTIC_PROTOCOL` 作为兜底要点 | 「工具：specweave_protocol 在工作区外返回与工作区无关的协议要点」 |
| F-09 | P3 | 工具描述与实现不符 | 描述改为「工作区外仍返回匹配到的规范路径，但不做存在性校验」 | 代码审查 |
| F-10 | P3 | 扫描异常被当作「未注入」 | 三态扫描把异常归为 `unknown` → 本轮不注入不确认 | 同 F-01 用例 |
| F-11 | P3 | `import.meta.dirname` 需 Node ≥20.11 | 改用 `fileURLToPath(new URL('.', import.meta.url))` | 代码审查 |

## 未验证项（评审者声明，不因本次修订而消失）

1. **Cordis 运行时语义**：`@deepseek-ai/cordis` 未包含在解包集合中，`ctx.inject(['skills'], cb)` 回调返回后在 microtask 内 `skillCtx.effect(...)` 是否被正确认领/释放无法离线证实（已解包的 6 个官方插件均在回调内同步注册）。
2. **装配层（Task 6）**：**已由装配验证轮解除**——`application: applied`、注入与四个工具均实机验证通过。仅剩「替换已安装包的模块代需重启 dsh」这一宿主既有语义（已写入 README/ACCESS）。
3. **宿主运行时 Node 版本**：无法确认，F-11 已按最保守方式消除依赖（改用 `fileURLToPath`）。
4. **客户端对未知 `source.kind` 的渲染**：客户端代码位于 `app.asar` 内，未能核实（风险低）；但注入消息在本会话 system-reminder 中以 `[SpecWeave 启动协议]` 正常呈现，说明既有渲染路径可用。
5. **本会话加载的是修复 render 之前的生成代**：`output.render` 的新文案已在新进程内逐条复核，但其在 live 会话中的呈现需重启 dsh 后确认（属待观察项，非缺陷）。
