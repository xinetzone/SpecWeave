# AI Agent 源码深度 OKF Wiki 教程 - 实施计划

## Task 1: 目录结构初始化与旧 bundle 重组
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将现有 `bundles/ai-agent/ai-agent/` 迁移为 `bundles/ai-agent/ai-agent-fundamentals/`（跨项目架构基础）
  - 在 `bundles/ai-agent/` 下创建 12 个项目 bundle 目录骨架：hermes-agent、veadk-python、zleap-agent、deepseek-harness、intelligent-terminal、cordis、second-me、agency-agents、agency-agents-app、anthropics-skills、book-to-skill、i-have-adhd
  - 每个 bundle 下创建 concepts/、examples/、references/ 子目录
  - 更新 fundamentals bundle 的 index.md 标题和描述，添加到各项目 bundle 的导航链接
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `rule` TR-1.1: 13 个 bundle 目录（12 项目 + 1 fundamentals）均存在且包含 concepts/examples/references 子目录；证据：目录列表
  - `rule` TR-1.2: fundamentals bundle 从旧 ai-agent 迁移完成，旧目录清理；证据：目录列表
- **Notes**: mindverse/ 下实际项目为 Second-Me，bundle 名用 second-me；Zleap-Agent 目录名大小写为 zleap-agent

## Task 2: R 阶段 — 第一批项目源码事实采集（并行 Group A+B+C）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 general_purpose_task 并行委派 6 个项目的 R 阶段事实采集：
    - Subtask 2a: hermes-agent（Python，802 文件）——深度读取 agent/、tools/、providers/、plugins/、gateway/、skills/、acp_adapter/ 核心模块，提取类名、方法签名、继承关系、数据流事实，编号 F-xxx
    - Subtask 2b: veadk-python（Python+TS）——深度读取 veadk/ 核心包（agent.py、runner.py、memory/、models/、tools/）、frontend/src/、examples/，提取核心类和函数事实
    - Subtask 2c: Zleap-Agent（TypeScript monorepo）——深度读取 packages/agent、packages/core、packages/ai、packages/cli、packages/store、packages/host 核心包，提取类/接口/函数事实
    - Subtask 2d: deepseek-harness（TypeScript monorepo）——深度读取 packages/core（agent/tools/session/scope）、packages/llm、packages/mcp、packages/acp、packages/sdk、packages/fs、packages/shell、packages/lsp 核心包
    - Subtask 2e: cordis（TypeScript）——深度读取 packages/core/src（context.ts、fiber.ts、events.ts、service.ts、registry.ts）、packages/hmr、packages/loader
    - Subtask 2f: second-me（Python+TS）——深度读取 lpm_kernel/L0、L1、L2（data_pipeline、dpo、train.py、memory_manager.py）、api/domains/
  - 每个子任务产出：编号事实清单（零推测，每个事实标注源文件路径和行号），写入 `<bundle>/.spec/facts.md`
- **Acceptance Criteria Addressed**: AC-3（事实基础）
- **Test Requirements**:
  - `rule` TR-2.1: 每个项目 facts.md 存在且包含 ≥30 条编号事实（Tier 1 ≥50 条，Tier 2 ≥30 条）；证据：文件行数统计
  - `rule` TR-2.2: 事实无推断性表述（不出现"用于"/"目的是"/"设计为"）；证据：关键词 Grep
  - `rule` TR-2.3: 每个事实标注源码文件路径；证据：Grep 验证路径格式
- **Notes**: 每子任务独立上下文，不共享会话状态；提供完整的 OKF 格式规范和 R 阶段 prompt 模板

