---
id: knowledgebase-module
title: 知识库(RAG)详解
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 知识库(RAG)详解

KnowledgeBase 模块提供检索增强生成（Retrieval-Augmented Generation, RAG）能力，允许 Agent 从私有文档中检索相关信息，基于你的内容而非仅依赖模型通用知识回答问题。

---

## 知识库 RAG 概述

### 什么是 RAG

RAG（检索增强生成）是一种将外部知识检索与大语言模型生成相结合的技术范式：

1. **索引阶段**：将文档切分、向量化（Embedding）后存储到向量数据库
2. **检索阶段**：用户提问时，将问题向量化并在向量库中检索最相关的文档片段
3. **生成阶段**：将检索到的相关片段作为上下文注入到 Prompt 中，供模型参考生成回答

### 为什么需要知识库

| 场景 | 问题 | 知识库解决方案 |
|------|------|---------------|
| 私有数据 | 模型训练数据不包含内部文档/FAQ/产品手册 | 注入私有知识，回答有据可依 |
| 时效性 | 模型知识截止于训练时间，无法获取最新信息 | 实时更新知识库，检索最新内容 |
| 幻觉减少 | 模型可能编造不存在的事实 | 基于检索内容回答，可溯源引用 |
| 领域定制 | 通用模型缺乏特定行业/企业术语理解 | 注入领域文档，提升回答专业性 |

VeADK 的 KnowledgeBase 封装了向量存储、文档加载、相似度检索等能力，挂载到 Agent 后自动提供检索工具，让 Agent 能"查阅"你的文档。

---

## KnowledgeBase 类 API

### 接口定义

**类签名**：
```python
class KnowledgeBase(BaseModel):
```

- 基类：`pydantic.BaseModel`
- 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L92-L357](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L92-L357)

### 构造参数

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `name` | `str` | `"user_knowledgebase"` | 知识库名称 |
| `description` | `str` | `"This knowledgebase stores some user-related information."` | 知识库描述 |
| `backend` | `Literal[...] \| BaseKnowledgebaseBackend` | `"local"` | 向量数据库后端类型或自定义后端实例。支持：`"local"`, `"opensearch"`, `"viking"`, `"redis"`, `"milvus"`, `"tos_vector"`, `"context_search"`, `"openviking"` |
| `backend_config` | `dict` | `{}` | 后端配置字典，若提供则直接传递给后端构造函数 |
| `top_k` | `int` | `10` | 检索时返回的最相似文档数量 |
| `app_name` | `str` | `""` | 关联的应用名称。若 `index` 未设置，将使用此值作为索引名 |
| `index` | `str` | `""` | 知识库索引/集合名称。必须提供 `index` 或 `app_name` 之一，否则抛出 `ValueError` |
| `enable_profile` | `bool` | `False` | 是否启用查询画像（profile）功能。启用后额外挂载 `load_kb_queries` 工具 |
| `query_with_user_profile` | `bool` | `False` | 是否使用用户画像进行查询增强。需配合 Viking Memory 后端使用 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L126-L154](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L126-L154)

**初始化校验逻辑**：
- 若传入 `BaseKnowledgebaseBackend` 实例，直接使用该实例作为后端
- 若 `backend_config` 非空，使用配置字典初始化后端
- 否则必须提供 `index` 或 `app_name`，否则抛出 `ValueError("Either 'index' or 'app_name' must be provided.")`

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L156-L185](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L156-L185)

### 核心方法

#### `add_from_directory` 方法
```python
def add_from_directory(self, directory: str, **kwargs) -> bool:
```
将指定目录下的所有文件添加到知识库。目录中的文件会被自动加载、分块、向量化后存储。

**参数**：
- `directory: str` - 目录路径
- `**kwargs` - 传递给后端的额外参数（如分块大小、重叠等）

**返回**：`bool` - 成功返回 `True`，失败返回 `False`

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L187-L211](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L187-L211)

#### `add_from_files` 方法
```python
def add_from_files(self, files: list[str], **kwargs) -> bool:
```
将指定文件列表添加到知识库。

**参数**：
- `files: list[str]` - 文件路径列表
- `**kwargs` - 传递给后端的额外参数

