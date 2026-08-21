---
id: 09-knowledgebase-facts
title: KnowledgeBase 模块事实记录
source: veadk-python codebase analysis
---

# KnowledgeBase 模块事实记录

## KnowledgeBase 类

### 类签名和继承关系
- 文件位置：veadk/knowledgebase/knowledgebase.py:92
- 类定义：`class KnowledgeBase(BaseModel):`
- 继承关系：继承自 `pydantic.BaseModel`

### 构造函数字段（Pydantic 模型字段）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| name | str | "user_knowledgebase" | 知识库名称 |
| description | str | "This knowledgebase stores some user-related information." | 知识库描述 |
| backend | Literal[...] \| BaseKnowledgebaseBackend | "local" | 知识库后端类型或实例 |
| backend_config | dict | Field(default_factory=dict) | 后端配置字典 |
| top_k | int | 10 | 搜索时返回的最相似文档数量 |
| app_name | str | "" | 关联的应用名称 |
| index | str | "" | 知识库索引名称 |
| enable_profile | bool | False | 是否启用 profile 功能 |
| query_with_user_profile | bool | False | 是否使用用户 profile 进行查询 |

backend 支持的字面量类型："local", "opensearch", "viking", "redis", "milvus", "tos_vector", "context_search", "openviking"

### 公开方法列表

#### 1. model_post_init 方法
- 位置：veadk/knowledgebase/knowledgebase.py:156-185
- 方法签名：`def model_post_init(self, __context: Any, /) -> None:`
- 执行步骤：
  1. 若 backend 是 BaseKnowledgebaseBackend 实例：直接使用该实例作为 _backend，设置 index 为 _backend.index，输出 info 日志并返回
  2. 若 backend_config 非空：使用 _get_backend_cls(self.backend)(**self.backend_config) 初始化 _backend 并返回
  3. 设置 self.index = self.index or self.app_name
  4. 若 index 为空：抛出 ValueError("Either `index` or `app_name` must be provided.")
  5. 输出 info 日志记录 backend、index、top_k 信息
  6. 使用 _get_backend_cls(self.backend)(index=self.index) 初始化 _backend
  7. 输出 info 日志记录后端类名
  8. 若 query_with_user_profile 为 True：输出 info 日志提示必须使用 Viking Memory 后端

#### 2. add_from_directory 方法
- 位置：veadk/knowledgebase/knowledgebase.py:187-211
- 方法签名：`def add_from_directory(self, directory: str, **kwargs) -> bool:`
- 功能：调用 self._backend.add_from_directory(directory=directory, **kwargs)，将目录中的文件添加到知识库后端。

#### 3. add_from_files 方法
- 位置：veadk/knowledgebase/knowledgebase.py:213-237
- 方法签名：`def add_from_files(self, files: list[str], **kwargs) -> bool:`
- 功能：调用 self._backend.add_from_files(files=files, **kwargs)，将文件列表添加到知识库后端。

#### 4. add_from_text 方法
- 位置：veadk/knowledgebase/knowledgebase.py:239-263
- 方法签名：`def add_from_text(self, text: str | list[str], **kwargs) -> bool:`
- 功能：调用 self._backend.add_from_text(text=text, **kwargs)，将文本或文本列表添加到知识库后端。

#### 5. search 方法
- 位置：veadk/knowledgebase/knowledgebase.py:265-282
- 方法签名：`def search(self, query: str, top_k: int = 0, **kwargs) -> list[KnowledgebaseEntry]:`
- 执行步骤：
  1. 设置 top_k = top_k if top_k != 0 else self.top_k
  2. 调用 self._backend.search(query=query, top_k=top_k, **kwargs) 获取 _entries
  3. 初始化 entries 为空列表
  4. 遍历 _entries：
     - 若 entry 是 KnowledgebaseEntry 实例：追加到 entries
     - 若 entry 是 str：创建 KnowledgebaseEntry(content=entry) 并追加
     - 否则：输出 error 日志，跳过该 entry
  5. 返回 entries

