# specweave-dsh-bridge — SpecWeave × DeepSeek Harness 入口桥

> 把 SpecWeave 工作区的 `AGENTS.md` + `.agents/` 规范容器接入 **DeepSeek Harness（dsh）** 会话入口：
> 会话一进入 SpecWeave 工作区就自动收到启动协议提醒，并获得任务路由、状态查询、提交前校验三类能力。
> 离开工作区时 **brief 注入完全静默**；工具、命令与技能是宿主级注册，在每个会话都可见，但工具会返回 `in_workspace: false`。

本目录是插件的**规范源码**（纳入版本控制）。安装由 dsh 自身的 `plugin_manager` 完成，**不需要**手工改写 profile 文件。

## 组件

| 组件 | 类型 | 作用 |
|---|---|---|
| `specweave_route` | 工具 | 任务关键词 → SpecWeave 规范入口路径（多命中 + 存在性校验 + 兜底路由表） |
| `specweave_status` | 工具 | 报告工作区根、子区域（apps/projects/vendor）、入口文件与产出物路径纪律 |
| `specweave_check` | 工具 | 返回提交前校验命令与判据（**不代为执行**，执行归会话沙箱与审批策略） |
| `specweave_protocol` | 工具 | 技能目录不可用时的协议兜底入口 |
| `/specweave` | 人机命令 | `status` / `route <任务>` / `skill <触发词>` / `help` |
| `specweave-protocol` | 只读技能 | 启动协议、内容敏感度分流、产出物路径纪律（内容取自本目录 SKILL.md） |
| 工作区技能提供方 | 技能 | 在插件作用域注册 provider，按 `options.cwd` 命中 SpecWeave 工作区时才把 `.agents/skills` 中**路由表引用的门面技能**作为候选给出，绕开失效的宿主 provider |
| `agent/pre-step` 注入 | 事件 | 在工作区内把启动协议 brief 注入**用户消息层**（不改 system prompt） |

## 目录结构

```
specweave-dsh-bridge/
├── package.json                    # bundle 清单：dsh.bundle.patch → cordis.patch.yml
├── cordis.patch.yml                # 装配补丁：插入 specweave-bridge 行（含可覆盖 config）
├── index.js                        # Cordis 插件入口：apply / inject / Config
├── lib/
│   ├── constants.js                # 路由表、签名常量、校验命令表（纯数据）
│   ├── detector.js                 # 工作区/子区域检测（AGENTS.md 签名 + 路由表结构标记）
│   ├── brief.js                    # 启动协议 brief 渲染（字节上限 + 框架转义）
│   ├── routes.js                   # 任务 → 规范路径解析与存在性校验
│   ├── skill-catalog.js            # 工作区技能扫描与 frontmatter 解析（绕开失效 provider）
│   ├── host-shims.js               # 宿主原语的本地等价实现（零宿主导入约束）
│   └── checks.js                   # 变更类型 → 提交前校验命令
├── skills/specweave-protocol/SKILL.md   # 协议技能正文（运行时注册的唯一真源）
├── locale/{zh,en}.json             # Plugin Manager 展示文案
└── tests/                          # 零依赖自测（宿主包由 stub-loader 重定向）
```

## 安装

在**已经装着 SpecWeave 仓库的 dsh 会话**里，对本目录的绝对路径执行一次 `plugin_manager`：

```
plugin_manager(action: "install_bundle", target: "<本目录绝对路径>")
```

- `target` 必须指向本目录（含 `package.json` 的绝对路径），由 `install_bundle` 负责包安装与 bundle 选择；
  **不要**手工写 profile 的 `package.json` / `cordis.patch.yml`，也不要手工跑 pnpm。
- 安装结果以返回值的 `application` 与 `warnings` 为准（`applied` 才算生效；新 bundle 可经 HMR 生效）。
- 安装后**新开会话**再验证（已存在的会话不重放历史注入）。

卸载：`plugin_manager(action: "remove_bundle", target: "@specweave/dsh-bridge")`。

## 验证

### 1. 仓库内自测（无需安装 dsh）