**返回**：`bool` - 成功返回 `True`，失败返回 `False`

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L213-L237](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L213-L237)

#### `add_from_text` 方法
```python
def add_from_text(self, text: str | list[str], **kwargs) -> bool:
```
直接将文本（或文本列表）添加到知识库。文本会被向量化后存储。适用于动态添加知识片段的场景。

**参数**：
- `text: str | list[str]` - 文本字符串或文本列表
- `**kwargs` - 传递给后端的额外参数

**返回**：`bool` - 成功返回 `True`，失败返回 `False`

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L239-L263](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L239-L263)

#### `search` 方法
```python
def search(self, query: str, top_k: int = 0, **kwargs) -> list[KnowledgebaseEntry]:
```
根据查询文本检索相关文档片段。

**参数**：
- `query: str` - 查询文本
- `top_k: int` - 返回结果数量，为 0 时使用构造函数中的 `self.top_k`（默认 10）
- `**kwargs` - 传递给后端的额外检索参数

**返回**：`list[KnowledgebaseEntry]` - 检索结果列表，每个结果包含 `content`（文本内容）和可选的 `metadata`（元数据）

返回结果规范化处理：
- 后端返回 `KnowledgebaseEntry` 实例 → 直接保留
- 后端返回 `str` → 包装为 `KnowledgebaseEntry(content=entry)`
- 其他类型 → 记录错误日志并跳过

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L265-L282](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L265-L282)

#### `close` 方法
```python
def close(self) -> None:
```
释放后端资源。若后端实现了 `close()` 方法则调用，否则无操作。适用于需要显式关闭连接的后端（如数据库连接）。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L284-L288](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L284-L288)

#### `__getattr__` 方法
```python
def __getattr__(self, name) -> Callable:
```
代理后端的其他方法。允许直接调用后端实现的扩展方法，如 `delete()`、`list_chunks()`、`list_docs()` 等，无需在 KnowledgeBase 类中显式定义。

```python
# 例如：如果后端支持 delete，可以直接调用
knowledgebase.delete(document_id="doc-123")
# 等价于 knowledgebase._backend.delete(document_id="doc-123")
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L290-L295](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L290-L295)

#### `generate_profiles` 方法（异步）
```python
async def generate_profiles(self, files: list[str], profile_path: str = ""):
```
为文档生成知识库画像（profile）。使用一个 `profile_generator` Agent 读取文档内容，生成结构化的 JSON 画像，包含 name、description、tags、keywords 字段。画像保存到 `./profiles/knowledgebase/profiles_<index>/` 目录。

**参数**：
- `files: list[str]` - 待生成画像的文件路径列表
- `profile_path: str` - 画像保存路径，为空时使用默认路径

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L297-L357](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L297-L357)

### KnowledgebaseEntry 结果结构

检索结果的数据结构：

```python
class KnowledgebaseEntry(BaseModel):
    content: str
    metadata: dict | None = None
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `str` | 检索到的文档片段文本内容 |
| `metadata` | `dict \| None` | 可选元数据，可能包含来源文件、页码、相似度分数等 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/entry.py#L18-L25](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/entry.py#L18-L25)

### KnowledgebaseProfile 画像结构

