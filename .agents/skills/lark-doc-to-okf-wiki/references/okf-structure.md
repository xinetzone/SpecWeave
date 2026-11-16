# OKF 知识包结构、frontmatter 与台账

## 1. 七件套

| 目录/文件 | 职责 | 最小要求 |
|---|---|---|
| `index.md` | Bundle 入口：定位、阅读路径、结论、toctree、元信息 | 3 条以上可追溯的结论 |
| `quickstart.md` | 5 分钟速查 | 骨架表 + 清单 + 坑 |
| `concepts/` | 每篇一个模式或主题 | 含 `index.md` 索引 |
| `examples/` | 可直接套用的模板/对照/蓝图 | 含 `index.md` 索引 |
| `references/` | 原文台账 + 核验口径 | 含来源、局限、复核触发 |
| `_spec/` | `facts.md`（R 阶段）+ `log.md`（链路与门） | 事实 ≥20，无因果词 |
| `assets/` | 本地图片 | 文件名语义化 |

## 2. frontmatter 模板

**index.md（Bundle）**

```yaml
---
okf_version: "0.2"
type: Bundle
title: <主题> · OKF 知识包
description: <一句话说明覆盖范围与产出>
tags: [<tag1>, <tag2>]
generated: { by: "agent:<skill-or-flow>", at: 2026-01-01 }
verified: { by: "process:seven-concepts-V", at: 2026-01-01 }
status: stable
stale_after: 2027-01-01
sensitivity: private
source:
  type: lark-docx
  url: <doc-url>
  title: <document title>
  revision_id: 1234
  fetched_at: 2026-01-01
  whiteboards: 6
---
```

**concepts/*.md**

```yaml
---
okf_version: "0.2"
type: Concept
title: <结论式标题>
description: <这篇回答什么>
tags: [<tag>]
generated: { by: "agent:<flow>", at: 2026-01-01 }
verified: { by: "process:seven-concepts-V", at: 2026-01-01 }
status: stable
source: "<来源文档标识>"
---
```

要点：

- `source` 若为中文散文，不要夹 `/`、`.md`、`.toml` 片段——链接门会把它当路径去解析并报断链。
- 私域包加 `sensitivity: private`；公开包可省略。
- `stale_after` 按主题时效设定（技术类 3-6 个月）。

## 3. 事实台账（facts.md）

格式：

| F 编号 | 事实 | 核验 |
|---|---|---|
| F-001 | 文档含 6 个 whiteboard 块，位置依次为… | ✅ |
| F-002 | 第 3 章把提问归为 7 件事并编号 1-7 | 📐 |

规则：

1. 一行一条，可复核，不含判断与因果。
2. 核验图例固定三种：✅ 原文可复核 ｜ 📐 画板节点/预览判读 ｜ 💬 评论区可见；口径存疑用 ⚠️ 并在 references 说明。
3. 文件末尾必须有**计数核对表**，与正文、索引三处一致。

## 4. 索引与导航

- `concepts/index.md`、`examples/index.md`、`references/index.md` 各给一张"文章 → 回答什么问题"的表 + toctree。
- `index.md` 的阅读路径用 Mermaid，节点数控制在 10 个以内，避免图比内容长。

## 5. 双门验收

```bash
# 链接门：0 断链、0 警告
python .agents/scripts/check-links.py --path <package-dir>

# 结构门（可选）：Sphinx 构建若启用 toctree，按项目约定验证
```

计数机械比对清单：

| 计数项 | 出现位置 | 必须一致 |
|---|---|---|
| 一级标题数 | facts / references / 正文 | ✅ |
| 画板数 | facts / references / 正文引用 | ✅ |
| 表格/代码块/媒体数 | facts 计数表 | ✅ |
| 事实条数 | facts 标题 / index 元信息 | ✅ |

## 6. 交付报告模板

| 项目 | 内容 |
|---|---|
| 产出路径 | 包根目录 |
| 文件数 | Markdown 数 / 图片数（是否入库） |
| 敏感度 | private / public，落盘位置 |
| 事实台账 | N 条，核验来源分布 |
| 门禁 | 链接门结果、计数比对结果 |
| 遗留 | 判读局限、未验证项、需复核触发条件 |
