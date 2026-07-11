---
id: "retrospective-mermaid-funnel-redesign-pdf-export-20260711"
title: "Mermaid五品漏斗图重绘与PDF导出任务复盘"
source: "../analysis-report.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/task-reports/retrospective-mermaid-funnel-redesign-pdf-export-20260711.toml"
maturity: "L1"
date: "2026-07-11"
tags: ["Mermaid", "PDF导出", "Playwright", "工具链", "Mermaid渲染"]
---

# Mermaid五品漏斗图重绘与PDF导出任务复盘

## 执行摘要

本次任务包含三个子任务：(1) 修正"工艺品"→"公益品"笔误；(2) 重新设计五品漏斗Mermaid图；(3) 将分析报告导出为PDF。任务总体顺利完成，但在PDF导出环节遇到了3个工具链问题，通过试错最终采用Pandoc+Mermaid.js+Playwright三段式方案成功导出含Mermaid渲染的A4 PDF（569KB）。

## 1. 事实还原

### 1.1 时间线

| 时间 | 事件 | 结果 |
|------|------|------|
| T0 | 用户指出"工艺品"应为"公益品" | 识别为源文件笔误（语音转写错误） |
| T1 | 修正报告中5处+源文件+spec.md+tasks.md | 7处修正完成，报告保留笔误说明 |
| T2 | 用户要求重绘Mermaid五品漏斗图 | 加载mermaid-cmd skill，召回黑白配色经验 |
| T3 | 遵循安全编码七规则重绘图表 | 5层subgraph信任分层、直线连接、渐变色系 |
| T4 | 运行check-mermaid.py | 发现其他2个Mermaid图有25个引号错误 |
| T5 | --fix自动修复所有引号问题 | 3个图全部0错误通过 |
| T6 | 用户要求导出PDF | 检查工具链：pandoc可用，无LaTeX/weasyprint/wkhtmltopdf |
| T7 | 初版Python markdown+Playwright方案 | Mermaid代码块未被识别为pre，渲染超时 |
| T8 | 改用pandoc转HTML | pandoc输出`<pre class="mermaid"><code>`格式正确 |
| T9 | 发现HTML实体编码问题 | `&#39;`导致mermaid init指令解析失败 |
| T10 | html.unescape()解码+wait_for_selector等待SVG | 3个Mermaid SVG全部检测到 |
| T11 | 生成PDF 569KB，清理临时文件 | 导出成功 |

### 1.2 产出物清单

| 文件 | 说明 |
|------|------|
| [analysis-report.md](../../../../../playground/reports/retrospective-yihuakaitian-meeting-20260711/analysis-report.md) | 修正笔误+优化Mermaid图后的报告（23.7KB） |
| [analysis-report.pdf](../../../../../playground/reports/retrospective-yihuakaitian-meeting-20260711/analysis-report.pdf) | A4格式PDF，含3个渲染好的Mermaid图表（569KB） |

### 1.3 问题记录

| 编号 | 问题 | 影响 | 修复方式 |
|------|------|------|---------|
| P1 | Python markdown库fenced_code扩展无法正确处理```mermaid代码块 | Mermaid块被转为内联code而非pre，无法渲染 | 切换为pandoc进行MD→HTML转换 |
| P2 | pandoc输出code块内容时HTML实体编码单引号为`&#39;` | Mermaid init配置中的`'theme':'base'`解析失败，图表无法渲染 | 使用`html.unescape()`解码mermaid代码块内容 |
| P3 | mermaid.run() Promise在SVG插入DOM前resolve | wait_for超时，Mermaid被认为渲染失败 | 改用`page.wait_for_selector('.mermaid svg')`轮询DOM状态 |
| P4 | 报告中另外2个Mermaid图（铁三角、五层架构）节点文本未加引号 | check-mermaid.py报告25个错误 | 使用--fix自动修复 |

## 2. 过程分析

### 2.1 做得好的地方

1. **遵循Mermaid安全编码七规则**：新写的五品漏斗图一次通过语法检查，中文文本全加双引号、使用`<br/>`换行、subgraph用英文ID、无空行
2. **召回经验避免重蹈覆辙**：利用ExperienceRecall召回黑白配色经验，在init中配置`curve:'linear'`强制直线，增大`nodeSpacing`/`rankSpacing`防止文字遮挡
3. **--fix自动修复存量问题**：运行check-mermaid.py时发现其他2个图的引号问题，顺势修复，提升了整体文档质量
4. **最终工具链选型正确**：在无LaTeX环境下，Pandoc+Mermaid.js CDN+Playwright的三段式方案成功实现了中文+Mermaid的PDF导出

### 2.2 问题根因分析

**P1+P2+P3都是PDF导出工具链的探索成本**：