```python
class KnowledgebaseProfile(BaseModel):
    name: str
    description: str
    tags: list[str]
    keywords: list[str]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 知识库/文档名称 |
| `description` | `str` | 知识库描述 |
| `tags` | `list[str]` | 分类标签，建议 3-5 个 |
| `keywords` | `list[str]` | 推荐查询关键词，建议 3-5 个 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/types.py#L18-L29](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/types.py#L18-L29)

---

## 支持的向量数据库后端

| 后端类型 | 对应实现类 | 依赖分组 | 适用场景 |
|----------|-----------|---------|---------|
| `local` | `InMemoryKnowledgeBackend` | extensions（llama-index） | 开发测试、内存向量存储，进程退出后数据丢失 |
| `opensearch` | `OpensearchKnowledgeBackend` | extensions（llama-index, opensearch-py） | 生产级 OpenSearch 集群 |
| `redis` | `RedisKnowledgeBackend` | database/extensions（redis, llama-index-redis） | Redis 向量检索，适合缓存场景 |
| `milvus` | `MilvusKnowledgeBackend` | extensions（llama-index-milvus, pymilvus） | Milvus 专业向量数据库 |
| `tos_vector` | `TosVectorKnowledgeBackend` | 内置（tos） | 火山引擎 TOS 向量存储 |
| `viking` | `VikingDBKnowledgeBackend` | 内置（vikingdb-python-sdk） | 火山引擎 VikingDB 向量数据库 |
| `context_search` | `ContextSearchBackend` | 内置 | 火山引擎上下文搜索服务 |
| `openviking` | `OpenVikingKnowledgeBackend` | 内置（openviking-sdk） | OpenViking 托管检索服务 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L30-L89](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L30-L89)

**注意**：基于 llama-index 的向量后端（local/opensearch/redis/milvus）需要安装 `veadk-python[extensions]`。导入失败时会抛出明确的 ImportError 提示安装。

### 后端基类接口

所有知识库后端必须实现 `BaseKnowledgebaseBackend` 抽象基类：

```python
class BaseKnowledgebaseBackend(ABC, BaseModel):
    index: str

    @abstractmethod
    def precheck_index_naming(self) -> None:
        """检查索引名称合法性，不合法时抛出异常"""

    @abstractmethod
    def add_from_directory(self, directory: str, *args, **kwargs) -> bool:
        """从目录添加文档"""

    @abstractmethod
    def add_from_files(self, files: list[str], *args, **kwargs) -> bool:
        """从文件列表添加文档"""

    @abstractmethod
    def add_from_text(self, text: str | list[str], *args, **kwargs) -> bool:
        """从文本添加知识"""

    @abstractmethod
    def search(self, *args, **kwargs) -> list:
        """检索相关文档"""
```

可选扩展方法（基类注释中预留）：
- `delete(**kwargs) -> bool` - 删除集合或文档
- `list_docs(**kwargs)` - 列出原始文档
- `list_chunks(**kwargs)` - 列出向量化后的文档块

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/backends/base_backend.py#L20-L72](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/backends/base_backend.py#L20-L72)

---

## 文档加载与检索流程

```mermaid
flowchart TD
    A[用户文档] --> B[文档加载]
    B --> C[文本分块 Chunking]
    C --> D[向量化 Embedding]
    D --> E[存储到向量数据库]

    F[用户提问] --> G[问题向量化]
    G --> H[向量相似度检索]
    E --> H
    H --> I[Top-K 相关片段]
    I --> J[注入到 Prompt 上下文]
    J --> K[LLM 生成回答]
    K --> L[返回给用户]

    subgraph 索引阶段（离线）
        A
        B
        C
        D
        E
    end

    subgraph 检索阶段（在线）
        F
        G
        H
        I
        J
        K
        L
    end
```

**流程说明**：

1. **索引阶段**（一次性或增量执行）：
   - 通过 `add_from_directory`/`add_from_files`/`add_from_text` 导入文档
   - 后端自动完成文档解析、文本分块、Embedding 向量化
   - 向量和原始文本存储到选定的向量数据库

2. **检索阶段**（每次提问时执行）：
   - Agent 通过自动挂载的 `load_knowledgebase` 工具调用检索
   - 用户问题向量化后在向量库中进行相似度搜索
   - 返回 Top-K 最相关文档片段
   - 检索结果作为上下文注入到模型 Prompt 中
   - 模型基于检索内容生成回答，减少幻觉

---

## enable_profile 查询画像功能

`enable_profile=True` 启用查询画像功能，用于多知识库场景下的智能路由。

### 功能机制

启用后，Agent 初始化时会额外挂载 `load_kb_queries` 工具：

```python
if self.knowledgebase.enable_profile:
    from veadk.tools.builtin_tools.load_kb_queries import load_kb_queries
    self.tools.append(load_kb_queries)
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L316-L324](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L316-L324)

### 使用流程

