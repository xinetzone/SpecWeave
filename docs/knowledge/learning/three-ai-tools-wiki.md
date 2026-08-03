---
title: "三个热门AI工具：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill"
source: "微信公众号文章（逛逛GitHub）"
date: "2026-07-04"
tags: ["ai-tools", "intelligent-terminal", "claudian", "book-to-skill", "ai-agent", "terminal", "obsidian", "claude-code", "agent-skills"]
---

# 三个热门AI工具学习Wiki

## 目录导航

- [文章概述](#文章概述)
- [工具一：intelligent-terminal（微软AI终端）](#工具一intelligent-terminal微软ai终端)
  - [项目定位](#项目定位)
  - [核心功能](#核心功能)
  - [技术亮点](#技术亮点)
  - [系统要求与安装](#系统要求与安装)
  - [适用人群](#适用人群)
- [工具二：Claudian（Obsidian+Claude Code插件）](#工具二claudianobsidianclaude-code插件)
  - [项目定位](#项目定位-1)
  - [核心价值](#核心价值)
  - [功能特性](#功能特性)
  - [社区热度](#社区热度)
  - [适用人群](#适用人群-1)
- [工具三：book-to-skill（技术书籍转AI Skill）](#工具三book-to-skill技术书籍转ai-skill)
  - [项目定位](#项目定位-2)
  - [核心思想：与RAG的本质差异](#核心思想与rag的本质差异)
  - [金句解读](#金句解读)
  - [基准测试数据](#基准测试数据)
  - [成本分析](#成本分析)
  - [使用方法](#使用方法)
- [对比分析](#对比分析)
  - [9维度对比表格](#9维度对比表格)
- [技术趋势分析](#技术趋势分析)
  - [趋势一：终端AI化](#趋势一终端ai化)
  - [趋势二：知识工具Agent化](#趋势二知识工具agent化)
  - [趋势三：知识结构化](#趋势三知识结构化)
- [内容评估](#内容评估)
- [常见问题解答（FAQ）](#常见问题解答faq)
- [资源链接](#资源链接)

---

## 文章概述

本文来自"逛逛GitHub"微信公众号，介绍了近期GitHub上三个热门的AI开源工具：

1. **intelligent-terminal**：微软在Build 2026发布的Windows Terminal实验分支，原生集成AI Agent
2. **Claudian**：Obsidian插件，将Claude Code深度嵌入笔记库，7个月获得1.3万Star
3. **book-to-skill**：将技术书籍编译成Agent Skills，2个月获得6.8k Star，token消耗节省15.6倍

这三个工具分别代表了AI工具发展的三个重要方向：终端AI化、知识工具Agent化、知识结构化。

原文链接：https://mp.weixin.qq.com/s/gFlPzfjpY8zs3tOcw3o5Lg

---

## 工具一：intelligent-terminal（微软AI终端）

### 项目定位

intelligent-terminal是微软在Build 2026上发布的Windows Terminal实验分支，核心创新是将AI Agent原生集成进命令行终端。用户无需在聊天窗口和终端之间反复切换，Agent可以直接监控Shell输出并提供即时帮助。

作为微软官方出品的工具，其最大特点是对所有主流Agent CLI一视同仁地支持，这在微软产品中较为少见。

### 核心功能

1. **Agent面板**
   - 停靠式上下文面板，自动读取Shell输出
   - 快捷键：`Ctrl+Shift+.` 一键唤起
   - 无需切换窗口即可与Agent交互

2. **错误自动检测**
   - 命令执行失败时，状态栏指示灯亮起
   - 快捷键：`Ctrl+Alt+.` 将错误上下文直接发送给Agent
   - Agent可以解释错误原因或直接修复问题

3. **协议无关设计**
   - 基于Agent Client Protocol（ACP）
   - 未来接入新的Agent几乎零成本
   - 开放协议设计，支持生态扩展

### 技术亮点

- **多Agent平等支持**：原生支持Copilot、Claude Code、OpenAI Codex、Gemini CLI，也支持本地自建Agent
- **本地传输层**：仅作为本地传输层，不直接调用云API
- **数据自主**：不持久化会话数据，数据走向完全由用户选择的Agent决定
- **架构简洁**：底层设计干净，职责单一，只做Agent与终端的连接层

### 系统要求与安装

**系统要求**：
- 仅支持 Windows 11 22H2 及以上版本

**安装命令**：
```bash
winget install --id Microsoft.IntelligentTerminal -e
```

**开源地址**：https://github.com/microsoft/intelligent-terminal

### 适用人群

- Windows 11用户
- 日常高频使用Shell/命令行的开发者
- 需要在终端中快速获得AI帮助的运维人员
- 多Agent CLI用户（同时使用Copilot、Claude Code等）

---

## 工具二：Claudian（Obsidian+Claude Code插件）

### 项目定位

Claudian是中文博主Jackywine开发的Obsidian插件，它将Claude Code深度嵌入Obsidian笔记库，让整个vault（笔记库）直接变成Agent的工作目录。

### 核心价值

在Claudian出现之前，Obsidian用户要使用Claude Code，大多需要依赖Terminal类插件，体验非常糟糕。Claudian解决了这个痛点，实现了在笔记软件内的AI Coding闭环。

### 功能特性

- **侧边栏集成**：Agent直接嵌入Obsidian侧边栏，无需切换应用
- **文件读写**：Agent可以直接读写笔记库中的文件
- **搜索功能**：在笔记库内进行全文搜索
- **跑bash命令**：直接在笔记环境中执行bash命令
- **多步工作流**：支持复杂的多步骤工作流，全在笔记库内闭环完成

### 社区热度

- **Star数据**：7个月拿下1.3万Star
- **社区地位**：已经成为Obsidian社区最火的AI插件之一
- **开发者背景**：中文博主Jackywine的作品

### 适用人群

- Obsidian重度用户
- 使用Claude Code进行AI Coding的开发者
- 希望在笔记环境中完成知识管理+编码工作流的用户
- 个人知识库与AI编码深度结合的实践者

**开源地址**：https://github.com/YishenTu/claudian

---

## 工具三：book-to-skill（技术书籍转AI Skill）

### 项目定位

book-to-skill能够将任意技术书籍编译成符合Agent Skills开放标准的结构化技能。当用户使用Claude Code、Codex等工具时，AI可以按章节即时调用书中的知识，而不是简单地检索原文片段。

### 核心思想：与RAG的本质差异

| 维度 | RAG（检索增强生成） | book-to-skill |
|------|---------------------|---------------|
| 处理时机 | 查询时实时处理 | 编译时一次性处理 |
| 处理方式 | 向量相似度搜索 | 深度挖掘作者知识框架 |
| 输出结果 | 返回原文片段 | 输出可推理的结构化知识 |
| 理解深度 | 表层匹配 | 理解框架、命名方法、反模式 |

作者的核心洞察是：RAG就像是在书架上找书（indexes a shelf），而book-to-skill是真正掌握了一本书的精髓（masters a spine）。

### 金句解读

> **"RAG indexes a shelf, book-to-skill masters a spine."**
>
> —— book-to-skill 作者

这句话精准概括了两种技术路线的本质区别：
- RAG是索引层面的匹配，知道"知识在哪里"
- book-to-skill是理解层面的掌握，知道"知识怎么用"

### 基准测试数据

作者提供的基准测试数据（基于256K token的技术书籍）：

| 方案 | 单题发现循环token消耗 | 相对倍数 |
|------|----------------------|----------|
| 全上下文塞入 | 77,866 token | 15.6倍 |
| book-to-skill | 5,000 token | 1倍 |

**结论**：使用skill后token消耗节省15.6倍。

### 成本分析

- **一次性编译成本**：单本书约1美元（使用Sonnet 4.5）
- **后续查询成本**：每次查询固定约5,000 token
- **性价比**：对于需要频繁参考某本书的场景，长期使用成本优势明显

### 使用方法

```bash
git clone https://github.com/virgiliojr94/book-to-skill.git ~/.claude/skills/book-to-skill/book-to-skill 你书籍的地址
```

**开源地址**：https://github.com/virgiliojr94/book-to-skill

**Star数据**：2个月破6.8k Star

---

## 对比分析

### 9维度对比表格

| 对比维度 | intelligent-terminal | Claudian | book-to-skill |
|---------|---------------------|----------|---------------|
| **工具定位** | AI原生终端（Windows Terminal实验分支） | Obsidian+Claude Code集成插件 | 技术书籍→Agent Skills编译器 |
| **出品方/作者** | 微软（Microsoft官方） | 中文博主Jackywine | virgiliojr94 |
| **发布场景** | Build 2026 | X平台（推特）推广 | GitHub开源 |
| **Star增长** | 微软官方项目（未提及具体Star） | 7个月1.3万Star | 2个月6.8k Star |
| **技术路线** | ACP协议+本地传输层+多Agent支持 | Obsidian插件+侧边栏嵌入+vault作为工作目录 | 编译时结构化+Agent Skills标准+可推理结构 |
| **核心价值** | 终结终端与聊天窗口切换，错误一键修复 | 笔记库内AI Coding闭环，替代蹩脚Terminal插件 | token消耗降15.6倍，从检索到真正掌握 |
| **平台要求** | Win11 22H2+ | Obsidian（跨平台） | Claude Code/Codex等支持Skills的Agent |
| **适用人群** | Windows终端重度用户 | Obsidian+Claude Code用户 | 需要深度使用技术书籍的开发者 |
| **代表趋势** | 终端AI化 | 知识工具Agent化 | 知识结构化 |

---

## 技术趋势分析

从这三个工具可以观察到AI工具生态发展的三个重要趋势：

### 趋势一：终端AI化

**代表工具**：intelligent-terminal

**核心特征**：
- AI不再是独立的聊天窗口，而是原生嵌入工作环境
- Agent能够实时感知上下文（Shell输出、错误状态）
- 快捷键唤起、错误自动检测等设计体现"AI在身边"而非"AI在对面"
- 协议标准化（ACP）让终端成为Agent的通用宿主

**发展方向**：未来的开发环境不再是"人找AI"，而是"AI在人工作的地方随时待命"。命令行作为开发者最核心的工作界面之一，其AI原生改造具有标志性意义。

### 趋势二：知识工具Agent化

**代表工具**：Claudian

**核心特征**：
- 笔记软件不再是单纯的"信息容器"，而是Agent的"工作区"
- Agent拥有对知识库的完整读写、搜索、执行权限
- 工作流在单一工具内闭环：记录→思考→编码→验证
- 个人知识库与AI Coding深度融合

**发展方向**：知识管理工具正在从"被动存储"向"主动工作"演进。Obsidian作为本地优先、高度可扩展的笔记工具，成为Agent的理想工作目录，这预示着未来PKB（Personal Knowledge Base）将成为每个人的AI工作主界面。

### 趋势三：知识结构化

**代表工具**：book-to-skill

**核心特征**：
- 从RAG的"片段检索"进化到"编译式理解"
- 知识处理从查询时前移到编译时，一次性深度加工
- 输出符合开放标准的可推理结构，而非原始文本
- token效率大幅提升（15.6倍）预示着成本结构的改变

**发展方向**：RAG解决了"能不能找到"的问题，book-to-skill解决了"会不会用"的问题。未来的知识处理将更加注重理解深度和推理能力，知识编译（Knowledge Compilation）可能成为一个重要的技术方向。与软件编译类似，一次编译、多次高效使用。

---

## 内容评估

### 准确性评估

- **信息来源可靠**：intelligent-terminal来自GitHub Trending（微软官方仓库），Claudian来自X平台中文博主推广，book-to-skill来自GitHub开源社区
- **数据可验证**：Star数量、token数据、安装命令、快捷键等均可通过GitHub仓库验证
- **客观性**：文章既介绍亮点，也指出劝退点（如intelligent-terminal只支持Win11 22H2+）

**准确性评分**：★★★★★（5/5）

### 实用性评估

- **每个工具都提供了明确的安装方法**：winget命令、git clone命令
- **适用场景清晰**：明确指出了每个工具的目标用户
- **快捷键、系统要求等关键信息齐全**：用户可以直接上手
- **不足**：Claudian未提供具体安装步骤，book-to-skill的书籍格式要求未说明

**实用性评分**：★★★★☆（4/5）

### 创新性评估

- **三个工具分别代表三个不同方向**：没有同质化
- **技术路线有新意**：特别是book-to-skill的"编译式"vs RAG的"检索式"对比
- **微软的开放态度值得关注**：多Agent平等支持在微软产品中少见
- **中文开发者作品登上国际舞台**：Claudian的成功有激励意义

**创新性评分**：★★★★★（5/5）

---

## 常见问题解答（FAQ）

### Q1：intelligent-terminal只支持Windows吗？有没有macOS/Linux版本？

**A**：根据原文信息，intelligent-terminal目前仅支持Win11 22H2+。这是Windows Terminal的实验分支，微软未提及macOS/Linux版本计划。不过由于它基于ACP开放协议，理论上未来可能有跨平台实现，或者其他终端模拟器会借鉴这个思路。

### Q2：Claudian必须使用Claude Code吗？能不能用其他AI模型？

**A**：根据原文，Claudian的定位是"在Obsidian里最便捷最强大地使用Claude Code"，从命名和描述来看它是与Claude Code深度集成的。原文未提及是否支持其他模型，建议查看项目GitHub仓库获取最新信息。

### Q3：book-to-skill支持哪些书籍格式？PDF、EPUB都可以吗？

**A**：原文未明确说明支持的书籍格式。从使用命令来看，它接受"你书籍的地址"作为参数，具体格式支持需要查看项目文档。这是一个相对早期的项目（2个月6.8k Star），格式支持可能在持续完善中。

### Q4：三个工具可以组合使用吗？

**A**：理论上可以形成有趣的组合：
- 在intelligent-terminal中使用Claude Code
- Claudian已经把Claude Code嵌进Obsidian
- book-to-skill编译的技能可以被Claude Code调用

也就是说，你甚至可以在intelligent-terminal里启动Claude Code，让它调用book-to-skill编译的技能，同时Claudian在Obsidian里管理整个过程的笔记。不过这是推测性的组合，原文并未提及这种用法。

### Q5：ACP（Agent Client Protocol）是什么协议？和LSP有关系吗？

**A**：原文提到intelligent-terminal基于Agent Client Protocol（ACP），这是一个用于Agent与客户端通信的开放协议。从设计理念上看，它和LSP（Language Server Protocol）有相似之处——都是通过标准化协议实现"一次实现，多处接入"。LSP标准化了编辑器与语言服务器的通信，ACP可能正在标准化终端/客户端与Agent的通信。

### Q6：book-to-skill与RAG是互斥的吗？

**A**：不是互斥关系，而是适用场景不同。对于临时查阅、大规模知识库等场景，RAG仍然是合适的选择；对于需要深度掌握某本书的知识体系、频繁参考、追求token效率的场景，book-to-skill的编译式方法更有优势。两者可以互补使用。

---

## 资源链接

### 原文来源
- 微信公众号文章：https://mp.weixin.qq.com/s/gFlPzfjpY8zs3tOcw3o5Lg
- 来源公众号：逛逛GitHub

### 工具GitHub仓库
- intelligent-terminal（微软AI终端）：https://github.com/microsoft/intelligent-terminal
- Claudian（Obsidian插件）：https://github.com/YishenTu/claudian
- book-to-skill（书籍转Skill）：https://github.com/virgiliojr94/book-to-skill

### 相关概念参考
- Agent Client Protocol（ACP）：intelligent-terminal所采用的开放协议
- Agent Skills开放标准：book-to-skill编译输出所遵循的标准
- Claude Code：Anthropic推出的AI编码工具
- Windows Terminal：微软官方的现代化终端应用
- Obsidian：本地优先的Markdown笔记工具
