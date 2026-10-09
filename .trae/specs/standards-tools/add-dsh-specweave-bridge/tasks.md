# Tasks — add-dsh-specweave-bridge

## Task 1: R 阶段——DSH 插件契约与既有桥接先例的事实采集
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 解包 dsh 安装包（`app.asar`）内的 `@deepseek-ai/dsh-*` 包，读取官方插件开发技能与真实实现源码，确定宿主插件契约
  - 采集 Hermes 先例 `specweave-bridge-skeleton/` 的结构、常量与安装方法论
  - 实测 dsh 当前的技能目录与 `AGENTS.md` 加载行为，落定入口断点
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-1.1: 产出的契约结论必须逐条可回溯到具体文件路径与行号（如 `dsh-tool-skill/lib/index.js:203-236` 的 pre-step 注入范式）；证据：调研记录与引用清单
  - `rule` TR-1.2: 断点结论必须由**实测**得出而非推断——`skill` 工具在父会话与全新子会话各失败一次，且磁盘技能目录存在；证据：工具返回 `unknown or no longer available` 的原始文本
- **Completion Evidence**:
  - `rule` TR-1.1：已读取 `cordis-plugin-development/SKILL.md` 与 `references/{host-plugin,practices,verification}.md`、`templates/`，以及 `dsh-agent-instructions`/`dsh-tool-skill`/`dsh-commands`/`dsh-skill`/`dsh-tool-fs`/`dsh-command-compact` 的 `lib/index.js`；关键结论均带 `文件:行号`
  - `rule` TR-1.2：`skill(load-specweave)`、`skill(git-commit)`、`skill(dsh-probe)` 均为 `Error: skill "…" is unknown or no longer available`；子会话 088f6d33 复测同样为空目录，且报告无 `<available_skills>` 块

## Task 2: 实现 Host 侧桥接插件
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建 `specweave-dsh-bridge/` bundle：`package.json`（`dsh.bundle.patch`）+ `cordis.patch.yml` + `index.js`
  - 实现工作区检测（签名关键词 + 结构签名路径）、brief 渲染、任务路由、校验命令解析四个模块
  - 注册 `agent/pre-step` 用户消息层注入、四个工具、`/specweave` 命令、`specweave-protocol` 只读技能
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-3、AC-4、AC-5
- **Test Requirements**:
  - `rule` TR-2.1: 仓库根被识别为工作区，`apps/projects/vendor` 均不被识别为工作区根；证据：`findSpecweaveRoot` 用例输出
  - `rule` TR-2.2: brief 注入在第二次 pre-step 不重复、非工作区为 0 条、`reject` 原样透传；证据：注入用例输出
  - `rule` TR-2.3: 四个工具的输出全部通过各自声明的 `output.schema`；证据：测试 stub 的 `defineTool` 校验（违约即抛错）
- **Completion Evidence**:
  - `rule` TR-2.1：`node tests/bridge.test.js` 中「检测」4 例全通过（含新增回归防线「含启动协议但缺路由表的子区域不得被误判为工作区根」）
  - `rule` TR-2.2：「注入」3 例全通过
  - `rule` TR-2.3：「工具」3 例全通过（stub 按 schema 校验返回值，并已捕获过 `exists` 字段类型漂移风险）
- **Notes**: R1 评审后追加修复（均带回归用例）：① 乐观缓存改为「三态扫描 + 确认态」自愈模型（未落盘则下一步重新注入，扫描失败既不注入也不确认）；② `renderStartupBrief` 在 `maxBytes < FRAME_BYTES` 时返回空串；③ 首步空批次不注入（对齐宿主护栏）；④ 反向子串匹配加 ≥3 字符门槛；⑤ `specweave_protocol` 工作区外返回与工作区无关的兜底要点；⑥ `import.meta.dirname` 改为 `fileURLToPath(new URL('.', import.meta.url))`；⑦ 检测缓存加上限；⑧ 工具描述纠正为「工作区外仍返回匹配路径但不做存在性校验」。