## Task 3: R 阶段 — 第二批项目源码事实采集（并行 Group D+E）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 general_purpose_task 并行委派 6 个项目的 R 阶段事实采集：
    - Subtask 3a: intelligent-terminal（C++）——只聚焦 Agent/ACP 相关模块：src/cascadia/（Agent 集成）、src/host/ft_host/（helper 进程）、识别 COM 服务器、Named Pipe 通信、OSC 133 相关文件
    - Subtask 3b: agency-agents（Markdown）——分析 315 个 md 文件的组织结构、SKILL.md 格式、persona 模板、部门分类体系、2 个 Python 脚本
    - Subtask 3c: agency-agents-app（Svelte+Rust/Tauri）——读取 src/lib/components、src/lib/stores、src/lib/data、src-tauri/src/，分析 Svelte store 模式、Tauri 命令、组件架构
    - Subtask 3d: anthropics-skills（Python+MD）——读取 skills/ 目录结构、Python 参考实现代码、SKILL.md 模板定义
    - Subtask 3e: book-to-skill（Python）——读取 book_to_skill/ 包核心模块、scripts/、tools/，分析四层产出流水线
    - Subtask 3f: i-have-adhd（MD+Shell）——读取 skills/ 目录、hooks/、scripts/，分析 10 条规则实现机制
  - 产出同 Task 2 格式
- **Acceptance Criteria Addressed**: AC-3（事实基础）
- **Test Requirements**:
  - `rule` TR-3.1: 每个项目 facts.md 存在且事实数量达标（Tier 1 ≥50，Tier 3 ≥15）；证据：行数统计
  - `rule` TR-3.2: intelligent-terminal 事实仅限 Agent/ACP 相关模块，不覆盖终端渲染等非 Agent 代码；证据：事实文件路径检查
  - `rule` TR-3.3: 事实无推断性表述；证据：关键词 Grep
- **Notes**: intelligent-terminal 是 C++ 超大规模项目，R 阶段只探索 Agent 相关子目录

## Task 4: I 阶段 — 架构洞察与知识地图设计
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 基于各项目 facts.md，为每个项目提炼 3-5 个核心架构洞察（陈述+证据+反常识+行动四元组）
  - 设计每个项目的知识地图：concepts 文档列表与依赖关系、examples 文档选题、学习路径
  - 确定每篇 concept 覆盖哪些 F-xxx 事实
  - 产出：每个 bundle 的 `.spec/insights.md` 和 `.spec/knowledge-map.md`
- **Acceptance Criteria Addressed**: AC-6（架构深度基础）
- **Test Requirements**:
  - `rule` TR-4.1: 每个项目 insights.md 包含 ≥3 个洞察四元组；证据：文件内容检查
  - `rule` TR-4.2: 每个项目 knowledge-map.md 列出所有 planned concepts/examples 标题和一句话简介；证据：文件内容检查
  - `rubric` TR-4.3: 知识地图合理性；维度：学习路径从入门到进阶；scale 1-5；anchors 1=文档排列无序/3=有顺序但缺乏递进/5=清晰的入门→核心→进阶路径，概念间依赖合理；threshold ≥4；证据：审查者阅读

## Task 5: E 阶段 — 第一批项目 references/ 信源登记生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 使用 general_purpose_task 并行生成第一批 6 个项目的 references/ 信源登记簿：
    - hermes-agent-sources.md
    - veadk-python-sources.md
    - zleap-agent-sources.md
    - deepseek-harness-sources.md
    - cordis-sources.md
    - second-me-sources.md
  - 每个信源文件包含：项目版本信息、核心目录结构、关键文件清单（路径+用途）、核心类/函数索引、架构概念映射
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-5.1: 每个 references/<project>-sources.md 存在且有正确 frontmatter（type: Reference）；证据：frontmatter 检查
  - `rule` TR-5.2: 每个信源文件列出 ≥10 个关键文件路径；证据：路径计数
  - `rule` TR-5.3: 文件路径均为真实存在的源码文件；证据：Grep/Test-Path 抽样验证
- **Notes**: 信源先行（references/ 必须先于 concepts/examples 生成）

## Task 6: E 阶段 — 第二批项目 references/ 信源登记生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 并行生成第二批 6 个项目的 references/：
    - intelligent-terminal-sources.md
    - agency-agents-sources.md
    - agency-agents-app-sources.md
    - anthropics-skills-sources.md
    - book-to-skill-sources.md
    - i-have-adhd-sources.md
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-6.1: 同 TR-5.1，6 个信源文件 frontmatter 正确；证据：frontmatter 检查
  - `rule` TR-6.2: intelligent-terminal-sources 仅包含 Agent/ACP 相关文件；证据：文件路径检查

