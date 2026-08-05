---
id: 04-examples-inventory
title: examples/ 目录示例清单
source: veadk-python codebase analysis
---

## 示例清单（共13个）

| 编号 | 目录名 | README 描述功能 | 核心 .py 文件名 |
|------|--------|-----------------|-----------------|
| 1 | 01_quickstart | 最小化 VeADK 程序示例，演示 Agent 承载模型和指令、Runner 驱动对话并返回最终答案 | main.py |
| 2 | 02_custom_tools | 演示如何让 Agent 调用自定义 Python 函数作为工具，工具需包含类型提示和文档字符串 | main.py |
| 3 | 03_short_term_memory | 演示短期记忆（多轮对话）功能，通过 session_id 标识对话上下文，支持 sqlite 等后端持久化 | main.py |
| 4 | 04_web_search | 演示内置 web_search 工具的使用，该工具调用火山引擎搜索 API 获取实时信息 | main.py |
| 5 | 05_knowledgebase_rag | 演示知识库 RAG 功能，使用 KnowledgeBase 将文档嵌入向量存储，挂载到 Agent 后自动添加检索工具 | main.py |
| 6 | 06_multi_agent | 演示多智能体工作流，包含 SequentialAgent 顺序执行和 ParallelAgent 并行执行两种模式 | main.py、parallel.py |
| 7 | 07_structured_output | 演示结构化输出功能，通过传入 Pydantic 模型作为 output_schema，让 Agent 返回符合 schema 的 JSON | main.py |
| 8 | 08_model_config | 演示模型配置，包括设置主模型和备用模型（fallbacks）、传递额外请求选项等 | main.py |
| 9 | 09_long_term_memory | 演示长期记忆功能，可跨会话记忆事实，支持 local、openviking、redis 等后端 | main.py |
| 10 | 10_agent_routing | 演示智能体动态路由功能，由协调者 Agent 在运行时决定将请求转发给哪个专门子智能体 | main.py |
| 11 | 11_tracing | 演示链路追踪与可观测性功能，通过挂载 tracer 记录每个 LLM 调用和工具调用，生成 trace_id | main.py |
| 12 | 12_mcp-tunnel | 演示隧道功能，通过出站隧道将企业内网的 MCP 服务器连接到云端 Agent，无需开放入站端口 | app.py、connector.py |
| 13 | 13_openviking | 演示使用 OpenViking 同时作为知识库检索和长期记忆后端，远程处理索引和记忆提取 | main.py |

---

本文件列出了 examples/ 目录下的13个编号示例。每个示例包含目录名、README 中描述的功能以及核心 .py 文件名。清单覆盖了快速开始、自定义工具、短期/长期记忆、网络搜索、知识库 RAG、多智能体工作流、结构化输出、模型配置、智能体路由、链路追踪、MCP 隧道、OpenViking 集成等功能场景。所有描述均直接从对应示例的 README 文件中提取，未进行主观评价或修改。