## Task 3: 建立零依赖自测套件
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 以 Node 内建 `node:test` 编写断言套件，并用解析钩子把 `@deepseek-ai/*` 重定向到本地 stub
  - stub 需近似宿主真实行为：`defineTool` 校验输出 schema，`createUserMessage` 生成带 id 的用户消息
  - 覆盖检测、路由、校验命令、brief 边界、插件契约、注入幂等、工具 schema 一致性、SKILL.md 合规
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-3、AC-4
- **Test Requirements**:
  - `rule` TR-3.1: 套件必须能在未安装 dsh 的环境中全绿运行；证据：运行输出 `pass 34 / fail 0`
  - `rule` TR-3.2: 必须包含至少一条针对已修缺陷的回归用例（子区域误判）；证据：用例名与断言内容
- **Completion Evidence**:
  - `rule` TR-3.1：`ℹ tests 48 / ℹ pass 48 / ℹ fail 0`（直接运行形式；`--test` 形式因沙箱禁止派生管道子进程报 `spawn EPERM`，已在 README 注明）
  - `rule` TR-3.2：「检测：含「启动协议」但缺路由表的子区域不得被误判为工作区根」用例存在并通过；该缺陷是在首次运行测试时被真实捕获的
  - R1 评审后套件扩充至 47 项（新增：`output.render` 声明断言、上限小于框架时返回空串、工作区外兜底协议、首步空批次护栏、未落盘自愈 + 确认后 O(1)、扫描失败不注入不确认、短任务反向匹配防线）；「已注入不重复」用例改为**先落盘到伪 surface 再断言**（原用例断言的是被 R1 判定为缺陷的行为）

## Task 4: 编写 README 与 ACCESS 接入文档
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - README（开发者向）：组件表、目录结构、安装方式（`plugin_manager install_bundle`）、验证、设计原则、配置、已知限制
  - ACCESS（使用者向）：前提、三层接入、反模式、检验标准
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-4.1: README 必须给出不依赖安装的自测命令与装配后验证命令；证据：README「验证」章节
  - `rule` TR-4.2: ACCESS 必须写明"失败如何判别"而非只写成功路径；证据：ACCESS「检验标准」章节末段
- **Completion Evidence**:
  - `rule` TR-4.1：README 含 `node tests/bridge.test.js` 与 `dsh --profile "$env:DSH_PROFILE" --dump-config`
  - `rule` TR-4.2：ACCESS 末段给出「接入成功 = 三条同时成立 / 接入失败 = application 非 applied 或注入缺失」及排查方向

## Task 5: 仓库索引登记与看板刷新
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 在 `.agents/context-routing.md` 常规任务路由表登记 DSH 桥接入口
  - 在根 `AGENTS.md` 核心规范入口表登记该桥接目录
  - 运行 docgen 刷新 Spec 主题看板与全局总览
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 登记后 `python .agents/scripts/check-links.py --path <变更目录>` 无断链；证据：脚本输出
  - `rule` TR-5.2: 看板由 docgen 生成而非手写；证据：`docgen.py theme-dashboards` / `update-spec-readme` 执行输出
- **Completion Evidence**:
  - `rule` TR-5.1：`python .agents/scripts/check-links.py --path specweave-dsh-bridge` → 「校验通过: 所有链接均有效」（exit 0）；同命令对 spec 目录亦通过
  - `rule` TR-5.2：`python .agents/scripts/docgen.py theme-dashboards` → 「已更新 13 个主题看板」；`update-spec-readme` → 「已压缩 .trae/specs/README.md（6 KB，662 个 Spec）」；standards-tools 看板出现自动生成行 `| 1 | [add-dsh-specweave-bridge](add-dsh-specweave-bridge/spec.md) | ? 待启动 | ✓✗✗ |`（未手改标记区）
  - 索引登记：`.agents/context-routing.md` 常规任务路由表新增「DeepSeek Harness 宿主入口桥」行；根 `AGENTS.md` 核心规范入口表新增「🌉 DeepSeek Harness 入口桥」行

## Task 6: 装配层验证（真实 dsh profile）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 执行 `plugin_manager(action: "install_bundle", target: "<绝对路径>")`，读取 `application` 与 `warnings`
  - 在真实会话中验证注入、工具面与工具执行
