---
id: headroom-wiki-02-compression-algorithms
title: "Headroom — 六种压缩算法详解"
source: "https://mp.weixin.qq.com/s/7zT5-9WDp8zi4naCC2EmOg?from=industrynews&color_scheme=light#rd"
date: "2026-08-03"
category: "learning"
tags: ["headroom", "compression-algorithms", "smartcrusher", "codecompressor", "kompress", "ast", "content-routing"]
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/learning/headroom-context-compression-wiki/02-compression-algorithms.toml"
---

# Headroom — 六种压缩算法详解

> 本章详细解析Headroom的内容路由机制和六种内置压缩算法，重点阐述SmartCrusher、CodeCompressor、Kompress-v2-base三种核心算法的工作原理与设计特点。

---

## 1. 内容路由机制：先诊断，再开方

Headroom不像很多同类工具那样"一把锤子敲所有钉子"——它的第一原则是**内容感知路由（Content-Aware Routing）**。

### 为什么需要内容路由？

简单截断或用一个小模型统一压缩所有内容，本质上是"信息盲"的：
- 截断不知道哪里重要，可能砍掉关键报错信息
- 小模型统一压缩无法利用结构化信息（JSON的键名、代码的语法树）
- 不同类型内容的冗余模式完全不同

### 路由流程

```
输入内容
    ↓
[格式检测] → JSON？代码？日志？自然语言？混合？
    ↓
[特征提取] → 提取结构特征（如JSON嵌套深度、代码语言类型）
    ↓
[算法选择] → 路由到最适合的压缩算法
    ↓
[参数调整] → 根据内容特征调整压缩参数
    ↓
[执行压缩]
```

### 支持的内容类型

| 内容类型 | 路由到的算法 | 典型压缩率 |
|---------|------------|-----------|
| JSON数据 | SmartCrusher | 70-90% |
| 源代码（Python/JS/Go/Rust/Java/C++） | CodeCompressor | 40-70% |
| 自然语言/对话历史 | Kompress-v2-base | 50-80% |
| 日志/终端输出 | 日志专用算法 | 80-95% |
| 混合内容 | 分块路由+多算法组合 | 视内容而定 |
| RAG检索片段 | RAG专用算法 | 40-60% |

---

## 2. SmartCrusher：JSON结构化压缩

SmartCrusher是Headroom针对JSON数据设计的专用压缩算法。

### 设计原理

工具返回的JSON（API响应、搜索结果、数据列表等）往往包含大量冗余：
- 重复的键名（数组中每个对象都有相同的键）
- 过长的嵌套路径
- 空值、默认值、重复值
- 数字ID、时间戳等对LLM推理无意义但占Token的字段

SmartCrusher利用JSON的**结构统计特征**进行压缩，而非语义理解：

1. **键名去重**：将重复出现的键名替换为短引用
2. **数组摘要**：长数组只保留前N个元素+总数统计
3. **嵌套打平**：深层嵌套的路径用点号表示打平
4. **空值移除**：null、空字符串、空数组直接移除
5. **类型标注**：保留数据类型信息，让LLM知道原结构

### 压缩效果

根据README数据，SmartCrusher对JSON的压缩率达到**70-90%**。

**压缩前（示例）**：
```json
{
  "results": [
    {"id": 12345, "name": "utils.py", "path": "/src/lib/utils.py", "size": 4521, "type": "python"},
    {"id": 12346, "name": "helpers.py", "path": "/src/lib/helpers.py", "size": 3210, "type": "python"},
    {"id": 12347, "name": "constants.py", "path": "/src/lib/constants.py", "size": 1890, "type": "python"},
    {"id": 12348, "name": "config.py", "path": "/src/lib/config.py", "size": 892, "type": "python"}
  ],
  "total_count": 47,
  "page": 1
}
```

**压缩后（概念示例）**：
```
[Struct] results(array, total=47, showing=4)
  {id:*, name:utils.py, path:/src/lib/utils.py, size:4.5k, type:py}
  {id:*, name:helpers.py, path:/src/lib/helpers.py, size:3.2k, type:py}
  {id:*, name:constants.py, path:..., size:1.9k, type:py}
  ...(+3 more)
page=1
```

---

## 3. CodeCompressor：基于AST的代码压缩

CodeCompressor是Headroom最精巧的算法之一——它基于**抽象语法树（AST）**进行代码压缩。

### 设计原理

代码不是普通文本，它有严格的语法结构。CodeCompressor利用这一点：
- 解析代码为AST（抽象语法树）
- 识别并保留结构关键信息
- 删除实现细节但保留"理解代码需要知道"的信息

### 保留什么？删除什么？

| 保留（必须） | 删除（可压缩） |
|------------|--------------|
| `import` / `require` 导入语句 | 函数体内的具体实现逻辑 |
| 函数/方法签名（名称、参数、返回类型） | 重复的注释和文档字符串 |
| 类定义、继承关系 | 空行、格式化空白 |
| 类型注解（Type Hints） | 调试代码（print、console.log） |
| 关键常量和枚举定义 | 冗余的错误处理样板代码 |
| 导出/公开API声明 | 长字符串字面量（摘要保留） |

