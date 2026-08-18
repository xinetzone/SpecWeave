---
id: create-okf-kit-wiki-tutorial-tasks
title: "okf-kit 完整 Wiki 教程 — 任务分解"
date: "2026-08-18"
category: "standards-tools"
spec_ref: "spec.md"
---

# okf-kit 完整 Wiki 教程 — 任务分解

## 方法论说明

本任务采用七概念方法论的**知识沉淀链路（R→I→E）**执行：

```
R (Retrospective 复盘) → I (Insight 洞察) → E (Extraction 萃取)
```

- **R 阶段**：系统采集 okf-kit 源码事实，还原项目完整架构和功能
- **I 阶段**：分析核心设计决策、识别关键概念和模式，形成结构化理解
- **E 阶段**：萃取为原子化 wiki 章节，确保知识可迁移、可复用

质量门：G1（事实无因果词）→ G2（洞察四元组完整）→ G3（模式可迁移）

---

## 任务清单

### 阶段一：R（Retrospective）— 事实采集与源码研读

#### Task 1: 创建 wiki 目录结构
- **优先级**: high
- **依赖 AC**: FR1, NFR2
- **状态**: pending
- **描述**: 创建 `docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/` 目录
- **测试要求**:
  - **rule**: 目录存在且可写
  - **evidence**: LS 验证目录创建

#### Task 2: 完整研读剩余源码模块
- **优先级**: high
- **依赖 AC**: FR2, NFR1
- **状态**: pending
- **描述**: 阅读尚未覆盖的核心模块，完成事实采集
  - `okf_kit/fetch/browser.py` — 浏览器渲染 Fetcher
  - `okf_kit/chat/retrieval.py` — 零 Key 检索回退
  - `okf_kit/chat/repl.py` — 交互式 REPL
  - `okf_kit/chat/history.py` — 聊天历史
  - `okf_kit/mcp.py` — MCP 服务器
  - `okf_kit/serve/` — HTTP API 服务（app.py, reader.py, run.py, settings.py）
  - `okf_kit/enrich.py` — LLM 富化
  - `okf_kit/visualize.py` — 可视化
  - `okf_kit/bundle_reader.py` — Bundle 读取工具
- **测试要求**:
  - **rule**: 每个模块的核心函数/类已识别并记录
  - **evidence**: 形成结构化笔记，覆盖所有公开 API
  - **G1 门控**: 笔记中无因果推断词（"因为"/"导致"/"所以"），纯客观描述

#### Task 3: 研读测试文件理解预期行为
- **优先级**: medium
- **依赖 AC**: NFR1
- **状态**: pending
- **描述**: 阅读 tests/ 目录下关键测试文件，验证对功能的理解
  - `test_build_integration.py` — 构建集成测试
  - `test_sync.py` — 同步逻辑测试
  - `test_chat.py` — 对话测试
  - `test_okf.py` — OKF 格式测试
- **测试要求**:
  - **rule**: 从测试中提取的使用模式已记录
  - **evidence**: 典型用法模式清单

---

### 阶段二：I（Insight）— 洞察分析与架构理解

#### Task 4: 绘制核心架构图
- **优先级**: high
- **依赖 AC**: FR2(5), NFR3
- **状态**: pending
- **描述**: 基于源码分析，绘制 Mermaid 架构图
  - 整体架构图（CLI → Core → Fetcher/Writer/Chat/MCP/Serve）
  - BFS 爬取流程图
  - Bundle 目录结构图
  - Chat Agent 导航循环图
- **测试要求**:
  - **rubric**: 架构图准确性（0-3）
    - 3: 准确反映代码模块关系和数据流
    - 2: 核心关系正确
    - 1: 有明显错误
    - 阈值: ≥2
  - **evidence**: Mermaid 代码可正确渲染，节点与实际模块对应
  - **G2 门控**: 洞察包含四元组（现象+根因+影响+建议）

#### Task 5: 识别核心设计模式与决策
- **优先级**: high
- **依赖 AC**: FR2, NFR1
- **状态**: pending
- **描述**: 分析关键设计决策及其理由
  - 为什么选择 BFS 而非 DFS 爬取
  - URL→路径映射的设计考量（trailing slash、扩展名、query hash）
  - 目录索引（index.md）如何实现 Agent 渐进式导航
  - content hash 增量同步的设计
  - Fetcher 抽象与插件化设计
  - 零 Key 检索回退的设计哲学
- **测试要求**:
  - **rubric**: 分析深度（0-3）
    - 3: 每个设计决策有代码依据和设计理由
    - 2: 主要决策有解释
    - 1: 表面描述
    - 阈值: ≥2
  - **evidence**: 设计决策记录，每个有代码位置引用

