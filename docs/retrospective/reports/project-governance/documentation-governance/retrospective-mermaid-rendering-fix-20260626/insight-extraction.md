+++
id = "insight-extraction"
source = "retrospective-mermaid-rendering-fix-20260626/README.md"
atomized = true
atomized_date = "2026-06-26"
insights_dir = "insights/"
+++

# 洞察萃取：Mermaid 安全编码规则

> ✅ **原子化归档完成**：本文件洞察内容已拆分为 7 个独立原子洞察文件和 1 份参考卡片，存放在 [insights/](insights/) 目录。
>
> 本文件保留为导航索引，与现有模式的关系保留于此，详细洞察内容请查阅各原子文件。

---

## 核心洞察导航

| 编号 | 洞察标题 | 原子文件 | 类型 |
|------|---------|---------|------|
| 01 | Mermaid 代码块内禁止空行——空行是语法元素而非排版元素 | [insights/insight-01-no-blank-lines.md](insights/insight-01-no-blank-lines.md) | 规则1 |
| 02 | 非纯英文单词的节点/边标签一律用双引号包裹 | [insights/insight-02-quote-principle.md](insights/insight-02-quote-principle.md) | 规则2 |
| 03 | 双引号不能阻止 Markdown 解析，须从内容层面避免列表触发模式 | [insights/insight-03-markdown-list-avoidance.md](insights/insight-03-markdown-list-avoidance.md) | 发现+规则2b |
| 04 | Subgraph 统一使用英文 ID + `["中文标题"]` 格式 | [insights/insight-04-subgraph-format.md](insights/insight-04-subgraph-format.md) | 规则3 |
| 05 | 边标签使用 `-->|"标签"|` 格式，中文/特殊字符双引号包裹 | [insights/insight-05-edge-label-format.md](insights/insight-05-edge-label-format.md) | 规则4 |
| 06 | 修复验证分层法——先修结构、后验内容，预期错误层层暴露 | [insights/insight-06-layered-verification.md](insights/insight-06-layered-verification.md) | 发现+方法（规则5） |
| 07 | 渲染器容错度差异导致"本地正常、线上失败"，应遵循最严规范 | [insights/insight-07-renderer-tolerance.md](insights/insight-07-renderer-tolerance.md) | 发现 |
| 参考 | 8 类常见 Mermaid 陷阱速查卡 | [insights/trap-cheatsheet.md](insights/trap-cheatsheet.md) | 参考卡片 |

完整索引见：[insights/README.md](insights/README.md)

---

## 五规则速查

| 规则 | 一句话总结 | 详细 |
|------|-----------|------|
| 规则1 | 代码块内禁止空行 | [insight-01](insights/insight-01-no-blank-lines.md) |
| 规则2 | 非纯英文文本双引号包裹 | [insight-02](insights/insight-02-quote-principle.md) |
| 规则2b | 避免「数字.空格」「- 空格」等列表触发模式 | [insight-03](insights/insight-03-markdown-list-avoidance.md) |
| 规则3 | Subgraph 用 `ID ["标题"]` 格式 | [insight-04](insights/insight-04-subgraph-format.md) |
| 规则4 | 边标签用 `-->|"标签"|` 格式 | [insight-05](insights/insight-05-edge-label-format.md) |
| 规则5 | 按「结构→Subgraph→文本→标签→Style」五层排查 | [insight-06](insights/insight-06-layered-verification.md) |

---

## 与现有模式的关系

本次洞察补充了现有 [mermaid-layered-visualization.md](../../../../patterns/methodology-patterns/mermaid-layered-visualization.md) 模式中未覆盖的安全编码细节。该模式侧重于 Mermaid 的分层可视化架构设计，本次新增的是**语法安全层**的编码规则，两者互补：

| 维度 | 现有模式（mermaid-layered-visualization） | 本次新增洞察 |
|------|------------------------------------------|------------|
| 关注点 | 图表结构设计、分层策略 | 语法安全、陷阱规避 |
| 解决问题 | "画什么、怎么分层" | "怎么写才能不渲染失败" |
| 关系 | 架构层设计规范 | 语法层编码规范，互补 |

分层错误屏蔽概念（见 [insight-06](insights/insight-06-layered-verification.md)）是一个具有普遍意义的调试元模式，可考虑补充到 root-cause-diagnosis 模式中。详见 [export-suggestions.md#现有模式更新](export-suggestions.md)。

---

## 原子化说明

- **拆分时间**：2026-06-26
- **拆分策略**：按主题（topic）拆分，每条核心发现/规则独立成文
- **原子文件数**：7 个洞察文件 + 1 个参考卡片 + 1 个索引文件
- **内容完整性**：原始洞察内容无丢失，全部迁移至对应原子文件
- **链接维护**：所有交叉引用已更新为相对路径

---
*所属报告：[Mermaid 渲染问题修复复盘](README.md)*
