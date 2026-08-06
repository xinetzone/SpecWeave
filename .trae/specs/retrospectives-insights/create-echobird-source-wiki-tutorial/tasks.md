# EchoBird 源码级深度学习与 Wiki 教程文档 - 实施计划

## [x] Task 1: R 阶段事实采集（源码 + 官网）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 系统采集 EchoBird 本地源码事实（只读，不修改源码）：
    - 前端 `src/pages/`：ModelNexus / LocalServer / AppManager / MyProjects / MotherAgent / Skills / AiPulse / AiCareer / Feedback
    - 后端 `src-tauri/src/services/`：model_manager / tool_manager / local_llm / codex_proxy / anthropic_proxy / agent_loop / agent_tools / skill_manager / usage_providers / ssh / ai_career
    - 数据层：`src/data/modelDirectory.json`（providers/relays 结构）、`src/data/officialEndpoints.ts`
    - 工具注册表：`tools/*/config.json` + `paths.json` 结构
    - 入口：`src-tauri/src/lib.rs`、`src-tauri/Cargo.toml`（依赖与版本）
  - 通过官网 https://echobird.ai/# 采集产品定位与功能描述
  - 产出事实清单（供后续章节引用），**G1 质量门：事实无因果推断词**
- **Acceptance Criteria Addressed**: [AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 采集覆盖前端页面、后端服务、数据层、工具注册表、入口
  - `human-judgement` TR-1.2: 采集内容为客观事实，无因果推断词
  - `programmatic` TR-1.3: 事实交叉验证（源码路径与描述一致）

## [x] Task 2: 创建 echobird-wiki 目录骨架与 README 索引
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `.agents/docs/knowledge/learning/03-agent-platforms-tools/echobird-wiki/` 创建目录骨架
  - 创建 README.md：目录导航、章节索引、学习路径、版本信息
  - 各章节文件（00-11）使用 YAML frontmatter（MDI v1.0），文件名 kebab-case 纯英文
  - **格式约束**：先读取同目录 eve-wiki/README.md 与 volcengine-agentkit-wiki/README.md 确认实际格式（frontmatter 风格、链接格式、章节结构），以其为权威标准
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: 目录与文件结构符合规范
  - `programmatic` TR-2.2: frontmatter 使用 YAML（--- 分隔）
  - `human-judgement` TR-2.3: README 索引链接完整可跳转

## [x] Task 3: 编写 00-overview 与 01-product-positioning 章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 00-overview.md：项目概述、核心定位、技术栈、版本信息
  - 01-product-positioning.md：产品定位（解决 60% 用户安装配置痛点）、核心价值（配置一次到处可用）、与概念层文章版 echobird-wiki.md 的关系
- **Acceptance Criteria Addressed**: [AC-1, AC-3]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 概述准确反映项目定位与技术栈
  - `human-judgement` TR-3.2: 定位章节与技术源码事实一致

## [x] Task 4: 编写 02-architecture 技术架构章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 解析 Tauri + Rust 前后端分层架构
  - 前端结构：src/pages、src/components、src/stores、src/data、src/utils
  - 后端结构：src-tauri/src/services、commands、models、utils
  - 入口 lib.rs 的初始化流程（单实例、窗口管理、托盘、插件注册、Codex Proxy 启动、孤儿进程清理）
  - 依赖清单（Cargo.toml 关键依赖）
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 前后端分层解析准确
  - `human-judgement` TR-4.2: 入口初始化流程描述准确
  - `human-judgement` TR-4.3: 模块划分清晰

## [x] Task 5: 编写 03-model-nexus 模型中心章节
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 解析 modelDirectory.json 结构：providers（baseUrl/anthropicUrl/modelId/modelIds/region）、relays
  - 模型服务商清单（小米/DeepSeek/GLM/Kimi/OpenAI/火山引擎等 18+）
  - "配置一次到处可用"的实现机制：Model Nexus 与工具、场景的绑定流程
  - officialEndpoints.ts 官方端点恢复机制
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-5.1: modelDirectory.json 结构解析准确
  - `human-judgement` TR-5.2: 模型服务商清单完整
  - `human-judgement` TR-5.3: 配置一次到处可用机制说明清楚

## [x] Task 6: 编写 04-core-scenarios 四大核心场景章节
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 场景一·安装修复 Agent：对话式安装与排查，前端（MotherAgent/AppManager）+ 后端（tool_manager/agent_tools/auto_fix）
  - 场景二·一键本地大模型：LocalServer 页面 + local_llm 服务
  - 场景三·我的 AI 项目：MyProjects 页面 + myProjectsStore
  - 场景四·应用管理器：AppManager 页面 + toolsStore + tool_config_manager
  - 每个场景包含：功能说明、源码实现、操作流程、应用价值
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 四个场景每个都有源码实现解析
  - `human-judgement` TR-6.2: 前端页面与后端服务对应关系准确

## [x] Task 7: 编写 05-local-llm 本地大模型章节
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 解析 services/local_llm/server.rs：start_server 引擎选择（vLLM/SGLang/llama.cpp）、命令构建
  - gpu.rs CUDA/GPU 检测
  - model_store.rs 模型下载、settings.rs 配置、pid_file.rs 进程管理
  - proxy.rs 本地代理
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 引擎选择逻辑解析准确
  - `human-judgement` TR-7.2: GPU 检测说明清楚
  - `human-judgement` TR-7.3: PID 进程管理说明清楚

## [x] Task 8: 编写 06-codex-proxy Codex 代理章节
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 解析 services/codex_proxy/server.rs：axum 绑定 127.0.0.1:53682、spawn_proxy_task
  - protocol_converter.rs：Responses↔Chat 协议转换
  - vendors/：GLM/Qwen/MiMo 厂商适配
  - stream_handler.rs 流式处理、session_store.rs 会话存储、config_manager.rs 配置
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 端口绑定与代理启动解析准确
  - `human-judgement` TR-8.2: 协议转换逻辑说明清楚
  - `human-judgement` TR-8.3: 多厂商适配说明清楚

## [x] Task 9: 编写 07-tool-registry 工具注册表章节
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 解析 tools/ 目录下 25+ 工具（claudecode/codex/kimicode/openclaw/trae/traecn 等）
  - config.json + paths.json 结构
  - services/tool_manager.rs、tool_config_manager.rs、tool_patcher.rs
  - officialEndpoints.ts 官方端点恢复
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 工具清单完整
  - `human-judgement` TR-9.2: config.json/paths.json 结构解析准确
  - `human-judgement` TR-9.3: 官方端点恢复机制说明清楚

## [x] Task 10: 编写 08-advanced-pages 高级功能章节
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 概述 AiPulse/AiCareer/MotherAgent/Skills/SSH/Feedback 等高级功能模块
  - 各模块的前端页面与后端命令对应关系
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 高级功能模块概述完整
  - `human-judgement` TR-10.2: 前后端对应关系准确

## [x] Task 11: 编写 09-quickstart 快速上手章节
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 四步快速上手：安装 EchoBird（官网脚本/手动下载）→ 安装 Agent → 配置模型中心 → 绑定模型并启动
  - 结合源码给出的实际配置路径与注意事项
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `human-judgement` TR-11.1: 四步指南完整
  - `programmatic` TR-11.2: 安装命令格式正确

## [x] Task 12: 编写 10-comparison-trends 与 11-faq-glossary 章节
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 10-comparison-trends.md：与同类工具对比、行业趋势洞察（可选）
  - 11-faq-glossary.md：FAQ（≥8 问）+ 术语表（≥15 个核心术语，含一句话白话解释）
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `human-judgement` TR-12.1: FAQ ≥8 问
  - `human-judgement` TR-12.2: 术语表 ≥15 个术语，每术语一句话白话解释（禁止用术语解释术语）

## [x] Task 13: 更新 03-agent-platforms-tools/README.md 索引
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 在子 Wiki 索引表中新增 echobird-wiki/ 目录条目（文件数、核心主题）
  - **格式约束**：先读取现有 README.md 表格格式，保持行结构一致
- **Acceptance Criteria Addressed**: [AC-12]
- **Test Requirements**:
  - `programmatic` TR-13.1: README.md 新增 echobird-wiki 条目
  - `human-judgement` TR-13.2: 摘要准确概括内容

## [x] Task 14: 全量验证（文件名/链接/frontmatter 一致性）
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 运行 `python .agents/scripts/check-filename-convention.py` 验证文件名合规
  - 运行 `python .agents/scripts/check-links.py` 验证链接有效性
  - 校验各文件 frontmatter 字段一致性（title/source/date/tags）
  - 校验 12 个 AC 全部满足
- **Acceptance Criteria Addressed**: [AC-1 至 AC-12]
- **Test Requirements**:
  - `programmatic` TR-14.1: 文件名命名规范检查通过
  - `programmatic` TR-14.2: 链接有效性检查通过
  - `human-judgement` TR-14.3: 12 个 AC 全部满足

## [x] Task 15: 原子提交（C 阶段）
- **Priority**: high
- **Depends On**: Task 14
- **Description**:
  - 使用 atomic-commit-cmd 进行原子提交，单一职责，Conventional Commits 规范
  - 提交信息如 `docs(wiki): 新增 EchoBird 源码级学习 Wiki 教程`
- **Acceptance Criteria Addressed**: [AC-1 至 AC-12]
- **Test Requirements**:
  - `programmatic` TR-15.1: 提交信息符合 Conventional Commits 规范
  - `programmatic` TR-15.2: 变更单一职责，提交后工作区干净

# Task Dependencies
- Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8 → Task 9 → Task 10 → Task 11 → Task 12 → Task 13 → Task 14 → Task 15
- 全部任务为串行依赖（每个 Task 依赖前一个 Task 完成后才能开始）
- Task 14（验证）依赖所有前序产出；Task 15（提交）依赖验证通过