#### Task 6: 编写 seven-concepts-report.md
- **优先级**: medium
- **依赖 AC**: NFR3, FR4
- **状态**: pending
- **描述**: 记录 R→I→E 执行过程、质量门通过情况、关键洞察
- **测试要求**:
  - **rule**: 报告包含 R/I/E 各阶段的输入输出
  - **rule**: G1/G2/G3 质量门检查结果有记录
  - **evidence**: seven-concepts-report.md 文件存在

---

### 阶段三：E（Extraction）— Wiki 章节撰写

#### Task 7: 编写 00-overview.md（概述）
- **优先级**: high
- **依赖 AC**: FR1, FR2(0), FR4, NFR2
- **状态**: pending
- **描述**: 教程概述页，包含一句话摘要、教程介绍、核心特性、章节导航、目标受众、阅读路径、术语表（≥15 个核心术语）、项目信息
- **测试要求**:
  - **rule**: 术语表 ≥15 个术语，每个术语有一句话解释
  - **rule**: 包含完整章节导航表格
  - **rule**: frontmatter 完整（id/title/source/date/category/tags）
  - **evidence**: 文件存在且符合格式规范

#### Task 8: 编写 01-installation.md（安装与配置）
- **优先级**: high
- **依赖 AC**: FR2(1), FR3
- **状态**: pending
- **描述**: 安装指南，包含前置依赖、pip/uvx 安装方式、可选依赖说明（chat/js/mcp/serve/enrich）、虚拟环境建议、~/.okf/ 目录结构、安装验证、常见安装问题
- **测试要求**:
  - **rule**: 所有 6 个 extras 依赖均有说明
  - **rule**: 安装命令可直接复制运行
  - **evidence**: 安装步骤覆盖 pyproject.toml 中所有可选依赖

#### Task 9: 编写 02-cli-reference.md（CLI 命令参考）
- **优先级**: high
- **依赖 AC**: FR2(2), FR3
- **状态**: pending
- **描述**: 完整 CLI 参考，包含全部 11 个子命令的详细说明、参数列表、使用示例
  - build/sync/validate/zip/list/get/chat/visualize/serve-mcp/serve
- **测试要求**:
  - **rule**: 所有命令和参数与 cli.py 中定义完全一致
  - **rule**: 每个命令至少一个使用示例
  - **evidence**: 对照 cli.py 逐命令验证

#### Task 10: 编写 03-okf-format.md（OKF 格式与 Bundle 结构）
- **优先级**: high
- **依赖 AC**: FR2(3)
- **状态**: pending
- **描述**: OKF v0.1 格式规范详解，包含目录结构、frontmatter 字段说明、index.md 导航机制、reserved 文件名规则、state.json 结构、log.md 历史、验证规则
- **测试要求**:
  - **rule**: frontmatter 字段与 okf.py/writer.py 中实现一致
  - **rule**: state.json 字段完整列出
  - **evidence**: 对照 model.py/okf.py/writer.py 验证

#### Task 11: 编写 04-core-architecture.md（核心架构）
- **优先级**: high
- **依赖 AC**: FR2(4), FR3
- **状态**: pending
- **描述**: 核心架构深入解析，包含模块依赖图、BFS 爬取算法、URL 规范化与路径映射、Fetcher 抽象层（HttpFetcher vs BrowserFetcher）、markdown 提取流程、Writer 写入流程、链接边计算
- **测试要求**:
  - **rubric**: 架构理解深度（0-3），阈值 ≥2
  - **rule**: 包含 Mermaid 架构图和流程图
  - **evidence**: 代码引用准确

#### Task 12: 编写 05-sync-mechanism.md（增量同步机制）
- **优先级**: medium
- **依赖 AC**: FR2(5)
- **状态**: pending
- **描述**: 增量同步机制详解，包含 content hash 原理、added/changed/removed 检测、安全阈值保护、post_sync 钩子扩展点、与 build 的代码复用
- **测试要求**:
  - **rule**: 安全阈值参数（SAFETY_MIN_PAGES=4, SAFETY_RATIO=0.5）准确记录
  - **evidence**: 对照 sync.py 验证

#### Task 13: 编写 06-chat-system.md（Chat 对话系统）
- **优先级**: high
- **依赖 AC**: FR2(6), FR3
- **状态**: pending
- **描述**: Chat 系统详解，包含 Agent 导航策略（SYSTEM prompt、工具定义、导航循环）、Provider 抽象（OpenAICompat/Anthropic/Ollama 预设）、零 Key 检索回退、对话历史管理、~/.okf/chats/ 存储、trace 模式
- **测试要求**:
  - **rule**: 所有 provider 预设（openai/ollama/openrouter/anthropic/custom）均有说明
  - **rule**: TOOLS 定义与 agent.py 一致
  - **evidence**: 对照 chat/agent.py 和 chat/providers.py 验证

