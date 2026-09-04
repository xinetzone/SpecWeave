# 腾讯 AI 生态 OKF Wiki 教程 - 实施计划

> 方法论：source-code-to-okf-wiki 五阶段（R→I→E→V）+ 七概念知识沉淀链路
> 每个知识束独立执行 R→I→E→V，但共享 tencent/ 生态索引

## [x] Task 1: 创建 tencent 生态分组目录与 CodeBuddy 产品知识束
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `bundles/tencent/` 目录结构和 `bundles/tencent/index.md` 生态索引
  - 创建 `bundles/tencent/codebuddy/` 知识束（外部文档分析模式，无源码）
  - R 阶段：将已抓取的 6 个网页内容整理为编号事实清单，写入 `codebuddy/spec/facts.md`
  - I 阶段：提炼产品矩阵洞察和知识地图，写入 `codebuddy/spec/insights.md`
  - E 阶段（信源先行）：
    1. 生成 `references/` 下 6 个信源文件（ide/docs-intro/cli/npc/workbuddy/security）
    2. 分批生成 `concepts/` 概念文档（每批 ≤ 7）：
       - 00-product-matrix（产品矩阵总览：IDE/插件/CLI/NPC/WorkBuddy/Security 六形态）
       - 01-ide（CodeBuddy IDE：产设研一体、Figma 转码、一键部署）
       - 02-cli（CodeBuddy Code：终端 AI、/init、MCP、Sub-agents、长期记忆）
       - 03-npc（Cloud Agent：目标驱动、CNB 集成、多 NPC 协同、自主修复）
       - 04-workbuddy（Web AI 助手：办公+开发双场景、Skill、产物面板）
       - 05-security（安全审计：六步闭环、Xcheck+AI 双引擎、PoC 验证、CVE 战绩）
    3. 生成 `examples/` 示例文档：
       - quick-start-cli（CLI 安装与 /init 上手）
       - ide-workflow（IDE 从需求到部署全流程示例）
    4. 最后生成各级 `index.md` 和 `log.md`
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构完整（references/concepts/examples/index.md/log.md）
  - `programmatic` TR-1.2: 每个 .md 文件 frontmatter 含 type 字段
  - `programmatic` TR-1.3: 6 个信源文件的 sources.resource URL 可访问
  - `human-judgement` TR-1.4: 产品特性描述与网页原文一致，无夸大或虚构
  - `human-judgement` TR-1.5: 概念文档学习路径合理，从总览到分产品递进
- **Notes**: CodeBuddy 无本地源码，不执行 Grep API 验证；事实来源为已抓取网页内容

## [x] Task 2: 生成 AI-Infra-Guard 源码知识束
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `bundles/tencent/ai-infra-guard/` 知识束
  - R 阶段：深度阅读 Go 源码（cmd/cli、common/websocket、common/runner、common/fingerprints、pkg/vulstruct、internal/mcp）和 Python 子模块（mcp-scan/、agent-scan/、AIG-PromptSecurity/），提取编号事实 F-xxx 写入 `spec/facts.md`
  - I 阶段：提炼架构洞察（分布式 Server-Agent、四任务类型、规则 DSL 引擎、Go/Python 桥接）写入 `spec/insights.md`
  - E 阶段（信源先行）：
    1. 生成 `references/` 信源文件：
       - go-server（cmd/cli + common/websocket：Gin 路由、任务管理器、SSE）
       - scan-engine（common/runner + common/fingerprints：目标解析、并发探测、指纹 DSL）
       - vuln-struct（pkg/vulstruct：CVE 版本范围 DSL）
       - python-subsystems（mcp-scan/agent-scan/AIG-PromptSecurity 三 Python 子模块）
       - data-rules（data/fingerprints + data/vuln + data/mcp + data/eval 规则库）
    2. 分批生成 `concepts/`：
       - 00-architecture（分布式 Server-Agent 架构总览）
       - 01-task-types（四种任务类型：AI-Infra-Scan/Mcp-Scan/Prompt-Redteam/Agent-Scan）
       - 02-fingerprint-dsl（指纹规则 DSL：词法分析、表达式、操作符）
       - 03-vuln-matching（CVE 漏洞匹配与版本范围 DSL）
       - 04-websocket-protocol（Agent↔Server WebSocket 消息协议）
       - 05-python-bridge（Go 调用 Python 子进程的桥接机制）
       - 06-mcp-scan（MCP Server 安全扫描：14 类风险、源码/动态双模式）
    3. 生成 `examples/`：
       - cli-scan（CLI 扫描命令使用示例）
       - custom-fingerprint（自定义指纹规则编写示例）
       - docker-deploy（Docker 部署与 API 调用示例）
    4. 最后生成 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: Grep 验证文档中所有 Go 结构体名（TaskManager、Runner、FingerprintParser、VulnStruct 等）在源码中存在
  - `programmatic` TR-2.2: Grep 验证四种任务类型的 handler/常量在 common/ 中存在
  - `programmatic` TR-2.3: 指纹 DSL 操作符（= == != ~= && ||）与 parser 源码一致
  - `programmatic` TR-2.4: Python 子模块入口脚本路径正确
  - `human-judgement` TR-2.5: 架构图清晰展示 Server↔Agent↔Python 子进程关系
