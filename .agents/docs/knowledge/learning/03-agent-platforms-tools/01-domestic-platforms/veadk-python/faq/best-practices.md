---
id: best-practices
title: 最佳实践与常见反模式
source: veadk-python codebase analysis (11-architecture-insights.md)
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 最佳实践与常见反模式

本文档基于 VeADK 架构洞察（10条核心设计决策）和代码分析，提炼出开发最佳实践和应当避免的反模式。

---

## 一、Agent 设计最佳实践

### 1.1 Instruction 编写最佳实践

**原则**：instruction 是 LLM 的行为准则，直接决定 Agent 的表现质量。

**最佳实践**：
- **明确角色定位**：首句清晰定义Agent身份和核心职责
- **给出工具使用指引**：说明何时使用哪个工具、工具间的调用顺序
- **约束输出格式**：明确要求输出格式（如JSON、Markdown、自然语言）
- **提供few-shot示例**：通过示例展示期望的交互模式
- **说明边界条件**：明确Agent不能做什么、遇到无法处理的情况如何回应

**参考**：[examples/02_custom_tools/main.py:66-70](file:///d:/AI/.chaos/libs/veadk-python/examples/02_custom_tools/main.py#L66-L70)

```python
instruction=(
    "You help users with weather. Use `get_city_weather` to look up "
    "conditions, then `recommend_clothing` based on the temperature. "
    "Always state the temperature you used."
),
```

### 1.2 工具选择最佳实践

- **显式传入工具列表**：初始化后检查 `agent.tools`，确认自动挂载的工具符合预期
- **精简工具集**：只挂载Agent实际需要的工具，过多工具会干扰LLM选择
- **工具描述质量优先**：工具的docstring/description是LLM选择工具的依据，务必写清晰
- **注意自动追加工具**：传入knowledgebase/long_term_memory/enable_authz等参数时，框架会自动追加对应工具（架构洞察1）

参考：[架构洞察1 - 初始化后检查工具列表](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L34-L38)

### 1.3 模型选择最佳实践

- **高可用场景配置fallback**：传入模型列表实现故障转移
  ```python
  model_name=["doubao-pro", "doubao-lite"]  # 主模型 + fallback
  ```
  参考：[架构洞察4 - Fallback模型链](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L117-L118)

- **按场景选择客户端**：
  - 需要豆包原生特性（多轮缓存、多模态）→ `enable_responses=True`（ArkLlm）
  - 需要通用OpenAI兼容接口 → `enable_responses=False`（LiteLlm）
  参考：[架构洞察4 - 双客户端切换](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L118)

- **不要覆盖默认头信息**：自定义 `model_extra_config` 时不要覆盖 `veadk-version`、`x-is-encrypted` 等默认头
  参考：[架构洞察4 - 用户覆盖风险](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L124)

### 1.4 Runtime选择最佳实践

- **默认使用 `runtime="adk"`**：获得最完整的Google ADK功能支持
- **生产环境固定runtime类型**：避免运行时切换导致不可预测行为
- **codex/piagent runtime注意功能差异**：非adk runtime不经过ADK原生LlmFlow，sub_agents复杂编排可能行为不一致
参考：[架构洞察3 - 使用建议](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L104-L108)

---

## 二、记忆配置最佳实践

### 2.1 短期记忆（ShortTermMemory）

- **开发环境**：可使用SQLite后端（默认），无需额外依赖
- **生产环境**：使用PostgreSQL或MySQL后端，支持多实例部署
- **不推荐在生产使用local内存后端**：in-memory后端重启数据丢失，多实例状态不一致

```python
from veadk.memory import ShortTermMemory
from veadk.memory.short_term_memory_backends import PostgresqlBackend

stm = ShortTermMemory(
    backend=PostgresqlBackend(
        host="localhost",
        port=5432,
        database="veadk",
        user="postgres",
        password="...",
    )
)
```

### 2.2 长期记忆（LongTermMemory）

- **开发/测试**：in_memory_backend（快速验证）
- **生产环境**：根据基础设施选择：
  - Redis：高性能、适合简单场景
  - OpenSearch/VikingDB：向量检索能力强
  - Mem0：支持高级记忆管理

```python
from veadk.memory import LongTermMemory
from veadk.memory.long_term_memory_backends import RedisBackend

ltm = LongTermMemory(
    backend=RedisBackend(
        index="agent-memory",
        redis_url="redis://localhost:6379/0",
    )
)
```

### 2.3 记忆使用场景判断

| 场景 | 使用短期记忆 | 使用长期记忆 |
|---|---|---|
| 多轮对话上下文 | ✅ | ❌ |
| 跨会话用户偏好 | ❌ | ✅ |
| 对话历史保存 | ✅ | ❌ |
| 用户画像积累 | ❌ | ✅ |
| 会话隔离需求 | ✅ | ✅ |

---

## 三、知识库RAG最佳实践

### 3.1 分块策略

- **按语义分块**：优先按段落/章节分块，而非固定字符数
- **块大小建议**：256-1024 tokens，根据文档类型调整
- **重叠分块**：块间保留10-20%重叠，避免上下文断裂
- **元数据标注**：为每个块添加来源、标题、章节等元数据

### 3.2 检索参数配置

- **top_k**：默认3-5，根据文档复杂度调整
- **相似度阈值**：设置最低相似度分数过滤不相关结果
- **混合检索**：向量检索 + 关键词检索结合（如OpenSearch支持）

### 3.3 后端选择

| 后端 | 适用场景 | 特点 |
|---|---|---|
| in_memory | 开发测试 | 零依赖，重启丢失 |
| Milvus | 生产环境大规模 | 高性能向量数据库 |
| OpenSearch | 已有ES生态 | 支持混合检索 |
| VikingDB | 火山引擎生态 | 原生集成 |
| Redis | 小规模快速验证 | 简单但功能有限 |

```python
from veadk.knowledgebase import KnowledgeBase
from veadk.knowledgebase.backends import MilvusBackend

kb = KnowledgeBase(
    backend=MilvusBackend(
        index="my-docs",
        host="localhost",
        port=19530,
    )
)
await kb.add_from_directory("./docs/")
```

---

## 四、工具开发最佳实践

### 4.1 函数式工具优先

简单无状态工具优先使用函数式工具，代码最简洁：

```python
def my_tool(param: str, tool_context: ToolContext | None = None) -> dict:
    """清晰的工具描述。"""
    ...
```

只有需要状态管理、复杂参数Schema或Tracing时才使用类式工具（继承BaseTool）。

### 4.2 描述编写规范

- 首句即核心功能
- 明确"什么时候该用"
- 参数说明详尽（含义、格式、示例）
- 返回值结构说明
- 包含使用示例
参考：[工具描述最佳实践](../extensions/custom-tool.md#五工具描述最佳实践)

### 4.3 错误处理

- 返回错误字符串，而非抛出异常
- 错误信息要有指导性（告诉LLM如何修正）
- 日志中脱敏敏感信息
- 参考：[工具错误处理模式](../extensions/custom-tool.md#六错误处理)

### 4.4 凭证管理

工具中获取凭证遵循四级优先级链（参考web_search实现）：
1. 工具专属环境变量
2. ToolContext状态
3. 全局环境变量
4. IAM角色（云端部署）

参考：[web_search.py:40-65](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L40-L65)

### 4.5 ToolContext使用

`tool_context` 提供运行时上下文访问：
- `tool_context.state`：会话状态字典，可跨工具共享数据
- `tool_context.session.id`：会话ID
- `tool_context._invocation_context.user_id`：用户ID

---

## 五、错误处理最佳实践

### 5.1 分层错误处理

1. **工具层**：捕获工具内部异常，返回友好错误信息给LLM
2. **RunProcessor层**：使用RunProcessor实现全局错误处理、重试逻辑
3. **应用层**：Runner/Agent外的全局异常捕获，处理致命错误

### 5.2 异步错误处理

- 异步工具中使用 `try/except` 包裹await调用
- 使用 `asyncio.to_thread()` 包装同步阻塞操作，避免阻塞事件循环
- Process中的异常要正确传递，不要静默吞掉

### 5.3 错误日志

- 预期内错误用 `logger.warning/debug`
- 未知异常用 `logger.exception` 记录完整栈
- 日志中脱敏API Key、Secret、Token等敏感信息

---

## 六、配置管理最佳实践

### 6.1 API Key四级优先级

API Key解析遵循严格优先级（参考[架构洞察7](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L193-L231)）：

1. **显式传参** `model_api_key="..."` → 优先级最高
2. **环境变量** `MODEL_AGENT_API_KEY` → 容器化部署推荐
3. **ARK Token服务** `model_api_key_name="..."` → 企业级密钥轮换
4. **配置文件** `settings.model.api_key` → 本地开发

认证失败排查顺序：显式传参 → 环境变量 → key_name配置 → config.yaml默认值。

### 6.2 环境变量命名规范

- 框架内部变量：`VOLCENGINE_ACCESS_KEY`、`MODEL_AGENT_API_KEY`
- 工具专属变量：`TOOL_WEB_SEARCH_ACCESS_KEY`、`TOOL_FEISHU_CHANNEL_APP_ID`
- 云服务商切换：`CLOUD_PROVIDER=byteplus` 切换到BytePlus海外环境

### 6.3 配置文件安全

- `config.yaml` 包含敏感信息，**不要提交到Git**
- 使用 `.env` 文件管理本地配置，确保在 `.gitignore` 中
- 生产环境通过环境变量注入，不依赖配置文件
- 参考vefaas.mdx的警告：[config.yaml安全提示](file:///d:/AI/.chaos/libs/veadk-python/docs/content/docs/framework/vefaas.mdx#L129-L131)

### 6.4 BytePlus跨云配置

BytePlus海外用户只需设置：
```bash
export CLOUD_PROVIDER=byteplus
export BYTEPLUS_ACCESS_KEY=your_ak
export BYTEPLUS_SECRET_KEY=your_sk
```
框架会自动映射到火山引擎环境变量名，无需重复设置。参考：[架构洞察7 - BytePlus自动映射](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L215)

---

## 七、性能优化建议

### 7.1 模型调用优化

- 配置fallback模型链提高可用性
- 使用流式输出（`streaming_mode=SSE`）提升首字响应时间
- 合理设置 `max_llm_calls` 防止无限循环
- 高并发场景考虑连接池配置

### 7.2 工具执行优化

- IO密集型工具使用异步实现
- 缓存重复的API调用结果到 `tool_context.state`
- 批量操作合并，减少LLM调用轮次
- 外部API调用设置合理超时

### 7.3 记忆/知识库优化

- 短期记忆定期清理过期会话
- 知识库定期重建索引
- 向量检索设置合理的top_k，避免返回过多无关内容
- 生产环境使用持久化后端，避免in-memory

### 7.4 Tracing和监控

启用Tracing便于性能分析：
```python
from veadk.tracing.telemetry.exporters import TlsExporter, InMemoryExporter

agent = Agent(
    ...,
    tracers=[TlsExporter(...)],  # 上报到TLS日志服务
)
```

---

## 八、回调链最佳实践

`before_agent_callback`、`after_agent_callback`、`before_tool_callback` 支持单函数/列表双形态（架构洞察2）。

### 最佳实践
- 需要精确控制顺序时直接传入列表形式
- 自定义回调做好幂等性设计，防止重复执行副作用
- 初始化后检查回调链确认顺序
- 框架自动添加的回调顺序：authz → dynamic_load_skills（如需移除可初始化后过滤）

参考：[架构洞察2 - 使用建议](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L70-L74)

---

## 九、反模式清单

以下做法已在代码分析中被证实存在风险或已被弃用，应当避免。

### ❌ 反模式1：使用 `skills_mode='local'`

**风险**：local模式已标记 `DeprecationWarning`，是废弃功能。

**代码依据**：[veadk/agent.py:537-547](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L180)

**正确做法**：
- 使用 Google ADK 原生的 `load_skill_from_dir`
- 或使用 VeSkillRegistry 技能注册机制
- 云端部署无需设置skills_mode，框架自动探测

---

### ❌ 反模式2：生产环境使用local内存后端

**风险**：in-memory后端数据存储在进程内存中，重启丢失，多实例部署时状态不一致。

**影响组件**：
- 短期记忆 `in_memory_backend`
- 长期记忆 `in_memory_backend`
- 知识库 `in_memory_backend`
- A2A Hub的内存存储
- A2A InMemoryTaskStore

**正确做法**：
- 生产短期记忆用PostgreSQL/MySQL
- 生产长期记忆用Redis/OpenSearch/VikingDB
- 生产知识库用Milvus/OpenSearch
- 参考对应backend目录的持久化实现

---

### ❌ 反模式3：硬编码API Key

**风险**：密钥泄露风险，无法轮换，不同环境无法切换。

**错误示例**：
```python
# ❌ 错误：硬编码密钥
agent = Agent(
    model_api_key="sk-abc123xyz...",
    ...
)
```

**正确做法**：
```python
# ✅ 正确：通过环境变量注入
import os
agent = Agent(
    model_api_key=os.getenv("MODEL_AGENT_API_KEY"),
    ...
)
```
生产环境使用密钥管理服务或IAM角色。

---

### ❌ 反模式4：初始化后不检查工具列表

**风险**：框架会根据knowledgebase/memory/enable_authz等参数自动追加工具，可能引入预期外的工具。

**代码依据**：[架构洞察1 - 隐式行为风险](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L30)

**正确做法**：
```python
agent = Agent(
    knowledgebase=kb,
    long_term_memory=ltm,
    tools=[my_tool],
)
# 初始化后检查
print([t.name for t in agent.tools])
```

---

### ❌ 反模式5：RunProcessor中不转发所有事件

**风险**：在 `async for event in event_generator_func()` 循环中遗漏 `yield event`，导致事件丢失，Agent响应不完整。

**错误示例**：
```python
async def wrapper():
    async for event in event_generator_func():
        pass  # ❌ 没有yield，事件被吞掉！
```

**正确做法**：必须yield所有事件，参考[RunProcessor开发注意事项](../extensions/custom-run-processor.md#七开发注意事项)

---

### ❌ 反模式6：覆盖默认model_extra_config头信息

**风险**：覆盖 `veadk-version`、`x-is-encrypted`、`veadk-source` 等默认头可能导致后端兼容性问题。

**代码依据**：[架构洞察4 - 用户覆盖风险](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L124)

**正确做法**：只添加自定义头，不修改已有默认头。

---

### ❌ 反模式7：Processor中替换runner方法后不恢复

**风险**：在RunProcessor中替换 `runner.run_async` 等方法后不在finally中恢复，会导致后续调用异常。

**正确做法**：参考AuthRequestProcessor的模式：
```python
original_run_async = runner.run_async
runner.run_async = wrapped_run_async
try:
    async for chunk in event_generator_func():
        yield chunk
finally:
    runner.run_async = original_run_async  # ✅ 必须恢复
```

---

### ❌ 反模式8：同步阻塞操作不包装

**风险**：在async函数中直接执行同步阻塞IO（如time.sleep、同步requests调用）会阻塞整个事件循环。

**错误示例**：
```python
async def my_tool():
    import time
    time.sleep(5)  # ❌ 阻塞事件循环
```

**正确做法**：
```python
async def my_tool():
    await asyncio.to_thread(time.sleep, 5)  # ✅ 在线程池中执行
```

---

### ❌ 反模式9：日志中输出敏感信息

**风险**：API Key、Secret、Token等敏感信息输出到日志会造成泄露。

**正确做法**：
- 参考ve_faas.py的正则脱敏模式
- 打印响应前先脱敏敏感字段
- 避免直接打印整个config对象

---

### ❌ 反模式10：使用空model_name列表依赖默认值

**风险**：虽然框架会回退到settings默认模型，但显式指定模型更清晰可控。

**正确做法**：
```python
model_name="doubao-pro"  # ✅ 显式指定
# 或
model_name=["doubao-pro", "doubao-lite"]  # ✅ 显式指定主备
```

---

## 十、检查清单

开发前对照以下清单：

### Agent配置
- [ ] instruction清晰定义角色和工具使用方式
- [ ] 显式指定model_name（或模型列表）
- [ ] 初始化后检查agent.tools列表
- [ ] 生产环境runtime固定为"adk"
- [ ] API Key通过环境变量注入，未硬编码

### 工具开发
- [ ] 工具描述清晰，首句说明核心功能
- [ ] 参数有类型提示和完整docstring
- [ ] 错误返回字符串而非抛出异常
- [ ] 异步IO使用async/await或asyncio.to_thread
- [ ] 凭证从环境变量/ToolContext/IAM链获取

### 记忆/知识库
- [ ] 生产环境使用持久化后端（PostgreSQL/Redis/Milvus等）
- [ ] 未在生产使用in-memory后端
- [ ] 知识库分块策略合理

### 安全
- [ ] config.yaml/.env在.gitignore中
- [ ] 日志脱敏敏感信息
- [ ] 生产环境启用网关认证
- [ ] 未硬编码任何密钥
