# Tasks

- [x] Task 1: 创建 Zleap-Agent wiki 教程文档集主框架
  - [x] SubTask 1.1: 创建 `zleap-agent-wiki/README.md` 索引（H1 标题、YAML frontmatter、适用人群表、8 章快速导航表、内容快照声明、资源链接）
  - [x] SubTask 1.2: 创建 8 个章节文件骨架（`00-overview.md` ~ `08-faq-glossary.md`），每个含 H1 标题、YAML frontmatter、底部上一章/返回目录/下一章导航

- [x] Task 2: 编写项目概述与核心定位章节（00）
  - [x] SubTask 2.1: 阐述项目定位（workspace-first Agent Harness）、核心哲学"Workspace Is All Agents Need"、核心宣称与原理解读
  - [x] SubTask 2.2: 说明项目背景（版本 v0.3.3、仓库 Zleap-AI/Zleap-Agent、预览状态、License 未定）、亮点列表、核心概念初览（Workspace/Context/Memory/Skill）

- [x] Task 3: 编写核心架构与技术栈章节（01）
  - [x] SubTask 3.1: 讲解 monorepo 结构与构建工具（pnpm、TypeScript、Node 20+）
  - [x] SubTask 3.2: 逐一讲解 13 个 package 的职责（agent/core/store/ai/web/cli/gateway/tasks/host/runtime/avatar/desktop 等）
  - [x] SubTask 3.3: 说明后端存储（PostgreSQL + pgvector）与架构分层（模型层/运行时/会话服务/网关/存储）

- [x] Task 4: 编写 Workspace 隔离机制与上下文组装章节（02）
  - [x] SubTask 4.1: 讲解 Workspace 代码实现：`main`/`work` 空间、数据库为唯一真源、`when`/`notFor` 路由提示、`persona`、`toolIds`（引用 `packages/agent/src/workspaces/index.ts`、`packages/core/src/workspace.ts`）
  - [x] SubTask 4.2: 讲解 Kernel 从 `session` 空间经 `switchWorkspace(space, task)` 路由到子空间、Main→work 深度为 1（引用 `packages/agent/src/kernel/kernel.ts`）
  - [x] SubTask 4.3: 讲解 `assembleContext` 的 stable/semiStable/variable 三块组装与缓存断点、"变化的记忆永不进入缓存前缀"不变量（引用 `packages/core/src/context/assembly.ts`）
  - [x] SubTask 4.4: 提炼 1-2 条架构洞察（数据库真源、缓存前缀不变量）

- [x] Task 5: 编写分区记忆系统章节（03）
  - [x] SubTask 5.1: 讲解 person/event/experience 三类记忆分区与 A 线（people notes）+ B 线（core records）双线（引用 `packages/core/src/memory/orchestrator.ts`）
  - [x] SubTask 5.2: 讲解 prefetch 快速读取（无 LLM）与 recall 精排（LLM）的区别
  - [x] SubTask 5.3: 讲解 RRF（Reciprocal Rank Fusion）多路径召回融合算法（引用 `packages/store/src/core/rrf.ts`）
  - [x] SubTask 5.4: 讲解抽取管线（LLM 抽取器 → event + 实体，content_hash 幂等）（引用 `packages/store/src/core/extract.ts`）

- [x] Task 6: 编写 Skill / 工具 / 权限章节（04）
  - [x] SubTask 6.1: 讲解 Skill 机制（SKILL.md 入口、SkillRegistry、敏感性审计、token 预算、章节索引、调用策略、信任状态）（引用 `packages/core/src/skills.ts`）
  - [x] SubTask 6.2: 讲解工具权限模型 `request_approval` / `full_access`（引用 `packages/agent/src/permissions.ts`）
  - [x] SubTask 6.3: 讲解 MCP Runtime 与 MCP Secrets 机制（引用 `packages/agent/src/mcpRuntime.ts`、`mcpSecrets.ts`）

- [x] Task 7: 编写模型提供方与对外入口章节（05）
  - [x] SubTask 7.1: 讲解模型提供方抽象（OpenAI-compatible + Anthropic、ProviderRegistry/ModelRegistry、SSE 流式）（引用 `packages/ai/src/registry.ts`、`providers/`）
  - [x] SubTask 7.2: 讲解 Web UI（Next.js）与 CLI 入口、环境变量
  - [x] SubTask 7.3: 讲解 `ConversationService` 作为所有触发（web/tasks/IM）统一入口、inbound → reply → 流式回传数据流（引用 `packages/agent/src/conversation/service.ts`、`packages/avatar/src/inboundRun.ts`）

- [x] Task 8: 编写网关与定时任务章节（06）
  - [x] SubTask 8.1: 讲解 IM 网关（飞书/微信/飞书 CLI 适配器、ChannelSupervisor、worker、dedup）（引用 `packages/gateway/src/`）
  - [x] SubTask 8.2: 讲解定时任务服务（cron、queue、worker、service）（引用 `packages/tasks/src/`）
  - [x] SubTask 8.3: 说明二者如何接入 `ConversationService`

- [x] Task 9: 编写快速上手指南章节（07）
  - [x] SubTask 9.1: 环境要求、安装依赖、启动 Web UI、配置模型、CLI 使用（与 README 一致）
  - [x] SubTask 9.2: 常用命令表与环境变量表（引用 README 与 package.json）

- [x] Task 10: 编写 FAQ 与术语表章节（08）
  - [x] SubTask 10.1: 编写至少 6 个 FAQ（适合什么用户、是否需要本地模型、与单一大 prompt 的区别、Workspace 之间如何协作、是否支持飞书/微信、如何导入 Skill 等）
  - [x] SubTask 10.2: 编写 ≥10 个核心术语表（Workspace、Context Layout、Person/Event/Experience Memory、Skill、RRF、MCP、Gateway、Turn Loop、Approval、main/work 等）

- [x] Task 11: 在知识库索引中登记新文档
  - [x] SubTask 11.1: 在 `.agents/docs/knowledge/learning/03-agent-platforms-tools/README.md` 的对应类目下追加 Zleap-Agent 学习 wiki 条目，包含文档标题与相对路径链接

- [x] Task 12: 验证与质量检查
  - [x] SubTask 12.1: 检查所有章节文件命名符合 kebab-case 规范（`00-*.md`、`README.md`）
  - [x] SubTask 12.2: 人工检查 README 目录导航锚点全部可跳转、每章底部导航完整、8 章内容完整、FAQ ≥6 个问题、术语表 ≥10 个术语、架构洞察 5-8 条且可追溯源码路径

# Task Dependencies
- Task 1 是所有后续任务的前置（先有文档骨架才能填充内容）
- Task 2、Task 3、Task 4、Task 5、Task 6、Task 7、Task 8 可在 Task 1 完成后并行编写（不同章节相互独立）
- Task 9 依赖 Task 1（需文档路径稳定）且内容与 Task 2 概览呼应
- Task 10 依赖各核心章节完成（FAQ/术语表需引用各章概念）
- Task 11 依赖 Task 1 完成（需要文档路径稳定后再登记索引）
- Task 12 依赖所有前置任务完成