#### Task 14: 编写 07-mcp-serve.md（MCP 与 HTTP 服务）
- **优先级**: medium
- **依赖 AC**: FR2(7-8)
- **状态**: pending
- **描述**: MCP 服务和本地 HTTP API 详解
  - MCP: stdio 协议、暴露的 4 个工具（list_bundles/list_directory/read_concept/search_bundle）、Docker 部署
  - HTTP API: FastAPI 端点、bearer token 认证、keychain 存储、GUI 集成
- **测试要求**:
  - **rule**: MCP 工具列表与 mcp.py 实现一致
  - **evidence**: 对照 mcp.py 和 serve/ 目录验证

#### Task 15: 编写 08-registry-visualize.md（Registry 与可视化）
- **优先级**: medium
- **依赖 AC**: FR2(9-10)
- **状态**: pending
- **描述**: Registry 机制和知识图谱可视化
  - Registry: awesome-okf-kit 注册表、registry.yaml 格式、bundle 下载与安装、本地 bundle 管理
  - Visualize: graph.html 生成、边计算逻辑、自包含 HTML 设计
- **测试要求**:
  - **rule**: DEFAULT_REGISTRY URL 准确记录
  - **evidence**: 对照 registry.py 和 visualize.py 验证

#### Task 16: 编写 09-extension-development.md（扩展与开发）
- **优先级**: medium
- **依赖 AC**: FR2(11)
- **状态**: pending
- **描述**: 扩展开发指南，包含源码结构概览、开发环境搭建（pip install -e ".[dev]"）、测试运行（pytest）、代码规范（ruff）、自定义 Fetcher 开发、calknowledge 生态关系、贡献指南
- **测试要求**:
  - **rule**: 开发命令与 CONTRIBUTING.md/pyproject.toml 一致
  - **evidence**: 开发步骤可实际执行

#### Task 17: 编写 10-faq-troubleshooting.md（FAQ 与排错）
- **优先级**: medium
- **依赖 AC**: FR2(12), FR3
- **状态**: pending
- **描述**: 常见问题与排错指南，包含 JS 渲染站点识别与处理、robots.txt 问题、短页面警告、连接错误、Provider 认证失败、模型不存在、Ollama 连接问题、Bundle 验证失败
- **测试要求**:
  - **rule**: 错误信息与 providers.py 中 describe_provider_error 一致
  - **rubric**: 实用性（0-3），阈值 ≥2
  - **evidence**: 每个问题有具体诊断步骤和解决方案

#### Task 18: 编写 11-summary-resources.md（总结与资源）
- **优先级**: low
- **依赖 AC**: FR2(13)
- **状态**: pending
- **描述**: 总结页，包含核心知识点回顾、命令速查表、生态链接（okf-desktop、calknowledge、awesome-okf-kit、knowledge-catalog）、相关项目对比、进一步学习资源
- **测试要求**:
  - **rule**: 包含完整命令速查表
  - **evidence**: 资源链接有效

#### Task 19: 更新 docs/knowledge/learning/03-agent-platforms-tools/README.md 索引
- **优先级**: low
- **依赖 AC**: FR1
- **状态**: pending
- **描述**: 在 learning wiki 索引中添加 okf-kit-wiki 条目
- **测试要求**:
  - **rule**: README.md 中包含 okf-kit-wiki 链接
  - **evidence**: 索引更新完成
  - **G3 门控**: 产出的 wiki 结构可作为其他工具教程的模板复用

---

## 任务依赖关系

```
Task 1 (创建目录)
  └─→ Task 2 (研读源码)
        ├─→ Task 3 (研读测试)
        │     └─→ Task 4 (架构图)
        │           ├─→ Task 5 (设计决策)
        │           │     ├─→ Task 6 (方法论报告)
        │           │     └─→ Task 7 (00-overview)
        │           │           ├─→ Task 8 (01-installation)
        │           │           │     └─→ Task 9 (02-cli-reference)
        │           │           │           ├─→ Task 10 (03-okf-format)
        │           │           │           │     ├─→ Task 11 (04-architecture)
        │           │           │           │     │     ├─→ Task 12 (05-sync)
        │           │           │           │     │     │     ├─→ Task 13 (06-chat)
        │           │           │           │     │     │     │     ├─→ Task 14 (07-mcp-serve)
        │           │           │           │     │     │     │     │     ├─→ Task 15 (08-registry)
        │           │           │           │     │     │     │     │     │     ├─→ Task 16 (09-extension)
        │           │           │           │     │     │     │     │     │     │     ├─→ Task 17 (10-faq)
        │           │           │           │     │     │     │     │     │     │     │     └─→ Task 18 (11-summary)
        │           │           │           │     │     │     │     │     │     │     │           └─→ Task 19 (更新索引)
```

## 完成定义（DoD）

所有任务完成需满足：

1. 所有 Task 状态为 completed
2. 每个 rule 类型 TR 有 passing evidence
3. 每个 rubric 类型 TR 达到阈值分数且有 rationale 和 evidence
4. G1/G2/G3 质量门全部通过
5. 独立 Review 结果为 pass
