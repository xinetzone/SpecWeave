---
title: "DeepSeek Harness 入口桥：让 AGENTS.md + .agents/ 成为 DSH 会话入口"
status: "completed"
id: "add-dsh-specweave-bridge"
source: "用户需求：把 AGENTS.md + .agents/ 的组合作为 DeepSeek Harness 的入口；对齐既有 Hermes 桥接先例 specweave-bridge-skeleton"
---

# DeepSeek Harness 入口桥 - Product Requirements Document

> **主题目录**: `.trae/specs/standards-tools/`（归入理由：本主题归入条件含「IDE/开发环境、CI/CD 的适配配置」与「构建、测试、部署工具链的配置优化」；本 spec 是 DSH 宿主侧适配配置，同主题已有 `optimize-trae-project-adaptation` 这一 IDE 适配先例。同类 Hermes 集成位于 `core-foundation`，但其属「从零建立新子系统」，本次是对既有 DSH 宿主做入口适配。）
> **内容敏感度**: 公开内容（SpecWeave 为公开仓库，本 spec 与产出物均入仓库 `specweave-dsh-bridge/`）
> **关联既有资产**: `specweave-bridge-skeleton/`（Hermes 桥接先例）、`.trae/specs/core-foundation/hermes-specweave-integration/`（同构蓝图）、`.trae/specs/okf-wiki-ecosystem/deepseek-harness-wiki/`（DSH 知识底座）

## Overview

- **Summary**：为 DeepSeek Harness（下称 dsh）新增一个 Host 侧桥接插件 `@specweave/dsh-bridge`，把 SpecWeave 工作区的 `AGENTS.md` + `.agents/` 规范容器变成 dsh 会话的入口：进入工作区自动注入启动协议 brief，并提供任务路由、状态查询、提交前校验与协议兜底四类能力。
- **Purpose**：消除"在 dsh 里工作却不知道 SpecWeave 规范在哪"的入口断点。dsh 原生已能把 `AGENTS.md` 作为工作区指令加载，但 `.agents/` 内部的规范路由、校验门禁与产出物路径纪律没有任何宿主侧入口。
- **Target Users**：在 dsh 中处理 SpecWeave 任务的使用者（人）与其会话中的智能体（模型）。

## Goals

- **G1**：会话工作目录位于 SpecWeave 工作区时，第一步即获得启动协议 brief（用户消息层注入，system prompt 字节级不变）。
- **G2**：提供"任务关键词 → 规范入口路径"的运行时路由，含多命中、存在性校验与兜底入口。
- **G3**：提供工作区状态与产出物路径纪律查询，覆盖 `apps/projects/vendor` 子区域。
- **G4**：提供提交前校验命令清单（只回答"跑什么"，不代为执行）。
- **G5**：把 brief 注入限定在工作区内（工作区外零注入），且各能力可分别关闭、总开关可一键关闭；
  工具/命令/技能按宿主级注册在每个会话可见，工作区外工具明确返回 `in_workspace: false`。

## Non-Goals

- **NG1**：不复制、不缓存、不同步 `.agents/` 规范内容（规范真源始终是仓库磁盘文件）。
- **NG2**：不代为执行 `.agents/scripts/` 下的校验脚本（执行归会话沙箱与审批策略）。
- **NG3**：不修改 dsh 本体、不修改既有 Hermes 桥接 `specweave-bridge-skeleton/`。
- **NG4**：不在本仓库内写入或改写 dsh profile 文件（安装由 `plugin_manager install_bundle` 完成）。

## Background & Context

dsh 的 standard preset 已挂载 `@deepseek-ai/dsh-agent-instructions`，会加载 `$DSH_HOME/AGENTS.md` 与项目根到 cwd 的 `AGENTS.md`/`CLAUDE.md` 链——**AGENTS.md 入口天然成立**。但实测确认两处断点：

