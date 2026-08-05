# VeADK-Python Wiki 知识库生成 - Product Requirement Document

## Overview
- **Summary**: 使用七概念方法论（知识沉淀场景 R→I→E→V）系统学习 `d:\AI\.chaos\libs\veadk-python` 代码库，生成结构化的中文 Wiki 知识库，涵盖架构概览、核心模块详解、API 参考、使用指南和最佳实践。
- **Purpose**: 火山引擎 Agent Development Kit (VeADK) 是一个集成火山引擎云服务能力的开源 Agent 开发框架，基于 Google ADK 构建。本项目旨在通过系统性的代码分析和方法论指导，产出一套完整、准确、易用的中文 Wiki，帮助开发者快速理解和使用 VeADK。
- **Target Users**: Python 开发者、AI Agent 开发者、需要使用火山引擎云服务构建智能体的工程师、VeADK 贡献者和学习者。

## Goals
- G1: 系统性分析 VeADK-Python 代码库架构，梳理模块依赖关系和核心设计模式
- G2: 产出完整的中文 Wiki 文档，包含：快速入门、架构概览、核心模块 API 文档、示例解析、扩展开发指南
- G3: 遵循七概念方法论知识沉淀流程（R→I→E→V），确保文档质量经过事实采集、本质洞察、模式萃取、对抗审查四个阶段
- G4: Wiki 结构清晰、可导航，符合开发者学习路径（从入门到进阶）

## Non-Goals (Out of Scope)
- 不修改 veadk-python 源代码或向上游提交贡献
- 不翻译官方英文文档为中文（而是基于代码分析产出原创性中文 Wiki）
- 不构建在线文档网站或静态站点生成器配置
- 不包含 veadk-python 中 frontend/ 目录（TypeScript 前端部分）的详细分析（仅作概览提及）
- 不生成视频教程或交互式学习材料

## Background & Context
- VeADK-Python 是火山引擎开源的 Agent 开发工具包，核心入口为 `veadk.Agent` 和 `veadk.Runner`
- 技术栈：Python ≥3.10，基于 Google ADK (google-adk ≥1.34.0)，集成 LiteLLM、OpenTelemetry、MCP、A2A 协议等
- 核心模块包括：agents/（多智能体）、memory/（短期/长期记忆）、knowledgebase/（知识库 RAG）、tools/（内置工具）、cli/（命令行工具）、a2a/（Agent2Agent 协议）、cloud/（云部署）、extensions/（飞书等扩展）
- 已有官方文档站点（https://volcengine.github.io/veadk-python/）和 examples/ 目录下 15+ 示例
- 项目使用 uv 作为包管理器，pytest 作为测试框架

## Functional Requirements
- **FR-1**: 代码库事实采集（R阶段）
  - 扫描并分析 `veadk/` 目录下所有 Python 模块
  - 阅读核心类和函数的 docstring 和实现代码
  - 分析 examples/ 目录下的示例代码
  - 梳理 pyproject.toml 中的依赖关系和可选功能分组
  - 产出客观事实清单（模块清单、类清单、函数清单、依赖清单），不含主观判断

- **FR-2**: 架构洞察与本质分析（I阶段）
  - 分析 Agent 类的初始化流程和生命周期
  - 识别核心设计模式（继承自 google-adk LlmAgent、插件式工具注册、回调机制等）
  - 梳理模块间依赖关系和扩展点
  - 产出核心洞察（每条包含现象描述、根因分析、影响评估、使用建议四元组）

- **FR-3**: 模式萃取与 Wiki 结构化（E阶段）
  - 将代码结构映射为 Wiki 章节结构
  - 萃取常见使用模式（创建 Agent、添加工具、配置记忆、使用知识库、多智能体协作、云部署等）
  - 生成各模块 API 参考文档（类签名、参数说明、返回值、使用示例）
  - 产出反模式（常见误用场景及规避方法）

- **FR-4**: 对抗审查与质量加固（V阶段）
  - 从四个视角审查文档：魔鬼代言人（逻辑漏洞）、新手开发者（可读性）、CTO（ROI/完整性）、学术研究员（准确性）
  - 验证代码示例的可运行性
  - 检查 API 文档与实际代码签名的一致性
  - 修正发现的问题，形成最终 Wiki

- **FR-5**: Wiki 文档产出
  - Wiki 首页与导航索引
  - 快速入门指南（安装、配置、Hello World）
  - 架构概览（整体设计、核心概念、模块关系图）
  - 核心模块文档（Agent、Runner、Memory、KnowledgeBase、Tools、CLI、A2A 等）
  - 示例解析（关键 examples 的中文解读）
  - 扩展开发指南（如何添加自定义工具、扩展、集成云服务）
  - 常见问题与最佳实践