```powershell
cd specweave-dsh-bridge
node tests/bridge.test.js          # 直接运行（推荐）
node --test tests/bridge.test.js   # 标准 runner 形式
```

覆盖：工作区检测（含「子区域不得被误判为根」回归防线）、路由匹配与存在性校验、校验命令解析、
brief 框架与字节上限、插件契约（导出/工具/命令/技能注册）、pre-step 注入幂等与自愈、工具输出与
声明的 `output.schema` 一致性、**零宿主导入**与 schema 子集、SKILL.md frontmatter 合规、
三处文档与真实用例数一致。

> 若环境不能派生管道子进程（沙箱限制），`node --test` 会以 `spawn EPERM` 失败，请用直接运行形式。

### 2. 装配后在会话内验证

```
/specweave status          # 应报告工作区根与子区域
specweave_route 复盘        # 应返回 .agents/skills/retrospective-cmd/SKILL.md
specweave_status            # 应返回 in_workspace=true
```

### 3. 装配层验证（不改 live profile）

```powershell
dsh --profile "$env:DSH_PROFILE" --dump-config   # 打印合成后的 profile，确认 specweave-bridge 行存在
```

## 工作区技能为何由桥接层提供

宿主自带的 `dsh-skill-filesystem` 本应扫描 `<项目根>/.agents/skills`（rank 200）。但在桌面构建下实测：
该 provider 对本工作区**返回 0 个候选**——`.agents/skills` 里 164 项技能一个都进不了注册表，
`skill("seven-concepts-cmd")` 返回 `unknown or no longer available`，`/七概念` 之类手势自然全部失配。
（反证：桥接层用 `ctx.skills.register` 注册的技能**可以**被正常加载，说明注册与发布链路本身是好的。）

因此桥接层自行读盘，并以**插件作用域 provider** 供候选：

- 扫描 `<工作区根>/.agents/skills/*/SKILL.md`，解析 frontmatter 的 `name`/`description`；
- 只接受满足宿主约束 `^[a-z0-9]+(?:-[a-z0-9]+)*$` 的名称（目录里 12 项因大写/中文名被跳过）；
- `skillSelection: routes`（默认）只提供**路由表引用到的门面技能**，避免把 160+ 条塞进每个会话的技能目录；
- 候选由**插件作用域 provider** 提供：`list(options)` 用 `options.cwd` 判定工作区根，离开工作区即返回空候选；插件卸载时随 provider 一并释放。
- ⚠️ **禁止回到 `agent.ctx` 注册**：agent 作用域上下文解析不到 `skills` 服务，属性探测（`agentCtx?.skills === undefined`）会抛 `cannot get property "skills" without inject`；该监听器位于会话创建事务内，异常会让 `session/new` 整体失败（2026-09-30 实测：SpecWeave 工作区新建会话必失败，默认工作区正常）。可选服务一律走 `ctx.inject([...])`。

**中文触发词的边界**：DSH 技能名强制 ASCII kebab-case，`七概念` 永远不能作为技能名。
所以中文入口走命令面：`/specweave skill 七概念` → 解析出 `seven-concepts-cmd` → 把技能正文
`agent.inject` 排入下一步；模型侧则用 `specweave_route` 拿到路径后自行加载。

## 为什么不导入宿主包（重要约束）

`plugin_manager install_bundle` 把本包装进 profile 后，**包内不得 `import` 任何 `@deepseek-ai/*` 宿主包**：

- 宿主包只存在于 dsh 安装的 `app.asar` 内，磁盘上没有可链接的副本；
- profile 的 `node_modules` 只含被安装的包本身，Node 从包路径向上解析不到宿主包；
- 实测：带宿主 import 的版本安装后该行报 `specweave-bridge (@specweave/dsh-bridge): failed to import`
  （`ERR_MODULE_NOT_FOUND: Cannot find package '@deepseek-ai/schemastery'`）。