1. `@deepseek-ai/dsh-skill-filesystem` 虽然默认扫描 `<项目根>/.agents/skills`（rank 200），本机桌面会话的技能目录为空：
   实测 `skill` 工具对 `load-specweave`、`git-commit`、`dsh-probe` 三个名称均返回 `unknown or no longer available`，
   且派生的全新子会话同样无 `<available_skills>` 目录；磁盘上 `~/.agents/skills`（25 个合法技能）与
   `.agents/skills`（164 项）均存在且 frontmatter 合法。结论：**不能把入口能力押在技能目录上**。
2. dsh 有 `commands` 注册表但**没有任何文件系统命令提供方**，`.agents/commands/*.md` 无法自动成为斜杠命令。

此外 `.agents/skills` 中 12 个技能的 `name` 违反 dsh 的 `^[a-z0-9]+(?:-[a-z0-9]+)*$` 规则
（`TRAE-*` 10 个、`天眼一下`、以及 3 个标题式名称），即使 provider 恢复也会被静默丢弃——本 spec 记录该事实，
但**不**在本次改动范围内修名（属独立治理项）。

## Functional Requirements

- **FR-1**：工作区检测 SHALL 同时要求 ① `AGENTS.md` 首部包含签名关键词「启动协议」；② 至少一个签名路径存在（默认 `.agents/context-routing.md`）。仅凭关键词不得认定工作区根。
- **FR-2**：插件 SHALL 在 `agent/pre-step` 瀑布监听中，把启动协议 brief 作为 user 角色消息折进本步，插入位置紧随本步被 claim 的用户消息之后；决策对象必须展开（`{...decision, messages}`）以保留 `startsRequestSeries` 等字段。
- **FR-3**：brief 注入 SHALL 幂等——同一会话同一工作区根只注入一次；会话日志回放（resume）后不得重复注入。
- **FR-4**：插件 SHALL 注册 `specweave_route`、`specweave_status`、`specweave_check`、`specweave_protocol` 四个工具，且每个工具都必须声明 `output.schema` 与 `output.render`。
- **FR-5**：`specweave_route` SHALL 对命中路径做存在性校验，缺失项标记 `stale` 并在返回中给出兜底入口 `.agents/context-routing.md`。
- **FR-6**：插件 SHALL 注册 `/specweave` 人机命令，支持 `status` / `route <任务>` / `help` 三个子命令与未知子命令的错误提示。
- **FR-7**：插件 SHALL 注册只读技能 `specweave-protocol`，其正文从 `skills/specweave-protocol/SKILL.md` 读取（单一真源，不做内容复制）。
- **FR-8**：插件 SHALL 只硬依赖 `tools`；`commands`、`skills` 缺失时仍可加载，仅少对应能力。
- **FR-9**：`enabled: false` 时插件 SHALL 不注册任何工具、命令、技能与事件监听。
- **FR-10**：插件 SHALL NOT 导入任何 `@deepseek-ai/*` 宿主包，SHALL NOT 导出 `Config`——profile 安装的 bundle 无法解析宿主包（宿主包仅存在于 dsh 安装的 `app.asar` 内），一旦导入该行即以 `failed to import` 激活失败。工具定义 SHALL 直接使用宿主支持的原生 JSON Schema 子集。
- **FR-11**：工具的 `output.render` SHALL 承载答案本身（命中的规范路径、协议正文、可执行校验命令），因为宿主的 `output.render` 返回值**就是**进入模型历史的工具结果内容。

## Non-Functional Requirements

- **NFR-1 提示词预算**：brief 渲染受 `maxBriefBytes` 约束（默认 4096 字节，低于 `FRAME_BYTES + MIN_BODY_BYTES` 时禁用注入并一次性告警），UTF-8 安全截断，且不得切断多字节字符。
- **NFR-2 前缀稳定**：实现不得注册 system prompt 段落或监听 `system-prompt/assemble`（保证宿主 system prompt 字节级不变）。
- **NFR-3 可测**：插件目录的测试 SHALL 无需安装 dsh、也无需任何 stub 解析钩子即可运行（插件零宿主导入，测试直接 import 真实模块）。
- **NFR-4 静默降级**：检测与路由的任何 I/O、权限异常 SHALL 静默降级为"非工作区/未命中"，不得影响宿主会话。
- **NFR-5 可配置**：签名关键词、签名路径、brief 上限与各能力开关 SHALL 可由 row `config` 覆盖，且每项都有默认值（因不导出 `Config`，配置契约以 README 为准）。