## Task 7: E 阶段 — Tier 1 大型项目 concepts/ 分批生成（Batch 1）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 为 5 个 Tier 1 大型项目生成第一批 concepts 文档（入门+核心模块，每项目 ≤7 篇）：
    - hermes-agent: 00-导论/架构概览、01-AIAgent 入口与配置、02-ToolRegistry 工具注册表、03-工具集 DAG 组合系统、04-MoA 多代理编排、05-Provider 抽象层
    - veadk-python: 00-导论/架构概览、01-Agent 类核心、02-Runner 执行引擎、03-模型配置与 Provider、04-短期记忆系统、05-工具管理系统
    - zleap-agent: 00-导论/Monorepo 架构、01-Core 核心模块（runtime/actors/events）、02-Agent 包（conversation/engine/turnLoop）、03-AI Provider 层、04-Workspace 执行模型
    - deepseek-harness: 00-导论/Cordis 插件架构、01-Core/Agent 调度器、02-Core/Tools 工具系统、03-Core/Session 会话管理、04-LLM 层抽象、05-MCP 协议集成
    - intelligent-terminal: 00-导论/终端 Agent 架构、01-双进程架构（helper+master）、02-ACP 协议集成、03-COM 进程外服务器
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: 每篇概念文档有正确 frontmatter（type: Concept）、含 sources 字段指向 references/；证据：frontmatter 检查
  - `rule` TR-7.2: 每篇文档包含至少 1 个真实源码代码片段（标注源文件路径）；证据：代码块检查
  - `rubric` TR-7.3: 代码片段真实性；维度：代码与源码一致性；scale 1-5；anchors 1=编造/3=来自源码但缺标注/5=精确标注路径、关键逻辑完整；threshold ≥4；证据：抽查对照源码
  - `rule` TR-7.4: 每批 ≤7 篇/项目（但可以多个项目并行）；证据：文件计数
- **Notes**: 多个项目可并行委派，每个项目独立上下文；每篇文档结尾有"## 相关概念"章节

## Task 8: E 阶段 — Tier 1 大型项目 concepts/ 分批生成（Batch 2）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 为 5 个 Tier 1 项目生成第二批 concepts 文档（高级/扩展模块）：
    - hermes-agent: 06-插件系统、07-Provider 详细实现、08-Gateway 网关、09-Skills 系统、10-ACP Adapter、11-记忆与上下文管理
    - veadk-python: 06-长期记忆系统、07-MCP 集成、08-多代理编排、09-Frontend 集成、10-运行时委托机制、11-知识检索 RAG
    - zleap-agent: 05-Store 持久化与 RRF 检索、06-记忆与压缩（compaction）、07-CLI 与 TUI、08-Gateway 多平台（飞书/微信）、09-Host 生命周期管理、10-Desktop Tauri 集成、11-MCP 运行时
    - deepseek-harness: 06-ACP 协议编解码、07-SDK 层（client/server/protocol）、08-FS 文件系统抽象、09-Shell 终端集成、10-LSP 语言服务器、11-Skill 系统、12-Goal 目标系统
    - intelligent-terminal: 04-Named Pipe 通信、05-OSC 133 错误事件、06-WTCLi 终端控制、07-Cascadia Agent UI 集成
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: 同 TR-7.1/7.2；证据：同 TR-7.1/7.2
  - `rule` TR-8.2: 交叉链接使用 `/concepts/xx.md` bundle-relative 路径；证据：链接格式检查
- **Notes**: 完成后 Tier 1 项目 concepts 总数 ≥8/项目

## Task 9: E 阶段 — Tier 2 中型项目 concepts/ 生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 为 2 个 Tier 2 项目生成全部 concepts 文档：
    - cordis: 00-导论/元框架设计理念、01-Context 原型链与依赖注入、02-Fiber 生命周期管理、03-事件系统（五种分发模式）、04-Service 服务注册与调用、05-插件机制与 HMR、06-Loader 配置加载（YAML组合）
    - second-me: 00-导论/三层记忆架构、01-L0 原始记忆摄取（FileInfo/BioInfo）、02-L1 身份洞察（Shade阴影生成）、03-L2 模型对齐（SelfQA/Preference/LoRA/DPO）、04-GraphRAG 知识检索、05-API 服务层、06-AI Space 去中心化网络
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-9.1: 每个 Tier 2 项目 concepts ≥5 篇；证据：文件计数
  - `rule` TR-9.2: frontmatter 和代码片段同 TR-7.1/7.2；证据：同 TR-7.1/7.2

