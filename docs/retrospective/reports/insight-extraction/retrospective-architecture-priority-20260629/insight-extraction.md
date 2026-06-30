+++
id = "architecture-priority-insight-extraction"
date = "2026-06-29"
type = "insight-extraction"
source = "README.md#核心洞察"
maturity = "L2"
+++

# 架构评估深层洞察萃取

本文件为索引页，6 个独立洞察已原子化拆分至 `insights/` 子目录。

## 📂 洞察索引

| 洞察 | 主题 | 可复用模式 | 文件 |
|------|------|-----------|------|
| **洞察 A** | 规范成熟度与可发现性呈反比 | 渐进式披露架构（Progressive Disclosure Architecture） | [insights/insight-a-progressive-disclosure-architecture.md](insights/insight-a-progressive-disclosure-architecture.md) |
| **洞察 B** | Human-First 文档天然不是 Agent-First 服务 | Markdown即接口（Markdown-as-Interface） | [insights/insight-b-markdown-as-interface.md](insights/insight-b-markdown-as-interface.md) |
| **洞察 C** | 架构重构应该从"瓶颈层"开始，而非"最容易改的层" | 瓶颈优先重构法（Bottleneck-First Refactoring） | [insights/insight-c-bottleneck-first-refactoring.md](insights/insight-c-bottleneck-first-refactoring.md) |
| **洞察 D** | 不重构决策的价值被严重低估 | 不重构清单（No-Touch List） | [insights/insight-d-no-touch-list.md](insights/insight-d-no-touch-list.md) |
| **洞察 E** | 三角验证法本身需要三角验证 | 架构决策三角验证（Architecture Triangulation） | [insights/insight-e-architecture-triangulation.md](insights/insight-e-architecture-triangulation.md) |
| **洞察 F** | 自我演进模块的实现时机被重新定义 | 元能力依赖倒置（Meta-Capability Inversion） | [insights/insight-f-meta-capability-inversion.md](insights/insight-f-meta-capability-inversion.md) |

## 概要

6 个架构洞察从 SpecWeave 当前架构成熟度评估与 Firecrawl 标杆对照中萃取，涵盖：
- **架构设计**：渐进式披露、瓶颈优先重构
- **接口设计**：Markdown即接口
- **决策方法**：架构三角验证、不重构清单
- **演进顺序**：元能力依赖倒置