## Constraints

- **Technical**：dsh 插件必须是 ESM 包，`package.json` 声明 `dsh.bundle.patch`；入口导出 `apply`/`inject`；**不得导入宿主包、不得导出 `Config`**（见 FR-10）；工具 `parameters` 与 `output.schema` 使用宿主支持的**原生 JSON Schema 子集**（`type/oneOf/properties/required/additionalProperties/items/enum/const` + 注解），不声明依赖。
- **Business**：本仓库为公开内容（标准工作流），产出物入仓库 `specweave-dsh-bridge/`，文档索引登记入 `AGENTS.md` 与 `.agents/context-routing.md`。
- **Dependencies**：无新增第三方依赖；测试仅用 Node 内建能力。
- **协作边界**：写入 dsh profile 属工作区外操作，须单独获得用户批准；本次交付**止于仓库内**。

## Assumptions

- dsh 的 desktop/web 会话由 standard preset 组合，`tools` 服务恒可用。
- 会话工作目录（`agent.session.header.cwd`）足以代表工作区位置。
- SpecWeave 工作区根可由「AGENTS.md 含签名关键词 + `.agents/context-routing.md` 存在」唯一识别（已用磁盘实测验证：`apps/`、`projects/`、`vendor/` 三个子区域均含关键词但均无路由表）。

## Acceptance Criteria

### AC-1: 工作区检测的精确性与抗误判
- **Type**: `rule`
- **Given**: 仓库根与 `apps/`、`projects/`、`vendor/` 三个子区域目录
- **When**: 分别调用 `isSpecweaveWorkspace` 与 `findSpecweaveRoot`
- **Then**: 仓库根返回 true；三个子区域均返回 false，且 `findSpecweaveRoot` 从任一子区域向上回溯得到仓库根
- **Pass Condition**: 四个断言全部成立，且子区域检测 `detectSubregion` 正确返回 `apps`/`projects`/`vendor`
- **Evidence**: `tests/bridge.test.js` 中「检测」相关 4 个用例通过输出

### AC-2: 注入的层次、幂等、自愈与静默
- **Type**: `rule`
- **Given**: 一个 SpecWeave 工作区 cwd 与一个非工作区 cwd；以及「已落盘」「未落盘」「会话日志扫描失败」三种会话状态
- **When**: 触发 `agent/pre-step` 监听器，并分别改变会话日志可见性
- **Then**: ① 首次返回 1 条带 `source.kind === 'specweave-bridge'` 的消息并插在被 claim 的用户消息之后（`startsRequestSeries` 保留）；② 日志可见该消息后不再注入，且不再扫描日志；③ 日志不可见时下一步**重新注入（自愈）**而非永久静默；④ 扫描抛错时本轮既不注入也不置为已注入（下一步重试）；⑤ 首步空批次不注入；⑥ 非工作区原样返回；⑦ `reject` 决策原样透传
- **Pass Condition**: 上述 7 项断言全部成立，且注入文本包含 `[SpecWeave 启动协议]` 与 `<system-reminder>` 框架
- **Evidence**: `tests/bridge.test.js` 中「注入」6 个用例通过输出

### AC-3: 工具面完整、输出与声明一致、兜底可用
- **Type**: `rule`
- **Given**: 插件在仅含 `tools` 服务的上下文中加载
- **When**: 断言已注册工具名清单与每个工具的 `output.schema`/`output.render`，并逐一执行四个工具（含工作区外执行）
- **Then**: 工具名集合恰为 `{specweave_check, specweave_protocol, specweave_route, specweave_status}`；每个工具都声明 `output.schema` 与 `output.render`；每次执行的返回值通过其声明的 schema 校验；`specweave_protocol` 在工作区外仍返回**非空**的与工作区无关的协议要点
- **Pass Condition**: 名称集合相等、render/schema 均为声明项、四次执行无 schema 违规、工作区外 protocol 非空
- **Evidence**: `tests/bridge.test.js` 中「注册」「工具」相关 7 个用例通过输出

