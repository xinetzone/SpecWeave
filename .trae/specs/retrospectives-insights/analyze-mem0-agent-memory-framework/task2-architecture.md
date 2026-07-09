---
source: "https://mp.weixin.qq.com/s/CyZv5BQyW3SSVIJ1U8Ba9A"
title: "Mem0 核心架构组件深度分析"
---

# Mem0 核心架构组件深度分析

## 一、三种接入方式概览

Mem0 官方提供了三种接入方式，三种方式的代码逻辑一致，仅使用方式不同：

| 接入方式 | 适用场景 | 特点 |
|---|---|---|
| 官方云端API | 不想自己部署折腾的用户 | 无需部署，直接使用官方服务 |
| 自建部署服务 | 企业使用场景 | 自主可控，数据本地化 |
| 直接使用SDK | 个人本地Agent | 数据保存在本地，轻量便捷 |

## 二、六大核心组件深度解析

在开源 Python SDK 中，核心入口是 `mem0/memory/main.py` 里的 `Memory` 和 `AsyncMemory`。初始化 `Memory()` 时会创建以下六类组件，其中前 5 个为必选组件，最后 1 个为可选组件。

### 2.1 llm（必选）

**职责**：负责从对话中抽取值得记住的事实。

**核心作用**：将"新对话 + 最近消息 + 相关旧记忆"作为输入，判断对话中是否有需要长期保存的事实（如用户偏好、计划、长期目标等），并输出结构化的记忆 JSON。LLM 只从新对话抽取记忆，旧记忆仅用于去重和关联。

### 2.2 embedding_model（必选）

**职责**：负责把记忆文本和查询文本向量化。

在写入流程中对抽取出的新记忆文本进行向量化；在检索流程中对用户查询文本进行向量化，用于语义相似度计算。

### 2.3 vector_store（必选）

**职责**：主记忆库，是记忆的主要存储载体。

**默认配置**：默认使用 Qdrant，本地数据默认放在 `/tmp/qdrant`，主记忆 collection 叫 `mem0`。

**支持的替代选项**：pgvector、Redis、Milvus、Pinecone 等。

**存储内容**：每条记忆包含记忆文本 `data`、向量 embedding、作用域信息（`user_id`/`agent_id`/`run_id`）、元数据（创建时间、更新时间、hash、角色、过期日期等）、BM25 辅助字段（词形还原后的 `text_lemmatized`）。

### 2.4 SQLiteManager（必选）

**职责**：本地 SQLite，保存记忆变更历史和最近消息窗口。

**核心表结构**：
- `history` 表：记录每条 memory 的 ADD、UPDATE、DELETE 事件，保存旧值、新值、时间、角色、actor 信息
- `messages` 表：保存最近消息窗口，每个 session scope 只保留最新 10 条

**作用**：既能追踪某条记忆如何变化，也能在下一次抽取时利用近期对话降低重复。写入时从 SQLite 取最近 10 条消息作为上下文，记忆保存后在 SQLite 记一条 history。

### 2.5 entity_store（必选）

**职责**：懒加载的实体索引库，用来把实体和记忆 ID 连起来。

**工作机制**：从记忆文本中抽取实体（人名、组织、地点、产品名、被引号包裹的关键词、复合名词短语等），建立"实体 → linked_memory_ids → 多条相关记忆"的索引关系。

**特点**：不建立实体之间的关系，只将抽离出的实体与记忆数据建立关系，系统可以通过实体查到以往的历史记忆数据。实体写入有去重逻辑，先按规范化文本精确匹配，未命中再做向量搜索，命中后更新 `linked_memory_ids` 而非新增实体。

### 2.6 reranker（可选）

**职责**：负责对召回结果二次排序。

**适用场景**：客服、医疗、法务、企业知识库等高精度场景，reranker 通常比单纯向量召回更稳。配置后可在候选结果融合后做二次排序处理。

## 三、组件协作架构