## Non-Functional Requirements
- **NFR-1**: 文档语言为标准现代汉语，术语首次出现时附英文原文和一句话解释
- **NFR-2**: 所有代码引用使用绝对路径链接格式，可直接点击跳转到对应代码位置
- **NFR-3**: Wiki 文档使用 Markdown 格式，章节层级清晰（H1-H3），支持 Mermaid 图表
- **NFR-4**: API 参考必须与代码签名完全一致，参数类型、默认值、返回值类型需从代码中提取
- **NFR-5**: 代码示例需可运行（或注明需要的前置条件和配置）
- **NFR-6**: Wiki 文件组织原子化，每个核心模块对应独立 Markdown 文件，通过索引文件导航
- **NFR-7**: 遵循项目文件命名规范（kebab-case、纯英文文件名）

## Constraints
- **Technical**: 仅分析 Python 代码部分（`veadk/` 目录），frontend/ 目录仅作概览；不执行需要真实 API Key 的代码运行测试
- **Business**: 文档需符合 Apache 2.0 许可证要求；产出物存放于项目知识库目录
- **Dependencies**: 依赖七概念方法论编排技能；依赖代码搜索和文件读取工具；子代理执行具体分析和文档生成任务

## Assumptions
- veadk-python 代码库已完整存在于 `d:\AI\.chaos\libs\veadk-python` 路径
- 用户具备基础 Python 知识和 LLM/Agent 相关概念基础
- Wiki 产出物存放路径默认在 `.agents/docs/knowledge/learning/veadk-python/` 下（公开内容标准路径），如有特殊需求可调整
- 不需要运行 veadk-python 的测试套件或实际调用云服务 API，静态代码分析足以支撑文档准确性
- examples/ 目录下的示例代码足以覆盖主要使用场景

## Acceptance Criteria

### AC-1: 事实采集完成度
- **Given**: veadk-python 代码库完整可用
- **When**: 完成 R（复盘/事实采集）阶段
- **Then**: 产出包含所有 veadk/ 子模块的客观事实清单，每个模块列出主要类/函数/文件，清单中无"因为/所以/导致"等因果判断词
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 事实清单作为 supporting analysis 存放，不直接进入最终 Wiki

### AC-2: 洞察四元组完整性
- **Given**: 已完成事实采集
- **When**: 完成 I（洞察）阶段
- **Then**: 产出 ≥5 条核心洞察，每条包含现象描述、根因分析（代码证据）、影响评估、使用建议四部分
- **Verification**: `human-judgment`

### AC-3: Wiki 结构完整性
- **Given**: 已完成洞察分析
- **When**: 完成 E（萃取）阶段，生成 Wiki 文档
- **Then**: Wiki 包含首页索引、快速入门、架构概览、≥8 个核心模块文档、≥5 个示例解析、扩展指南、FAQ 共 7 大类文档
- **Verification**: `programmatic`（文件计数+结构检查）+ `human-judgment`

### AC-4: API 文档准确性
- **Given**: Wiki 核心模块文档已生成
- **When**: 进行 V（对抗审查）阶段的准确性校验
- **Then**: 抽查 ≥20 个类/函数签名与实际代码一致，参数说明与代码逻辑匹配，关键方法有使用示例
- **Verification**: `programmatic`（签名对比）+ `human-judgment`

### AC-5: 文档可读性与导航性
- **Given**: 完整 Wiki 已生成
- **When**: 从新手开发者视角审查
- **Then**: 新开发者可按快速入门在 30 分钟内跑通 Hello World 示例；文档间交叉引用有效；术语表覆盖 ≥15 个核心术语
- **Verification**: `human-judgment`

### AC-6: 产出物路径与格式规范
- **Given**: Wiki 文档全部完成
- **When**: 最终交付检查
- **Then**: 所有文件位于正确目录（`.agents/docs/knowledge/learning/veadk-python/`），文件名遵循 kebab-case，Markdown 格式正确，frontmatter 符合 MDI 规范
- **Verification**: `programmatic`（文件名检查脚本）+ `human-judgment`

## Open Questions
- [ ] Wiki 产出物的具体存放位置：使用默认的 `.agents/docs/knowledge/learning/veadk-python/` 还是用户指定其他路径？
- [ ] 是否需要包含 frontend/（TypeScript 前端部分）的详细分析文档，还是仅做简要提及？
- [ ] Wiki 中代码示例的详细程度：是保持最小可运行片段，还是包含完整配置和错误处理？
- [ ] 是否需要生成 Mermaid 架构图/流程图？（建议包含，但需确认）