### AC-4: 服务门控与总开关
- **Type**: `rule`
- **Given**: 上下文只提供 `tools` 服务；以及配置 `enabled: false`
- **When**: 分别加载插件
- **Then**: 前者注册 4 个工具、0 个命令、0 个技能；后者工具/命令/技能/事件监听均为 0
- **Pass Condition**: 两组数量断言全部成立
- **Evidence**: `tests/bridge.test.js` 中「服务门控」「总开关」2 个用例通过输出

### AC-5: 宿主原语的正确使用（可维护性维度）
- **Type**: `rubric`
- **Dimension**: 对 dsh 插件契约的贴合度与升级稳定性
- **Scale**: 1-5
- **Anchors**: 1 = 使用未声明依赖的服务、手工改写 profile、或直接监听 `system-prompt/assemble` 改文本；3 = 服务声明正确但使用强机制（system prompt 段落）注入内容，或输出 schema 缺失；5 = 只硬依赖 `tools`、可选服务走 `ctx.inject`、内容经用户消息层注入、每个工具声明 `output.schema` + `render`、配置整段替换语义在文档中明示
- **Pass Threshold**: >= 4
- **Evidence**: `index.js` 的 `inject`/`Config`/注册调用清单 + README「设计原则」章节 + 独立评审 R1 结论

### AC-6: 装配可用（在真实 dsh profile 中）
- **Type**: `rule`
- **Given**: 已通过 `plugin_manager install_bundle` 把本包装入当前 profile 的 dsh 实例
- **When**: 读取安装返回的 `application`，并观察一个工作区内会话的注入与工具面
- **Then**: ① 返回 `application: applied` 且 `warnings` 为空；② 该会话第一步出现 `[SpecWeave 启动协议]` brief；③ 四个 `specweave_*` 工具出现在工具面且 `parameters` 被宿主接受；④ 工具可实际执行并返回工作区根与命中的规范路径
- **Pass Condition**: 四项全部观察到
- **Evidence**: `plugin_manager set_bundle` 两次返回 `application: applied`（`warnings: []`）；本会话收到注入 brief；宿主下发四个工具的 schema 更新；`specweave_route 复盘` / `specweave_status` 实机执行成功

## Open Questions

- [ ] 已安装的 bundle 是 `link:` 到仓库目录，源码更新后需**重启 dsh** 才会加载新的 JS 模块代（`set_bundle` 重挂载不会重新导入模块）；这是宿主既有语义，已写入 README 与 ACCESS。
- [ ] `.agents/skills` 中 12 个非法技能名的治理（是否统一改为 kebab-case）是否单独立项。
- [ ] dsh 技能目录为空的根因已被装配验证收窄：插件注册的 runtime skill 生效后，`skill("specweave-protocol")` 可加载且目录只含该条——说明**目录发布链路本身正常**，问题在 `dsh-skill-filesystem` 对本工作区 `.agents/skills`（164 项）**返回了 0 个候选**（若 provider 快照不完整，消费方会整体不发布，不会只发一条）。建议后续用 `cordis_inspect_query` 检查该行的 provider 根解析，或在 DSH 上游反馈。
- [ ] 根级宿主集成目录的 frontmatter 义务未定：`check-frontmatter.py` 在被显式指向本目录与既有 `specweave-bridge-skeleton/` 时，两者**同样**各报 2 处「缺少 id / x-toml-ref」，而 `.meta/toml/` 目前只镜像 `.agents/`、`.trae/`、`apps/`、`docs/`、`projects/`，根级目录无 TOML 归属。本次沿用既有先例未补，建议单列治理项决定「根级目录是否纳入元数据分层」。