## Task 10: E 阶段 — Tier 3 小型项目 concepts/ 生成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 为 5 个 Tier 3 项目生成全部 concepts 文档：
    - agency-agents: 00-导论/280+ Persona 体系、01-SKILL.md 格式与部门分类、02-Persona 模板结构、03-工具适配脚本、04-Playbook 编排
    - agency-agents-app: 00-导论/Tauri 桌面应用架构、01-Svelte Store 状态管理、02-组件体系与目录浏览器、03-Rust 后端命令、04-多工具适配层
    - anthropics-skills: 00-导论/Skills 标准定义、01-SKILL.md 格式规范、02-Python 参考实现架构、03-技能运行时
    - book-to-skill: 00-导论/知识编译理念、01-四层产出流水线、02-核心编译器模块、03-脚本与工具链
    - i-have-adhd: 00-导论/认知适配理念、01-10条输出规则解析、02-Hooks 机制、03-技能集成模式
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-10.1: 每个 Tier 3 项目 concepts ≥3 篇；证据：文件计数
  - `rule` TR-10.2: frontmatter 和代码片段同 TR-7.1/7.2；证据：同 TR-7.1/7.2

## Task 11: E 阶段 — examples/ 示例文档生成（Tier 1+2）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8, Task 9
- **Description**:
  - 为 7 个 Tier 1+2 项目生成 examples/ 深度走读文档：
    - hermes-agent: ex01-AIAgent 初始化与工具注册完整走读、ex02-MoA fan-out→aggregate 调用链分析、ex03-插件加载与生命周期走读
    - veadk-python: ex01-Agent+Runner 快速启动走读、ex02-记忆系统（ST/LT）配置与使用、ex03-MCP 工具集成走读
    - zleap-agent: ex01-Workspace Turn 循环状态机走读、ex02-消息发送→工具调用→响应完整链路、ex03-Store RRF 检索走读
    - deepseek-harness: ex01-Cordis 插件定义与加载走读、ex02-Agent dispatch→tool call→LLM stream 完整链路、ex03-MCP client 工具发现与调用
    - intelligent-terminal: ex01-helper 进程 ACP 消息处理走读、ex02-COM 服务器注册与 Named Pipe 通信、ex03-OSC 133 错误检测与 UI 反馈
    - cordis: ex01-Context 创建→插件注册→服务调用完整走读、ex02-Fiber 生命周期 PENDING→ACTIVE→DISPOSED 走读
    - second-me: ex01-L0→L1→L2 记忆训练完整流水线、ex02-AI Space host/participant 通信走读
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-11.1: Tier 1 ≥3 examples，Tier 2 ≥2 examples；证据：文件计数
  - `rule` TR-11.2: 每篇 example 有正确 frontmatter（type: Example）；证据：frontmatter 检查
  - `rubric` TR-11.3: 调用链走读深度；维度：端到端流程覆盖；scale 1-5；anchors 1=仅列函数名/3=有调用顺序但缺数据流/5=完整调用链+参数传递+状态变化+代码片段；threshold ≥4；证据：审查者评分

## Task 12: E 阶段 — examples/ 示例文档生成（Tier 3）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 为 5 个 Tier 3 项目生成 examples/：
    - agency-agents: ex01-一个 Persona SKILL.md 的完整结构走读
    - agency-agents-app: ex01-Svelte Store→Component→Tauri Command 数据流走读
    - anthropics-skills: ex01-一个官方 Skill 的定义与运行时加载走读
    - book-to-skill: ex01-书籍→四层产出的编译流水线走读
    - i-have-adhd: ex01-10条规则的实际输出效果对比
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-12.1: 每个 Tier 3 项目 ≥1 example；证据：文件计数

