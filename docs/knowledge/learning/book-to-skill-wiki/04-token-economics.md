# Token 经济学与性能

book-to-skill 的核心价值主张之一是 **24×-51× 的 token 节省**。这不是营销口号——有专门的测量工具和数学解释。

## Discovery Loop Tax 原理

### 什么是 Discovery Loop？

当你让 Agent "读一下这本书的第5章关于 replication 的部分"时，它不会直接跳到那一页。它会：

1. 先读取目录（ToC）了解结构
2. 发现某个术语不理解，拉取更多页面
3. 回溯找定义
4. 在多次跳转中，每一跳的内容都进入对话历史
5. **后续每一轮都会重新处理这些历史内容**

为了保持在预算内，子 Agent 被迫以残酷的比例压缩它读过的内容，给主 Agent 返回一个**降级的、无法与源事实核查的摘要**。

这就是 Discovery Loop Tax：导航成本不是一次付清的，而是**每一轮重复支付**，并且每次压缩都会丢失信息。

### book-to-skill 的解决方案

book-to-skill 在**编译时一次付清**导航成本：
- 运行时只加载一个小的常驻核心（SKILL.md ~4K tokens）
- 加上一个预编译的章节文件（~1K tokens）
- 没有发现循环，没有被迫压缩
- 完整提取的源文件留在磁盘上用于验证

## 性能基准数据

### 提取速度基准（103页技术书籍，CPU only）

| 方法 | 时间 | Tokens | 表格 | 代码块 |
|------|------|--------|------|--------|
| pdftotext | 0.1s | 27K | 0 | 0 |
| Docling | 164s | 27K (+1.2%) | 48 | 36 |

> 来源：[README.md#L208-L214](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/README.md#L208-L214)

### 真实书籍转换成本（Claude Sonnet 4.5 @ $3/$15 per MTok 估算）

| 书籍 | 格式 | 页数 | Tokens | 章节数 | 估算成本 |
|------|------|-----:|-------:|--------:|---------:|
| Think Python 2 | PDF | 244 | 119K | 19 | ~$0.88 |
| Working Backwards | PDF | 371 | 175K | 10 | ~$0.96 |
| Pro Git | PDF | 501 | 229K | — † | ~$1.23 |
| Moby-Dick | EPUB | — | 301K | — † | ~$1.42 |

> † 没有明确 "Chapter N" 标题的书需要手动分段。一本书的完整转换成本大约 **$1/本**——远低于每次会话重新读 PDF 的成本。

### Token 节省实测（Discovery Loop Tax 测量）

| 书籍（大小） | 上下文 Dump | Discovery Loop | book-to-skill | vs dump / loop |
|-------------|-----------:|---------------:|--------------:|:--------------:|
| Think Python 2（119K，小章节） | 119,264 | 12,152 | ~5,000 | 24× / **2.4×** |
| Working Backwards（175K，中章节） | 175,253 | 33,444 | ~5,000 | 35× / 6.7× |
| AI Engineering（256K，大章节） | 256,287 | 77,866 | ~5,000 | 51× / **15.6×** |

**关键洞察**：优势随着章节大小**规模化增长**：
- 相比上下文 dump：稳定 24–51×（而且这个成本**每一轮都重复发生**）
- 相比一次性 Discovery Loop：小章节书 2.4×，大章节书 15.6×

### 自己复现测量

```bash
python3 tools/discovery_tax.py --full-text /tmp/book_skill_work/full_text.txt --target-chapter 5
```

## 为什么大上下文窗口不是解决方案？

Claude 有 1M token 窗口了，为什么不直接把整本书放进去？三个原因：

1. **按 token 付费，按次调用**。1M 窗口不会让这些 token 免费——它让大额、重复性账单成为可能。Skill 加载千字节，不是兆字节。

2. **填充率上升，召回率下降**。模型在接近满的上下文中检索特定事实的精度会下降（"lost in the middle"问题）。一个 1K 的精编章节胜过 200K 原始散文回答单个问题。

3. **窗口 ≠ 结构**。全本书在上下文中仍然是原始文本，模型每轮都要重新解析。Skill 运送预提取的框架——是推理，不是检索。

**经验法则**：
- 大窗口用于：一次性通读你再也不需要的材料
- Skill 用于：你反复查阅的知识

## RAG vs Skill：互补而非竞争

| 维度 | RAG | book-to-skill |
|------|-----|---------------|
| 工作时机 | 查询时（Query-time） | 编译时（Compile-time） |
| 核心操作 | 分块 → Embedding → 向量相似度 → 注入提示 | 深度分析提取作者的实际框架，命名，描述使用时机，捕获反模式 |
| 回答方式 | *"这里是与你查询相近的文本块"* | *"这是作者构建的 12 个框架，随时可以用来推理"* |
| 优化目标 | "找提到 X 的部分" | "作者会怎么思考这个问题" |
| 适用形态 | **宽而浅**：几十本书的图书馆 | **窄而深**：一本书或紧密相关的资料簇 |

一句话总结：RAG 索引书架，book-to-skill 精通一本书脊。它们是互补的。

## 大书 REPL 式访问策略

对于 >50K tokens 的书籍，**绝对不要**一次性把 full_text.txt 读入上下文。使用 REPL 风格的程序化探测：

```bash
# 1. 先看大小，决定策略
wc -w "$FULL_TEXT_PATH"

# 2. 找章节偏移（不全量读取）
grep -n -E "^\s*(Chapter|CHAPTER)\s+[0-9]+" "$FULL_TEXT_PATH" | head -40

# 3. 只拉取你需要的章节（行范围）
sed -n '1500,2300p' "$FULL_TEXT_PATH"

# 4. 验证框架确实被提及再写入 SKILL.md
grep -c -i "westrum\|dora" "$FULL_TEXT_PATH"

# 5. 用带 offset/limit 的 Read 避免 dump 整个文件
# Read(file_path=full_text.txt, offset=1500, limit=800)
```

**为什么这很重要**：
- 一本 200 页的书约 75K tokens
- 如果每章重读一遍（28 次），就是 ~2M 输入 tokens
- 用 grep + sed 按需拉取，使生成成本与输出成正比，而非与源大小成正比

## 估算公式

### 输入 Token 估算

```
input_tokens ≈ estimated_tokens (from metadata) × 1.3
```

1.3 倍是每章提示词的开销——多轮对话中每章都有系统提示+上下文。

### 输出 Token 估算

```
output_tokens ≈ chapter_count × per_chapter_budget + 4000 (SKILL.md) + 4500 (glossary+patterns+cheatsheet)
```

每章预算中点值（按 BOOK_TYPE）：
- `text` ≈ 1,000 tokens
- `technical` ≈ 1,800 tokens

（DEPTH 在 Step 4 确定后可以提高预算）

---

**事实来源**：本章节基于以下事实编号 F-029, F-030
