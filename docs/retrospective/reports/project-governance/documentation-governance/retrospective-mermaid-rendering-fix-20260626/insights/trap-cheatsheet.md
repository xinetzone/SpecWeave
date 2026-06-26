+++
id = "mermaid-trap-cheatsheet"
date = "2026-06-26"
type = "reference-card"
scope = "mermaid"
source = "../insight-extraction.md#三"
+++

# Mermaid 陷阱速查表

> 快速查阅卡片：编写 Mermaid 时遇到渲染问题，对照此表逐一排查。

## 陷阱清单

| 陷阱 | 错误示例 | 正确写法 | 错误现象 |
|------|---------|---------|---------|
| Subgraph 间空行 | `end\n\nsubgraph` | `end\nsubgraph` | 渲染失败，后续内容丢失 |
| 节点文本"数字.空格"触发列表 | `A[1. 启动]` 或 `A["1. 启动"]` | `A["1：启动"]`（中文冒号） | "Unsupported markdown: list" |
| 边标签含@未加引号 | `-->|@role|` | `-->|"@role"|` | 语法解析错误 |
| 中文 Subgraph 裸 ID | `subgraph 感知层` | `subgraph S1 ["感知层"]` | Subgraph 无法渲染/连线失效 |
| Style 前有空行 | `--> E\n\nstyle A` | `--> E\nstyle A` | Style 被忽略或解析失败 |
| 边标签含中文无引号 | `-->|数据|` | `-->|"数据"|` | 部分渲染器解析失败 |
| 全角冒号在 ID 中 | `subgraph 角色：架构师` | `subgraph ARCH ["角色：架构师"]` | Subgraph 渲染失败 |
| Mermaid 代码块内空行 | 任意空行 | 不使用空行 | 解析器误判图表结束 |

## 快速排查流程

遇到渲染问题时，按以下顺序检查：

1. 代码块内有无空行？→ 删除所有空行
2. Subgraph ID 是否为纯英文？→ 改为 `ID ["标题"]` 格式
3. 节点文本是否含「数字.空格」「- 空格」「* 空格」？→ 改用中文冒号或去除空格
4. 边标签含中文/特殊字符是否加引号？→ 使用 `-->|"标签"|`
5. Style 语句前是否有空行？→ 删除空行
6. 运行自动化检查：`python .agents/scripts/check-mermaid.py`

## 相关规则

- 详细规则说明：[README.md](README.md) 中的五规则速查表
- 分层排查法：[insight-06-layered-verification.md](insight-06-layered-verification.md)

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
