---
id: 05-core-classes-list
title: 核心类清单
source: veadk-python codebase analysis
---

## 核心类概览

| 类名 | 文件路径 | 类签名 |
|------|----------|--------|
| Runner | veadk/runner.py | `class Runner(ADKRunner)` |
| AgentBuilder | veadk/agent_builder.py | `class AgentBuilder` |
| VeADKConfig（Config） | veadk/config.py | `class VeADKConfig(BaseModel)` |
| ShortTermMemory | veadk/memory/short_term_memory.py | `class ShortTermMemory(BaseModel)` |
| LongTermMemory | veadk/memory/long_term_memory.py | `class LongTermMemory(BaseMemoryService, BaseModel)` |
| KnowledgeBase | veadk/knowledgebase/knowledgebase.py | `class KnowledgeBase(BaseModel)` |

## 各类简要信息

### Runner
- 文件：veadk/runner.py:329
- 继承自 google.adk.runners.Runner（ADKRunner）
- 功能：驱动 Agent 对话执行，集成短期记忆、长期记忆、链路追踪、媒体上传等能力

### AgentBuilder
- 文件：veadk/agent_builder.py:38
- 无显式父类
- 功能：从 YAML 配置文件构建 Agent 实例，支持子智能体和工具的动态加载

### VeADKConfig（Config）
- 文件：veadk/config.py:64
- 继承自 pydantic.BaseModel
- 功能：全局配置类，包含模型配置、工具配置、可观测性配置、数据库配置、TOS 配置、VeIdentity 配置等，全局实例为 `settings`

### ShortTermMemory
- 文件：veadk/memory/short_term_memory.py:57
- 继承自 pydantic.BaseModel
- 功能：短期记忆（会话上下文）管理，支持 local（内存）、mysql、sqlite、postgresql、database 等后端

### LongTermMemory
- 文件：veadk/memory/long_term_memory.py:98
- 继承自 google.adk.memory.base_memory_service.BaseMemoryService 和 pydantic.BaseModel
- 功能：长期记忆管理，支持 local、opensearch、viking、redis、mem0、openviking、tos_context 等后端

### KnowledgeBase
- 文件：veadk/knowledgebase/knowledgebase.py:92
- 继承自 pydantic.BaseModel
- 功能：知识库 RAG 管理，支持 local、opensearch、redis、milvus、tos_vector、viking、context_search、openviking 等后端

---

本文件列出了 Runner、AgentBuilder、Config、ShortTermMemory、LongTermMemory、KnowledgeBase 六个核心类的文件路径和类签名概览。其中 Config 对应代码中的 VeADKConfig 类，该类在 veadk/config.py 中定义并实例化为全局 settings 对象。所有类签名和继承关系均直接从源代码中提取，未进行主观推断。该清单为快速定位核心类位置提供索引。