- **Notes**: Go 源码中实际结构体名需在 R 阶段确认，不可凭推测

## [x] Task 3: 生成 WorkBuddy/Octop 源码知识束
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `bundles/tencent/octop/` 知识束
  - R 阶段：深度阅读 src/octop/ 源码（launch.py、config.py、infra/server.py、infra/agents/manager.py、infra/gateway/、infra/db/、api/app.py、cli/main.py、cli/registry.py），提取编号事实写入 `spec/facts.md`
  - I 阶段：提炼架构洞察（四层依赖禁令、组合根模式、DI 容器、单进程模型、Harness 栈集成、ACP 双向）写入 `spec/insights.md`
  - E 阶段（信源先行）：
    1. 生成 `references/` 信源文件：
       - server-launch（launch.py + infra/server.py：OctopServer 生命周期）
       - agent-manager（infra/agents/manager.py：AgentManager 60+ 方法）
       - gateway（infra/gateway/：Gateway、GlobalProcessor、ChannelManager）
       - db-layer（infra/db/：SqlitePool/PostgresPool、RepoBundle、22 Repo）
       - cli-api（cli/ + api/：20 子命令、50+ 路由、JWT 认证）
       - harness-stack（harness-agent/gateway/memory/browser 外部依赖）
    2. 分批生成 `concepts/`：
       - 00-architecture（四层架构与依赖禁令、组合根、单进程模型）
       - 01-server-lifecycle（OctopServer 启动/停止流程、_boot_runtime）
       - 02-agent-runtime（AgentManager、HarnessAgent、Provider、专家库、MBTI）
       - 03-gateway-channels（Gateway、IM 通道、GlobalProcessor、WebSocket/CLI Hub）
       - 04-db-di（DatabasePool、RepoBundle、SharedServices DI、迁移）
       - 05-acp-protocol（ACP 双向集成：入站 stdio 服务器、出站 runner 委托）
       - 06-cli-commands（20 个 CLI 子命令、三层传输：Offline/Embedded/External）
    3. 生成 `examples/`：
       - self-hosted-setup（octop init → run 完整自托管部署示例）
       - custom-agent（创建自定义 Agent 与专家配置示例）
       - acp-integration（ACP 入站/出站配置示例）
    4. 最后生成 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1: Grep 验证 OctopServer、AgentManager、Gateway、SharedServices、RepoBundle、_LazyCLI、PathLayout 在 src/octop/ 中存在
  - `programmatic` TR-3.2: 20 个 CLI 子命令与 cli/registry.py COMMANDS 字典一致
  - `programmatic` TR-3.3: 四层架构禁令（infra↛api/cli/launch）与 AGENTS.md 一致
  - `programmatic` TR-3.4: ACP runner 列表（opencode/codebuddy/claude_code/codex）与 docs/acp.md 一致
  - `human-judgement` TR-3.5: 概念文档清晰解释 Harness 栈边界（外部依赖 vs Octop 自有代码）
- **Notes**: harness-agent 等为外部包，文档中只描述 Octop 如何调用，不虚构其内部 API

