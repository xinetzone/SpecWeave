# EchoBird 百灵鸟项目学习与 Wiki 教程文档 - 实施计划

## [x] Task 1: 创建 Wiki 教程文档基础框架与目录导航
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 docs/knowledge/learning/ 目录下创建 echobird-wiki.md 文件
  - 添加符合 MDI v1.0 规范的 YAML frontmatter（--- 包裹，包含 title/source/date/tags 字段）
  - 创建完整的目录导航系统，包含所有章节的锚点链接
  - 添加原文参考和 GitHub 项目链接的开头引用
  - **格式约束**：frontmatter 必须使用 YAML 格式（--- 分隔），不得使用 TOML（+++ 分隔）；如需完整元数据可使用 `x-toml-ref` 引用外部 TOML 文件
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-11]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于正确路径 docs/knowledge/learning/echobird-wiki.md
  - `programmatic` TR-1.2: frontmatter 使用 YAML 格式（--- 分隔）且包含所有必填字段（title/source/date/tags）
  - `human-judgement` TR-1.3: 目录导航结构完整，所有章节链接可跳转
  - `programmatic` TR-1.4: 包含原文 URL、GitHub 项目 URL 和官网 URL
- **Notes**: 参考已有的 text-to-cad-wiki.md / the-agency-project-wiki.md 的文档结构和格式（执行前先读取 1-2 个现有同类 wiki 文件确认实际格式）

## [x] Task 2: 编写项目概述与核心痛点章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 引用原文核心数据："超过 60% 的用户在第一次尝试 AI Agent 工具时，卡在了'安装和配置'阶段"
  - 阐述传统 AI Agent 工具使用的 5 个痛点：
    1. 安装命令复杂，容易失败
    2. 每个 Agent 配置格式不同
    3. 切换模型要改配置文件
    4. 本地大模型部署门槛高
    5. 国内网络访问不稳定
  - 引出 EchoBird：由开发者 edison7009 开源的 AI Agent 桌面管理工具，灵感来自《赛博朋克 2077》中的 Songbird
  - 用"传统痛点 vs EchoBird 解决方案"对照表呈现核心定位
  - 强调核心定位：把最令人头疼的几件事集中到一个软件里解决
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 清晰阐述 5 个传统痛点
  - `human-judgement` TR-2.2: 准确引用"60% 用户卡在安装配置阶段"数据
  - `human-judgement` TR-2.3: 项目背景介绍包含开发者、灵感来源、核心定位
  - `human-judgement` TR-2.4: 使用表格清晰对照"痛点 vs 解决方案"

## [x] Task 3: 编写核心架构与 Model Nexus 设计章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 阐述整体架构设计：一个共享的模型数据中心（Model Nexus）支撑四大应用场景
  - 用一句话概括核心价值："配置一次，到处可用"
  - 详细解析 Model Nexus 的设计思路：
    - 所有场景共享同一个模型配置中心
    - 用户不用在每个工具里分别填 API Key、Base URL、Model Name
    - 在 Model Nexus 里配置一次，所有功能自动生效
  - 提供架构示意图（文字描述 + Mermaid 图表可选）
  - 阐述该设计思路的聪明之处：避免重复配置、统一管理、一次生效
  - 简述技术栈：Tauri + Rust（安装包约 50MB、启动快、全平台覆盖）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 清晰说明 Model Nexus 与四大场景的关系
  - `human-judgement` TR-3.2: 准确概括"配置一次，到处可用"核心价值
  - `human-judgement` TR-3.3: Model Nexus 设计思路解析到位（避免重复配置、统一管理、一次生效）
  - `human-judgement` TR-3.4: 技术栈说明完整（Tauri + Rust、体积、启动、全平台）