1. **离线生成画像**：为每个知识库/文档调用 `generate_profiles()`，生成包含 name/description/tags/keywords 的 JSON 画像
2. **在线查询路由**：Agent 先调用 `load_kb_queries` 工具，根据用户问题匹配最相关的知识库画像
3. **定向检索**：在匹配到的知识库中执行精确检索，提升检索效率和准确率

此功能适用于挂载多个知识库的场景（如企业内有产品手册、HR 政策、技术文档等多个独立知识库），通过画像帮助 Agent 选择正确的知识库进行检索。

### query_with_user_profile

`query_with_user_profile=True` 启用用户画像增强查询，需要配合 Viking Memory 后端使用，将长期记忆中的用户偏好信息用于检索结果的个性化排序。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L182-L185](file:///d:/AI/.chaos/libs/veadk-python/veadk/knowledgebase/knowledgebase.py#L182-L185)

---

## 知识库工具自动挂载机制

将 KnowledgeBase 实例传入 Agent 构造函数后，VeADK 在初始化阶段自动完成工具挂载：

```python
if self.knowledgebase:
    from veadk.tools.builtin_tools.load_knowledgebase import LoadKnowledgebaseTool
    load_knowledgebase_tool = LoadKnowledgebaseTool(knowledgebase=self.knowledgebase)
    self.tools.append(load_knowledgebase_tool)

    if self.knowledgebase.enable_profile:
        from veadk.tools.builtin_tools.load_kb_queries import load_kb_queries
        self.tools.append(load_kb_queries)
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L306-L324](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L306-L324)

### 自动挂载的工具

| 工具 | 挂载条件 | 功能 |
|------|---------|------|
| `LoadKnowledgebaseTool`（load_knowledgebase） | 配置了 `knowledgebase` | 核心检索工具，Agent 调用此工具从知识库中检索相关内容 |
| `load_kb_queries` | `enable_profile=True` | 知识库画像查询工具，用于多知识库路由 |

**最佳实践**：在 Agent 的 instruction 中明确指示 Agent 在回答相关问题前先查询知识库，例如：
> "Answer questions about the company. Always consult the knowledge base first and base your answer on what you retrieve."

---

## 使用示例

### 基础示例：本地目录 RAG

```python
import asyncio
from pathlib import Path
from veadk import Agent, Runner
from veadk.knowledgebase import KnowledgeBase

DOCS_DIR = Path(__file__).parent / "docs"

async def main() -> None:
    knowledgebase = KnowledgeBase(backend="local", index="company_faq")
    knowledgebase.add_from_directory(str(DOCS_DIR))

    agent = Agent(
        name="rag_agent",
        description="Answers questions using the company knowledge base.",
        instruction=(
            "Answer questions about the company. Always consult the knowledge "
            "base first and base your answer on what you retrieve. If the answer "
            "is not in the knowledge base, say so."
        ),
        knowledgebase=knowledgebase,
    )

    runner = Runner(agent=agent, app_name="rag_demo")

    answer = await runner.run(
        messages="公司的年假政策是怎样的？远程办公可以吗？",
        session_id="demo-session",
    )
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

> 示例来源：[file:///d:/AI/.chaos/libs/veadk-python/examples/05_knowledgebase_rag/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/05_knowledgebase_rag/main.py)

### 动态添加文本

```python
from veadk.knowledgebase import KnowledgeBase

kb = KnowledgeBase(backend="local", index="dynamic_kb")

kb.add_from_text("""
产品A是一款企业级数据分析平台，支持以下功能：
1. 实时数据可视化仪表盘
2. 多数据源接入（MySQL, PostgreSQL, CSV）
3. AI 驱动的异常检测
""")

kb.add_from_text([
    "客服热线：400-123-4567，工作时间 9:00-18:00",
    "退款政策：购买后7天内可无理由退款",
])
```

### 使用 Milvus 后端

```python
knowledgebase = KnowledgeBase(
    backend="milvus",
    backend_config={
        "index": "product_docs",
        "uri": "http://localhost:19530",
        "collection_name": "product_docs",
    },
    top_k=5,
)
knowledgebase.add_from_directory("./product_manuals")
```

### 使用 VikingDB 后端

```python
knowledgebase = KnowledgeBase(
    backend="viking",
    backend_config={
        "index": "enterprise_kb",
        "viking_host": "your-viking-endpoint",
        "viking_region": "cn-beijing",
    },
    enable_profile=True,
)
```

### 自定义后端实例

可以传入自定义后端实例（需继承 `BaseKnowledgebaseBackend`）：

```python
from veadk.knowledgebase.backends.base_backend import BaseKnowledgebaseBackend

class CustomBackend(BaseKnowledgebaseBackend):
    index: str = "custom"

    def precheck_index_naming(self):
        pass

    def add_from_directory(self, directory, **kwargs):
        return True

    def add_from_files(self, files, **kwargs):
        return True

    def add_from_text(self, text, **kwargs):
        return True

    def search(self, **kwargs):
        return []

custom_backend = CustomBackend()
kb = KnowledgeBase(backend=custom_backend)
```

---

## 最佳实践

### 1. 文档分块策略

文档分块（Chunking）直接影响检索质量：

| 策略 | 适用场景 | 建议参数 |
|------|---------|---------|
| 固定长度分块 | 通用文档 | chunk_size=512-1024 tokens，chunk_overlap=100-200 tokens |
| 按段落/章节分块 | 结构化文档（Markdown/HTML） | 按标题层级分割，保持语义完整性 |
| 句子边界分块 | 问答对、FAQ | 按句子或问答对分割，保留完整语义单元 |

**建议**：
- 分块不宜过大（超过模型上下文窗口的 1/3）
- 保留适度重叠（overlap）避免上下文断裂
- 结构化文档优先按语义边界（标题、段落）分割
- 关键信息（标题、来源）应在每个 chunk 中重复或通过 metadata 保留

### 2. 检索参数调优

**top_k 选择**：
- 简单事实查询：`top_k=3-5`
- 复杂问题/汇总：`top_k=5-10`
- 多跳推理：可适当增大，但注意上下文长度限制

**相似度阈值**：
- 部分后端支持设置相似度分数阈值，过滤低相关度结果，避免噪声注入
- 生产环境建议设置阈值并添加兜底逻辑（检索不到时告知用户）

### 3. Prompt 工程

在 Agent instruction 中明确使用知识库的规范：

```python
instruction="""
You are a company assistant. Follow these rules:
1. ALWAYS call load_knowledgebase before answering company-related questions.
2. Base your answer ONLY on the retrieved content.
3. If the retrieved content does not contain the answer, say "I cannot find this information in the knowledge base."
4. Cite the source when possible.
5. Answer in the user's language.
"""
```

### 4. 索引命名规范

- 使用小写字母、数字、下划线、连字符
- 按环境/应用/用途命名，如 `prod_hr_faq_v2`、`staging_product_manuals`
- 版本迭代时使用新索引名，避免直接覆盖（支持回滚）

### 5. 生产环境建议

- **后端选择**：生产环境使用 Milvus/OpenSearch/VikingDB 等专业向量数据库，避免 local 内存后端
- **资源释放**：程序退出时调用 `knowledgebase.close()` 释放连接
- **增量更新**：定期更新知识库，添加新文档而非重建整个索引
- **监控**：记录检索命中率、平均相关度分数等指标
- **Embedding 模型**：选择与业务语言匹配的 Embedding 模型，中文场景优先考虑多语言或中文专用模型

---

## 依赖说明

| 依赖分组 | 安装命令 | 包含的后端 |
|---------|---------|-----------|
| 基础依赖（内置） | `pip install veadk-python` | viking, vikingdb, tos_vector, context_search, openviking |
| database | `pip install "veadk-python[database]"` | redis |
| extensions | `pip install "veadk-python[extensions]"` | llama-index 生态：local, opensearch, redis, milvus |

> 依赖来源：[file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L60-L84](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L60-L84)

**环境变量要求**：
- 使用基于 llama-index 的向量后端时，需配置 Embedding 模型相关环境变量（如 `OPENAI_API_KEY` 或火山引擎 Ark 相关配置）
- OpenSearch/Milvus/Redis 后端需配置对应的服务连接信息
- VikingDB/OpenViking 后端需配置火山引擎访问凭证