## [x] Task 4: 生成 ncnn 源码知识束
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `bundles/tencent/ncnn/` 知识束
  - R 阶段：深度阅读 src/ 核心头文件（net.h、mat.h、layer.h、option.h、allocator.h、blob.h、paramdict.h、modelbin.h、gpu.h、pipeline.h），提取编号事实写入 `spec/facts.md`；算子层按类别采样（卷积/池化/激活/数学/注意力各选代表）
  - I 阶段：提炼架构洞察（零依赖极简基础设施、PIMPL、引用计数 Mat、运行时 CPU 分发、SIMD 打包、Vulkan 双后端）写入 `spec/insights.md`
  - E 阶段（信源先行）：
    1. 生成 `references/` 信源文件：
       - net-extractor（net.h：Net 加载、Extractor 推理）
       - mat-tensor（mat.h：Mat 维度系统、elempack、像素转换、VkMat）
       - layer-base（layer.h：Layer 虚函数、生命周期、能力标志位）
       - allocator（allocator.h：PoolAllocator、VkAllocator 层级）
       - vulkan-backend（gpu.h/pipeline.h/command.h：Vulkan 设备、管线、命令缓冲）
       - build-system（CMakeLists.txt：构建选项、架构支持、Python 绑定）
    2. 分批生成 `concepts/`（分两批，每批 ≤ 7）：
       - 第一批（核心架构）：
         - 00-overall-architecture（整体架构：无依赖、CPU/GPU 双后端、全架构覆盖）
         - 01-net-extractor（Net 模型加载与 Extractor 推理会话）
         - 02-mat-tensor-system（Mat 张量：维度秩、elempack 打包、引用计数、零拷贝）
         - 03-layer-abstraction（Layer 算子基类：虚函数、能力标志位、多后端 forward）
         - 04-allocator（内存分配器：PoolAllocator、对齐、Vulkan 分配器层级）
         - 05-option-config（Option 推理选项：lightmode、线程、量化、Vulkan 开关）
       - 第二批（高级机制）：
         - 06-vulkan-gpu（Vulkan GPU 后端：VkMat、Pipeline、Command、PipelineCache）
         - 07-simd-packing（SIMD 打包存储：elempack、运行时 CPU 特性分发 ruapu）
         - 08-paramdict-modelbin（ParamDict 参数解析与 ModelBin 权重加载）
         - 09-layer-registry（算子注册表与自定义层机制）
         - 10-python-binding（Python 绑定：pybind11、numpy 零拷贝、model_zoo）
         - 11-quantization（量化推理：int8/fp16/bf16 存储与计算路径）
    3. 生成 `examples/`：
       - first-inference（C++ 加载模型首次推理完整示例）
       - python-yolo（Python 使用 ncnn.model_zoo 运行 YOLO 检测示例）
       - custom-layer（自定义 Layer 注册与实现示例）
       - vulkan-inference（Vulkan GPU 推理启用示例）
    4. 最后生成 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: Grep 验证 Net、Extractor、Mat、Layer、Blob、Option、Allocator、PoolAllocator、VkAllocator、ParamDict、ModelBin、VkMat、Pipeline、VkCompute 在 src/ 中存在
  - `programmatic` TR-4.2: Mat 维度系统（dims 0-4、w/h/d/c、elempack、cstep）与 mat.h 一致
  - `programmatic` TR-4.3: Layer 虚函数签名（forward/forward_inplace/load_param/load_model/create_pipeline）与 layer.h 一致
  - `programmatic` TR-4.4: Allocator 继承体系与 allocator.h 一致
  - `programmatic` TR-4.5: CMake 构建选项（NCNN_VULKAN/NCNN_INT8/NCNN_PYTHON 等）与 CMakeLists.txt 一致
  - `human-judgement` TR-4.6: 概念文档从核心运行时到高级机制递进，算子层不逐个罗列 120+ 算子
- **Notes**: ncnn 源码规模最大，采用分层采样策略；src/layer/ 下数百文件不逐一阅读，按类别在 references 中列表登记

## [x] Task 5: V 阶段独立审查与全量修复
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 对四个知识束（tencent/index + codebuddy + ai-infra-guard + octop + ncnn）执行独立 V 阶段审查：
    1. 结构完整性检查（目录结构、文件数量）
    2. Frontmatter 检查（type/title/description/tags/generated/verified/status/stale_after/sources）
    3. 链接检查（所有 `/` 开头交叉链接目标文件存在）
    4. **Grep API 验证**（最关键）：
       - ai-infra-guard: 对文档中所有 Go 结构体/函数名在 external/libs/ai/Tencent/AI-Infra-Guard/ 中 Grep
       - octop: 对所有 Python 类/方法名在 external/libs/ai/Tencent/WorkBuddy/Octop/src/ 中 Grep
       - ncnn: 对所有 C++ 类/方法在 external/libs/ai/Tencent/ncnn/src/ 中 Grep
    5. 代码示例语法检查
    6. Index 完整性（根 index 和子目录 index 列出所有文件）
    7. CodeBuddy 产品事实溯源（与抓取的网页内容比对）
  - 输出检查报告，按 🔴虚构API/🟡链接断裂/🟢格式问题 分级
  - 逐一修复所有问题，修复后重新验证直到清零
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 零虚构 API（Grep 验证全部通过）
  - `programmatic` TR-5.2: 零断链（所有交叉链接目标存在）
  - `programmatic` TR-5.3: 所有非保留 .md 文件含 type 字段
  - `programmatic` TR-5.4: 子目录 index.md 无 frontmatter
  - `human-judgement` TR-5.5: 代码示例可运行或语法正确
- **Notes**: V 阶段必须独立于 E 阶段执行，可委派 black-box 验证子代理