- **根因1（工具选型熟悉度偏差）**：最初选择Python markdown库而非pandoc，是因为Python"看起来更可编程"，但pandoc作为专门的文档转换工具对Markdown fenced code的处理更标准。这是"熟悉度偏差"——倾向于用自己熟悉的通用工具而非领域专用工具。
- **根因2（HTML实体编码盲区）**：pandoc为了安全会对code块内的特殊字符做HTML实体转义，但这在需要将code内容交给Mermaid.js解析时造成了问题。这是"工具输出假设错误"——假设pandoc输出的HTML可以直接被下游JS消费，但实际需要额外的unescape处理。
- **根因3（异步渲染检测方法不当）**：依赖JS Promise回调来判断渲染完成，在无头浏览器环境中不可靠。这是"API语义理解偏差"——`.run()`的resolve代表"渲染流程已启动"而非"渲染已完成"。

### 2.3 瓶颈识别

- **中文PDF导出在Windows无LaTeX环境下无一键方案**：需要组装三段式工具链，这是当前项目的工具链缺口
- **Mermaid无头浏览器渲染检测**：必须依赖DOM状态轮询，不能依赖JS回调

## 3. 核心洞察

### 洞察1：工具选择的"熟悉度偏差"陷阱

当有多个工具可完成同一任务时，容易选择自己最熟悉的通用工具（如Python），而非领域专用工具（如pandoc）。通用工具虽然"可编程性强"，但领域专用工具对标准格式的处理更可靠，试错成本更低。

**规律**：文档格式转换类任务，优先选用pandoc；数据处理类任务优先选用Python；不要因为"更熟悉"而选择错误的工具类别。

### 洞察2：无头浏览器中渲染完成检测必须基于DOM状态

Mermaid.js等前端可视化库的API Promise通常只代表"任务已提交"，不代表"DOM已更新"。在Playwright/Puppeteer等无头浏览器自动化场景中，检测异步渲染完成的可靠方式是**轮询目标DOM元素出现**（`wait_for_selector`），而非依赖JS层面的回调标志。

**规律**：浏览器自动化中，"JS回调说完成了"≠"DOM真的渲染好了"。SVG/canvas等渲染结果以DOM元素存在为准。

### 洞察3：自动化检查是"免费"的质量提升机会

运行check-mermaid.py时发现了之前未被检测到的25个引号错误（在另外2个Mermaid图中）。如果只关注新写的图而不做全量检查，这些错误会继续潜伏。

**规律**：每次修改文档中的Mermaid代码后，都应该对整个文件（而非仅修改部分）运行自动化检查，往往能发现并修复存量问题。

## 4. 可复用模式萃取

### 模式：三段式中文Markdown+Mermaid→PDF导出法

| 属性 | 内容 |
|------|------|
| **模式名称** | 三段式中文PDF导出法（Three-Stage Mermaid-Aware PDF Export） |
| **成熟度** | L1（单次场景验证成功） |
| **适用场景** | Windows/Linux无LaTeX环境，需将含Mermaid图表的中文Markdown文档导出为PDF；Playwright可用 |
| **核心工具链** | Pandoc（MD→HTML）+ Mermaid.js CDN（浏览器端渲染）+ Playwright Chromium（HTML→PDF） |
| **核心步骤** | 1. Pandoc用`--syntax-highlighting=none`转HTML<br>2. 正则替换`<pre class="mermaid"><code>`为`<pre class="mermaid">`并`html.unescape()`解码内容<br>3. HTML模板内嵌Mermaid.js CDN+CSS中文字体样式<br>4. Playwright `page.goto(file://URL)` + `wait_for_selector('.mermaid svg')`等待渲染<br>5. `page.pdf()`打印为A4 PDF |
| **关键注意事项** | - 必须对mermaid代码块内容做html.unescape()，否则HTML实体会破坏Mermaid语法<br>- 等待渲染完成必须用DOM选择器（`.mermaid svg`），不能依赖JS Promise<br>- 需要`wait_until="networkidle"`等待Mermaid CDN加载<br>- CSS中文字体栈用：`"Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif` |

**模式验证证据**：本次导出3个Mermaid图表全部渲染为SVG，PDF大小569KB，中文正常显示，直线/渐变色样式保留。

## 5. 行动项

| 优先级 | 行动项 | 验收标准 |
|--------|--------|---------|
| 🟡 中 | 将三段式PDF导出脚本封装为.agents/scripts/export-md-to-pdf.py | 任意含Mermaid的中文MD文件可一键导出PDF，脚本有--help参数 |
| 🟢 低 | 后续新写Mermaid图时全量运行check-mermaid.py检查整个文件 | 形成习惯，不跳过 |

## 6. 经验关联

- 关联模式：[mermaid-safe-coding-rules.md](../../patterns/code-patterns/mermaid-safe-coding-rules.md)（验证了安全编码规则的有效性）
- 关联经验：Mermaid黑白配色经验（Experience 1073667，init配置curve:linear解决曲线遮挡）
- 待沉淀：三段式PDF导出法可进一步验证后升级为L2模式并加入脚本库