## Task 13: E 阶段 — indexes 与 log 生成（信源、概念、示例索引）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 11, Task 12
- **Description**:
  - 为所有 12 个项目 bundle 生成：
    - concepts/index.md（概念索引，无 frontmatter，按学习路径分组链接）
    - examples/index.md（示例索引，无 frontmatter）
    - references/index.md（信源索引，无 frontmatter）
    - 根 index.md（含 okf_version frontmatter，三层导航：基础概念/核心机制/高级主题+实战示例+信源）
    - log.md（更新日志）
  - 为 fundamentals bundle 更新 index.md 和子索引，添加到各项目 bundle 的链接
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-13.1: 所有 index.md 存在；证据：文件存在性检查
  - `rule` TR-13.2: 子目录 index.md 无 frontmatter，根 index.md 有 okf_version；证据：frontmatter 检查
  - `rule` TR-13.3: index.md 列出的所有文档链接 0 断裂；证据：Python 链接检查脚本
- **Notes**: Index 必须最后生成（所有内容文档定稿后统一写）

## Task 14: 更新 bundles 全局索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 更新 `bundles/index.md`：
    - 更新 total_bundles 数字（29 + 12 = 41）
    - 更新 groups 数字（保持 9，新增 bundles 在 ai-agent 组内）
    - 更新 ai-agent 分组导航表，列出所有 13 个 bundle
    - 更新分组详情，为每个项目 bundle 添加一句话简介
    - 更新生态关系图
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-14.1: total_bundles 与实际 bundle 数量一致；证据：计数对比
  - `rule` TR-14.2: ai-agent 分组列出全部 13 个 bundle 链接；证据：链接检查

## Task 15: V 阶段 — 自动化验证（frontmatter+链接+Grep API）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 14
- **Description**:
  - 运行 Python 验证脚本：
    1. 遍历所有 13 个 bundle，检查 frontmatter 必填字段（type/title/description）
    2. 验证 type 值正确（Concept/Example/Reference）
    3. 检查所有内部 Markdown 链接（.md 结尾）的可达性
    4. 对每个文档中的代码格式标识符（反引号包裹的类名/函数名），在源码中 Grep 验证存在性（抽样≥30%）
    5. 检查子目录 index 无 frontmatter、根 index 有 okf_version
    6. 生成验证报告
  - 修复所有发现的问题
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-15.1: 验证脚本 0 errors（frontmatter+链接）；证据：脚本输出
  - `rule` TR-15.2: Grep 抽样验证的 API 名称存在率 100%；证据：Grep 输出
  - `rule` TR-15.3: 所有发现问题已修复；证据：修复后重新验证通过
- **Notes**: 这是实施者自验证阶段，不是最终独立审查

## Task 16: V 阶段 — 独立审查
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 15
- **Description**:
  - 使用 general_purpose_task 委派一个独立的 review agent（fresh context）：
    - 提供 spec.md、tasks.md、所有生成的文档路径
    - 审查 contract：检查 AC-1 到 AC-7 的所有检查点
    - 重点检查：虚构 API（随机抽样 10 个类名/方法名 Grep 验证）、代码片段真实性（对照源码抽查）、文档深度（阅读评分）、链接完整性
  - 根据审查结果，若 fail 则创建修复 issue 并回到 Task 15 修复；若 pass 则完成
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-16.1: 独立审查者检查所有 7 个 AC 并给出 pass/fail/blocked 结论；证据：review.md 中的审查报告
  - `rule` TR-16.2: 审查者对每个 AC 提供证据；证据：review.md 中的 checkpoint results
  - `rubric` TR-16.3: 代码片段质量（AC-5）评分 ≥4；证据：审查者评分+rationale
  - `rubric` TR-16.4: 架构分析深度（AC-6）评分 ≥4；证据：审查者评分+rationale
- **Notes**: 独立审查者必须 fresh context，不共享实施阶段的会话上下文；审查结果为 fail 时必须创建 remediation issues

## Task 17: C 阶段 — 模式沉淀与交付总结
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 16（审查 pass 后）
- **Description**:
  - 总结本次多项目并行 OKF Wiki 生成的经验教训
  - 更新 source-code-to-okf-wiki 模式文档的反模式和最佳实践（如多项目并行策略、monorepo 分析模式、C++项目 Agent 模块聚焦策略）
  - 生成最终交付总结报告
- **Acceptance Criteria Addressed**: 项目收尾
- **Test Requirements**:
  - `rule` TR-17.1: 交付总结包含每个 bundle 的文档统计和审查结论；证据：summary 内容