## [x] Task 4: 编写四大场景详解章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - **场景一·安装修复 Agent**：
    - 核心功能：对话式 AI 自动安装和排查 Agent 工具
    - 支持的 Agent（12+）：Claude Code（上限最高的 AI 编程助手）、Codex（OpenAI 官方）、OpenClaw（开源 Agent 工作流框架）、Aider（与 Git 仓库深度集成）、OpenCode（轻量代码助手）、Hermes Agent（多功能 Agent 框架）、NanoBot/PicoClaw/ZeroClaw（轻量级工具）等
    - 工作流程：告诉 EchoBird 要装什么 → 自动检测环境 → 处理依赖 → 配置镜像源 → 完成安装
    - 报错排查能力：本地诊断 + 远程协助（缺运行环境 / 配置文件错误 / API Key 没配对）
  - **场景二·一键本地大模型**：
    - 内置推理引擎：llama.cpp、vLLM、SGLang
    - 三步操作流程：①选择量化版本 → ②点 START → ③等待加载完成
    - 自动处理：引擎选择、模型下载、端口与 endpoint 配置
    - 适用人群：不依赖云端 API / 有本地数据隐私需求的用户
  - **场景三·我的 AI 项目**：
    - 功能说明：导入自研 AI 应用或游戏，统一管理和启动
    - 定位：AI 工具的集中管理站
  - **场景四·应用管理器**：
    - 卡片式启动面板：展示已安装的 Agent 与导入的项目
    - 一键启停、查看当前使用的模型、随时切换模型
    - 配合 Model Nexus 形成顺滑流程：安装 Agent → 配置模型 → 分配模型 → 启动
  - 每个场景包含：功能说明、操作流程、应用价值三部分
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 四个场景每个都有详细说明
  - `human-judgement` TR-4.2: 场景一列出至少 7 款 Agent 工具及简要说明
  - `human-judgement` TR-4.3: 场景二包含三步操作流程和内置推理引擎列表
  - `human-judgement` TR-4.4: 场景四说明与 Model Nexus 配合的完整使用流程

## [x] Task 5: 编写四步快速上手指南章节
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - **第一步：安装 EchoBird**
    - Windows（PowerShell）命令：`irm https://echobird.ai/install.ps1 | iex`
    - macOS / Linux 命令：`curl -fsSL https://echobird.ai/install.sh | sh`
    - 脚本能力：自动检测操作系统、下载对应安装包、已安装最新版则跳过
    - 手动下载备选：https://github.com/edison7009/EchoBird/releases/latest
  - **第二步：安装一个 Agent**
    - 进入"应用管理"（App Manager）页面，选择想用的 Agent
    - 重要提示：不要一次装一堆，先成功启动一个，再扩展其他工具
  - **第三步：配置模型中心**
    - 进入"模型中心"页面，添加模型服务商（DeepSeek、OpenAI、Anthropic、Qwen、Kimi、GLM、MiniMax 等）
    - 填写四个字段：API Key / Base URL（Endpoint） / Model Name / Protocol
    - 重点说明每个字段的作用与易错点（详见 Task 6）
  - **第四步：绑定模型到 Agent，然后启动**
    - 回到应用管理页面，把配置好的模型分配给 Agent
    - 点击启动，几秒钟后 AI Agent 即可运行
    - 全程不需要碰终端、不需要改配置文件、不需要查环境变量
  - 所有命令必须以代码块形式呈现，可直接复制执行
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 四个步骤完整
  - `programmatic` TR-5.2: Windows PowerShell 命令（irm | iex）格式正确
  - `programmatic` TR-5.3: macOS/Linux curl 命令格式正确
  - `human-judgement` TR-5.4: 包含"先成功启动一个再扩展"的注意事项
  - `human-judgement` TR-5.5: 第四步强调"全程不需要碰终端"的体验优势

