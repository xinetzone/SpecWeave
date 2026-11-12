---
type: Concept
title: "记忆：Basic Memory 笔记与中文检索"
description: "PhonePal 的记忆是一目录 Basic Memory 格式的 Markdown：观察行、关系行与 wiki link；写入原子替换、按 mtime/size 增量索引，中文检索用双字主词 + 单字弱词的 BM25，成功路径沉淀成 howto 笔记"
tags: [phonepal, memory, basic-memory, markdown, bm25, cjk, retrieval]
generated:
  by: specweave-agent
  at: "2026-11-12T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-12T00:00:00+08:00"
status: stable
stale_after: "2027-05-12"
sources:
  - id: S-01
    resource: ../references/00-source-inventory.md
    title: 信源登记：PhonePal 源码快照
---

# 记忆：Basic Memory 笔记与中文检索

PhonePal 没有把「记住用户说过什么」做成数据库，而是做成**一目录可以直接用 Obsidian 打开的 Markdown**。这个选择决定了后面所有的实现：格式要人类可读、写入要原子、检索要能处理中文、删除就是真删文件。

## 1. 一个笔记长什么样

```markdown
---
title: 家
type: place
permalink: places/家
tags: [地址]
---
# 家

## Observations
- [address] 北京市海淀区某某路 1 号 #常用 (用户 2026-10-30 告知)
- [alias] 公司附近的那个家

## Relations
- lives_in [[北京]]
- nearby [[中关村]]
```

三类可被解析的内容 [F-045]：

| 行形式 | 解析结果 | 说明 |
|---|---|---|
| `- [category] content #tag (context)` | `Observation(category, content, tags, context)` | 必须整行匹配；`- [ ]`/`- [x]` 任务框不算 |
| `- 关系类型 [[目标]] (context)` | `Relation(type, target, context)` | 目标里的 `Target|alias`、`Target#heading` 都归一为 `Target` |
| 正文任意 `[[wiki link]]` | `Relation("links_to", target)` | 行内代码里的 `[[...]]` 会被剔掉 |

围栏代码块（```` ``` ```` 或 `~~~`）内的行不参与解析 [F-045]。这一点很重要：否则一段示例 Markdown 会把整篇笔记的观察与关系污染。

## 2. 写回：不覆盖用户内容

`BasicMemoryFormat.render` 分两种情况 [F-046]：

- **正文为空**：按 `observations`/`relations` 生成 `# 标题`、`## Observations`、`## Relations`；
- **正文非空**：只把「正文里还没有的」观察/关系插入对应小节；已有前言、用户自己写的段落一律保留。

这就是「工具写记忆」和「用户在 Obsidian 里编辑」能共存的原因：工具是增量补写，不是整篇重写。

## 3. 存储与并发

`FileMemoryStore` 的三条硬规则 [F-051/F-052]：

1. **路径即键**：`permalink = places/家` → `<root>/places/家.md`；
2. **不能逃出根目录**：`fileFor` 用 canonical path 前缀校验，`../` 之类的 permalink 直接报错；
3. **原子写**：先写同目录临时文件并 `fd.sync()`，再 `ATOMIC_MOVE` 替换；文件系统不支持时退化为 `REPLACE_EXISTING`。写完把 mtime 设为 `clock()`，让索引知道这是新版本。

所有读写经 `Mutex` 串行化并切到 `Dispatchers.IO`，因此 UI 线程不会碰磁盘 [F-051]。

## 4. 索引：按 mtime/size 增量同步

`MemoryIndex.sync` 每次搜索前扫描根目录 [F-047]：

- 递归 `*.md`，跳过点开头的文件与目录（`.obsidian` 不会进索引）；
- 用 `lastModified + length` 判断文件是否变化，没变就复用缓存；
- 文件消失就从索引里移除；
- 标题权重 3.0、标签权重 2.0、正文 1.0。

这意味着用户在 Obsidian 里改完保存，PhonePal 下一次搜索就能看到，不需要「重新导入」或「重建索引」。

## 5. 中文检索：BM25 + 主词过滤

中文没有空格，直接按整串建索引会让「北京市海淀区」变成一个词。PhonePal 的 tokenizer 做了两件事 [F-049]：

| 文本 | 索引词 |
|---|---|
| `北京市海淀区` | 单字：北、京、市、海、淀、区；双字：北京、京市、市海、海淀、淀区 |
| `Wi-Fi 6` | `wi`、`fi`、`6`（非 CJK 连续字母数字小写） |

查询时的权重不同：**双字是主词 1.0，单字是弱词 0.3**；单字查询本身仍是主词。

排序用 BM25（`K1 = 1.2`、`B = 0.75`），并加两条短语加权：标题包含完整查询串 ×1.5，正文包含 ×1.2 [F-048]。

最关键的一行是**主词过滤**：

```kotlin
return scored.filter { it.primary }   // 只命中弱词的笔记不参与排序
```

没有这行，「你好」会把所有含「好」的笔记都拉进聊天提示词。有了这行，单字只在「同一篇笔记还命中了别的双字主词」时才有贡献 [F-048]。

## 6. 摘要怎么选

`Snippets.best` 逐行给每行打分（命中的查询词权重之和），取最高分那一行，最长 120 字符，按命中位置向两侧裁剪，并处理 UTF-16 代理对边界 [F-050]。所以聊天提示词里看到的是「最相关的一行」，而不是整篇笔记。

## 7. `howto`：把成功路径变成下次的提示

任务成功后，`PhonePalAgent.learn` 会写一条特殊笔记 [F-024]：

```markdown
## Observations
- [path] 打开高德 → 打车 → 输入目的地 → 快车 → 停在确认呼叫 #taxi-home
```

- permalink 是 `howto/<技能名或包名>`，`type = howto`；
- 下次同类任务开始前，先读该技能的 `howto/<name>`，再按目标搜索其他 `howto` 笔记，最多取 3 条、每条 800 字；
- 相同内容的路径不会重复追加。

注意它是「参考」而不是「脚本」：这些文本进入操作提示词的「以前成功的操作路径（仅供参考）」分节，模型仍要重新观察屏幕再决策 [F-029]。

## 8. 能力边界

| 能做 | 不能做 |
|---|---|
| 全库全文检索（标题/正文/观察/标签） | 语义检索/向量召回（没有 embedding） |
| 中文单字与双字召回 | 分词词典、同义词扩展 |
| 外部编辑后自动增量同步 | 多设备同步（目录在单机外部存储） |
| 真删除 + 自动清理空目录 | 软删除/回收站/版本历史 |

这些边界不是缺陷，而是「可读文件优先」的取舍：换来的是用户能直接看、直接改、直接备份。

## 相关概念

- [一轮聊天：记忆命中如何进入提示词](02-chat-and-tools.md)
- [技能与 flow：`memory` 字段引用哪些笔记](06-skills-and-flows.md)
- [工程模式：为什么选择文件而不是数据库](10-engineering-patterns.md)
- [信源登记](../references/00-source-inventory.md)