因此本插件是**自包含**的：工具定义直接写宿主支持的**原生 JSON Schema 子集**
（`type/oneOf/properties/required/additionalProperties/items/enum/const` + 注解），
user 消息用 [lib/host-shims.js](lib/host-shims.js) 中与宿主等价的最小实现构造
（行为取自宿主源码，见该文件注释），并且**不导出 `Config`**——声明 Config 需要 schemastery。
代价：row `config` 不再有 schema 校验；所有配置项在下方「配置」中逐项列出，且每项都有默认值。
测试套件含两条守卫：源码不得出现 `@deepseek-ai/` 导入、所有 schema 必须落在宿主支持的子集内。

## 设计原则

- **不改 system prompt**：启动协议 brief 经 `agent/pre-step` 折进用户消息层（紧随本步被 claim 的用户消息之后），
  宿主 system prompt 保持字节级不变，复用 prompt cache 前缀（对齐 Hermes 先例 `specweave-bridge-skeleton`）。
- **服务门控**：只硬依赖 `tools`；`commands`/`skills` 经 `ctx.inject` 可选挂载，宿主缺服务时插件仍可用（仅少对应能力）。
- **零越权执行**：桥接层不执行任何脚本；校验命令交由会话的 pwsh 工具执行，权限仍由沙箱与审批策略决定。
- **路由表可漂移检测**：命中路径在运行时会做存在性校验，缺失即标记 `stale` 并回退到 `.agents/context-routing.md`。
- **一键开关**：`enabled: false` 时插件完全不注册任何能力；`registerTools/registerCommand/registerSkill/injectBrief` 可分别关闭。

## 配置（profile patch 中按 id 覆盖）

```yaml
- id: specweave-bridge
  config:
    enabled: true            # 总开关
    injectBrief: true        # 启动协议 brief 注入
    registerTools: true      # 四个模型侧工具
    registerCommand: true    # /specweave 人机命令
    registerSkill: true      # specweave-protocol 只读技能
    maxBriefBytes: 4096      # brief 渲染上限（UTF-8 安全截断；低于 189 字节＝框架 61 + 最小正文 128 时禁用注入并告警一次）
    registerWorkspaceSkills: true   # 注册 .agents/skills 中的门面技能（绕开失效的宿主 provider）
    skillSelection: routes   # routes=只注册路由表引用的门面技能；all=注册目录下全部合格技能
    workspaceSkillsDir: ".agents/skills"
    signatureKeyword: "启动协议"
    signaturePaths: [".agents/context-routing.md"]
```

> ⚠️ Loader 的覆盖语义是**整段替换 config**，不是深合并——覆盖时必须重述所有需要保留的字段。

## 已知限制

- **只做入口，不做规范同步**：桥接层不复制 `.agents/` 规范内容；规范真源始终是仓库磁盘文件。
- **子区域判定基于目录前缀**：`apps/`、`projects/`、`vendor/` 之下即视为对应子区域，不校验该区域自身入口文件是否存在。
- **检测向上回溯上限 64 层**：更深的嵌套工作目录会静默判为「非工作区」（防御性上限，正常仓库深度远低于此）。
- **关键词匹配为双向子串（大小写不敏感）**：正向是「任务文本包含关键词」；反向是「关键词包含任务文本」，
  仅用于「链接 → 链接检查」这类更短的任务词，并按输入体裁设门槛——**含非 ASCII（中文等）时任意长度均启用反向匹配**
  （中文任务词常只有 2 个字），**纯 ASCII 则需 ≥3 字符**（挡掉单字母造成的大面积误命中）。
  因此短而泛的输入仍可能多命中；工具返回的是命中清单而非单一答案，请结合 `.agents/context-routing.md` 判断。
- **零宿主导入（硬约束）**：本包不 import 任何 `@deepseek-ai/*` 宿主包，也不导出 `Config`——见「为什么不导入宿主包」。
  代价是 row `config` 无 schema 校验：配置项以本文档为准，且每项都有默认值。
- **未在本机安装验证**：本包已通过仓库内 48 项自测，但**尚未**在本机 profile 中执行 `install_bundle`
  （写 profile 属工作区外操作，需单独批准）。装配层的 `application`/`warnings` 结果待安装时确认。