- **Acceptance Criteria Addressed**: AC-6（并在过程中回归 AC-2、AC-3、AC-5）
- **Test Requirements**:
  - `rule` TR-6.1: 安装返回 `application: applied` 且 `warnings` 为空；证据：安装返回值
  - `rule` TR-6.2: 工作区内会话出现 `[SpecWeave 启动协议]` 注入，且 `specweave_route 复盘` 与 `specweave_status` 实机执行成功；证据：会话注入文本 + 工具输出
- **Completion Evidence**:
  - `rule` TR-6.1：首轮 `install_bundle` 返回 **`application: failed`**（`specweave-bridge (@specweave/dsh-bridge): failed to import`，根因 `ERR_MODULE_NOT_FOUND: Cannot find package '@deepseek-ai/schemastery'`）→ 按 FR-10 改为零宿主导入后，`set_bundle`（先禁用再启用）两次均返回 **`application: applied`、`warnings: []`**
  - `rule` TR-6.2：本会话 system-reminder 实际出现 `[SpecWeave 启动协议]` 注入文本；宿主下发四个 `specweave_*` 工具 schema；`specweave_route 复盘` 与 `specweave_status` 在本会话实机执行成功（返回工作区根 `C:\Users\admin\Desktop\Dao\flows\SpecWeave`）
  - 装配期新发现的缺陷：① 宿主包不可解析（F-01 之外的新约束，已固化为 FR-10 + 测试守卫「源码不得出现 `@deepseek-ai/` 导入」）；② **`output.render` 才是模型可见内容**，原 render 过于简略（路由只报条数、协议只报标题）→ 已改为承载答案本身（FR-11），并新增「render 输出必须承载答案」断言与真机复核
- **Notes**: 写 profile 属工作区外操作，已获用户指示执行。已安装的是 `link:` 依赖（指向本仓库目录），**源码更新后需重启 dsh 才会加载新的 JS 模块代**；当前会话加载的是修复 render 之前的生成代（注入与工具均正常，仅工具结果文案较简）。

## Task 7: 独立对抗性评审
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3、Task 4
- **Description**:
  - 以全新上下文（不共享实现过程）只读复核：契约贴合度、注入正确性、测试是否真实覆盖 AC、文档与实现是否一致
  - 评审结论与发现回写 `review.md`
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-3、AC-4、AC-5
- **Test Requirements**:
  - `rule` TR-7.1: 每条 AC 至少被一个检查点覆盖；证据：review.md 的 `Covers` 字段
  - `rule` TR-7.2: 评审必须独立复跑测试套件，不得只引用实现者结论；证据：评审过程的命令与输出
- **Completion Evidence**:
  - `rule` TR-7.1：review.md 含 CP-R1…CP-R8 + CP-U1/CP-U2 检查点，`Covers` 覆盖 AC-1…AC-5（AC-5 为 rubric，证据为插件契约清单 + README 设计原则 + R1–R4 结论）
  - `rule` TR-7.2：评审者四轮均独立复跑并核对 `test(` 与 `assert.` 计数（逐轮实测 `pass 27 / 25 / 34 / 35 / 37`），另用真实 `@deepseek-ai/dsh-tools` 编译注册四个工具、以只读探针复现每条结论；最终 **R4 = pass**
  - 四轮共 18 条发现全部闭环，其中 4 条固化为套件内的回归防线（子区域误判、注入自愈、2 字中文召回、文档数字漂移）
- **Notes**: 评审者是只读角色（四轮报告均声明未创建/修改/删除任何文件）。R1 = `fail` → R2 = `fail`（含一条由修复引入的回归）→ R3 = `pass` → R4 = `pass`；pass 之后的 P3 已闭环并补断言。

# Task Dependencies

- Task 2 ← Task 1
- Task 3 ← Task 2
- Task 4 ← Task 2
- Task 5 ← Task 4
- Task 6 ← Task 5（且需用户授权）
- Task 7 ← Task 3、Task 4
