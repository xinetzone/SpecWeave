---
id: "subagent-output-quality-checklist"
title: "通用子代理输出质量校验清单"
source: "retrospective-sunlogin-bootbox-analysis-20260704"
x-toml-ref: "../../.meta/toml/.agents/templates/subagent-output-quality-checklist.toml"
---
# 通用子代理输出质量校验清单

> 基于向日葵开机盒子分析任务中发现的"子代理误将TodoWrite工具标签写入文档"问题萃取，适用于所有使用`general_purpose_task`委托子代理的场景（文档编写、代码修改、分析报告等），防止工具调用标签污染产出物。
>
> 与 [subagent-wiki-delivery-checklist.md](subagent-wiki-delivery-checklist.md) 的区别：本清单是通用型检查，适用于所有子代理任务；后者是wiki创作专用检查，包含更多wiki特有的frontmatter/编号/TOML检查。

---

## 🔒 子代理委托Query强制约束（P0级）

**每次调用`general_purpose_task`时，必须在query末尾附加以下内容（根据任务类型裁剪）：**

```
【输出格式强制约束 - 必须遵守】

1. 内容纯净性：你输出的所有内容都将直接写入文档/代码，绝对禁止包含任何工具调用格式，包括但不限于：
   - 禁止<seed:tool_call>、<function>、<parameter>等XML工具调用标签
   - 禁止出现TodoWrite、Read、Write、Edit、Grep、Shell等工具名称
   - 禁止出现toolcall_result、toolcall_status等系统标签
   - 禁止出现<system-reminder>、<available_skills>、<toolcall_result>等上下文标签
   - 输出内容应该是纯粹的文档正文/代码，不包含任何工具调用或系统提示格式

2. 单一职责：本次任务只完成<描述具体任务>，不要执行额外操作
```

---

## ✅ 子代理交付前自检（子代理应执行）

子代理在标记任务完成前，应快速确认：
- [ ] 输出中没有`<seed:tool_call>`标签
- [ ] 输出中没有`<function `或`<parameter `标签
- [ ] 输出中没有`TodoWrite`、`toolcall_result`、`toolcall_status`等工具相关字符串出现在正文上下文中
- [ ] 输出内容直接是最终交付物，不需要主代理再做清理

---

## 🔍 主代理验收检查（接收子代理产出后必须执行）

**检查方法**：使用Grep工具扫描子代理修改/创建的文件，搜索以下关键词：

| # | 搜索关键词 | 说明 | 发现问题后的处理 |
|---|-----------|------|----------------|
| 1 | `<seed:tool_call>` | 工具调用起始标签 | 立即删除整个标签块及被污染的段落 |
| 2 | `<function ` | 函数调用标签 | 检查是否为误插入的工具调用，若是则删除 |
| 3 | `<parameter ` | 参数标签 | 同上 |
| 4 | `TodoWrite` | 待办工具名（需上下文判断，代码注释中出现是合法的） | 正文/Markdown文档中出现则删除 |
| 5 | `toolcall_result` | 工具结果标签 | 立即删除 |
| 6 | `toolcall_status` | 工具状态标签 | 立即删除 |
| 7 | `<system-reminder>` | 系统提醒标签 | 立即删除 |

**P1级 - 长文档多轮委托专项检查**：

当一个文档经过多轮子代理分批编写后，不仅要检查新增部分，还要对整个文档做一次全量扫描（之前轮次的子代理可能在之前的批次中也插入了标签）。Grep命令示例：

```
Grep pattern: <seed:tool_call>|TodoWrite|<function |toolcall_result
Path: 目标文件
output_mode: content
-n: true
```

**验收耗时**：单个文件10秒；长文档全量扫描30秒。
**重要性**：如果不做此检查，被污染的标签会进入版本控制，后续阅读文档时会出现奇怪的工具调用代码块，严重影响文档质量。

---

## 📋 通用质量检查项（根据任务类型选用）

除了内容纯净性外，根据子代理任务类型，还应检查：

### 文档编写类任务
- [ ] 标题层级正确（从h1开始，不跳级）
- [ ] frontmatter格式正确（如果有）
- [ ] 列表和表格格式渲染正常
- [ ] 段落衔接自然，无重复内容
- [ ] 章节编号连续（如果使用编号）

### 代码修改类任务
- [ ] 修改后的代码语法正确（无明显语法错误）
- [ ] 没有遗留的调试代码（print语句、console.log、注释掉的代码块）
- [ ] 变量命名与文件现有风格一致
- [ ] 没有硬编码的敏感信息（密钥、密码、token）

### 分析报告类任务
- [ ] 结论有事实/数据支撑
- [ ] 引用的信息准确
- [ ] 逻辑结构清晰
- [ ] 改进建议可行动

---

## 🔗 关联参考

- [subagent-wiki-delivery-checklist.md](subagent-wiki-delivery-checklist.md) - Wiki创作专用检查清单（含frontmatter/编号/TOML检查）
- [retrospective-sunlogin-bootbox-analysis-20260704](../../docs/retrospective/reports/competitive-analysis/retrospective-sunlogin-bootbox-analysis-20260704/) - 本清单的来源复盘报告

## Changelog

- **v1.0.0** (2026-07-04): 初始版本，基于向日葵开机盒子分析任务复盘萃取，核心解决子代理误插入工具调用标签污染文档的问题