## [x] Task 6: 编写模型配置四字段详解章节
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 原文特别强调这四个字段"非常容易填错或漏填"，需独立章节详解：
    - **API Key**：模型平台的密钥，从对应模型服务商控制台获取
    - **Base URL / Endpoint**：接口地址，原文特别标注"非常容易填错或漏填"
    - **Model Name**：模型名，必须和平台文档一致，"不要自己猜"
    - **Protocol**：协议类型，OpenAI API / Anthropic API 要分清
  - 列出支持的模型服务商：DeepSeek、OpenAI、Anthropic、Qwen、Kimi、GLM、MiniMax 等
  - 提供配置示例（虚构示例，避免泄露真实密钥）
  - 强调"配置一次到处可用"——这是 Model Nexus 的核心价值体现
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 四个字段每个都有详细说明和易错点提示
  - `human-judgement` TR-6.2: 包含支持的模型服务商完整列表
  - `human-judgement` TR-6.3: 提供配置示例（脱敏）
  - `human-judgement` TR-6.4: 强调"配置一次到处可用"与 Model Nexus 呼应

## [x] Task 7: 编写关键技术要点章节
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - **技术栈优势 Tauri + Rust**：
    - 安装包体积小（约 50MB）
    - 启动速度快
    - 全平台覆盖（Windows / macOS / Linux）
    - 相比 Electron 的优势（隐含对比）
  - **Model Nexus 统一配置设计**：
    - 一个共享的模型数据中心支撑四大场景
    - 避免在每个工具里重复填写 API Key / Base URL / Model Name
    - 一次配置所有功能自动生效
  - **国内镜像源适配**：
    - 自动匹配国内镜像源，解决国内网络访问不稳定问题
    - 降低国内用户使用门槛
  - **Agent 工具持续加入机制**：
    - 当前支持 12+ 工具（列出主要工具）
    - 持续加入更多工具的扩展机制
  - **对话式安装与排查设计**：
    - 用对话方式让 AI 自动安装和排查
    - 支持本地诊断 + 远程协助双模式
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 至少包含 4 个技术要点
  - `human-judgement` TR-7.2: 技术栈优势说明清晰（体积、启动、全平台）
  - `human-judgement` TR-7.3: Model Nexus 设计要点与核心架构章节呼应
  - `human-judgement` TR-7.4: 国内镜像源适配说明价值

## [x] Task 8: 编写核心价值总结与展望章节
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 引用原文核心观点："AI Agent 的真正价值，从来不是会用终端命令或者能看懂配置文件"
  - 阐述产品哲学："真正的价值在于——用 AI 帮你把事情做成"
  - 概括 EchoBird 的本质："把 AI 工具用起来之前的那段路铺平"
  - 重申设计理念：
    - 用户不需要懂 Node.js 版本管理
    - 不需要查每个模型平台的 API 文档
    - 不需要折腾推理引擎
    - 用户只需要关心想做什么（写代码 / 跑本地模型 / 管理应用）
  - 与开头痛点形成呼应（60% 用户卡在安装配置 → EchoBird 把这段路铺平）
  - 展望：随着 12+ 工具持续加入，将成为 AI Agent 工具的统一入口
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 核心价值总结到位
  - `human-judgement` TR-8.2: 与开头痛点形成呼应
  - `human-judgement` TR-8.3: 引用原文"把那段路铺平"的产品哲学
  - `human-judgement` TR-8.4: 语言精炼有洞察力

## [x] Task 9: 编写 FAQ 常见问题解答章节
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - 整理常见问题并提供解答，如：
    - Q: EchoBird 是免费的吗？开源协议是什么？
    - Q: EchoBird 支持哪些操作系统？
    - Q: EchoBird 支持哪些 AI Agent 工具？
    - Q: EchoBird 支持哪些模型服务商？
    - Q: 必须联网才能使用吗？本地模型需要什么硬件？
    - Q: 配置模型时 Base URL 该怎么填？
    - Q: 一个 Agent 装不上怎么办？报错如何排查？
    - Q: EchoBird 与 Claude Code 官方安装方式有什么区别？
    - Q: 是否支持中文界面？
    - Q: 是否可以导入自己开发的 AI 应用？
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 至少包含 8 个 FAQ 问题
  - `human-judgement` TR-9.2: 问题具有实际参考价值
  - `human-judgement` TR-9.3: 解答清晰准确