```mermaid
flowchart TD
    Input["用户输入<br/>(对话/查询)"] --> Entry["Memory / AsyncMemory<br/>(核心入口)"]

    subgraph Compute["计算层"]
        LLM["llm<br/>(事实抽取)"]
        Embedding["embedding_model<br/>(向量化)"]
        Reranker["reranker<br/>(二次排序·可选)"]
    end

    subgraph Storage["存储层"]
        SQLite["SQLiteManager<br/>(history+messages)"]
        VectorStore["vector_store<br/>(主记忆库·默认Qdrant)"]
        EntityStore["entity_store<br/>(实体索引)"]
    end

    subgraph Optional["可选增强层"]
        BM25["BM25关键词检索"]
        EntityBoost["实体命中加权"]
    end

    Entry --> WriteOp{"写入/检索?"}

    WriteOp -->| "写入(add)" | W1["从SQLite取最近10条消息"]
    W1 --> W2["从Vector Store取10条相关旧记忆"]
    W2 --> W3["新对话+最近消息+旧记忆 → LLM抽取"]
    W3 --> W4["embedding_model向量化"]
    W4 --> W5["md5去重"]
    W5 --> W6["批量写入Vector Store"]
    W6 --> W7["SQLite记录history"]
    W7 --> W8["抽取实体写入Entity Store"]
    W8 --> OutputWrite["记忆写入完成"]

    WriteOp -->| "检索(search)" | S1["查询向量化+实体抽取"]
    S1 --> S2["三路召回"]
    S2 --> S2a["Vector Store语义检索<br/>(Semantic Score)"]
    S2 --> S2b["BM25关键词匹配<br/>(BM25 Score)"]
    S2 --> S2c["Entity Store实体检索<br/>(Entity Boost)"]
    S2a --> S3["候选池(扩大4倍召回)"]
    S2b --> S3
    S2c --> S3
    S3 --> S4["阈值过滤"]
    S4 --> S5["分数融合<br/>final_score=(semantic+bm25+entity)/max_possible"]
    S5 --> S6{"是否配置reranker?"}
    S6 -->| "是" | S7["reranker二次排序"]
    S6 -->| "否" | S8["返回Top-K结果"]
    S7 --> S8
    S8 --> OutputSearch["检索结果返回"]

    Entry -.-> LLM
    Entry -.-> Embedding
    Entry -.-> Reranker
    LLM -.-> SQLite
    LLM -.-> VectorStore
    Embedding -.-> VectorStore
    Embedding -.-> EntityStore
    VectorStore -.-> BM25
    EntityStore -.-> EntityBoost
```

## 四、架构设计亮点分析

### 4.1 ADD-only 写入策略，保留事实演化轨迹

Mem0 v3 采用 ADD-only 策略，新事实默认作为新记忆加入，而非直接覆盖旧记忆。这种设计的好处是保留事实演化轨迹，让时间推理、多跳检索和冲突处理更有空间。

为避免记忆膨胀，设计了两层去重机制：LLM 在看到相关旧记忆后尽量不重复抽取；SDK 对新记忆文本计算 md5 hash，若 hash 已存在则跳过写入。同时仍提供 update 和 delete 方法支持显式记忆维护。

### 4.2 多路信号融合检索，提升召回质量

检索不只依赖向量相似度，而是融合 Semantic Score（语义相似度）、BM25 Score（关键词匹配）、Entity Boost（实体命中加权）三路信号。其中语义分数先过阈值过滤，BM25 适合精确词/日期/术语，实体加权适合围绕人/项目/地点/产品的查询。

分数归一化采用动态 max_possible 分母，根据实际启用的检索方式调整，避免因启用多路信号导致分数虚高。内部检索时将 top k 扩大 4 倍形成候选池，避免过早丢掉相关记忆。

### 4.3 批量优先+降级策略，面向生产场景

落库时优先走批量路径：对抽取出的记忆文本调用 `embed_batch` 再一次性 `insert` 到向量库；历史记录优先 `batch_add_history`。若 provider 不支持或调用失败，才降级成逐条处理，兼顾吞吐与可靠性。

### 4.4 实体索引设计，建立记忆连接

Entity Store 不构建复杂的知识图谱实体关系，而是聚焦"实体→记忆ID"的关联索引，既实现了围绕实体的记忆召回，又保持了实现的简洁性。实体去重采用规范化文本精确匹配+向量相似度匹配的两级策略，让同一实体能逐渐连接越来越多的记忆。

### 4.5 作用域设计清晰，支持多维度隔离

每条记忆和实体都携带 `user_id`/`agent_id`/`run_id` 作用域字段，保证检索时记忆不会乱串。同时支持 metadata 做业务隔离（如 `project_id`/`workspace_id`/`category`），方便后续过滤。