### 支持的语言

- Python
- JavaScript / TypeScript
- Go
- Rust
- Java
- C++

### 压缩效果示例

**压缩前（Python代码）**：
```python
import os
import sys
from typing import List, Dict, Optional

def process_user_data(users: List[Dict], config: Optional[Dict] = None) -> Dict:
    """
    Process user data according to configuration.
    Handles validation, transformation, and aggregation.
    """
    results = {}
    default_config = {"validate": True, "transform": False}
    if config is None:
        config = default_config
    for user in users:
        user_id = user.get("id")
        if not user_id:
            print(f"Warning: user without id, skipping")
            continue
        if config["validate"]:
            if "email" not in user:
                print(f"User {user_id} missing email")
                continue
        # ... 50 more lines of processing logic
        results[user_id] = processed
    return results
```

**压缩后（概念示例）**：
```python
import os
import sys
from typing import List, Dict, Optional

def process_user_data(users: List[Dict], config: Optional[Dict] = None) -> Dict:
    """Process user data: validate, transform, aggregate"""
    # [Impl: processes users, validates emails based on config, returns results dict]
    # Key logic: config["validate"] checks email presence; skips invalid users
```

> **关键价值**：模型读压缩后的代码仍然能正确理解模块结构、API接口、类型信息，但Token消耗大幅减少。当模型需要看具体实现时，可以通过`headroom_retrieve`取回。

---

## 4. Kompress-v2-base：Agent场景专用自然语言压缩

Kompress-v2-base是Headroom作者专门训练的一个小模型，用于自然语言压缩。

### 为什么需要专门训练？

通用的文本摘要模型（如BART、T5）是为新闻文章、文档摘要设计的，它们不知道AI Agent场景下什么重要：
- Agent对话中，工具调用和错误信息比寒暄重要
- 思考过程（Chain of Thought）中的推理步骤不能丢
- 用户的具体指令和约束条件必须保留

### Kompress-v2-base的特点

- **训练数据**：大量Agentic Trace（Agent真实执行轨迹）
- **领域知识**：知道Agent场景下哪些话可以丢掉，哪些必须保留
- **指令遵循**：专门训练为"保留对LLM推理有用的信息，删除冗余寒暄和重复内容"
- **体积小**：作为压缩模型，本身运行速度快、成本低

### 适用场景

- 多轮对话历史压缩
- RAG检索结果的语义去重
- 长文本摘要和要点提取
- 错误日志的自然语言描述压缩

---

## 5. 其他压缩算法

除了上述三种核心算法，Headroom还内置了针对特定场景的压缩方案：

### 日志专用压缩算法
- 识别日志级别（INFO/DEBUG/WARN/ERROR），默认过滤DEBUG和部分INFO
- 合并重复堆栈，只保留首次出现+出现次数统计
- 提取关键错误行，移除无关上下文

### RAG专用压缩算法
- 识别多个检索片段中的重复信息进行去重
- 保留与query最相关的片段，相关性低的片段只保留摘要
- 合并相邻片段中重叠的内容

### 混合内容路由算法
- 对包含多种类型内容的消息（如既有代码又有自然语言解释）
- 先分块识别类型，再对不同块使用不同算法
- 最后合并压缩结果，保持块之间的逻辑关联

---

## 6. 与简单截断/统一压缩的对比优势

| 对比维度 | 简单截断 | 小模型统一压缩 | Headroom内容感知路由 |
|---------|---------|--------------|-------------------|
| 信息保留 | 可能截断关键信息 | 无法利用结构特征 | 保留关键结构+按需取回 |
| 代码理解 | 差（截断可能断在代码中间） | 一般（不理解语法） | 好（保留AST结构） |
| JSON处理 | 可能截断JSON导致无效 | 一般 | 优（统计式压缩） |
| 可逆性 | 不可逆（丢了就没了） | 不可逆 | 可逆（CCR机制） |
| 压缩率 | 高但风险大 | 中等 | 高且质量有保障 |
| 质量影响 | 可能严重损失 | 部分场景下降 | 不降反升（注意力更集中） |

---

## 7. 设计思想洞察：对症下药的工程智慧

Headroom压缩算法体系体现了一个深刻的工程原则：**利用结构，而非对抗结构**。

- 面对结构化数据（JSON），利用统计特征压缩
- 面对半结构化数据（代码），利用语法树（AST）压缩
- 面对非结构化数据（自然语言），用专门训练的模型压缩
- 面对混合数据，分块路由、组合使用

这与Unix哲学中的"做一件事并做好"一脉相承——每个算法只解决自己最擅长的场景，通过路由层组合成完整方案。这比"一个万能模型处理一切"更高效、更可靠、更可解释。

---

- ← [上一章：核心架构与设计理念](01-core-architecture.md)
- [下一章：CCR可逆机制深度解析](03-ccr-mechanism.md) →