## [x] Task 10: 编写相关资源链接章节
- **Priority**: medium
- **Depends On**: Task 9
- **Description**: 
  - GitHub 项目地址：https://github.com/edison7009/EchoBird
  - 官网：https://echobird.ai
  - 原文链接：微信公众号文章 URL（https://mp.weixin.qq.com/s/iN7C_mZJo6bz4x2BR7OJjg）
  - GitHub Release 页面：https://github.com/edison7009/EchoBird/releases/latest
  - 一键安装脚本：Windows（https://echobird.ai/install.ps1）与 macOS/Linux（https://echobird.ai/install.sh）
  - 相关 Agent 工具资源链接（如适用，可链接到 Claude Code、Codex、OpenClaw、Aider 等官方资源）
  - 相关推理引擎资源链接（llama.cpp、vLLM、SGLang）
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-10.1: GitHub 链接正确
  - `programmatic` TR-10.2: 原文链接正确
  - `programmatic` TR-10.3: 官网链接正确
  - `human-judgement` TR-10.4: 资源分类清晰（项目 / 安装 / 相关工具）

## [x] Task 11: 更新知识库索引 README.md
- **Priority**: high
- **Depends On**: Task 10
- **Description**: 
  - 在 docs/knowledge/README.md 的 learning 分类表格中新增 echobird 教程条目
  - 条目包含：标题、摘要、日期（2026-07-04）、标签（echobird、ai-agent、tauri、rust、model-nexus、claude-code、codex、openclaw、local-llm、desktop-tool）
  - 遵循现有索引格式，保持表格结构一致
  - **格式约束**：先读取 docs/knowledge/README.md 现有条目确认实际表格格式，再追加新行
- **Acceptance Criteria Addressed**: [AC-12]
- **Test Requirements**:
  - `programmatic` TR-11.1: README.md 中 learning 分类新增了条目
  - `human-judgement` TR-11.2: 摘要准确概括教程内容
  - `human-judgement` TR-11.3: 标签设置合理
  - `programmatic` TR-11.4: 表格格式与现有条目一致

## [x] Task 12: 子代理产出物验收（5 项快速验收点）
- **Priority**: high
- **Depends On**: Task 11
- **Description**: 
  - 主代理对子代理交付的 wiki 文档执行 5 项快速验收：
    1. **frontmatter 格式合规**：使用 YAML（--- 分隔）而非 TOML（+++ 分隔）
    2. **文件路径正确**：位于 docs/knowledge/learning/echobird-wiki.md
    3. **文件名合规**：kebab-case、纯英文、无中文字符（运行 `python .agents/scripts/check-filename-convention.py` 验证）
    4. **内容完整性**：12 个 AC 全部满足，章节结构完整
    5. **链接有效性**：目录导航锚点可跳转、外部 URL 指向正确资源（运行 `python .agents/scripts/check-links.py` 验证）
  - 任一验收点未通过则创建修复任务并交回子代理处理
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-11, AC-12]
- **Test Requirements**:
  - `programmatic` TR-12.1: frontmatter 使用 YAML 格式
  - `programmatic` TR-12.2: 文件路径与命名合规
  - `programmatic` TR-12.3: 文件名命名规范检查通过
  - `human-judgement` TR-12.4: 12 个 AC 全部满足
  - `programmatic` TR-12.5: 链接有效性检查通过

# Task Dependencies
- Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8 → Task 9 → Task 10 → Task 11 → Task 12
- 全部任务为串行依赖（每个 Task 依赖前一个 Task 完成后才能开始）
- Task 12（验收）依赖所有前序任务完成
