---
id: veadk-python-knowledgebase
title: 05 - 知识库RAG示例
source: d:\AI\.chaos\libs\veadk-python\examples\05_knowledgebase_rag\main.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# 知识库RAG示例 (Knowledge Base RAG)

## 1. 示例功能介绍

本示例展示 Retrieval-Augmented Generation（检索增强生成，RAG）能力。通过 `KnowledgeBase` 类，你可以将自有文档（如公司 FAQ、产品手册、政策文档等）嵌入并存储到向量后端，然后挂载到 Agent 上。VeADK 会自动为 Agent 添加一个检索工具，让 Agent 在回答前先检索你的文档内容——从而将回答"锚定"在你的私有内容上，而不是依赖模型的通用知识。

**演示的核心能力**：
- KnowledgeBase 初始化（本地向量后端）
- 从目录批量添加文档（自动分块、嵌入）
- 将知识库挂载到 Agent
- VeADK 自动添加检索工具
- Agent 基于检索结果回答问题（而非模型预训练知识）

---

## 2. 核心代码展示

完整代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/05_knowledgebase_rag/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/05_knowledgebase_rag/main.py)：

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

示例文档位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/05_knowledgebase_rag/docs/company_faq.md](file:///d:/AI/.chaos/libs/veadk-python/examples/05_knowledgebase_rag/docs/company_faq.md)，包含公司年假、远程办公等政策信息。

---

## 3. 关键代码行逐行解释

| 行号 | 代码 | 解释 |
|------|------|------|
| 32 | `from veadk.knowledgebase import KnowledgeBase` | 导入知识库类，这是 RAG 功能的核心入口 |
| 34 | `DOCS_DIR = Path(__file__).parent / "docs"` | 获取示例 docs 目录的绝对路径，这里存放待入库的 Markdown 文档 |
| 39 | `knowledgebase = KnowledgeBase(backend="local", index="company_faq")` | 创建知识库实例：<br>- `backend="local"`：使用本地内存向量存储（适合演示和小规模）<br>- `index="company_faq"`：索引名称，用于隔离不同知识库 |
| 40 | `knowledgebase.add_from_directory(str(DOCS_DIR))` | **关键步骤**：从指定目录批量加载文档。VeADK 会自动：<br>1. 读取目录下所有支持的文档（.md、.txt 等）<br>2. 对文档进行分块（chunking）<br>3. 调用 embedding 模型将文本块转换为向量<br>4. 存入向量索引中 |
| 43-52 | `agent = Agent(..., knowledgebase=knowledgebase,)` | **挂载知识库到 Agent**：只需传入 `knowledgebase` 参数，VeADK 会自动：<br>1. 为 Agent 添加一个检索工具（如 `search_knowledgebase`）<br>2. 在指令中提示 Agent 在需要时使用检索工具<br>3. 管理检索结果的注入到上下文中 |
| 46-50 | `instruction=(...)` | **指令引导很重要**：明确告诉 Agent "总是先查询知识库"、"如果知识库中没有答案就说明"，能显著提升 RAG 准确率，减少幻觉 |
| 56-59 | `runner.run(messages="公司的年假政策是怎样的？远程办公可以吗？")` | 用户提问。Agent 不会直接凭记忆回答，而是：<br>1. 识别问题需要查询公司政策<br>2. 自动调用检索工具搜索相关文档块<br>3. 将检索到的相关片段作为上下文<br>4. 基于检索内容生成回答 |

### 🔑 RAG 工作原理

```
用户提问 → 查询改写 → 向量检索 → 相关文档块 → 注入上下文 → LLM 生成回答
                                                         ↓
                                                  回答基于你的文档
```

1. **入库阶段**：文档 → 分块 → Embedding → 向量库
2. **查询阶段**：问题 → Embedding → 相似度搜索 → Top-K 相关块 → 作为上下文传给 LLM

### 💡 为什么需要在指令中强调"先查询知识库"？

默认情况下，模型可能倾向于直接用预训练知识回答。通过在 `instruction` 中明确：
- "Always consult the knowledge base first"（总是先查询知识库）
- "base your answer on what you retrieve"（基于检索到的内容回答）
- "If the answer is not in the knowledge base, say so"（知识库没有就说明）

可以强制 Agent 走 RAG 流程，避免生成与你文档不符的"幻觉"回答。

---

## 4. 运行前置条件

### 环境要求
- Python 3.10+
- 已安装 veadk-python 包
- **RAG 需要 embedding 模型支持，需安装扩展依赖**：

```bash
pip install "veadk-python[extensions]"
```

### API Key 配置
需要配置火山引擎方舟（Ark）的 API Key，以及 embedding 模型相关配置：

```bash
# Windows PowerShell
$env:ARK_API_KEY = "your-api-key-here"

# Linux/Mac
export ARK_API_KEY="your-api-key-here"
```

请参考示例目录下的 `.env.example` 文件配置完整的环境变量，特别是 embedding 模型相关参数。

### 文档准备
将你的知识库文档（Markdown、TXT 等格式）放入一个目录中，就像示例中的 `docs/` 目录一样。支持的格式包括：
- `.md` - Markdown
- `.txt` - 纯文本
- 其他格式（需额外配置解析器）

---

## 5. 预期运行效果/输出

运行命令：
```bash
cd 05_knowledgebase_rag
python main.py
```

**预期执行流程**：
1. 程序启动，初始化本地知识库
2. 自动加载 `docs/company_faq.md` 并进行分块、嵌入
3. Agent 收到问题后，自动调用检索工具
4. 检索到年假政策和远程办公政策相关片段
5. Agent 基于检索结果生成准确回答

**预期输出**（示例，具体内容取决于 company_faq.md 中的内容）：
```
根据公司政策：

**年假政策**：
- 入职满1年可享受5天年假
- 入职满3年可享受10天年假
- 入职满5年可享受15天年假
- 年假需提前3天申请，经主管批准后生效

**远程办公政策**：
- 公司支持每周1-2天远程办公
- 远程办公需提前在OA系统提交申请
- 核心岗位（如运维、客服）不支持远程办公

以上信息均来自公司知识库。
```

注意回答中不会包含模型"编造"的内容——如果问题超出知识库范围（如"公司年终奖是多少？"），Agent 会如实回答"知识库中没有相关信息"。

---

## 6. 延伸学习

- 上一示例：[记忆示例](memory.md)
- 下一步学习：[多智能体协作示例](multi-agent.md) - 学习如何组合多个 Specialist Agent
- 相关文档：
  - [知识库模块详解](../modules/knowledgebase.md)
  - [记忆模块](../modules/memory.md)
  - [最佳实践](../faq/best-practices.md)