#### 6. close 方法
- 位置：veadk/knowledgebase/knowledgebase.py:284-288
- 方法签名：`def close(self) -> None:`
- 功能：获取 _backend 的 close 属性，若可调用则调用该方法释放后端资源。

#### 7. __getattr__ 方法
- 位置：veadk/knowledgebase/knowledgebase.py:290-295
- 方法签名：`def __getattr__(self, name) -> Callable:`
- 功能：返回 getattr(self._backend, name)，用于代理后端的其他方法（如 delete、list_chunks 等）。

#### 8. generate_profiles 方法
- 位置：veadk/knowledgebase/knowledgebase.py:297-357
- 方法签名：`async def generate_profiles(self, files: list[str], profile_path: str = ""):`
- 执行步骤：
  1. 读取文件列表中每个文件的内容
  2. 创建一个 profile_generator Agent，配置特定的 instruction 要求输出 JSON 格式
  3. 创建 Runner 实例
  4. 遍历每个文件内容，调用 runner.run 获取响应
  5. 尝试解析 JSON 为 KnowledgebaseProfile，解析失败时输出 error 日志并跳过
  6. 输出 debug 日志记录生成的 profiles 数量
  7. 若未提供 profile_path，设置默认路径
  8. 将每个 profile 写入单独的 JSON 文件
  9. 将 profile 名称列表写入 profile_list.json 文件

### 模块级函数

#### _get_backend_cls
- 位置：veadk/knowledgebase/knowledgebase.py:30-89
- 功能：根据 backend 字符串返回对应的后端类，支持的后端映射：
  - "local" → InMemoryKnowledgeBackend
  - "opensearch" → OpensearchKnowledgeBackend
  - "redis" → RedisKnowledgeBackend
  - "milvus" → MilvusKnowledgeBackend
  - "tos_vector" → TosVectorKnowledgeBackend
  - "viking" → VikingDBKnowledgeBackend
  - "context_search" → ContextSearchBackend
  - "openviking" → OpenVikingKnowledgeBackend
- 导入失败时若涉及 llama_index，抛出 ImportError 提示安装 veadk-python[extensions]

---

## KnowledgebaseProfile 类（types.py）

### 类签名和继承关系
- 文件位置：veadk/knowledgebase/types.py:18
- 类定义：`class KnowledgebaseProfile(BaseModel):`
- 继承关系：继承自 `pydantic.BaseModel`

### 字段列表

| 字段名 | 类型 | Field 描述 |
|--------|------|-----------|
| name | str | The name of the knowledgebase. |
| description | str | The description of the knowledgebase. |
| tags | list[str] | Some tags of the knowledgebase. It represents the category of the knowledgebase. About 3-5 tags should be provided. |
| keywords | list[str] | Recommanded query keywords of the knowledgebase. About 3-5 keywords should be provided. |

---

## enable_profile 功能相关代码位置

### 1. KnowledgeBase 类中的字段定义
- 位置：veadk/knowledgebase/knowledgebase.py:152
- 字段：`enable_profile: bool = False`

### 2. Agent 初始化中的判断逻辑
- 位置：veadk/agent.py:316-324
- 执行步骤：
  1. 在挂载 knowledgebase 工具后，检查 `self.knowledgebase.enable_profile` 是否为 True
  2. 若为 True：输出 debug 日志，内容为 "Knowledgebase {self.knowledgebase.index} profile enabled"
  3. 从 veadk.tools.builtin_tools.load_kb_queries 导入 load_kb_queries 工具
  4. 将 load_kb_queries 追加到 self.tools 列表

---

本文档记录了 KnowledgeBase 类的类签名、构造参数字段、8个公开方法及 _get_backend_cls 模块级函数。本文档包含 KnowledgebaseProfile 类的字段定义，以及 enable_profile 功能在两个文件中的代码位置。所有内容均从代码中客观提取，未包含主观评价。
